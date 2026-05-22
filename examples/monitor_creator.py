"""
Track your own video health over time.

Maintain a list of recently-uploaded video URLs (you can pull these from
your own TikTok analytics CSV export or any internal tracker), then run
this on a schedule. Each run appends a snapshot to ``creator_monitor.jsonl``
that you can plot in a dashboard.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/monitor_creator.py
"""

import json
import time
from pathlib import Path

from tiktok_shadowban_checker import TikTokShadowBanClient


# Replace with your own recent video URLs
MY_RECENT_VIDEOS = [
    "https://www.tiktok.com/@tiktok/video/7480279424202575159",
    "https://www.tiktok.com/@khaby.lame/video/7299530268907818273",
]
LOG_FILE = Path("creator_monitor.jsonl")


def main() -> None:
    client = TikTokShadowBanClient(timeout=900)
    videos, summary = client.check_urls(MY_RECENT_VIDEOS)

    if not summary:
        print("Run produced no summary (zero successful videos). Skipping log.")
        return

    snapshot = {
        "ts": int(time.time()),
        "checked": summary["totalChecked"],
        "shadowbannedCount": summary["shadowbannedCount"],
        "shadowbannedPct": summary["shadowbannedPct"],
        "avgHealthScore": summary["avgHealthScore"],
        "avgEngagementRate": summary.get("avgEngagementRate"),
        "topRestrictions": summary.get("mostCommonRestrictions") or [],
        "verdict": summary["recommendation"],
        # Per-video detail for trend analysis
        "videos": [
            {
                "url": v.get("url"),
                "videoId": v.get("videoId"),
                "shadowbanned": v.get("shadowbanned"),
                "health": v.get("videoHealthScore"),
                "engagement": v.get("engagementRate"),
                "topRecommendation": (v.get("recommendations") or [None])[0],
            }
            for v in videos
            if v.get("success")
        ],
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")

    print(f"Logged snapshot:")
    print(f"  shadowbanned:    {snapshot['shadowbannedCount']}/{snapshot['checked']}"
          f"  ({snapshot['shadowbannedPct']}%)")
    print(f"  avg health:      {snapshot['avgHealthScore']}/100")
    print(f"  avg engagement:  {snapshot.get('avgEngagementRate')}%")
    print(f"  verdict:         {snapshot['verdict']}")
    print(f"\nAppended to {LOG_FILE.resolve()}")


if __name__ == "__main__":
    main()
