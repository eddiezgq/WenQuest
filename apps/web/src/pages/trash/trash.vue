<template>
  <AppShell nav="courses" :title="t('life.title')">
    <text class="h1">{{ t("life.title") }}</text>

    <!-- downloads being made or ready -->
    <view class="panel">
      <view class="p-head">
        <text class="h2">{{ t("life.downloads") }}</text>
        <text class="link" @click="loadExports">{{ t("life.refresh") }}</text>
      </view>
      <text class="note">{{ t("life.downloadsHint") }}</text>
      <view v-if="!jobs.length" class="muted">{{ t("life.noDownloads") }}</view>
      <view v-for="j in jobs" :key="j.id" class="row">
        <view class="r-body">
          <text class="r-name">{{ j.name }} · {{ j.kind === "backup" ? t("life.kindBackup") : t("life.kindFiles") }}</text>
          <text class="r-meta">{{ when(j.created) }}<text v-if="j.size"> · {{ size(j.size) }}</text></text>
          <text v-if="j.status === 'failed'" class="r-err">{{ t("life.failed") }}：{{ j.error }}</text>
        </view>
        <text v-if="j.status === 'running'" class="st running">{{ t("life.packing") }}</text>
        <view v-else-if="j.status === 'done'" class="btn primary" @click="download(j.url)">↓ {{ t("life.download") }}</view>
      </view>
    </view>

    <!-- recycle bin -->
    <view class="panel">
      <text class="h2">{{ t("life.bin") }}</text>
      <text class="note">{{ t("life.binHint") }}</text>
      <view v-if="loading" class="muted">{{ t("common.loading") }}</view>
      <view v-else-if="error" class="error">{{ errorText(error) }}</view>
      <view v-else-if="!items.length" class="muted">{{ t("life.binEmpty") }}</view>
      <view v-for="it in items" :key="it.binid" class="row bin">
        <view class="r-body">
          <text class="r-name">{{ it.name }}</text>
          <text class="r-meta">{{ it.shortname }} · {{ t("life.deletedAt", { when: when(it.timecreated), who: it.deletedby }) }} · {{ size(it.filesize) }}</text>
          <text v-if="it.projects.length" class="r-meta">{{ t("life.hasProject", { name: it.projects.map((p) => p.title).join("、") }) }}</text>
        </view>
        <view class="acts">
          <view class="btn" :class="{ disabled: busy }" @click="restore(it)">{{ t("life.restore") }}</view>
          <view class="btn" :class="{ disabled: busy }" @click="exportBin(it)">↓ {{ t("life.kindBackup") }}</view>
          <view class="btn danger" :class="{ disabled: busy }" @click="purgeOpen = it.binid; typed = ''; delProject = false">{{ t("life.purge") }}</view>
        </view>
        <!-- 永久删除: type the course name; offer the backup first -->
        <view v-if="purgeOpen === it.binid" class="purge">
          <text class="pg-t">{{ t("life.purgeWarn") }}</text>
          <view class="btn" @click="exportBin(it)">↓ {{ t("life.downloadFirst") }}</view>
          <text class="pg-l">{{ t("life.typeName", { name: it.name }) }}</text>
          <input class="pg-in" v-model="typed" :placeholder="it.name" />
          <view v-if="it.projects.length" class="pg-c" @click="delProject = !delProject">
            <text class="box" :class="{ on: delProject }">{{ delProject ? "✓" : "" }}</text>
            <text>{{ t("life.alsoProject", { name: it.projects.map((p) => p.title).join("、") }) }}</text>
          </view>
          <view class="pg-b">
            <text class="link" @click="purgeOpen = 0">{{ t("common.cancel") }}</text>
            <view class="btn danger" :class="{ disabled: typed.trim() !== it.name.trim() || busy }" @click="purge(it)">{{ t("life.purgeNow") }}</view>
          </view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { onUnmounted, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { absolute, ApiError } from "../../api";
import { type ExportJob, lifeApi, type TrashItem } from "../../courseApi";
import { errorText, t } from "../../i18n";

const items = ref<TrashItem[]>([]);
const jobs = ref<ExportJob[]>([]);
const loading = ref(true);
const error = ref("");
const busy = ref(false);
const purgeOpen = ref(0);
const typed = ref("");
const delProject = ref(false);
let timer: ReturnType<typeof setTimeout> | null = null;

async function load() {
  loading.value = true;
  error.value = "";
  try {
    items.value = (await lifeApi.trash()).items;
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
  await loadExports();
}
async function loadExports() {
  try {
    jobs.value = (await lifeApi.exports()).exports;
  } catch {
    /* shown as empty */
  }
  if (timer) clearTimeout(timer);
  if (jobs.value.some((j) => j.status === "running")) timer = setTimeout(loadExports, 3000);
}
onShow(load);
onUnmounted(() => timer && clearTimeout(timer));

function toast(e: unknown) {
  uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
}
async function restore(it: TrashItem) {
  busy.value = true;
  uni.showLoading({ title: t("life.restoring") });
  try {
    const r = await lifeApi.restore(it.binid);
    uni.hideLoading();
    uni.showToast({ title: t("life.restored"), icon: "none" });
    uni.navigateTo({ url: `/pages/course/course?id=${r.courseid}` });
  } catch (e) {
    uni.hideLoading();
    toast(e);
  } finally {
    busy.value = false;
  }
}
async function exportBin(it: TrashItem) {
  try {
    await lifeApi.exportBin(it.binid);
    uni.showToast({ title: t("life.packingStarted"), icon: "none" });
    await loadExports();
  } catch (e) {
    toast(e);
  }
}
async function purge(it: TrashItem) {
  if (typed.value.trim() !== it.name.trim()) return;
  busy.value = true;
  try {
    await lifeApi.purge(it.binid, delProject.value);
    purgeOpen.value = 0;
    uni.showToast({ title: t("life.purged"), icon: "none" });
    await load();
  } catch (e) {
    toast(e);
  } finally {
    busy.value = false;
  }
}
function download(link: string) {
  const url = absolute(link);
  // #ifdef H5
  window.open(url, "_blank", "noopener");
  // #endif
  // #ifndef H5
  uni.setClipboardData({ data: url });
  uni.showToast({ title: t("life.linkCopied"), icon: "none" });
  // #endif
}
function when(ts: number) {
  const d = new Date(ts * 1000);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}
function size(n: number) {
  return n > 1 << 30 ? (n / (1 << 30)).toFixed(1) + " GB" : n > 1 << 20 ? (n / (1 << 20)).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1024)) + " KB";
}
</script>

<style scoped>
.h1 { display: block; font-size: 22px; font-weight: 700; margin: 4px 0 14px; }
.h2 { font-size: 17px; font-weight: 700; }
.panel { background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; padding: 14px 16px; margin-bottom: 16px; }
.p-head { display: flex; justify-content: space-between; align-items: center; }
.note { display: block; color: #667; font-size: 13px; margin: 4px 0 10px; line-height: 1.6; }
.muted { color: #889; font-size: 14px; padding: 6px 0; }
.error { color: #b42318; }
.row { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; padding: 10px 0; border-top: 1px solid var(--wq-line); }
.r-body { flex: 1; min-width: 220px; display: flex; flex-direction: column; }
.r-name { font-weight: 600; }
.r-meta { color: #667; font-size: 13px; }
.r-err { color: #b42318; font-size: 13px; }
.acts { display: flex; gap: 8px; flex-wrap: wrap; }
.btn { border: 1px solid var(--wq-line); border-radius: 6px; padding: 5px 12px; font-size: 14px; cursor: pointer; background: #fff; }
.btn.primary { background: var(--wq-accent, #1f5f8b); color: #fff; border-color: transparent; }
.btn.danger { color: #b42318; border-color: #f3b4b4; }
.btn.disabled { opacity: 0.45; pointer-events: none; }
.st.running { color: var(--wq-link, #1f5f8b); font-size: 13px; }
.link { color: var(--wq-link, #1f5f8b); cursor: pointer; font-size: 14px; }
.purge { width: 100%; background: #fff5f5; border: 1px solid #f3b4b4; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.pg-t { color: #8a1c1c; font-weight: 600; }
.pg-l { font-size: 13px; color: #555; }
.pg-in { border: 1px solid var(--wq-line); border-radius: 6px; padding: 6px 8px; background: #fff; height: 34px; }
.pg-c { display: flex; gap: 8px; align-items: center; font-size: 14px; cursor: pointer; }
.box { width: 16px; height: 16px; border: 1px solid #999; border-radius: 3px; text-align: center; line-height: 16px; font-size: 12px; }
.box.on { background: #b42318; color: #fff; border-color: #b42318; }
.pg-b { display: flex; justify-content: flex-end; gap: 12px; align-items: center; }
.purge .btn { align-self: flex-start; }
.pg-b .btn { align-self: auto; }
</style>
