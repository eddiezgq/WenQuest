"""问渠电子帮助录像（第 113 轮 P6）：起草台、问渠贴片、网页审图各录一段，字幕直接显示在画面下方。

    python3 services/eda/tools/record_help.py --out services/eda/web/help/videos

在本机起一份服务（AI 换成事先写好的示例回答，画面上写明），用 Playwright 自动操作、录屏。页面改了就重录。
用的都是演示数据：示例设计、虚构工厂。要 Python 版 playwright 和 Chromium。"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SERVICE = os.path.dirname(HERE)
os.environ.setdefault("EDA_SIM", "0")
sys.path.insert(0, SERVICE)

SIZE = {"width": 1280, "height": 720}


def S(key, value, source="requirement", quote="", why=""):
    return {"key": key, "value": value, "source": source, "quote": quote, "why": why}


DRAFT = {"spec": [S("bus_voltage_v", 48, quote="48 V"), S("phase_current_a", 8.5, quote="额定相电流 8.5 A"),
                  S("phase_current_peak_a", 30, quote="峰值 30 A")],
         "units": [{"type": "encoder", "params": [S("lines", 2500, quote="2500 线")]}],
         "questions": [], "unsupported": []}


class _R:
    status_code = 200

    def __init__(self, b):
        self.b = b

    def json(self):
        return self.b


class _Client:
    """替身网关：起草台和问题单的 AI 回答是事先写好的示例（录像里写明）"""

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def post(self, url, headers=None, json=None):
        if url.endswith("/eda/ai/issues"):
            ids = [r["id"] for r in json["results"]]
            return _R({"draft": {"issues": [
                {"cites": ids[:1],
                 "question": "C47 在坐标里有，物料清单里没有：这个位置要不要贴？如果要贴，请补上物料编号。",
                 "options": ["要贴：补物料编号后重新发物料清单", "不贴：从坐标里删掉"],
                 "reply_required": True}]}, "run": 1})
        return _R({})


def start():
    import uvicorn

    import app as A

    A.gateway_model = lambda request: ((lambda r, c, lang, f: (DRAFT, 1)), (lambda *a: None))
    A._client = lambda: _Client()
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    srv = uvicorn.Server(uvicorn.Config(A.app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=srv.run, daemon=True).start()
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", port), 0.2).close()
            break
        except OSError:
            time.sleep(0.1)
    return srv, "http://127.0.0.1:{}".format(port)


CAPTION_JS = """(t) => {
  let d = document.getElementById('wq-cap');
  if (!d) { d = document.createElement('div'); d.id = 'wq-cap';
    d.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);max-width:86%;z-index:99999;' +
      'background:rgba(16,22,20,.86);color:#fff;font:600 22px/1.5 "Noto Sans CJK SC","PingFang SC",sans-serif;' +
      'padding:10px 18px;border-radius:8px;text-align:center;pointer-events:none';
    document.body.appendChild(d); }
  d.textContent = t; d.style.display = t ? 'block' : 'none';
}"""


def cap(page, text, wait=2.6):
    page.evaluate(CAPTION_JS, text)
    page.wait_for_timeout(int(wait * 1000))


def desk(page, base):
    page.goto(base + "/")
    cap(page, "问渠电子 · 起草台：一句话需求，起草一块电机驱动板")
    page.click("#examples button")
    cap(page, "点一个示例需求（演示里 AI 的回答是事先准备的示例）")
    page.click("#go")
    page.wait_for_selector("#tally b", timeout=120000)
    cap(page, "每个数都标了来源：需求原文、规则推出、AI 假设", 3.2)
    page.locator("#unitsT").scroll_into_view_if_needed()
    cap(page, "代码马上展开电路、跑计算和仿真；四种结论：通过、不通过、待核对、未知", 3.2)
    page.locator("#boardT").scroll_into_view_if_needed()
    cap(page, "板子检查：用模板板子按新规格查工艺、布局和发热", 3.2)
    page.fill("#s-phase_current_a", "15")
    page.click("#again")
    page.wait_for_timeout(4000)
    page.locator("#boardT").scroll_into_view_if_needed()
    cap(page, "额定电流改到 15 A，大电流线宽马上判不通过", 3.4)
    page.locator("#ok").scroll_into_view_if_needed()
    page.check("#ok")
    cap(page, "看过 AI 假设的数、勾选确认，才能下载设计描述", 3.0)
    cap(page, "", 0.5)


def factory(page, base):
    page.goto(base + "/factory/")
    page.wait_for_selector("#factory option", state="attached")
    cap(page, "问渠贴片：客户的资料包进厂前先查一遍")
    page.click("#demo")
    page.wait_for_selector("#res tr[data-id]", timeout=60000)
    cap(page, "演示资料包：驱动板 A 版，故意漏了一个物料编号", 3.0)
    page.click('#res tr[data-id="R1"]')
    cap(page, "点一行结果，板图上标出位置：C47 在坐标里有、物料清单里没有", 3.6)
    page.locator("#qty").scroll_into_view_if_needed()
    cap(page, "数量统计是报价依据：贴片件、焊点、通孔件、物料种类", 3.2)
    page.locator("#draft").scroll_into_view_if_needed()
    page.click("#draft")
    page.wait_for_selector(".issue", timeout=60000)
    cap(page, "AI 只拿到没通过的检查结果，起草给客户的问题单；每条都要引用一条结果", 3.6)
    page.check("#ok")
    cap(page, "工程师改完、确认后下载：YAML 给设计端，Markdown 发客户", 3.2)
    cap(page, "", 0.5)


def view(page, base):
    page.goto(base + "/view/")
    page.wait_for_selector("#issues li[data-i]", timeout=60000)
    page.wait_for_timeout(5000)
    cap(page, "网页审图：不装软件，看原理图和板子", 3.0)
    page.click('#issues li[data-i="2"]')
    cap(page, "点报告里的一条，板子上跳到那个器件", 3.4)
    page.click('.tabs button[data-tab="sch"]')
    page.wait_for_timeout(3000)
    cap(page, "原理图也能看；自己电脑上的 KiCad 文件只在浏览器里打开，不上传", 3.6)
    cap(page, "在 KiCad 9 里用插件：一键检查、定位、读回摆放、出报告", 3.2)
    cap(page, "", 0.5)


def main(argv=None):
    from playwright.sync_api import sync_playwright

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    srv, base = start()
    tmp = tempfile.mkdtemp(prefix="wq-rec-")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for name, flow in (("desk", desk), ("factory", factory), ("view", view)):
                ctx = b.new_context(viewport=SIZE, record_video_dir=tmp, record_video_size=SIZE, locale="zh-CN")
                ctx.add_cookies([{"name": "wq_sso", "value": "demo", "url": base}])
                page = ctx.new_page()
                flow(page, base)
                path = page.video.path()
                ctx.close()
                shutil.move(path, os.path.join(a.out, name + ".webm"))
                print(name, os.path.getsize(os.path.join(a.out, name + ".webm")), "字节")
            b.close()
    finally:
        srv.should_exit = True
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
