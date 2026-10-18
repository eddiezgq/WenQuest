"""Build site/vendor/: fonts and browser libraries served from our own server instead of Google Fonts and cdnjs
(第 34 轮: in mainland China Google Fonts cannot be reached and cdnjs is slow; a blocked stylesheet in <head> holds the
whole page). Same font files and library versions as before, so pages look the same.

    cd tools/vendor && npm ci --ignore-scripts && python3 build.py ../../site/vendor

Output:
    fonts/<family>.css + fonts/<family>/*.woff2   (unicode-range slices: a browser downloads only the characters used)
    three/r128/three.min.js, katex/0.16.9/katex.min.js, npm/digitaljs@0.14.2/dist/ (Verilog lab simulator)
    VERSION   (hash of package-lock.json: the deploy copies the folder only when it changed)
"""
import hashlib
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NM = HERE / "node_modules"

# family name as pages use it -> (package dir, css files). Weights cover every page (localize.FAMILIES lists them).
FONTS = {
    "Noto Sans SC": ("@fontsource/noto-sans-sc", ["400", "500", "600", "700"]),
    "Noto Serif SC": ("@fontsource/noto-serif-sc", ["500", "600", "700", "900"]),
    "Noto Sans": ("@fontsource/noto-sans", ["400", "500", "700"]),
    "Noto Serif": ("@fontsource/noto-serif", ["700"]),
    "JetBrains Mono": ("@fontsource/jetbrains-mono", ["400", "500", "600", "700"]),
    "IBM Plex Mono": ("@fontsource/ibm-plex-mono", ["400", "500", "600"]),
    "IBM Plex Sans": ("@fontsource/ibm-plex-sans", ["400", "500", "600"]),
    "Source Serif 4": ("@fontsource/source-serif-4", ["400", "600", "400-italic"]),
    "Archivo": ("@fontsource-variable/archivo", ["wdth"]),
}
LIBS = {
    "three/r128/three.min.js": "three/build/three.min.js",
    "katex/0.16.9/katex.min.js": "katex/dist/katex.min.js",
    # Verilog 实验的仿真器（国内部署时网关让页面从这里取，window.WQ_ENGINE_BASE = '/vendor/npm/'）
    "npm/digitaljs@0.14.2/dist/main.js": "digitaljs/dist/main.js",
    "npm/digitaljs@0.14.2/dist/285.main.js": "digitaljs/dist/285.main.js",
    "npm/digitaljs@0.14.2/dist/821.main.js": "digitaljs/dist/821.main.js",
    # 浏览器 MuJoCo（第 41 轮）：官方单线程版，与教材构建用的 Python 版 mujoco==3.14.0 同一版本
    "npm/@mujoco/mujoco@3.14.0/mujoco.js": "@mujoco/mujoco/mujoco.js",
    "npm/@mujoco/mujoco@3.14.0/mujoco.wasm": "@mujoco/mujoco/mujoco.wasm",
    # 白板讲课（第 35 轮）的手绘线条
    "roughjs/4.6.6/rough.js": "roughjs/bundled/rough.js",
}


def slug(family: str) -> str:
    return family.lower().replace(" ", "-")


def font_css(family: str, pkg: str, parts: list[str], out: Path) -> int:
    src_dir = NM / pkg
    dest = out / "fonts" / slug(family)
    dest.mkdir(parents=True, exist_ok=True)
    css, n = [], 0
    for part in parts:
        text = (src_dir / f"{part}.css").read_text(encoding="utf-8")
        for block in re.findall(r"@font-face\s*\{[^}]*\}", text):
            m = re.search(r"url\(\./files/([^)]+?\.woff2)\)\s*format\('([^']+)'\)", block)
            if not m:
                continue
            name, fmt = m.groups()
            shutil.copyfile(src_dir / "files" / name, dest / name)
            n += 1
            block = re.sub(r"src:[^;]*;", f"src: url({slug(family)}/{name}) format('{fmt}');", block)
            block = re.sub(r"font-family:\s*'[^']*'", f"font-family: '{family}'", block)
            css.append(block)
    (out / "fonts" / f"{slug(family)}.css").write_text("\n".join(css) + "\n", encoding="utf-8")
    return n


def main(out: Path) -> None:
    if not NM.is_dir():
        sys.exit("tools/vendor/node_modules is missing: run npm ci in tools/vendor first")
    if out.exists():
        shutil.rmtree(out)
    files = 0
    for family, (pkg, parts) in FONTS.items():
        files += font_css(family, pkg, parts, out)
    for dest, src in LIBS.items():
        (out / dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(NM / src, out / dest)
    version = hashlib.sha256((HERE / "package-lock.json").read_bytes() + Path(__file__).read_bytes()).hexdigest()[:16]
    (out / "VERSION").write_text(version + "\n")
    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    print(f"site/vendor: {len(FONTS)} font families ({files} files), {len(LIBS)} libraries, {size / 1e6:.1f} MB, version {version}")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else HERE.parent.parent / "site" / "vendor").resolve())
