#!/usr/bin/env python3
"""《机械制造技术》各章的网页互动课件（第 13 轮十）。先构建本书（python3 textbook/tools/build.py mfgtech），再：

    python3 textbook/mfgtech/course/tools/build_slides.py ch54 --out <目录> [--preview all] [--media <本地 Manim 视频目录>]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "webcourse"))
import wc_book  # noqa: E402

if __name__ == "__main__":
    sys.exit(wc_book.main("mfgtech"))
