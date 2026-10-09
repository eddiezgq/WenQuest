"""实验页中英合一（第 29 轮）：文字都在页内的 TX 字典里（[中文, English]），按 <html lang> 选语言。
改了 src/zh/labs/*.html 以后运行本程序，生成 src/en/labs/ 下的英文页（只改 lang 和 <title>、少量静态标签）。
    python3 tools/sync_labs.py"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES = {"weibull": "Weibull reliability: how long will the machine last?", "pmopt": "Choosing the service interval"}
for p in sorted((ROOT / "src" / "zh" / "labs").glob("*.html")):
    s = p.read_text(encoding="utf-8")
    s = s.replace('<html lang="zh-CN">', '<html lang="en">', 1)
    if p.stem in TITLES:
        s = re.sub(r"<title>.*?</title>", f"<title>{TITLES[p.stem]}</title>", s, count=1)
    s = s.replace("（h）</label>", " (h)</label>")
    (ROOT / "src" / "en" / "labs" / p.name).write_text(s, encoding="utf-8")
    print("en/labs/" + p.name)
