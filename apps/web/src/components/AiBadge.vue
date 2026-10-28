<template>
  <!-- 第 48 轮：国内服务器上，AI 生成的内容旁显示“AI 生成”（《人工智能生成合成内容标识办法》）；美国服务器上不显示 -->
  <text v-if="isCN" class="ai-badge" :title="t('ai.badgeTitle')">{{ t("ai.badge") }}</text>
</template>

<script setup lang="ts">
import { t } from "../i18n";
import { isCN } from "../site";
</script>

<style scoped>
.ai-badge { display: inline-block; font-size: 11px; line-height: 1.4; font-weight: 600; color: #0e6c63; background: #e3f4f1;
  border: 1px solid #9fd8cf; border-radius: 999px; padding: 0 7px; margin: 0 4px; vertical-align: middle; white-space: nowrap; }
</style>
