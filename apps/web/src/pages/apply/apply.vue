<template>
  <AppShell nav="account" :title="t('apply.pageTitle')">
    <view class="wrap">
      <text class="wq-h1">{{ t("apply.pageTitle") }}</text>
      <text v-if="loading" class="wq-muted">{{ t("common.loading") }}</text>
      <text v-else-if="loadError" class="wq-error">{{ loadError }}</text>

      <view v-else-if="teacher" class="wq-card ok">
        <text class="big">✓ {{ t("apply.isTeacher") }}</text>
        <view class="wq-row acts"><view class="wq-btn primary" @click="go('/pages/studio/studio')">✦ {{ t("create.button") }}</view></view>
      </view>

      <template v-else>
        <!-- status -->
        <view v-if="app" class="wq-card status" :class="app.status">
          <view class="wq-row">
            <text class="wq-tag" :class="tagClass">{{ t("apply.status." + app.status) }}</text>
            <text class="wq-muted">{{ t("apply.submittedAt", { d: day(app.created) }) }}</text>
          </view>
          <text class="st-text">{{ t("apply.statusText." + app.status) }}</text>
          <view v-if="app.status === 'need_more' && app.more" class="note warn">{{ app.more }}</view>
          <view v-if="app.status === 'rejected' && app.reason" class="note">{{ app.reason }}</view>
        </view>

        <!-- form: new application, re-apply, or add evidence -->
        <view v-if="!app || open" class="wq-card">
          <text class="sec">{{ app && app.status !== 'rejected' ? t("apply.update") : t("apply.formTitle") }}</text>
          <text class="wq-label">{{ t("apply.institution") }} *</text>
          <input v-model="f.institution" class="wq-input" :placeholder="t('apply.institutionHint')" />
          <view class="two">
            <view><text class="wq-label">{{ t("apply.department") }}</text><input v-model="f.department" class="wq-input" /></view>
            <view><text class="wq-label">{{ t("apply.jobTitle") }}</text><input v-model="f.title" class="wq-input" :placeholder="t('apply.jobTitleHint')" /></view>
          </view>
          <text class="wq-label">{{ t("apply.note") }}</text>
          <textarea v-model="f.note" class="wq-textarea short" :placeholder="t('apply.noteHint')" />
          <text class="wq-label">{{ t("apply.evidence") }}</text>
          <text class="wq-muted block">{{ t("apply.evidenceHint") }}</text>
          <view class="files">
            <view v-for="n in (app && app.status !== 'rejected' ? app.evidence : [])" :key="'s' + n" class="file"><text>📎 {{ n }}</text><text class="wq-tag ok">{{ t("apply.uploaded") }}</text></view>
            <view v-for="(fl, i) in files" :key="i" class="file"><text>📎 {{ fl.name }}</text><text class="wq-link" @click="files.splice(i, 1)">✕</text></view>
            <view class="wq-btn small" @click="pick">＋ {{ t("apply.addFile") }}</view>
          </view>
          <text v-if="error" class="wq-error">{{ error }}</text>
          <view class="wq-row acts">
            <view class="wq-btn primary" :class="{ disabled: busy || !f.institution.trim() }" @click="submit">{{ busy ? busyText : t("apply.submit") }}</view>
          </view>
        </view>
        <view v-else-if="app && app.status === 'rejected'" class="wq-row"><view class="wq-btn" @click="open = true">{{ t("apply.again") }}</view></view>
      </template>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { type MyApplication, accountApi } from "../../accountApi";
import { ApiError, token } from "../../api";
import { errorText, t } from "../../i18n";

const app = ref<MyApplication | null>(null);
const teacher = ref(false);
const loading = ref(true);
const loadError = ref("");
const open = ref(false);
const busy = ref(false);
const busyText = ref("");
const error = ref("");
const files = ref<File[]>([]);
const f = reactive({ institution: "", department: "", title: "", note: "" });
const tagClass = computed(() => ({ approved: "ok", rejected: "live", need_more: "", pending: "info" } as Record<string, string>)[app.value?.status || ""] || "");

async function load() {
  loading.value = true;
  try {
    const r = await accountApi.myApplication();
    app.value = r.application;
    teacher.value = r.teacher;
    if (r.application) Object.assign(f, { institution: r.application.institution, department: r.application.department, title: r.application.title });
    open.value = !r.application || ["pending", "need_more"].includes(r.application.status);
  } catch (e) {
    loadError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    loading.value = false;
  }
}
function pick() {
  // #ifdef H5
  const input = document.createElement("input");
  input.type = "file";
  input.multiple = true;
  input.accept = "image/*,.pdf";
  input.onchange = () => { for (const x of Array.from(input.files || [])) if (files.value.length < 5) files.value.push(x); };
  input.click();
  // #endif
}
async function submit() {
  busy.value = true;
  error.value = "";
  try {
    busyText.value = t("common.saving");
    app.value = (await accountApi.apply({ ...f })).application;
    for (const [i, x] of files.value.entries()) {
      busyText.value = t("reg.uploading", { i: i + 1, n: files.value.length });
      app.value = await accountApi.uploadEvidence(x);
    }
    files.value = [];
    busyText.value = t("reg.reviewing");
    app.value = (await accountApi.submitApplication()).application;
    open.value = app.value.status === "need_more";
    uni.showToast({ title: t("apply.sent"), icon: "none" });
  } catch (e) {
    error.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    busy.value = false;
  }
}
const day = (s: number) => new Date(s * 1000).toLocaleDateString();
const go = (url: string) => uni.reLaunch({ url });
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login?back=" + encodeURIComponent("/pages/apply/apply") });
  load();
});
</script>

<style scoped>
.wrap { max-width: 720px; }
.big { font-size: 18px; font-weight: 700; color: var(--wq-ok); }
.ok { border-left: 4px solid var(--wq-ok); }
.status.need_more { border-left: 4px solid var(--wq-accent); }
.status.pending { border-left: 4px solid var(--wq-link); }
.status.rejected { border-left: 4px solid var(--wq-danger); }
.st-text { display: block; margin-top: 8px; line-height: 1.7; color: var(--wq-text); }
.note { margin-top: 10px; background: var(--wq-bg); border-radius: 6px; padding: 10px 12px; line-height: 1.6; }
.note.warn { background: #fff6dc; color: #6b4e00; }
.sec { display: block; font-weight: 700; color: var(--wq-ink); font-size: 16px; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.short { min-height: 70px; }
.block { display: block; }
.files { display: flex; flex-direction: column; gap: 6px; margin: 8px 0; align-items: flex-start; }
.file { display: flex; gap: 10px; align-items: center; font-size: 13px; background: var(--wq-bg); border-radius: 6px; padding: 5px 10px; }
.acts { margin-top: 14px; }
@media (max-width: 600px) { .two { grid-template-columns: 1fr; } }
</style>
