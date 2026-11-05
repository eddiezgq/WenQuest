# 评价系统（第 83 轮进仓库）

另一个窗口设计的“教学评价”程序包（那边的第 3～5 轮），原样放在这里。报告见 `docs/方案/评价系统/`，本轮细则见 `docs/实施细则/第83轮_2026-11-05_评价系统流水线上线.md`。

| 文件 | 用途 |
|---|---|
| `cat_engine.py` | 自适应诊断与考试（第 3 轮） |
| `process_scoring.py` | 虚拟实验过程考核（E8、E9） |
| `defense/defense_panel.py` | AI 答辩组合议（模拟评分，不是真模型调用） |
| `build_transcript.py` | 成绩单：A55/B30/C15、七档等级、四维画像 |
| `r4/` | 课程目标达成度、教师报告指标、评教、课程质量审核、问渠 ⇄ 校情中枢数据契约 v1 |
| `r5/learning_path.py` | 学习路径推荐 |
| `r5/pipeline.py` | 一条流水线跑完一学期（30 人模拟班），11 条规则检查 |
| `reports/build.py` | **第 83 轮新增**：用流水线结果生成三份评估报告（网页 + Word）和两个演示页：官网 `/eval/`（学生、教师、学校三端）、`/xq/`（校情中枢 V0） |

运行：

```bash
pip install numpy jsonschema openpyxl python-docx
python3 services/eval/r5/pipeline.py          # 结果写在 r5/pipeline_*.json
python3 services/eval/reports/build.py        # 生成 site/eval/、site/xq/
python3 -m pytest -q services/eval/tests      # 11 条规则 + 报告与流水线一致
```

在仓库里的改动：没有改原程序；只加了 `reports/`、`tests/` 和本说明。数据全部是模拟的。
