"""
Audit the last N videos of a TikTok account.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/account_audit.py
"""

from tiktok_shadowban_checker import TikTokShadowBanClient


USERNAME = "tiktok"
LIMIT = 30


def main() -> None:
    client = TikTokShadowBanClient(timeout=900)
    print(f"Auditing last {LIMIT} videos of @{USERNAME} "
          f"(estimated cost: ${client.estimate_cost(LIMIT)})...\n")

    videos, summary = client.check_account(USERNAME, limit=LIMIT, max_retries=5)

    if not videos:
        print("No videos returned. Account may be private or username invalid.")
        return

    print(f"=== Per-video results ===")
    print(f"{'#':<3} {'Date':<11} {'Banned':<7} {'Health':>6} "
          f"{'Eng %':>7} {'Views':>10}")
    print("-" * 56)
    for i, v in enumerate(videos, 1):
        if not v.get("success"):
            continue
        date = v.get("createDate") or "?"
        banned = "YES" if v.get("shadowbanned") else ""
        health = v.get("videoHealthScore") or "?"
        eng = v.get("engagementRate")
        eng_s = f"{eng:>6.2f}%" if eng is not None else "    -"
        views = (v.get("stats") or {}).get("views") or 0
        print(f"{i:<3} {date:<11} {banned:<7} {health:>6} {eng_s} {views:>10,}")

    if summary:
        print(f"\n=== Account audit summary ===")
        print(f"  Account:             @{USERNAME}")
        print(f"  Checked:             {summary['totalChecked']} videos")
        print(f"  Shadowbanned:        {summary['shadowbannedCount']} "
              f"({summary['shadowbannedPct']}%)")
        print(f"  Healthy:             {summary['healthyCount']}")
        print(f"  Restricted:          {summary['restrictedCount']}")
        print(f"  Avg health score:    {summary['avgHealthScore']}/100")
        print(f"  Avg engagement rate: {summary.get('avgEngagementRate')}%")
        if summary.get("mostCommonRestrictions"):
            print(f"\n  Most common restrictions:")
            for hint, count in summary["mostCommonRestrictions"]:
                print(f"    [{count}x] {hint}")
        print(f"\n  Verdict: {summary['recommendation']}")


if __name__ == "__main__":
    main()
