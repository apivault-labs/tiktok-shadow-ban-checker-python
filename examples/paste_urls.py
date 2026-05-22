"""
Check a multi-line block of TikTok URLs without manually splitting them.

Useful when you copy-paste a column from a Google Sheet, Notion table or
Slack message — `check_text()` accepts any whitespace or comma separator,
deduplicates client-side and forwards everything to the actor.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/paste_urls.py
"""

from tiktok_shadowban_checker import TikTokShadowBanClient


# Paste raw — newlines, tabs, commas, mixed whitespace all work
URL_BLOCK = """
https://www.tiktok.com/@tiktok/video/7480279424202575159
https://www.tiktok.com/@khaby.lame/video/7299530268907818273

https://www.tiktok.com/@addisonre/video/7299530268907818275, https://www.tiktok.com/@bellapoarch/video/7227253960028196138
"""


def main() -> None:
    client = TikTokShadowBanClient(timeout=900)
    videos, summary = client.check_text(URL_BLOCK, include_recommendations=True)

    print(f"Found and checked {len(videos)} videos\n")
    for v in videos:
        if not v.get("success"):
            continue
        author = "@" + ((v.get("author") or {}).get("uniqueId") or "?")
        verdict = "BANNED" if v.get("shadowbanned") else "ok"
        health = v.get("videoHealthScore")
        print(f"  {author:<22} {verdict:<7} health={health}/100")
        for rec in (v.get("recommendations") or [])[:2]:
            print(f"      {rec}")

    if summary:
        print(f"\nOverall: {summary['recommendation']}")


if __name__ == "__main__":
    main()
