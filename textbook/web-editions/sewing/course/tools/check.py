#!/usr/bin/env python3
"""本书的检查每讲文件：调用公用工具 textbook/tools/webcourse/wc_check.py（第 29 轮起各书共用，书与书不同的写在 ../course.yaml）。"""
import os
import sys
from pathlib import Path

_COURSE = Path(__file__).resolve().parents[1]
os.environ["WQ_COURSE_DIR"] = str(_COURSE)
sys.path.insert(0, str(_COURSE.parents[2] / "tools" / "webcourse"))
from wc_check import *  # noqa: E402,F401,F403  （讲课视频的程序从这里取 make_deck）
from wc_check import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
