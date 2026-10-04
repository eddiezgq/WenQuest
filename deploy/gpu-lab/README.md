# 问渠 GPU 实验环境（《人工智能》第 14 轮附）

- `wqgpu.py`：实验笔记本里用的小工具——检查环境（`check`）、运行命令（`sh`）、计时（`bench`）、把测得的数签名回传问渠（`submit`）。
  只用 Python 标准库。教材构建时复制到 `build/<书>/gpulab/`，网关开机后把它放进学生的 JupyterLab。
- `Dockerfile`：学校自有 GPU 服务器（方案 C）用的镜像。AutoDL、Lambda 用平台的基础镜像，不需要它。

整体设计见 `docs/实施细则/第14轮附_2026-10-03_云端GPU实验环境.md`；网关部分是 `services/gateway/app/gpulab.py`；
教材写法见 `textbook/tools/gpulab.py`（GPU 实验）与 `textbook/tools/gpurun.py`（书中数字的实测）。
