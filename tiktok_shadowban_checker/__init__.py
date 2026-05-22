"""
TikTok Shadow Ban Checker — Python SDK

Official Python client for the apivault_labs/tiktok-shadow-ban-checker Apify
actor. Detect TikTok shadow bans on individual videos or audit an entire
account's recent uploads with one API call.

Returns 30+ signals per video:
- shadow ban verdict (composite of takeDown, secret, privateItem, forFriend,
  isReviewing, divertToPrivate, indexEnabled, forYou, search, plus soft
  restrictions like duet / stitch / comment / download / share)
- videoHealthScore (0-100)
- engagementRate, viralPotentialScore
- banReasonHints[] — human-readable list of every detected restriction
- author + stats + music + hashtags

Quick start:

    from tiktok_shadowban_checker import TikTokShadowBanClient

    client = TikTokShadowBanClient(api_token="apify_api_xxxxxx")

    # Check one video
    result = client.check_one(
        "https://www.tiktok.com/@tiktok/video/7480279424202575159"
    )
    print(result["shadowbanned"], result["videoHealthScore"])

    # Audit last 30 videos of an account
    videos, summary = client.check_account("creator_handle", limit=30)
    print(f"Shadowbanned: {summary['shadowbannedCount']}/{summary['totalChecked']}")

See https://github.com/apivault-labs/tiktok-shadow-ban-checker-python for full docs.
"""

from .client import TikTokShadowBanClient
from .exceptions import (
    TikTokShadowBanError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    "TikTokShadowBanClient",
    "TikTokShadowBanError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
