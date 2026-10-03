"""第 1 章浏览器实验自动测试（第 17 轮 2b 验收）。
逐个实验按任务要求设置参数、填答案，检查全部任务自动判定完成；中/EN 切换；手机宽度无横向滚动；无脚本错误。
用法：python labs/micro/tools/test_dic_ch1.py [--shots 目录]
"""
import json, sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[3]
PAGE = ROOT / "labs/micro/dic-ch1/index.html"
REF = json.loads((ROOT / "samples/数字集成电路设计/生成脚本/ref.json").read_text(encoding="utf-8"))
shots = pathlib.Path(sys.argv[sys.argv.index("--shots") + 1]) if "--shots" in sys.argv else None


def set_range(page, rid, value):
    page.evaluate("([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input')); e.dispatchEvent(new Event('change')); }", [rid, value])


def answer(page, lab, task, value):
    sel = f'#tk{lab} input[data-task="{lab}:{task}"]'
    page.fill(sel, str(value))
    page.press(sel, "Enter")


def done(page, lab):
    return page.evaluate(f"WQLab.tasks['{lab}'].list.map(t => [t.id, t.ok])")


def main():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1280, "height": 900})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: m.type == "error" and "Failed to load resource" not in m.text and errors.append(m.text))
        page.goto(PAGE.as_uri())
        page.evaluate("WQLab.reset()")

        # 1.1
        page.click('nav.tabs [data-lab="1"]')
        page.click("#vin1lo"); page.click("#vin1hi")
        set_range(page, "il1", 1.0); set_range(page, "wn1", round(REF["p11"]["Wn"] + 0.02, 2))
        page.wait_for_timeout(50)
        vol2 = None
        answer(page, 1, "twice", 0.443)
        if shots: page.screenshot(path=str(shots / "lab1.png"), full_page=True)
        # 1.2
        page.click('nav.tabs [data-lab="2"]')
        set_range(page, "r2", 2.25)
        set_range(page, "r2", 1.0); answer(page, 2, "nml", round(REF["p12"]["ratio1"]["NML"], 3))
        set_range(page, "nz2", 0.3); set_range(page, "r2", 2.25)
        if shots: page.screenshot(path=str(shots / "lab2.png"), full_page=True)
        # 1.3
        page.click('nav.tabs [data-lab="3"]')
        set_range(page, "fo3", 4); set_range(page, "r3", 2.25); set_range(page, "r3", 1.5)
        answer(page, 3, "mis", round(REF["p13"]["ratio1"]["mismatch"] * 100, 1))
        if shots: page.screenshot(path=str(shots / "lab3.png"), full_page=True)
        # 1.4
        page.click('nav.tabs [data-lab="4"]')
        set_range(page, "cl4", 10); set_range(page, "n4", 7); set_range(page, "n4", 5)
        f6 = REF["p14"]["F"] ** (1 / 6)
        answer(page, 4, "f", round(f6, 2))
        if shots: page.screenshot(path=str(shots / "lab4.png"), full_page=True)
        # 1.5
        page.click('nav.tabs [data-lab="5"]')
        answer(page, 5, "read", round(REF["p15"]["P_VDD"] * 1e3, 2))
        set_range(page, "v5", 1.2)
        set_range(page, "v5", 1.21)
        if shots: page.screenshot(path=str(shots / "lab5.png"), full_page=True)

        results = {lab: done(page, lab) for lab in "12345"}
        total = sum(len(v) for v in results.values()); ok = sum(o for v in results.values() for _, o in v)
        # 语言切换
        page.click("#lang")
        en_title = page.inner_text("h1")
        prog = page.inner_text("#progress")
        if shots: page.screenshot(path=str(shots / "lab5_en.png"), full_page=True)
        page.click("#lang")
        log_types = page.evaluate("[...new Set(WQLab.log.map(m => m.type))]")
        # 手机宽度
        m = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        m.on("pageerror", lambda e: errors.append("mobile: " + str(e)))
        m.goto(PAGE.as_uri())
        overflow = []
        for lab in "12345":
            m.click(f'nav.tabs [data-lab="{lab}"]'); m.wait_for_timeout(50)
            if m.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1"): overflow.append(lab)
            if shots and lab in "13": m.screenshot(path=str(shots / f"mobile_lab{lab}.png"), full_page=True)
        b.close()

    print("任务：", json.dumps(results, ensure_ascii=False))
    print(f"完成 {ok}/{total}；英文标题：{en_title}；进度：{prog}")
    print("操作记录类型：", log_types)
    print("手机横向溢出：", overflow or "无")
    print("脚本错误：", errors or "无")
    if ok != total or overflow or errors or en_title != "CMOS Inverter Lab Bench":
        sys.exit(1)


if __name__ == "__main__":
    main()
