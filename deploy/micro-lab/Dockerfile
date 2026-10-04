# 问渠微电子实验镜像 wenquest/micro-lab（第 17 轮附 3.1）
# = IIC-OSIC-TOOLS（林茨大学集成电路研究所，Apache-2.0）＋ 问渠层：实验起始文件与参考解、wqlab 小工具，默认 SKY130。
# 基础镜像按摘要值锁定（BASE 的 @sha256 部分），升级时改这里并重新跑 .github/workflows/micro-lab.yml 验收。
ARG BASE=hpretl/iic-osic-tools:2026.08@sha256:3c371645b19c6f6564dc8c7b21e39ad1c1833d274fe5b85639afe1ba9d7987e7
FROM ${BASE}
USER root
ENV PDK=sky130A \
    WQ_HOME=/foss/wenquest
# 中文字体：Xschem、KLayout 里的中文标注（如原理图标题）需要；文泉驿微米黑约 5 MB
RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends fonts-wqy-microhei \
 && rm -rf /var/lib/apt/lists/*
COPY wenquest /foss/wenquest
RUN chmod -R a+rX /foss/wenquest \
 && chmod a+x /foss/wenquest/bin/wqlab \
 && ln -sf /foss/wenquest/bin/wqlab /usr/local/bin/wqlab
LABEL org.opencontainers.image.title="WenQuest micro-lab" \
      org.opencontainers.image.description="IIC-OSIC-TOOLS + WenQuest microelectronics labs (SKY130 default)" \
      org.opencontainers.image.source="https://github.com/eddiezgq/WenQuest"
USER 1000:1000
