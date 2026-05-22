# TikTok Shadow Ban Checker — Python SDK

> **Detect TikTok shadow bans on any public video: 30+ signals per video, composite health score, engagement rate, viral potential, plain-English ban reasons and actionable recommendations — all in one call.**

Python client for the [TikTok Shadow Ban Checker Apify Actor](https://apify.com/apivault_labs/tiktok-shadow-ban-checker) — the most-used shadow ban detection tool on Apify Store, going beyond the legacy `indexEnabled` flag with a multi-signal composite verdict.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue?logo=apify)](https://apify.com/apivault_labs/tiktok-shadow-ban-checker)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![PyPI-friendly](https://img.shields.io/badge/install-pip-success)](#installation)

---

## What it does

For any TikTok video URL this actor returns a single rich JSON record combining **multiple shadow-ban signals**, **engagement metrics**, **a composite health score** and **a list of actionable, plain-English recommendations** — plus an optional **batch summary** when checking multiple videos.

Built because the legacy `indexEnabled` flag has been progressively scrubbed from public TikTok HTML in 2026. This SDK uses an aggregate verdict from **all** signals TikTok still exposes:

- Hard signals: `takeDown`, `secret`, `privateItem`, `forFriend`, `isReviewing`, `warnInfo`, `divertToPrivate`, legacy `indexEnabled`, `forYou`, `searchVisible`
- Soft signals: `duetDisabled`, `stitchDisabled`, `commentDisabled`, `downloadDisabled`, `shareDisabled`

A direct, pay-per-use alternative to:
- Manual TikTok HTML inspection (multi-step, breaks weekly)
- Browser-extension shadow-ban checkers (single-video, no API, no health score)
- Generic creator-analytics platforms ($49-$199/mo)

**Pricing:** $0.01 per video ($10 / 1000). No subscriptions, no quotas.

> **Note:** Account-mode (audit a whole TikTok username in one call) was removed in v1.2 because TikTok stopped shipping the user video list in public HTML. Pass video URLs directly with `check_urls()` or `check_text()` — every other signal is unchanged.

---

## Quick start

```python
from tiktok_shadowban_checker import TikTokShadowBanClient

client = TikTokShadowBanClient(api_token="apify_api_xxxxxx")

# Check one video
result = client.check_one(
    "https://www.tiktok.com/@tiktok/video/7480279424202575159"
)

print(f"Shadowbanned:    {result['shadowbanned']}")
print(f"Health score:    {result['videoHealthScore']}/100 ({result['videoHealthStatus']})")
print(f"Engagement rate: {result['engagementRate']}%")
print(f"Viral score:     {result['viralPotentialScore']}/100")

if result.get("banReasonHints"):
    print("Reasons:")
    for hint in result["banReasonHints"]:
        print(f"  - {hint}")

if result.get("recommendations"):
    print("\nRecommendations:")
    for rec in result["recommendations"]:
        print(f"  {rec}")
```

Output:
```
Shadowbanned:    False
Health score:    95/100 (healthy)
Engagement rate: 4.23%
Viral score:     72/100

Recommendations:
  ✅ Video looks healthy. No shadow-ban action needed.
  🔥 Engagement rate 4.23% is excellent (industry avg 3-6%). Keep this format/topic in rotation — it converts.
```

Or paste a multi-line block of URLs (great for spreadsheet copy-paste):

```python
videos, summary = client.check_text("""
    https://www.tiktok.com/@a/video/1
    https://www.tiktok.com/@b/video/2
    https://www.tiktok.com/@c/video/3
""")

print(f"Shadowbanned: {summary['shadowbannedCount']}/{summary['totalChecked']}")
print(f"Verdict:      {summary['recommendation']}")
```

---

## Installation

```bash
pip install git+https://github.com/apivault-labs/tiktok-shadow-ban-checker-python.git
```

Or clone and use directly:

```bash
git clone https://github.com/apivault-labs/tiktok-shadow-ban-checker-python.git
cd tiktok-shadow-ban-checker-python
pip install -r requirements.txt
```

Requires Python 3.9+ and the [`requests`](https://pypi.org/project/requests/) library.

---

## Get your API token (free)

1. Sign up at [apify.com](https://apify.com) — free tier includes $5 monthly credits, no card required
2. Go to [Account → Integrations](https://console.apify.com/account/integrations)
3. Copy your Personal API token

```bash
export APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
```

Or pass it explicitly:

```python
client = TikTokShadowBanClient(api_token="apify_api_xxxxxx")
```

---

## What you get for $0.01 per video

### 🚨 Shadow ban verdict
- **`shadowbanned`** — final composite verdict (boolean)
- **`banReasonHints[]`** — every detected restriction in plain English
- **`restrictionCount`** — total number of active restrictions

### 🔍 All raw signals exposed individually
Hard signals (any one = shadowbanned):
- `takeDown`, `secret`, `privateItem`, `forFriend`, `isReviewing`
- `divertedToPrivate`, `indexEnabled` (legacy), `hasWarning`

Soft signals (3+ active = composite ban):
- `duetDisabled`, `stitchDisabled`, `commentDisabled`, `downloadDisabled`, `shareDisabled`

Forward-compat signals (when TikTok exposes them):
- `forYouEligible`, `searchVisible`

### 📊 Computed metrics
- **`videoHealthScore`** (0-100) — composite of all ban indicators + engagement
- **`videoHealthStatus`** — `healthy` / `slightly_restricted` / `restricted` / `heavily_restricted` / `shadowbanned`
- **`engagementRate`** — (likes + comments + shares) / views × 100
- **`viralPotentialScore`** (0-100) — views velocity (per day) + engagement bonus

### 🎬 Video metadata (for context)
- `videoId`, `description`, `duration`, `ratio`, `coverUrl`
- `createTime`, `createDate`, `locationCreated`
- `hashtags[]`, `music` (title, author, original-vs-licensed)

### 📈 Stats
- `views`, `likes`, `comments`, `shares`, `saves`

### 👤 Author block
- `nickname`, `uniqueId`, `verified`
- `followerCount`, `followingCount`, `heartCount`, `videoCount`

### 📋 Optional batch summary
When checking multiple videos:
- `totalChecked`, `shadowbannedCount`, `shadowbannedPct`
- `healthyCount`, `restrictedCount`
- `avgHealthScore`, `avgEngagementRate`
- `mostCommonRestrictions[]` — top 5 restrictions across the batch
- `recommendation` — human-readable verdict

---

## Examples

See the [`examples/`](examples) folder for full code:

| File | What it does |
|---|---|
| [`quickstart.py`](examples/quickstart.py) | Check one video, print verdict + reasons + recommendations |
| [`bulk_check.py`](examples/bulk_check.py) | Check many video URLs in one batch |
| [`paste_urls.py`](examples/paste_urls.py) | Paste a multi-line block of URLs (spreadsheet-friendly) |
| [`monitor_creator.py`](examples/monitor_creator.py) | Track health of your own recent videos over time |
| [`export_to_csv.py`](examples/export_to_csv.py) | Save results to CSV / Excel (including recommendations) |
| [`only_shadowbanned.py`](examples/only_shadowbanned.py) | Filter list to banned videos only with action items |
| [`agency_dashboard.py`](examples/agency_dashboard.py) | Generate per-client health reports |

---

## API reference

### `TikTokShadowBanClient(api_token=None, timeout=600)`

| Param | Type | Description |
|---|---|---|
| `api_token` | `str` | Apify API token. Falls back to `APIFY_API_TOKEN` env var. |
| `timeout` | `int` | Max seconds to wait for the actor run. Default 600 (10 min). |
| `poll_interval` | `float` | Seconds between status polls. Default 3. |

### `client.check_urls(urls, **kwargs)`

Check a batch of video URLs.

| Param | Type | Default | Description |
|---|---|---|---|
| `urls` | `list[str]` | required | TikTok video URLs (full or `vm.tiktok.com` short links) |
| `include_summary` | `bool` | `True` | Append a batch-summary record |
| `include_recommendations` | `bool` | `True` | Add a `recommendations[]` array to each video result |
| `max_retries` | `int` | 5 | Retry attempts per URL with new proxy IP |
| `proxy_country` | `str` | `"US"` | ISO 2-letter code; pin to avoid region-redirects |
| `custom_proxy_urls` | `list[str]` | `None` | Override Apify proxy with your own |
| `actor_timeout_secs` | `int` | 600 | Actor runtime hint passed to Apify |

Returns: `tuple[list[dict], dict | None]` — `(video_results, batch_summary)`.

### `client.check_one(url, **kwargs)`

Convenience wrapper for a single URL. Returns one `dict` or raises `ActorRunError`.

### `client.check_text(url_text, **kwargs)`

Accept a multi-line / multi-comma block of TikTok URLs (mimics the actor's `urlText` textarea). Splits on any whitespace or comma, deduplicates client-side, forwards to `check_urls()`. Useful for spreadsheet copy-paste.

```python
videos, summary = client.check_text("""
    https://www.tiktok.com/@a/video/1
    https://www.tiktok.com/@b/video/2
""")
```

Returns: `tuple[list[dict], dict | None]`.

### `client.estimate_cost(video_count)`

Returns the estimated USD cost (`video_count × 0.01`).

---

## Sample per-video output

```json
{
  "url": "https://www.tiktok.com/@tiktok/video/7480279424202575159",
  "videoId": "7480279424202575159",
  "success": true,

  "shadowbanned": false,
  "indexEnabled": true,
  "forYouEligible": null,
  "searchVisible": null,
  "divertedToPrivate": false,
  "duetDisabled": false,
  "stitchDisabled": false,
  "commentDisabled": false,
  "downloadDisabled": false,
  "privateAccount": false,
  "isAd": false,
  "banReasonHints": [],
  "restrictionCount": 0,

  "videoHealthScore": 95,
  "videoHealthStatus": "healthy",
  "engagementRate": 4.23,
  "viralPotentialScore": 72,

  "description": "Welcome back to TikTok",
  "locationCreated": "US",
  "createDate": "2025-03-15",
  "createTime": 1742054400,
  "duration": 30,

  "author": {
    "nickname": "TikTok",
    "uniqueId": "tiktok",
    "verified": true,
    "followerCount": 91000000,
    "followingCount": 12,
    "heartCount": 612000000,
    "videoCount": 884
  },

  "stats": {
    "views": 4523000,
    "likes": 182300,
    "comments": 9400,
    "shares": 23100,
    "saves": 5670
  },

  "music": {
    "title": "original sound",
    "authorName": "tiktok",
    "original": true
  },

  "hashtags": ["fyp", "tiktok"],

  "recommendations": [
    "✅ Video looks healthy. No shadow-ban action needed.",
    "🔥 Engagement rate 4.23% is excellent (industry avg 3-6%). Keep this format/topic in rotation — it converts."
  ]
}
```

## Sample batch summary

```json
{
  "dataType": "batch_summary",
  "totalChecked": 30,
  "shadowbannedCount": 4,
  "shadowbannedPct": 13.3,
  "healthyCount": 22,
  "restrictedCount": 8,
  "avgHealthScore": 78.4,
  "avgEngagementRate": 3.21,
  "mostCommonRestrictions": [
    ["comments disabled", 3],
    ["duet disabled", 2],
    ["takeDown=true (TikTok removed video)", 1]
  ],
  "recommendation": "\u26a0\ufe0f Some restrictions detected \u2014 monitor closely"
}
```

---

## Use cases

### 🎥 Creator self-audit
Catch shadow bans before they tank your reach:
- Maintain a list of your recent video URLs (export from your TikTok analytics CSV) and run `check_urls()` on them weekly as a cron job
- Alert when `shadowbannedPct > 20%`
- Inspect `banReasonHints` to identify the policy violation
- Use `recommendations[]` to know exactly what to fix in each video
- Track `avgHealthScore` as a trailing health metric

### 🏢 Agency client reporting
Generate per-client shadow-ban reports at scale:
- Bulk-check all client accounts in one run
- Export to CSV for white-labeled PDF reports
- Flag clients with declining `videoHealthScore` trends
- Use `viralPotentialScore` to spot rising vs decaying creators

### 🔍 Brand-deal due diligence
Vet UGC creators before signing partnerships:
- Confirm none of their last 30 videos are `shadowbanned`
- Verify `engagementRate` matches their reported numbers
- Check `restrictionCount > 0` as a brand-safety risk flag

### 📊 Competitor intelligence
Audit competitor accounts systematically:
- How many of their videos are shadow-banned?
- Which restrictions appear most often?
- Track `avgHealthScore` deltas over time

### 🤖 Automation pipelines
Hook into content workflows:
- Block scheduled re-uploads that flagged as `shadowbanned`
- Auto-DM creators with low `videoHealthScore`
- Feed `banReasonHints` into LLMs for human-readable summaries

### 🛡️ Trust & safety / forensics
For platforms moderating creator partnerships:
- Detect mass-takedowns (`takeDown=true` clusters)
- Identify accounts with `divertedToPrivate` patterns
- Build training data for ban-prediction ML models

---

## Pricing

Pay only for what you check:

| Volume | Cost |
|---|---|
| 1 video | $0.01 |
| 100 videos | $1.00 |
| 1,000 videos | $10.00 |
| 10,000 videos | $100.00 |

Free Apify tier includes ~$5 monthly credit — that's **500 free shadow-ban checks per month**.

---

## How it works

The actor uses **public TikTok page HTML** with multiple fetch strategies — no logins, no TikTok API key:

1. **Mobile UA on `www.tiktok.com`** — modern endpoint, includes legacy `indexEnabled` when present
2. **Mobile UA on `m.tiktok.com`** — same payload, alternate host
3. **Desktop UA fallback** — most reliable for metadata
4. **Googlebot UA** — bypasses login walls
5. **Embed v2 / legacy embed** — last-resort for blocked pages
6. **oEmbed** — guaranteed metadata even when full HTML fails

Embedded JSON is parsed from `__UNIVERSAL_DATA_FOR_REHYDRATION__`, `__NEXT_DATA__`, or legacy `SIGI_STATE` blocks. The `analyze_shadow_ban()` function aggregates 15+ signals into a single composite verdict.

Health-score formula:
```
indexEnabled = +40 pts (or +20 if unknown)
forYouEligible = +20 pts (or +10 if unknown)
searchVisible = +15 pts (or +7 if unknown)
not divertedToPrivate = +15 pts
engagementRate >= 3% = +10 pts (or +5 if >= 1%)
```

A fully healthy video scores 100; a video with `takeDown=true` and 3+ soft restrictions scores under 20.

---

## Speed & reliability

- **8–20 seconds per video** (HTTP only, multi-strategy retries)
- **Residential proxy by default** — pinned to `US` to avoid region-redirects
- **5 retries per URL** with proxy IP rotation
- **Custom proxy support** — bring your own `host:port:user:pass` rotation
- **Graceful failure** — every record contains `success` boolean; failed checks include `error` field

---

## FAQ

**Q: Is `indexEnabled=false` still the gold-standard signal?**
A: It was, until TikTok started removing it from public HTML in 2026. The actor now uses an aggregate of 15+ signals so the verdict survives even when `indexEnabled` is missing. When `indexEnabled` is exposed, it's still factored in as the primary hard signal.

**Q: Why does `forYouEligible` show `null` sometimes?**
A: TikTok exposes this field inconsistently. When `null`, the score gives partial credit and relies on other signals.

**Q: Will it work on private accounts?**
A: Direct video URLs from private accounts return an error — only public videos can be analysed.

**Q: How accurate is the verdict?**
A: When **hard signals fire** (`takeDown`, `secret`, `privateItem`, `forFriend`, `isReviewing`, `warnInfo`, `divertToPrivate`), accuracy is essentially 100% — these are TikTok's own moderation flags. The composite-soft path (3+ restrictions) is a heuristic and may produce false positives on creators who genuinely disabled features by choice — inspect `banReasonHints` to verify.

**Q: Can I bring my own proxies?**
A: Yes. Pass `custom_proxy_urls=["host:port:user:pass", ...]` to override Apify residential proxies entirely. Round-robin rotation is automatic.

**Q: What's the difference vs the [TikTok Profile Scraper SDK](https://github.com/apivault-labs/tiktok-profile-scraper-python)?**
A: Profile Scraper returns account-level metadata (followers, bio, total likes). Shadow Ban Checker returns video-level health and ban verdicts. Use both together for full creator intelligence.

**Q: Is this allowed by TikTok's ToS?**
A: This actor only reads publicly accessible video pages, the same data any browser sees. Use responsibly and respect TikTok's Terms of Service for your jurisdiction.

---

## Related Apify actors

- [TikTok Profile Scraper](https://apify.com/apivault_labs/tiktok-profile-scraper) — full profile data with creator-tier signals
- [TikTok Shop Scraper](https://apify.com/apivault_labs/tiktok-shop-scraper) — TikTok Shop product listings
- [Instagram Profile Scraper](https://apify.com/apivault_labs/instagram-profile-scraper) — same pattern for Instagram

See [all actors by apivault_labs](https://apify.com/apivault_labs).

---

## License

MIT — see [LICENSE](LICENSE).

This client is open source. The underlying Apify actor is a paid service ($0.01/video).

---

## Keywords

`tiktok-shadow-ban` `tiktok-shadow-ban-checker` `tiktok-shadowban-api` `shadow-ban-detection` `tiktok-fyp-checker` `tiktok-search-visibility` `tiktok-suppression-detection` `tiktok-video-health` `tiktok-engagement-rate-api` `tiktok-viral-score` `creator-analytics` `creator-self-audit` `agency-tools` `brand-safety` `content-moderation-detection` `tiktok-without-api-key` `tiktok-research-api-alternative` `web-scraping` `apify` `apify-actor` `python-sdk`
