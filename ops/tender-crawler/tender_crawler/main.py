"""入口：tender-crawler run | check | test-source <名称> | publish

每天由 systemd 定时器调用 `run`：按配置抓取 → 规则提取 → 去重 → 写出 JSON 与摘要 → （开关打开时）推送。
只访问公开页面；不登录、不报名、不联系任何人。"""
import argparse
import json
import logging
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

from . import __version__, extract
from .http import BlockedError, PoliteSession
from .sources import FETCHERS, SEARCHABLE
from .store import Store

log = logging.getLogger("tender_crawler")
CST = timezone(timedelta(hours=8))


def today_cst():
    """统一按北京时间取"今天"，不依赖服务器时区设置。"""
    return datetime.now(CST).date()
DEFAULT_CONFIG = "/opt/tender-crawler/config.yaml"


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for key in ("run", "politeness", "keywords", "sources", "output"):
        if key not in cfg:
            raise ValueError(f"配置缺少 {key}")
    if cfg.get("llm", {}).get("enabled"):
        raise ValueError("llm.enabled：本版本只用规则提取，请保持 false")
    return cfg


def all_keywords(cfg):
    seen, out = set(), []
    for ws in cfg["keywords"].values():
        for w in ws:
            if w not in seen:
                seen.add(w)
                out.append(w)
    return out


def detail_text(http, url):
    r = http.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    return soup.get_text("\n", strip=True)[:60000]


def collect(cfg, http, only=None):
    """返回 (原始列表项, 来源状态)。某来源被拦截即停止该来源，不影响其他来源。"""
    raw, status = [], []
    kws = all_keywords(cfg)
    for src in cfg["sources"]:
        if only and src["name"] != only:
            continue
        st = {"name": src["name"], "type": src.get("type"), "status": "disabled", "items": 0, "message": ""}
        status.append(st)
        if not src.get("enabled") and not only:
            continue
        fetch = FETCHERS.get(src.get("type"))
        if not fetch:
            st.update(status="error", message="未知的来源类型 %s" % src.get("type"))
            continue
        before = http.requests
        errors, consecutive = [], 0
        try:
            queries = kws if src["type"] in SEARCHABLE else [None]
            for kw in queries:
                try:
                    for it in fetch(http, src, cfg, kw):
                        it["query"] = kw
                        raw.append(it)
                        st["items"] += 1
                    consecutive = 0
                except BlockedError:
                    raise
                except Exception as e:  # noqa: BLE001 — 单个关键词出错，记下后继续；连续 3 次出错才放弃该来源
                    consecutive += 1
                    errors.append(f"{kw}: {type(e).__name__}")
                    log.warning("%s 关键词 %s 出错：%s", src["name"], kw, e)
                    if consecutive >= 3:
                        raise
            st["status"] = "ok" if not errors else "partial"
            st["message"] = "; ".join(errors)[:300]
        except BlockedError as e:
            st.update(status="blocked", message=str(e))
            log.warning("%s 被拦截，今天不再访问：%s", src["name"], e)
        except Exception as e:  # noqa: BLE001 — 一个来源出错不影响其他来源
            st.update(status="error", message=f"{type(e).__name__}: {e}"[:300])
            log.error("%s 连续出错，今天停止：%s", src["name"], e)
        st["requests"] = http.requests - before
    return raw, status


def build_items(cfg, raw, http, store, today):
    wanted = set(cfg.get("notice_types_wanted") or [])
    focus = cfg.get("focus", {})
    start = (today_cst() - timedelta(days=int(cfg["run"].get("days_back", 2)))).isoformat()
    by_key, details_left = {}, int(cfg["run"].get("max_details_per_run", 0)) if cfg["run"].get("fetch_details") else 0
    for it in raw:
        title = it.get("title") or ""
        if not title or (it.get("date") and it["date"] < start):
            continue
        blob = " ".join(filter(None, [title, it.get("buyer"), it.get("type_text")]))
        if extract.excluded(title, cfg.get("exclude", [])):
            continue
        groups, words = extract.keyword_hits(blob, cfg["keywords"])
        if not words:
            continue  # 搜索引擎可能按全文命中；标题和采购人没命中就不收，减少噪音
        key, first = store.first_seen(it, today)
        rec = by_key.get(key)
        if rec:
            rec["keywords"] = sorted(set(rec["keywords"]) | set(words))
            rec["groups"] = sorted(set(rec["groups"]) | set(groups))
            if it["source"] not in rec["sources"]:
                rec["sources"].append(it["source"])
            continue
        ntype = extract.notice_type(it.get("type_text", "") + " " + title)
        rec = {
            "id": key, "title": title, "url": it["url"], "sources": [it["source"]],
            "publish_date": it.get("date"), "first_seen": first, "is_new": first == today,
            "notice_type": ntype, "is_result": ntype == "result",
            "region": it.get("region") or extract.region(blob), "buyer": it.get("buyer") or extract.buyer(blob),
            "budget_cny": None, "deadline": None, "groups": groups, "keywords": words, "focus": [],
            "detail_fetched": False, "detail_excluded_by": [],
        }
        if ntype not in wanted and ntype not in ("result", "other"):
            continue
        if details_left > 0 and rec["is_new"] and not rec["is_result"]:
            details_left -= 1
            try:
                text = detail_text(http, rec["url"])
                rec.update(detail_fetched=True, budget_cny=extract.budget_cny(text), deadline=extract.deadline(text))
                rec["buyer"] = rec["buyer"] or extract.buyer(text)
                rec["region"] = rec["region"] or extract.region(text[:3000])
                g2, w2 = extract.keyword_hits(text, cfg["keywords"])
                rec["keywords"] = sorted(set(rec["keywords"]) | set(w2))
                rec["groups"] = sorted(set(rec["groups"]) | set(g2))
                rec["detail_excluded_by"] = extract.excluded(text[:5000], cfg.get("exclude", []))
            except BlockedError:
                details_left = 0
            except Exception as e:  # noqa: BLE001
                log.info("详情页读取失败 %s: %s", rec["url"], e)
        hay = " ".join(filter(None, [title, rec["buyer"], rec["region"]]))
        rec["focus"] = [p for p in focus.get("provinces", []) if p in hay] + \
                       [u for u in focus.get("universities", []) if u in hay]
        by_key[key] = rec
    items = list(by_key.values())
    items.sort(key=lambda r: r["publish_date"] or "", reverse=True)        # 新发布的在前
    items.sort(key=lambda r: (r["is_result"], not r["focus"], not r["is_new"]))  # 稳定排序：招标类、重点、新增优先
    return items


def write_outputs(cfg, items, status, today):
    out = Path(cfg["output"]["dir"])
    out.mkdir(parents=True, exist_ok=True)
    start = (today_cst() - timedelta(days=int(cfg["run"].get("days_back", 2)))).isoformat()
    by_group = {}
    for r in items:
        for g in r["groups"]:
            by_group[g] = by_group.get(g, 0) + 1
    feed = {
        "schema": "tender-feed/1", "generator": f"tender-crawler {__version__}",
        "generated_at": datetime.now(CST).isoformat(timespec="seconds"), "date": today,
        "window": {"from": start, "to": today},
        "sources": status,
        "summary": {"total": len(items), "new": sum(r["is_new"] for r in items),
                    "open_calls_new": sum(r["is_new"] and not r["is_result"] for r in items), "by_group": by_group},
        "notes": "规则提取，未经人工核对；能否投标由人判断（资质、主体、现场）。",
        "items": items,
    }
    js = json.dumps(feed, ensure_ascii=False, indent=2)
    (out / f"{today}.json").write_text(js, encoding="utf-8")
    (out / "latest.json").write_text(js, encoding="utf-8")
    md = render_md(feed)
    (out / f"{today}.md").write_text(md, encoding="utf-8")
    (out / "latest.md").write_text(md, encoding="utf-8")
    keep = int(cfg["output"].get("keep_days", 90))
    cutoff = (today_cst() - timedelta(days=keep)).isoformat()
    for f in out.glob("20*-*-*.*"):
        if f.stem < cutoff:
            f.unlink()
    return feed, out


def render_md(feed):
    gname = {"engineering": "工程", "education": "教育", "management": "管理"}
    lines = [f"# 招标信息 {feed['date']}", "",
             f"抓取窗口 {feed['window']['from']} ~ {feed['window']['to']}；共 {feed['summary']['total']} 条，"
             f"新增 {feed['summary']['new']} 条（其中招标/采购类 {feed['summary']['open_calls_new']} 条）。", "",
             "## 来源状态", ""]
    for s in feed["sources"]:
        lines.append(f"- {s['name']}：{s['status']}，{s['items']} 条 {s.get('message') or ''}".rstrip())
    lines += ["", "## 新增（招标 / 采购类）", ""]
    new = [r for r in feed["items"] if r["is_new"] and not r["is_result"]]
    for r in new or []:
        budget = f"{r['budget_cny'] / 10000:.2f} 万元" if r["budget_cny"] else "预算未识别"
        lines.append(f"- [{r['title']}]({r['url']})  \n  {r['publish_date'] or ''} · {r['region'] or ''} · "
                     f"{r['buyer'] or '采购人未识别'} · {budget} · 截止 {r['deadline'] or '未识别'} · "
                     f"{'/'.join(gname.get(g, g) for g in r['groups'])} · 关键词：{'、'.join(r['keywords'])}"
                     + (f" · 重点：{'、'.join(r['focus'])}" if r["focus"] else ""))
    if not new:
        lines.append("（无）")
    return "\n".join(lines) + "\n"


def publish(cfg, out, today):
    pub = cfg.get("publish", {})
    files = [out / f"{today}.json", out / f"{today}.md", out / "latest.json", out / "latest.md"]
    o = pub.get("oss", {})
    if o.get("enabled"):
        import oss2  # 只有打开 OSS 开关才需要安装：pip install oss2
        auth = oss2.Auth(os.environ[o["access_key_id_env"]], os.environ[o["access_key_secret_env"]])
        bucket = oss2.Bucket(auth, o["endpoint"], o["bucket"])
        for f in files:
            bucket.put_object_from_file(o.get("prefix", "") + f.name, str(f))
        log.info("已上传到 OSS %s/%s", o["bucket"], o.get("prefix", ""))
    e = pub.get("email", {})
    if e.get("enabled"):
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText((out / f"{today}.md").read_text(encoding="utf-8"), "plain", "utf-8")
        msg["Subject"] = f"招标信息 {today}"
        msg["From"] = os.environ[e["username_env"]]
        msg["To"] = ", ".join(e["to"])
        with smtplib.SMTP_SSL(e["smtp_host"], int(e.get("smtp_port", 465))) as s:
            s.login(os.environ[e["username_env"]], os.environ[e["password_env"]])
            s.sendmail(msg["From"], e["to"], msg.as_string())
        log.info("已发送邮件给 %s", e["to"])


def cmd_run(cfg, only=None):
    today = today_cst().isoformat()
    out = Path(cfg["output"]["dir"])
    out.mkdir(parents=True, exist_ok=True)
    http = PoliteSession(cfg)
    store = Store(str(out / "seen.sqlite3"))
    raw, status = collect(cfg, http, only)
    items = build_items(cfg, raw, http, store, today)
    feed, out = write_outputs(cfg, items, status, today)
    log.info("完成：%s 条，新增 %s 条；请求 %s 次", feed["summary"]["total"], feed["summary"]["new"], http.requests)
    if not only:
        publish(cfg, out, today)
    return feed


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tender-crawler")
    ap.add_argument("-c", "--config", default=os.environ.get("TENDER_CONFIG", DEFAULT_CONFIG))
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="抓取一次（定时任务调用这个）")
    sub.add_parser("check", help="检查配置文件")
    t = sub.add_parser("test-source", help="只试抓一个来源，结果写到 output 目录")
    t.add_argument("name")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        cfg = load_config(args.config)
    except Exception as e:  # noqa: BLE001
        print(f"配置有误：{e}", file=sys.stderr)
        return 2
    if args.cmd == "check":
        en = [s["name"] for s in cfg["sources"] if s.get("enabled")]
        print(f"配置正常。关键词 {len(all_keywords(cfg))} 个；启用来源：{'、'.join(en) or '无'}")
        return 0
    if args.cmd == "test-source":
        if args.name not in [s["name"] for s in cfg["sources"]]:
            print(f"没有名为 {args.name} 的来源", file=sys.stderr)
            return 2
        feed = cmd_run(cfg, only=args.name)
        print(json.dumps(feed["sources"], ensure_ascii=False, indent=2))
        print(f"收录 {feed['summary']['total']} 条，见 {cfg['output']['dir']}/latest.md")
        return 0
    feed = cmd_run(cfg)
    bad = [s for s in feed["sources"] if s["status"] in ("blocked", "error")]
    return 1 if bad and len(bad) == len([s for s in feed["sources"] if s["status"] != "disabled"]) else 0


if __name__ == "__main__":
    sys.exit(main())
