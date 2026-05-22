"""
Filter a list of TikTok videos down to only the shadow-banned ones.

Use case: pull a creator's entire feed, then surface only the videos that
need investigation or re-uploading.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/only_shadowbanned.py
"""

from tiktok_shadowban_checker import TikTokShadowBanClient


USERNAME = "tiktok"
LIMIT = 30


def main() -> None:
    client = TikTokShadowBanClient(timeout=900)
    videos, summary = client.check_account(USERNAME, limit=LIMIT)

    banned = [v for v in videos if v.get("shadowbanned")]

    print(f"\nChecked {len(videos)} videos, {len(banned)} shadowbanned:\n")
    for v in banned:
        print(f"  {v.get('createDate')}  health={v.get('videoHealthScore')}  "
              f"{(v.get('description') or '')[:60]}")
        for hint in (v.get("banReasonHints") or []):
            print(f"      - {hint}")
        print(f"      {v.get('url')}")

    if summary:
        print(f"\nOverall: {summary['recommendation']}")


if __name__ == "__main__":
    main()
