"""把编译好的 CircuitJS 拼成一个不联网的单文件嵌入页（第 7 轮第 6 步）。

    python3 tools/circuitjs/bundle.py <circuitjs1 源码目录> <输出文件> <上游提交号>

内联：页面自带样式、图标字体（woff2 转 data:）、GWT Clean 主题样式及其图片、模块样式 style.css、
lz-string、单文件脚本（sso 链接器的输出）、中文界面文字。
外层页面把 `<!--WQ-CONFIG-->` 换成自己的设置脚本（启动电路、参数），见 labkit 的电路实验。
"""
import base64
import re
import sys
from pathlib import Path

src, out, commit = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
war = src / "war"
gwt_out = src / "build" / "gwt" / "out" / "circuitjs1"
pub = src / "src" / "com" / "lushprojects" / "circuitjs1" / "public"


def data_uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


shell = (war / "circuitjs.html").read_text(encoding="utf-8")
page_style = re.search(r"<style>.*?</style>", shell, re.S).group(0)

font_css = (war / "font" / "fontello.css").read_text(encoding="utf-8")
woff2 = data_uri(war / "font" / "fontello.woff2", "font/woff2")
font_css = re.sub(r"src:\s*url\('../font/fontello\.eot[^;]*;\s*src:[^;]*;", f"src: url('{woff2}') format('woff2');", font_css, flags=re.S)
font_css = re.sub(r"src:\s*url\('../font/fontello\.svg[^;]*;", f"src: url('{woff2}') format('woff2');", font_css)
if "fontello.eot" in font_css or "fontello.svg" in font_css:
    sys.exit("bundle: 图标字体的 url 没有全部换掉")

clean_dir = gwt_out / "gwt" / "clean"
clean_css = (clean_dir / "clean.css").read_text(encoding="utf-8")
clean_css = re.sub(r"url\(images/([\w.-]+)\)", lambda m: f"url({data_uri(clean_dir / 'images' / m.group(1), 'image/png' if m.group(1).endswith('.png') else 'image/gif')})", clean_css)
module_css = (pub / "style.css").read_text(encoding="utf-8")
if re.search(r"url\((?!data:)", clean_css + module_css):
    sys.exit("bundle: 样式里还有外部 url")

script = (gwt_out / "circuitjs1.nocache.js").read_text(encoding="utf-8")
lz = (war / "lz-string.min.js").read_text(encoding="utf-8")
zh = (pub / "locale_zh.txt").read_text(encoding="utf-8")


def js_str(s: str) -> str:
    import json
    return json.dumps(s, ensure_ascii=False).replace("</", "<\\/")


html = f"""<!DOCTYPE html>
<!-- CircuitJS1 by Paul Falstad and Iain Sharp, GPL-2.0. Upstream https://github.com/pfalstad/circuitjs1 commit {commit};
     embedding patch and build script: WenQuest repository tools/circuitjs/. -->
<html><head><meta charset="utf-8"><meta name="gwt:property" content="locale=en_UK">
{page_style}
<style>{font_css}</style>
<style>{clean_css}</style>
<style>{module_css}</style>
</head><body>
<script>window.CircuitJSEmbedded = true; window.CircuitJSLocaleText = {js_str(zh)};</script>
<!--WQ-CONFIG-->
<script>{lz.replace("</script", "<\\/script")}</script>
<script>{script.replace("</script", "<\\/script")}</script>
</body></html>
"""
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"bundle: {out} {len(html.encode()) / 1e6:.2f} MB")
