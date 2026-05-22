# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] — 2026-05-22

### Added
- **`include_recommendations` parameter** on `check_urls()` and `check_one()`
  (default `True`). The actor now returns a `recommendations[]` array on every
  video result with plain-English advice tied to the detected signals
  (e.g. `"💬 Comments are disabled. Re-enable them..."`,
  `"📉 Engagement rate 0.4% is well below average for 50,000 views..."`).
- **`check_text(url_text, **kwargs)` method** — accepts a multi-line / multi-comma
  block of TikTok URLs (mirrors the actor's `urlText` textarea). Splits on any
  whitespace or comma, deduplicates client-side, then forwards to `check_urls()`.
  Convenient for spreadsheet copy-paste workflows.

### Removed
- **`check_account()` method** — TikTok stopped shipping the user video list
  in public HTML in 2026 and the lazy-loaded XHR endpoint requires JS-generated
  signatures we can't reproduce server-side. Audit your own / a client's videos
  by passing the URLs directly to `check_urls()` instead.

### Changed
- Sample output and quickstart in README now show recommendations
- `account_audit.py` example replaced by `paste_urls.py` demonstrating `check_text()`
- `monitor_creator.py`, `only_shadowbanned.py`, `agency_dashboard.py` updated to
  take URL lists instead of TikTok usernames
- `export_to_csv.py` adds two new columns: `topRecommendation` and `allRecommendations`

### Migration
```python
# Before (v0.1)
videos, summary = client.check_account("creator", limit=30)

# After (v0.2) — pass URLs directly
recent_urls = ["https://www.tiktok.com/@creator/video/1", "..."]
videos, summary = client.check_urls(recent_urls)

# Or paste a multi-line block (new!)
videos, summary = client.check_text("""
    https://www.tiktok.com/@creator/video/1
    https://www.tiktok.com/@creator/video/2
""")
```

## [0.1.0] — 2026-05-22

### Added
- Initial release of the Python SDK
- `TikTokShadowBanClient` with three primary methods:
  `check_urls()`, `check_one()`, `check_account()`
- Forwarding of all 6 actor inputs:
  `mode`, `urls`, `username`, `accountLimit`, `includeSummary`,
  `maxRetries`, `proxyCountry`, `customProxyUrls`
- Automatic split of dataset into per-video records and the optional
  batch-summary dict (`dataType="batch_summary"`)
- 7 example scripts: quickstart, bulk check, account audit, creator
  monitoring, CSV export, shadowbanned-only filter, agency dashboard
- MIT license
