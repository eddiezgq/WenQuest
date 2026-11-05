"""官网首页“看视频认识问渠”的数据（第 80 轮）：读 YouTube 频道里几个播放列表，只取公开的视频，写 site/data/videos.json。

    python3 tools/site_home/videos.py            # 要 YT_CLIENT_ID、YT_CLIENT_SECRET、YT_REFRESH_TOKEN（与上传公开课视频同一组）

由工作流 site-videos.yml 每天跑一次。播放列表、首页挑的“典型”几讲写在 catalog.yaml 的 videos 一节；
列表里没有的播放列表跳过（例如白板科普还没上传时），不报错。读列表约 1 个配额单位一页，很省。
"""
from __future__ import annotations

import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools" / "video"))


def playlists(yt) -> dict[str, str]:
    out, req = {}, yt.playlists().list(part="snippet", mine=True, maxResults=50)
    while req:
        r = req.execute()
        out.update({p["snippet"]["title"]: p["id"] for p in r.get("items", [])})
        req = yt.playlists().list_next(req, r)
    return out


def items(yt, pid: str) -> list[dict]:
    """播放列表里的视频（公开的才留），按发布时间新的在前"""
    ids, req = [], yt.playlistItems().list(part="contentDetails", playlistId=pid, maxResults=50)
    while req:
        r = req.execute()
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        req = yt.playlistItems().list_next(req, r)
    vids = []
    for k in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,status,contentDetails", id=",".join(ids[k:k + 50])).execute()
        for v in r.get("items", []):
            if v["status"].get("privacyStatus") != "public" or not v["status"].get("embeddable", True):
                continue
            sn = v["snippet"]
            vids.append({"id": v["id"], "title": sn["title"], "date": sn.get("publishedAt", "")[:10],
                         "dur": v["contentDetails"].get("duration", "")})
    vids.sort(key=lambda x: x["date"], reverse=True)
    return vids


def main():
    from upload_youtube import client
    cat = yaml.safe_load((HERE / "catalog.yaml").read_text(encoding="utf-8"))
    yt = client()
    have = playlists(yt)
    ch = yt.channels().list(part="snippet", mine=True).execute().get("items", [])
    out = {"channel": f"https://www.youtube.com/channel/{ch[0]['id']}" if ch else "", "lists": {}}
    for key, titles in cat["videos"]["playlists"].items():
        vids = []
        for t in titles:
            if t in have:
                vids += items(yt, have[t])
            else:
                print(f"播放列表还没有：{t}")
        out["lists"][key] = sorted({v["id"]: v for v in vids}.values(), key=lambda x: x["date"], reverse=True)
        print(key, len(out["lists"][key]), "个公开视频")
    p = ROOT / "site" / "data" / "videos.json"
    p.parent.mkdir(exist_ok=True)
    old = p.read_text(encoding="utf-8") if p.exists() else ""
    new = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    if new != old:
        p.write_text(new, encoding="utf-8")
        print("已更新", p)


if __name__ == "__main__":
    main()
