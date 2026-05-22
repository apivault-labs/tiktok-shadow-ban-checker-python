"""
Track shadow-ban rate over time for a single creator.

Run this once per day from a cron job and append the summary record to a
local JSONL file. Plot avgHealthScore and shadowbannedPct in a dashboard.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/monitor_creator.py
"""

import json
import time
from pathlib import Path

from tiktok_shadowban_checker import TikTokShadowBanClient


USERNAME = "tiktok"
LIMIT = 20
LOG_FILE = Path("creator_monitor.jsonl")


def main() -> None:
    client = TikTokShadowBanClient(timeout=900)
    videos, summary = client.check_account(USERNAME, limit=LIMIT)

    if not summary:
        print("Run produced no summary (zero successful videos). Skipping log.")
        return

    snapshot = {
        "ts": int(time.time()),
        "username": USERNAME,
        "checked": summary["totalChecked"],
        "shadowbannedCount": summary["shadowbannedCount"],
        "shadowbannedPct": summary["shadowbannedPct"],
        "avgHealthScore": summary["avgHealthScore"],
        "avgEngagementRate": summary.get("avgEngagementRate"),
        "topRestrictions": summary.get("mostCommonRestrictions") or [],
        "verdict": summary["recommendation"],
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")

    print(f"Logged snapshot for @{USERNAME}:")
    print(f"  shadowbanned:    {snapshot['shadowbannedCount']}/{snapshot['checked']}"
          f"  ({snapshot['shadowbannedPct']}%)")
    print(f"  avg health:      {snapshot['avgHealthScore']}/100")
    print(f"  avg engagement:  {snapshot.get('avgEngagementRate')}%")
    print(f"\nAppended to {LOG_FILE.resolve()}")


if __name__ == "__main__":
    main()
