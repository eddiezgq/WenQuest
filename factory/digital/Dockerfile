# 问渠数字工厂：枢纽服务（历史库写入、看板指标、AI 助手、MES、工作台网页）与仿真车间共用这个镜像
# 构建上下文是上一级目录（问渠仓库的 factory/，要用到其中的工厂数据 factory/factory/）

FROM node:22-slim AS web
WORKDIR /web
COPY digital/web/package.json digital/web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY digital/web/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 TZ=America/New_York
WORKDIR /app
COPY digital/requirements.txt digital/requirements.txt
RUN pip install -r digital/requirements.txt
COPY factory/ factory/
COPY digital/wqbus/ digital/wqbus/
COPY digital/sim/ digital/sim/
COPY digital/hub/ digital/hub/
COPY digital/mock_erpnext/ digital/mock_erpnext/
COPY --from=web /web/dist digital/web/dist
WORKDIR /app/digital
EXPOSE 8100
CMD ["uvicorn", "hub.app:app", "--host", "0.0.0.0", "--port", "8100"]
