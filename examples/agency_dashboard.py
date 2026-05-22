"""
Generate a per-client shadow-ban dashboard for an agency.

Bulk-checks a list of recent video URLs grouped by client name, prints a
sortable summary table that can be pasted into a slide deck, and surfaces
the worst offenders for follow-up.

In a real workflow you'd read the URL groups from a CSV / spreadsheet,
the client's TikTok analytics export, or your CRM.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/agency_dashboard.py
"""

from tiktok_shadowban_checker import TikTokShadowBanClient


CLIENT_VIDEOS: dict[str, list[str]] = {
    "TikTok Inc": [
        "https://www.tiktok.com/@tiktok/video/7480279424202575159",
    ],
    "Khaby Lame": [
        "https://www.tiktok.com/@khaby.lame/video/7299530268907818273",
    ],
    "Charli D'Amelio": [
        "https://www.tiktok.com/@charlidamelio/video/7227253960028196138",
    ],
}


def main() -> None:
    client = TikTokShadowBanClient(timeout=1800)

    rows = []
    for name, urls in CLIENT_VIDEOS.items():
        if not urls:
            continue
        print(f"  Auditing {name}...")
        try:
            videos, summary = client.check_urls(urls)
        except Exception as e:
            print(f"    failed: {e}")
            continue
        if not summary:
            # Single-video case — synthesise a tiny summary
            ok = [v for v in videos if v.get("success")]
            if not ok:
                continue
            summary = {
                "totalChecked": len(ok),
                "shadowbannedCount": sum(1 for v in ok if v.get("shadowbanned")),
                "shadowbannedPct": round(
                    sum(1 for v in ok if v.get("shadowbanned")) / len(ok) * 100, 1
                ),
                "avgHealthScore": round(
                    sum((v.get("videoHealthScore") or 0) for v in ok) / len(ok), 1
                ),
                "avgEngagementRate": (
                    round(
                        sum((v.get("engagementRate") or 0) for v in ok) / len(ok), 2
                    )
                    if any(v.get("engagementRate") is not None for v in ok)
                    else None
                ),
                "recommendation": "(single-video sample)",
            }

        rows.append({
            "name": name,
            "checked": summary["totalChecked"],
            "banned": summary["shadowbannedCount"],
            "banned_pct": summary["shadowbannedPct"],
            "avg_health": summary["avgHealthScore"],
            "avg_eng": summary.get("avgEngagementRate") or 0,
            "verdict": summary["recommendation"],
        })

    rows.sort(key=lambda r: (-r["banned_pct"], -r["banned"]))

    print(f"\n{'#':<3} {'Client':<22} {'Checked':>8} {'Banned':>7} "
          f"{'%':>6} {'Health':>7} {'Eng %':>7}")
    print("-" * 70)
    for i, r in enumerate(rows, 1):
        print(f"{i:<3} {r['name']:<22} {r['checked']:>8} {r['banned']:>7} "
              f"{r['banned_pct']:>5.1f}% {r['avg_health']:>7} {r['avg_eng']:>6.2f}%")

    print(f"\nDetailed verdicts:")
    for r in rows:
        print(f"  {r['name']}: {r['verdict']}")

    total_videos = sum(r["checked"] for r in rows)
    total_cost = client.estimate_cost(total_videos)
    print(f"\nTotal videos checked: {total_videos}  (cost: ${total_cost})")


if __name__ == "__main__":
    main()
