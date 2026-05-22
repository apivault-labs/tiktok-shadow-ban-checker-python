"""
Filter a list of TikTok video URLs down to only the shadow-banned ones.

Use case: feed a long list of recent uploads (yours or a competitor's),
surface only the videos that need investigation or re-uploading, and
print the actionable recommendations alongside.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/only_shadowbanned.py
"""

from tiktok_shadowban_checker import TikTokShadowBanClient


VIDEO_URLS = [
    "https://www.tiktok.com/@tiktok/video/7480279424202575159",
    "https://www.tiktok.com/@khaby.lame/video/7299530268907818273",
    "https://www.tiktok.com/@charlidamelio/video/7227253960028196138",
    "https://www.tiktok.com/@addisonre/video/7299530268907818275",
    "https://www.tiktok.com/@bellapoarch/video/7227253960028196138",
]


def main() -> None:
    client = TikTokShadowBanClient(timeout=900)
    videos, summary = client.check_urls(VIDEO_URLS)

    banned = [v for v in videos if v.get("shadowbanned")]

    print(f"\nChecked {len(videos)} videos, {len(banned)} shadowbanned:\n")
    for v in banned:
        author = "@" + ((v.get("author") or {}).get("uniqueId") or "?")
        date = v.get("createDate") or "?"
        health = v.get("videoHealthScore") or "?"
        desc = (v.get("description") or "")[:60]
        print(f"  {author:<22} {date}  health={health}  {desc}")

        for hint in (v.get("banReasonHints") or []):
            print(f"      hint: {hint}")
        for rec in (v.get("recommendations") or [])[1:]:  # skip verdict line
            print(f"      💡 {rec}")
        print(f"      url: {v.get('url')}\n")

    if summary:
        print(f"Overall: {summary['recommendation']}")


if __name__ == "__main__":
    main()
