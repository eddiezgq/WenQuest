#!/usr/bin/env python3
"""Practical AI at Work · web slides (one deck per session), built with the shared engine textbook/tools/webcourse/wc_slides.py.

    python3 training/us/ai-at-work/course/tools/build_slides.py ch01 --lang en --out <dir> [--preview all]
US classes use --lang en (round 140: English only); the yaml keeps [中文, English] pairs so the content can be reviewed in Chinese.
"""
import os
import sys
from pathlib import Path

_COURSE = Path(__file__).resolve().parents[1]
os.environ["WQ_COURSE_DIR"] = str(_COURSE)
sys.path.insert(0, str(_COURSE.parents[3] / "textbook" / "tools" / "webcourse"))
from wc_slides import *  # noqa: E402,F401,F403
from wc_slides import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
