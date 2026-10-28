<template>
  <!-- 第 48 轮：国内服务器上的平台页脚：公司、备案号、AI 服务说明（网页版；小程序由微信展示备案信息） -->
  <view v-if="isCN && h5" class="site-foot">
    <text>© 2026 {{ site.company || site.brand }}</text>
    <a v-if="site.icp" href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">{{ site.icp }}</a>
    <a v-if="site.psb" :href="'https://beian.mps.gov.cn/#/query/webSearch?code=' + psbCode" target="_blank" rel="noopener">{{ site.psb }}</a>
    <a :href="home + '/privacy/'" target="_blank">隐私政策</a>
    <a :href="home + '/terms/'" target="_blank">用户协议</a>
    <a :href="home + '/ai/'" target="_blank">AI 服务说明</a>
    <a :href="home + '/report/'" target="_blank">投诉与举报</a>
    <text class="ai">本平台 AI 功能调用已备案的 {{ site.ai_model || "DeepSeek" }} 大模型，生成内容标注“AI 生成”，经人工审核后生效。<template v-if="site.ai_reg">登记编号：{{ site.ai_reg }}</template></text>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { isCN, site } from "../site";

let h5 = false;
// #ifdef H5
h5 = true;
// #endif
const psbCode = computed(() => (site.value.psb || "").replace(/\D/g, ""));
const home = computed(() => {
  // learn.<域名> 上的平台 → 官网 <域名>
  if (typeof location === "undefined") return "";
  return location.protocol + "//" + location.host.replace(/^learn\./, "");
});
</script>

<style scoped>
.site-foot { display: flex; flex-wrap: wrap; gap: 4px 16px; justify-content: center; padding: 18px 16px 24px; font-size: 12px; color: var(--wq-muted); }
.site-foot a { color: var(--wq-muted); text-decoration: none; }
.site-foot a:hover { text-decoration: underline; }
.site-foot .ai { flex-basis: 100%; text-align: center; }
</style>
