"""
Check TikTok videos and export the flattened results to CSV.

Drop into Excel, Google Sheets, Numbers, or import into a database.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/export_to_csv.py > shadowban_report.csv
"""

import csv
import sys

from tiktok_shadowban_checker import TikTokShadowBanClient


VIDEO_URLS = [
    "https://www.tiktok.com/@tiktok/video/7480279424202575159",
    "https://www.tiktok.com/@khaby.lame/video/7299530268907818273",
    "https://www.tiktok.com/@charlidamelio/video/7227253960028196138",
]


COLUMNS = [
    "url",
    "videoId",
    "shadowbanned",
    "videoHealthScore",
    "videoHealthStatus",
    "engagementRate",
    "viralPotentialScore",
    "restrictionCount",
    "indexEnabled",
    "forYouEligible",
    "searchVisible",
    "divertedToPrivate",
    "duetDisabled",
    "stitchDisabled",
    "commentDisabled",
    "downloadDisabled",
    "privateAccount",
    "createDate",
    "locationCreated",
    "duration",
    "description",
    "author_uniqueId",
    "author_nickname",
    "author_verified",
    "author_followers",
    "author_videoCount",
    "views",
    "likes",
    "comments",
    "shares",
    "saves",
    "hashtags",
    "banReasonHints",
    "topRecommendation",
    "allRecommendations",
]


def flatten(rec: dict) -> dict:
    a = rec.get("author") or {}
    s = rec.get("stats") or {}
    out = {
        "url":                  rec.get("url"),
        "videoId":              rec.get("videoId"),
        "shadowbanned":         rec.get("shadowbanned"),
        "videoHealthScore":     rec.get("videoHealthScore"),
        "videoHealthStatus":    rec.get("videoHealthStatus"),
        "engagementRate":       rec.get("engagementRate"),
        "viralPotentialScore":  rec.get("viralPotentialScore"),
        "restrictionCount":     rec.get("restrictionCount"),
        "indexEnabled":         rec.get("indexEnabled"),
        "forYouEligible":       rec.get("forYouEligible"),
        "searchVisible":        rec.get("searchVisible"),
        "divertedToPrivate":    rec.get("divertedToPrivate"),
        "duetDisabled":         rec.get("duetDisabled"),
        "stitchDisabled":       rec.get("stitchDisabled"),
        "commentDisabled":      rec.get("commentDisabled"),
        "downloadDisabled":     rec.get("downloadDisabled"),
        "privateAccount":       rec.get("privateAccount"),
        "createDate":           rec.get("createDate"),
        "locationCreated":      rec.get("locationCreated"),
        "duration":             rec.get("duration"),
        "description":          (rec.get("description") or "").replace("\n", " ")[:200],
        "author_uniqueId":      a.get("uniqueId"),
        "author_nickname":      a.get("nickname"),
        "author_verified":      a.get("verified"),
        "author_followers":     a.get("followerCount"),
        "author_videoCount":    a.get("videoCount"),
        "views":                s.get("views"),
        "likes":                s.get("likes"),
        "comments":             s.get("comments"),
        "shares":               s.get("shares"),
        "saves":                s.get("saves"),
        "hashtags":             "; ".join(rec.get("hashtags") or []),
        "banReasonHints":       "; ".join(rec.get("banReasonHints") or []),
        "topRecommendation":    (rec.get("recommendations") or [None])[0],
        "allRecommendations":   " | ".join(rec.get("recommendations") or []),
    }
    return out


def main() -> None:
    client = TikTokShadowBanClient()
    videos, _ = client.check_urls(VIDEO_URLS, include_summary=False)

    writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    writer.writeheader()
    for v in videos:
        if not v.get("success"):
            continue
        writer.writerow(flatten(v))


if __name__ == "__main__":
    main()
