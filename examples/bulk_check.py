"""
Check many TikTok videos in one batch.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/bulk_check.py
"""

from tiktok_shadowban_checker import TikTokShadowBanClient


VIDEO_URLS = [
    "https://www.tiktok.com/@tiktok/video/7480279424202575159",
    "https://www.tiktok.com/@khaby.lame/video/7299530268907818273",
    "https://www.tiktok.com/@charlidamelio/video/7227253960028196138",
]


def main() -> None:
    client = TikTokShadowBanClient(timeout=900)
    print(f"Checking {len(VIDEO_URLS)} videos "
          f"(estimated cost: ${client.estimate_cost(len(VIDEO_URLS))})...\n")

    videos, summary = client.check_urls(VIDEO_URLS, max_retries=5)

    print(f"{'Author':<22} {'Banned?':<8} {'Health':>6} {'Eng %':>7} {'Hints':>5}")
    print("-" * 60)
    for v in videos:
        if not v.get("success"):
            print(f"  ERROR: {v.get('url')[:50]} -> {v.get('error', '?')[:30]}")
            continue
        author = "@" + ((v.get("author") or {}).get("uniqueId") or "?")
        banned = "YES" if v.get("shadowbanned") else "no"
        health = v.get("videoHealthScore") or "?"
        eng = v.get("engagementRate")
        eng_s = f"{eng:>6.2f}%" if eng is not None else "    -"
        hints = v.get("restrictionCount") or 0
        print(f"{author[:22]:<22} {banned:<8} {health:>6} {eng_s} {hints:>5}")

    if summary:
        print(f"\n=== Batch summary ===")
        print(f"  total checked:       {summary['totalChecked']}")
        print(f"  shadowbanned:        {summary['shadowbannedCount']} "
              f"({summary['shadowbannedPct']}%)")
        print(f"  healthy:             {summary['healthyCount']}")
        print(f"  avg health score:    {summary['avgHealthScore']}/100")
        print(f"  avg engagement rate: {summary.get('avgEngagementRate')}%")
        if summary.get("mostCommonRestrictions"):
            print(f"  top restrictions:")
            for hint, count in summary["mostCommonRestrictions"]:
                print(f"    [{count}x] {hint}")
        print(f"\n  {summary['recommendation']}")


if __name__ == "__main__":
    main()
