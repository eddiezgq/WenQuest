<template>
  <!-- 缝纫机设计与制造软件（第 39 轮）：来宾也能打开（试算），登录后在平台里打开 -->
  <AppShell v-if="token" nav="sewing" :title="t('sew.title')"><SewDesigner ref="d" :start-tab="startTab" :start-machine="startMachine" /></AppShell>
  <PublicFrame v-else back="/pages/sewing/sewing"><SewDesigner ref="d" :start-tab="startTab" :start-machine="startMachine" /></PublicFrame>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import PublicFrame from "../../components/auth/PublicFrame.vue";
import SewDesigner from "../../components/sewing/SewDesigner.vue";
import { token } from "../../api";
import { t } from "../../i18n";

const d = ref<InstanceType<typeof SewDesigner> | null>(null);
const startTab = ref("");
const startMachine = ref("");
onLoad((q: any) => { startTab.value = String(q?.tab || ""); startMachine.value = String(q?.machine || ""); });
let first = true;
onShow(() => {
  uni.setNavigationBarTitle({ title: t("sew.title") });
  if (first) return (first = false);
  d.value?.loadMe();
});
</script>
