# 问渠数字工厂：枢纽服务（历史库写入、看板指标、AI 助手、MES、工作台网页）与仿真车间共用这个镜像
# 构建上下文是上一级目录（问渠仓库的 factory/，要用到其中的工厂数据 factory/factory/）

FROM node:22-slim AS web
WORKDIR /web
COPY digital/web/package.json digital/web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY digital/web/ ./
RUN npm run build

# 固定 Debian 12（bookworm）：Debian 13 的 calculix-ccx 因 openmpi 升级装不上（Debian bug #1089784）
FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 TZ=America/New_York
WORKDIR /app
# build123d（网页设计台出 STEP，第 6 轮 W3）用到 OpenCASCADE，需要这几个系统库；
# 有限元（第 11 轮）：CalculiX 求解器 ccx，gmsh 需要 libGLU 等
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libxrender1 libx11-6 libxext6 \
        calculix-ccx libglu1-mesa libxcursor1 libxft2 libxinerama1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY digital/requirements.txt digital/requirements.txt
RUN pip install -r digital/requirements.txt "requests>=2.31"
COPY factory/ factory/
# 服务器首次安装时用它把减速器厂数据导入 ERPNext（第 3 轮 D6）
COPY seed.py seed.py
COPY digital/wqbus/ digital/wqbus/
COPY digital/sim/ digital/sim/
COPY digital/hub/ digital/hub/
COPY digital/freecad/ digital/freecad/
COPY digital/cae/ digital/cae/
COPY digital/mock_erpnext/ digital/mock_erpnext/
COPY --from=web /web/dist digital/web/dist
WORKDIR /app/digital
EXPOSE 8100
CMD ["uvicorn", "hub.app:app", "--host", "0.0.0.0", "--port", "8100"]
