"""评价系统流水线的验收（第 83 轮）：跑一遍 r5/pipeline.py，11 条规则必须全部通过；三份报告能生成，数字与流水线一致。"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def test_pipeline_all_checks_pass():
    subprocess.run([sys.executable, str(HERE / "r5" / "pipeline.py")], check=True, capture_output=True, timeout=300)
    run = json.loads((HERE / "r5" / "pipeline_run.json").read_text(encoding="utf-8"))
    bad = [c["检查"] for c in run["检查"] if not c["通过"]]
    assert not bad, f"未通过：{bad}"
    assert run["检查通过"] == f"{len(run['检查'])}/{len(run['检查'])}"


def test_reports_build_and_match(tmp_path):
    subprocess.run([sys.executable, str(HERE / "reports" / "build.py"), "--out", str(tmp_path)], check=True, timeout=300)
    d = json.loads((tmp_path / "eval" / "data.json").read_text(encoding="utf-8"))
    run = json.loads((HERE / "r5" / "pipeline_run.json").read_text(encoding="utf-8"))
    for co, v in run["课程目标达成度"].items():
        assert d["course"]["objectives"][co]["direct"] == v["直接"]
    for f in ("eval/课程目标达成情况评价报告.docx", "eval/课程教学质量报告.docx", "xq/毕业要求达成情况评价报告.docx",
              "eval/index.html", "xq/index.html"):
        assert (tmp_path / f).stat().st_size > 1000, f
