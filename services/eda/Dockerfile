# 问渠电子 WenQuest Electronics（第 105 轮 P3）：起草台。网址 <主域名>/eda/。
# Build from the repository root:  docker build -f services/eda/Dockerfile .
# 模型只经网关调用（WQ_GATEWAY_URL）；校验、展开、判定、仿真都在本容器里由 wqeda 的确定性代码做。没有密钥。
FROM python:3.12-slim-bookworm
WORKDIR /srv/repo
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 EDA_REPO=/srv/repo EDA_WEB_DIR=/srv/repo/services/eda/web
RUN apt-get update -qq && apt-get install -y -q --no-install-recommends ngspice && rm -rf /var/lib/apt/lists/*
COPY services/eda/requirements.txt services/eda/requirements.txt
RUN pip install --no-cache-dir -r services/eda/requirements.txt
COPY eda/wqeda eda/wqeda
COPY eda/parts eda/parts
COPY factory/designs/drv-joint/design.yaml factory/designs/drv-joint/design.yaml
COPY factory/digital/cae/__init__.py factory/digital/cae/circuit.py factory/digital/cae/motors.py factory/digital/cae/
COPY services/eda/app.py services/eda/app.py
COPY services/eda/web services/eda/web
RUN useradd -r -u 10008 eda
USER eda
WORKDIR /srv/repo/services/eda
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)" || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
