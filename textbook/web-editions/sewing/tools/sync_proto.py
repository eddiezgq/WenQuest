"""The virtual-machine pages carry both languages in one source; the English page is the Chinese page with lang="en".
    python3 tools/sync_proto.py        # writes the English copies of the pages listed in PAGES
"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1] / "src"
PAGES = ["proto-lockstitch.html", "tune-lockstitch.html"]          # only the bilingual virtual-machine pages (not proto-ls / proto-fk, which are separate labs)
for p in [ROOT / "zh" / "labs" / n for n in PAGES]:
    s = p.read_text(encoding="utf-8").replace('<html lang="zh-CN">', '<html lang="en">', 1)
    s = s.replace('<a class="back" href="../index.html"', '<a class="back" href="../index.html"', 1)
    (ROOT / "en" / "labs" / p.name).write_text(s, encoding="utf-8")
    print("en/labs/" + p.name)
