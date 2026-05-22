"""
TikTokShadowBanClient — synchronous wrapper around the Apify
``apivault_labs/tiktok-shadow-ban-checker`` actor.

The actor handles all heavy work (residential proxy rotation, multiple HTML
fetch strategies, embedded-JSON parsing, shadow-ban signal aggregation, health
score, engagement-rate computation and actionable recommendations) on Apify
infrastructure. This client forwards inputs, polls until the run finishes, then
downloads the dataset and splits it into per-video records and the optional
batch summary.

Usage:

    from tiktok_shadowban_checker import TikTokShadowBanClient

    client = TikTokShadowBanClient(api_token="apify_api_xxxxxx")

    # Check specific video URLs
    results, summary = client.check_urls([
        "https://www.tiktok.com/@tiktok/video/7480279424202575159",
        "https://vm.tiktok.com/abc123/",
    ])
    for r in results:
        for rec in r.get("recommendations", []):
            print(rec)

    # Or paste a multi-line block of URLs
    results, summary = client.check_text(
        '''
        https://www.tiktok.com/@a/video/1
        https://www.tiktok.com/@b/video/2
        '''
    )
"""

from __future__ import annotations

import os
import re
import time
from typing import Any, Iterable, Sequence

import requests

from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    TikTokShadowBanError,
)


ACTOR_ID = "apivault_labs~tiktok-shadow-ban-checker"
APIFY_API_BASE = "https://api.apify.com/v2"

TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}

PRICE_PER_CHECK_USD = 0.01


class TikTokShadowBanClient:
    """Synchronous client for the TikTok Shadow Ban Checker Apify actor.

    Parameters
    ----------
    api_token : str, optional
        Apify Personal API token. If omitted, falls back to the
        ``APIFY_API_TOKEN`` environment variable.
    timeout : int, optional
        Maximum seconds to wait for an actor run to finish. Default 600.
    poll_interval : float, optional
        Seconds between status polls. Default 3.
    base_url : str, optional
        Override the Apify API base URL (mostly for testing).
    """

    def __init__(
        self,
        api_token: str | None = None,
        timeout: int = 600,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "Apify API token is required. Pass api_token='apify_api_...' "
                "or set the APIFY_API_TOKEN environment variable. "
                "Get a token at https://console.apify.com/account/integrations"
            )
        self._token = token
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "tiktok-shadowban-checker-python/0.2.0",
        })

    # ------------------------------------------------------------------ public

    def check_urls(
        self,
        urls: Iterable[str],
        *,
        include_summary: bool = True,
        include_recommendations: bool = True,
        max_retries: int = 5,
        proxy_country: str = "US",
        custom_proxy_urls: Sequence[str] | None = None,
        actor_timeout_secs: int = 600,
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Check a batch of TikTok video URLs for shadow-ban status.

        Parameters
        ----------
        urls : iterable of str
            TikTok video URLs (full or `vm.tiktok.com` short links).
        include_summary : bool, optional
            Append a batch-summary record at the end of the dataset. Default ``True``.
        include_recommendations : bool, optional
            Add a ``recommendations`` array to every video result with specific
            advice based on the detected signals (e.g. *"Comments are disabled.
            Re-enable them..."*). Default ``True``.
        max_retries : int, optional
            Per-URL retry attempts with a fresh proxy IP. Default 5.
        proxy_country : str, optional
            ISO 2-letter code for residential proxy. Default ``"US"``.
        custom_proxy_urls : sequence of str, optional
            Override Apify residential proxy with your own.
        actor_timeout_secs : int, optional
            Maximum runtime hint for the actor. Default 600.

        Returns
        -------
        tuple[list[dict], dict | None]
            ``(video_results, batch_summary)``. ``batch_summary`` is ``None``
            when ``include_summary=False`` or when the actor produced no
            successful records.
        """
        cleaned = [u.strip() for u in urls if u and u.strip()]
        if not cleaned:
            raise ValueError("urls must contain at least one non-empty URL")

        payload = self._build_payload(
            urls=cleaned,
            include_summary=include_summary,
            include_recommendations=include_recommendations,
            max_retries=max_retries,
            proxy_country=proxy_country,
            custom_proxy_urls=custom_proxy_urls,
        )
        records = self._run(payload, actor_timeout_secs=actor_timeout_secs)
        return self._split_summary(records)

    def check_one(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Convenience wrapper for a single video.

        Returns the result record. Raises ``ActorRunError`` if the actor
        produced no records or only an error record.
        """
        kwargs.setdefault("include_summary", False)
        results, _ = self.check_urls([url], **kwargs)
        if not results:
            raise ActorRunError(
                f"Actor returned no records for {url!r} — TikTok may have blocked "
                "all retries. Try a fresher URL or increase max_retries."
            )
        rec = results[0]
        if not rec.get("success", True) and "shadowbanned" not in rec:
            raise ActorRunError(
                f"Check failed for {url!r}: {rec.get('error', '?')}"
            )
        return rec

    def check_text(
        self,
        url_text: str,
        **kwargs: Any,
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Convenience wrapper that accepts a multi-line / multi-comma block
        of TikTok URLs (the same way the Apify Console ``urlText`` textarea
        does it). URLs are split on any whitespace or comma, deduplicated
        client-side and forwarded to :meth:`check_urls`.

        Useful when copying URLs out of a spreadsheet column or a Slack
        message.
        """
        if not url_text or not url_text.strip():
            raise ValueError("url_text must contain at least one URL")
        chunks = re.split(r"[\s,]+", url_text.strip())
        urls = [c for c in chunks if c]
        return self.check_urls(urls, **kwargs)

    def estimate_cost(self, video_count: int) -> float:
        """Return the estimated USD cost for checking ``video_count`` videos.

        Pricing is $0.01 per video ($10 / 1000).
        """
        return round(video_count * PRICE_PER_CHECK_USD, 4)

    # ------------------------------------------------------------------ internal

    @staticmethod
    def _build_payload(
        *,
        urls: Sequence[str],
        include_summary: bool = True,
        include_recommendations: bool = True,
        max_retries: int = 5,
        proxy_country: str = "US",
        custom_proxy_urls: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "urls": list(urls),
            "includeSummary": bool(include_summary),
            "includeRecommendations": bool(include_recommendations),
            "maxRetries": max(1, min(10, int(max_retries))),
            "proxyCountry": (proxy_country or "").strip().upper(),
        }
        if custom_proxy_urls:
            payload["customProxyUrls"] = [str(p).strip() for p in custom_proxy_urls if p]
        return payload

    @staticmethod
    def _split_summary(
        records: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Separate the optional batch-summary record from per-video records."""
        videos: list[dict[str, Any]] = []
        summary: dict[str, Any] | None = None
        for rec in records:
            if isinstance(rec, dict) and rec.get("dataType") == "batch_summary":
                summary = rec
            else:
                videos.append(rec)
        return videos, summary

    def _run(
        self,
        payload: dict[str, Any],
        *,
        actor_timeout_secs: int,
    ) -> list[dict[str, Any]]:
        run_id = self._start_run(payload, actor_timeout_secs=actor_timeout_secs)
        run = self._wait_for_run(run_id)
        return self._fetch_dataset(run["defaultDatasetId"])

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        params = {"timeout": int(actor_timeout_secs)}
        try:
            r = self._session.post(url, params=params, json=payload, timeout=30)
        except requests.RequestException as e:
            raise TikTokShadowBanError(f"Failed to start actor run: {e}") from e

        if r.status_code == 401:
            raise AuthenticationError(
                "Apify rejected the API token. Generate a new one at "
                "https://console.apify.com/account/integrations"
            )
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when starting run: {r.text[:300]}"
            )

        data = r.json().get("data") or {}
        run_id = data.get("id")
        if not run_id:
            raise ActorRunError(f"Apify response missing run id: {r.text[:300]}")
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=30)
            except requests.RequestException as e:
                raise TikTokShadowBanError(f"Failed to poll run status: {e}") from e

            if r.status_code >= 400:
                raise ActorRunError(
                    f"Apify returned HTTP {r.status_code} when polling run: {r.text[:300]}"
                )

            run = r.json().get("data") or {}
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(
                    f"Actor run {run_id} ended with status={status}: "
                    f"{run.get('statusMessage') or '(no message)'}"
                )

            if time.time() > deadline:
                raise ActorTimeoutError(
                    f"Actor run {run_id} did not finish within {self._timeout}s "
                    f"(last status={status}). The run may still be running on Apify; "
                    "increase `timeout=` or fetch the dataset manually."
                )

            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        try:
            r = self._session.get(url, params=params, timeout=120)
        except requests.RequestException as e:
            raise TikTokShadowBanError(f"Failed to download dataset: {e}") from e

        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when fetching dataset: "
                f"{r.text[:300]}"
            )

        try:
            data = r.json()
        except ValueError as e:
            raise ActorRunError(f"Apify dataset is not valid JSON: {e}") from e

        if not isinstance(data, list):
            raise ActorRunError(
                f"Unexpected dataset payload (not a list): {type(data).__name__}"
            )
        return data
