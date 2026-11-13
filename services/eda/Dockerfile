# 问渠电子 WenQuest Electronics（第 105 轮 P3）：起草台。网址 <主域名>/eda/。
# Build from the repository root:  docker build -f services/eda/Dockerfile .
# 模型只经网关调用（WQ_GATEWAY_URL）；校验、展开、判定、仿真都在本容器里由 wqeda 的确定性代码做。没有密钥。
FROM python:3.12-slim-bookworm
WORKDIR /srv/repo
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 EDA_REPO=/srv/repo EDA_WEB_DIR=/srv/repo/services/eda/web
# 第 111 轮：CalculiX 算板子温升（起草台的板子检查）
RUN apt-get update -qq && apt-get install -y -q --no-install-recommends ngspice calculix-ccx && rm -rf /var/lib/apt/lists/*
COPY services/eda/requirements.txt services/eda/requirements.txt
RUN pip install --no-cache-dir -r services/eda/requirements.txt
COPY eda/wqeda eda/wqeda
COPY eda/parts eda/parts
COPY factory/designs/drv-joint/design.yaml factory/designs/drv-joint/design.yaml
# 第 111 轮：模板板子的板子模型（服务器上没有 KiCad）和示例工厂的工艺能力表
COPY factory/designs/drv-joint/report/board-model.json.gz factory/designs/drv-joint/report/board-model.json.gz
COPY eda/examples/factories eda/examples/factories
# 第 112 轮：工厂端演示资料包（故意带错，标明）：驱动板 A 版的光绘 + 漏了 C47 物料编号的物料清单和坐标
COPY factory/designs/drv-joint/out/gerber.zip factory/designs/drv-joint/out/gerber.zip
COPY eda/examples/pcba-demo/bom.csv eda/examples/pcba-demo/pos.csv eda/examples/pcba-demo/
# 第 159 轮 159d3：问渠贴片“用平缝机控制器 CTRL-LS 的资料包”
COPY factory/designs/ctrl-ls/out/gerber.zip factory/designs/ctrl-ls/out/bom.csv factory/designs/ctrl-ls/out/pos.csv factory/designs/ctrl-ls/out/
# 第 113 轮：KiCad 插件（下载时现场打包）
COPY eda/kicad-plugin eda/kicad-plugin
# 第 113 轮：网页审图看的示例设计（KiCad 原理图、板子、工程文件）和它们的报告
COPY factory/designs/drv-joint/kicad/ factory/designs/drv-joint/kicad/
COPY factory/designs/drv-joint-b/kicad/ factory/designs/drv-joint-b/kicad/
COPY factory/designs/drv-joint/report/report.json factory/designs/drv-joint/report/report.json
COPY factory/designs/drv-joint-b/report/report.json factory/designs/drv-joint-b/report/report.json
COPY eda/examples/drv-joint-24v/report/report.json eda/examples/drv-joint-24v/report/report.json
COPY factory/digital/cae/__init__.py factory/digital/cae/circuit.py factory/digital/cae/motors.py factory/digital/cae/
COPY services/eda/app.py services/eda/factory_api.py services/eda/view_api.py services/eda/
COPY services/eda/web services/eda/web
RUN useradd -r -u 10008 eda
USER eda
WORKDIR /srv/repo/services/eda
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)" || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
