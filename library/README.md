# 问渠零件与机器人库

课程与数字工厂共用的零件、机器人、机构库。设计依据：`factory/digital/实施细则_第2轮_零件与机器人库.md`（条目格式见附录 B，发布与接口见 B.10–B.13，分期见 L13）。

- `catalog/<部分>/<编号>/entry.yaml`：条目（身份、参数定义、来源与许可、教学、工厂对应）；`specs.csv`：规格表
- `schema/entry.v1.json`：条目格式
- `generators/`：造型程序（标准件调用 bd_warehouse）
- `tools/`：`import_bd.py` 从 bd_warehouse 数据生成规格表；`validate.py` 校验条目；`build.py` 生成发布目录
- `tests/`：条目校验、规格表可重新生成、模型尺寸与规格表一致

模型文件不进仓库（L5），由 GitHub Actions 生成并发布。本地试跑：

```bash
pip install build123d "git+https://github.com/gumyr/bd_warehouse" trimesh matplotlib pyyaml jsonschema pytest
python3 tools/validate.py
python3 -m pytest -q tests
python3 tools/build.py --version 2026.10.0 --limit 3      # 每个条目只造 3 个规格，结果在 build/
```

## 发布失败“建版本标签失败”怎么办

GitHub 不许自动部署的令牌给“工作流文件与 main 最新提交不同”的提交建标签。发布开始时就先建标签；如果恰好有人在这几秒内推送了 `.github/workflows` 的改动，本次会停在“定版本号”一步并注明原因。处理：在 Actions → “Parts library 零件库发布” 点 **Run workflow**（分支 main），从最新提交重新发布即可。
