# Changelog

All notable changes to this project will be documented in this file.

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
