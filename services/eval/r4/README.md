# 问渠 第 4 轮程序包（本窗口第 1–2 步）

| 文件 | 步骤 | 用途 |
|---|---|---|
| attainment.py | 1 | 课程目标达成度计算（含追溯、毕业要求汇总示范） |
| attainment_ch1.xlsx | 1 | 同一计算的公式版表格，可手工复核 |
| class_ch1_scores.json / mapping.json / attainment_ch1.json | 1 | 模拟班级数据、对应关系配置、计算结果 |
| contract/wenquest_contract_v1.schema.json | 2 | 问渠数据契约 v1（JSON Schema） |
| contract/sample_push.json | 2 | 问渠→校情中枢 推送样例（达成度、增值、评教主题、学业预警） |
| contract/sample_task.json | 2 | 校情中枢→问渠 改进任务样例 |
| contract/build_contract.py | 2 | 生成契约和样例，并用正例、反例校验 |

运行：`python3 attainment.py`，`python3 contract/build_contract.py`（需要 jsonschema）。
依据：项目文件《第4轮_教学评价与院校评估_总则》及第 1、2 步说明。
