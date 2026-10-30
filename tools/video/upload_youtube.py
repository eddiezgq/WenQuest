"""上传到 YouTube（第 22 轮 2.4；2026-10-30 起中文版也传，Eddie：“以后把中文也传到YouTube”）：官方 YouTube Data API v3，Eddie 授权一次（刷新令牌存仓库密钥）。

    python3 tools/video/upload_youtube.py OUT_DIR/en|OUT_DIR/zh [--privacy private|unlisted|public] [--playlist "Linear Algebra (WenQuest)"]

OUT_DIR/<lang> 是 make.py 的输出：lecture.mp4、upload.json（标题、简介、标签、语言、播放列表）、cover_youtube.png、lecture.srt。
语言按 upload.json 的 lang（zh → 简体中文，否则英文）；播放列表按 upload.json 的 playlist（中英各一个），没有时用 --playlist。
环境变量：YT_CLIENT_ID、YT_CLIENT_SECRET、YT_REFRESH_TOKEN。
注意：Google 审核通过前，接口上传的视频会被锁为私密（private），要 Eddie 在 YouTube Studio 里手动公开。
配音是 AI 合成，status.containsSyntheticMedia = true（YouTube 的“改动或合成内容”声明）。
每个视频约用 1600 + 50 + 400 + 50 配额单位，默认每天 10000 单位，约 4–5 个视频。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def client():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"].strip(), client_id=os.environ["YT_CLIENT_ID"].strip(),
                        client_secret=os.environ["YT_CLIENT_SECRET"].strip(), token_uri="https://oauth2.googleapis.com/token",
                        scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"])
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def playlist_id(yt, title: str, lang: str = "en") -> str:
    req = yt.playlists().list(part="snippet", mine=True, maxResults=50)
    while req:
        r = req.execute()
        for p in r.get("items", []):
            if p["snippet"]["title"] == title:
                return p["id"]
        req = yt.playlists().list_next(req, r)
    p = yt.playlists().insert(part="snippet,status", body={"snippet": {"title": title, "defaultLanguage": lang},
                                                           "status": {"privacyStatus": "public"}}).execute()
    return p["id"]


def upload(d: Path, privacy: str, playlist: str | None) -> str:
    from googleapiclient.http import MediaFileUpload
    meta = json.loads((d / "upload.json").read_text(encoding="utf-8"))
    zh = meta.get("lang") == "zh"
    yl = "zh-Hans" if zh else "en"
    playlist = playlist or meta.get("playlist") or "Linear Algebra (WenQuest)"
    yt = client()
    body = {"snippet": {"title": meta["title"][:100], "description": meta["description"][:5000], "tags": meta["tags"],
                        "categoryId": "27", "defaultLanguage": yl, "defaultAudioLanguage": yl},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True,
                       "license": "youtube", "embeddable": True}}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(d / "lecture.mp4"), chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", flush=True)
    vid = resp["id"]
    yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(d / "cover_youtube.png"))).execute()
    if (d / "lecture.srt").exists():
        yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": yl, "name": "中文" if zh else "English"}},
                             media_body=MediaFileUpload(str(d / "lecture.srt"), mimetype="application/octet-stream")).execute()
    if playlist:
        yt.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": playlist_id(yt, playlist, yl),
                                                                    "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
    print(f"https://youtu.be/{vid}  ({privacy})")
    return vid


def check():
    """授权检查：列出频道名和播放列表（约 2 个配额单位），不上传任何东西。"""
    yt = client()
    ch = yt.channels().list(part="snippet,statistics", mine=True).execute().get("items", [])
    if not ch:
        sys.exit("授权有效，但这个账号下没有 YouTube 频道")
    for c in ch:
        print(f"频道：{c['snippet']['title']}（{c['id']}），视频 {c['statistics'].get('videoCount')} 个")
        print(f"::notice title=YouTube 授权有效::频道 {c['snippet']['title']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    ap.add_argument("--playlist", default=None, help="不写时用 upload.json 里的 playlist（没有就是 Linear Algebra (WenQuest)）")
    a = ap.parse_args()
    for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
        if not os.environ.get(k):
            sys.exit(f"没有设置 {k}")
    if a.dir == "check":
        check()
    else:
        upload(Path(a.dir), a.privacy, a.playlist)
