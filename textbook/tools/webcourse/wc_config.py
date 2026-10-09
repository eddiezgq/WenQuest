# -*- coding: utf-8 -*-
"""网页版教材开课的公用工具（第 29 轮从《缝纫机设计与制造》抽出来）：每本书的入口（textbook/web-editions/<书>/course/tools/*.py）
设好 WQ_COURSE_DIR（这本书的 course/ 目录）再调用这里的程序；书与书不同的东西都写在 course/course.yaml。"""
import os
from pathlib import Path

import yaml


def course_dir() -> Path:
    d = os.environ.get("WQ_COURSE_DIR")
    if not d:
        raise SystemExit("请用各书 course/tools/ 里的入口运行（它会设 WQ_COURSE_DIR）")
    return Path(d).resolve()


def load(course: Path) -> dict:
    cfg = yaml.safe_load((course / "course.yaml").read_text(encoding="utf-8")) or {}
    cfg.setdefault("deck_id", cfg.get("book"))
    cfg.setdefault("exams", [])
    cfg.setdefault("batches", [{"no": 1, "lessons": cfg.get("lessons") or [], "exams": cfg["exams"]}])
    cfg.setdefault("labs", {})
    cfg.setdefault("heavy_pages", [])
    cfg.setdefault("placeholders", False)
    cfg["labs"] = {int(k): v for k, v in cfg["labs"].items()}
    for k in ("name", "summary", "info"):     # [中文, English]：YAML 里没加引号、含“: ”的一句会被读成字典（第 29 轮）
        v = cfg.get(k)
        if not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, str) for x in v)):
            raise SystemExit(f"course.yaml: {k} 应是 [中文, English] 两句文字（含“: ”的句子要加引号）")
    return cfg
