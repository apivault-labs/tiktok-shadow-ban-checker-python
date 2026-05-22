"""
Quickstart: check a single TikTok video for shadow ban.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from tiktok_shadowban_checker import TikTokShadowBanClient


def main() -> None:
    client = TikTokShadowBanClient()  # picks up APIFY_API_TOKEN from env

    url = "https://www.tiktok.com/@tiktok/video/7480279424202575159"
    result = client.check_one(url)

    print(f"\n=== {url} ===")
    print(f"  Shadowbanned:        {result['shadowbanned']}")
    print(f"  Video health:        {result['videoHealthScore']}/100  ({result['videoHealthStatus']})")
    print(f"  Engagement rate:     {result.get('engagementRate')}%")
    print(f"  Viral potential:     {result.get('viralPotentialScore')}/100")
    print(f"  Restriction count:   {result['restrictionCount']}")

    print(f"\n  Video meta:")
    print(f"    description: {(result.get('description') or '')[:80]}")
    print(f"    created:     {result.get('createDate')}  ({result.get('locationCreated')})")
    print(f"    duration:    {result.get('duration')}s")
    print(f"    hashtags:    {', '.join(result.get('hashtags') or [])}")

    print(f"\n  Author:")
    a = result.get("author") or {}
    print(f"    @{a.get('uniqueId')}  ({a.get('nickname')})")
    print(f"    {a.get('followerCount'):,} followers, {a.get('videoCount')} videos")
    print(f"    verified: {a.get('verified')}")

    print(f"\n  Stats:")
    s = result.get("stats") or {}
    print(f"    views:    {s.get('views', 0):,}")
    print(f"    likes:    {s.get('likes', 0):,}")
    print(f"    comments: {s.get('comments', 0):,}")
    print(f"    shares:   {s.get('shares', 0):,}")

    if result.get("banReasonHints"):
        print(f"\n  Ban reason hints:")
        for hint in result["banReasonHints"]:
            print(f"    - {hint}")


if __name__ == "__main__":
    main()
