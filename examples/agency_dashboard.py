"""
Generate a per-client shadow-ban dashboard for an agency.

Bulk-checks a list of client TikTok handles, prints a sortable summary
table that can be pasted into a slide deck, and surfaces the worst
offenders for follow-up.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/agency_dashboard.py
"""

from tiktok_shadowban_checker import TikTokShadowBanClient


CLIENTS = [
    "tiktok",
    "khaby.lame",
    "charlidamelio",
    "addisonre",
    "bellapoarch",
]
PER_CLIENT_LIMIT = 15


def main() -> None:
    client = TikTokShadowBanClient(timeout=1800)

    rows = []
    for handle in CLIENTS:
        print(f"  Auditing @{handle}...")
        try:
            _, summary = client.check_account(handle, limit=PER_CLIENT_LIMIT)
        except Exception as e:
            print(f"    failed: {e}")
            continue
        if not summary:
            print(f"    no summary returned")
            continue

        rows.append({
            "handle": handle,
            "checked": summary["totalChecked"],
            "banned": summary["shadowbannedCount"],
            "banned_pct": summary["shadowbannedPct"],
            "avg_health": summary["avgHealthScore"],
            "avg_eng": summary.get("avgEngagementRate") or 0,
            "verdict": summary["recommendation"],
        })

    rows.sort(key=lambda r: (-r["banned_pct"], -r["banned"]))

    print(f"\n{'#':<3} {'Handle':<22} {'Checked':>8} {'Banned':>7} "
          f"{'%':>6} {'Health':>7} {'Eng %':>7}")
    print("-" * 70)
    for i, r in enumerate(rows, 1):
        print(f"{i:<3} @{r['handle']:<21} {r['checked']:>8} {r['banned']:>7} "
              f"{r['banned_pct']:>5.1f}% {r['avg_health']:>7} {r['avg_eng']:>6.2f}%")

    print(f"\nDetailed verdicts:")
    for r in rows:
        print(f"  @{r['handle']}: {r['verdict']}")

    total_videos = sum(r["checked"] for r in rows)
    total_cost = client.estimate_cost(total_videos)
    print(f"\nTotal videos checked: {total_videos}  (cost: ${total_cost})")


if __name__ == "__main__":
    main()
