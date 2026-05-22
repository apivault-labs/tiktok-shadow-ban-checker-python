"""
TikTok Shadow Ban Checker — Python SDK

Official Python client for the apivault_labs/tiktok-shadow-ban-checker Apify
actor. Detect TikTok shadow bans on individual videos with one API call.

Returns 30+ signals per video plus a list of plain-English recommendations:
- shadow ban verdict (composite of takeDown, secret, privateItem, forFriend,
  isReviewing, divertToPrivate, indexEnabled, forYou, search, plus soft
  restrictions like duet / stitch / comment / download / share)
- videoHealthScore (0-100), videoHealthStatus
- engagementRate, viralPotentialScore
- banReasonHints[] — every detected restriction in plain English
- recommendations[] — actionable advice based on the detected signals
- author + stats + music + hashtags

Quick start:

    from tiktok_shadowban_checker import TikTokShadowBanClient

    client = TikTokShadowBanClient(api_token="apify_api_xxxxxx")

    # Check one video
    result = client.check_one(
        "https://www.tiktok.com/@tiktok/video/7480279424202575159"
    )
    print(result["shadowbanned"], result["videoHealthScore"])
    for rec in result.get("recommendations", []):
        print(rec)

    # Or paste a multi-line block of URLs
    videos, summary = client.check_text('''
        https://www.tiktok.com/@a/video/1
        https://www.tiktok.com/@b/video/2
    ''')

See https://github.com/apivault-labs/tiktok-shadow-ban-checker-python for full docs.
"""

from .client import TikTokShadowBanClient
from .exceptions import (
    TikTokShadowBanError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.2.0"
__all__ = [
    "TikTokShadowBanClient",
    "TikTokShadowBanError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
