<template>
  <AppShell nav="whiteboard" :title="t('wb.title')">
    <view class="wrap">
      <view class="head">
        <view>
          <text class="h1">{{ t("wb.title") }}</text>
          <text class="lead">{{ t("wb.lead") }}</text>
        </view>
        <view class="primary" @click="openNew">＋ {{ t("wb.new") }}</view>
      </view>

      <view v-if="error" class="alert">{{ errorText(error) }}</view>
      <view v-if="loading" class="muted">{{ t("common.loading") }}</view>
      <view v-else-if="!list.length" class="empty">{{ t("wb.none") }}</view>
      <view v-else class="list">
        <view v-for="w in list" :key="w.id" class="row" @click="edit(w)">
          <view class="r-main">
            <text class="r-title">{{ w.title.zh || t("wb.untitled") }}</text>
            <text class="r-meta">{{ t("wb.source." + w.source) }}<text v-if="w.course && w.course.title"> · {{ w.course.title }}</text>
              <text v-if="w.duration"> · {{ mmss(w.duration) }}</text> · {{ formatDate(w.updated) }}</text>
            <text v-if="w.error" class="r-err">{{ w.error }}</text>
          </view>
          <text v-if="w.job" class="chip busy">{{ w.job.label }}<text v-if="w.job.progress"> {{ w.job.progress }}%</text></text>
          <text v-else-if="w.state === 'waiting'" class="chip warn">{{ t("wb.waiting") }}</text>
          <text v-else-if="w.state === 'failed'" class="chip bad">{{ t("wb.failed") }}</text>
          <text v-else-if="w.mp4" class="chip ok">MP4</text>
          <text v-if="w.state === 'ready'" class="link" @click.stop="play(w)">{{ t("wb.play") }}</text>
          <text class="link danger" @click.stop="remove(w)">{{ t("wb.delete") }}</text>
          <text class="chev">›</text>
        </view>
      </view>
      <text class="foot">{{ t("wb.desktop") }}</text>
    </view>

    <!-- 新建白板课 -->
    <view v-if="dialog" class="scrim" @click="dialog = false" />
    <view v-if="dialog" class="dialog">
      <text class="d-title">{{ t("wb.new") }}</text>
      <view class="tabs">
        <text class="tab" :class="{ on: form.source === 'topic' }" @click="form.source = 'topic'">{{ t("wb.fromTopic") }}</text>
        <text class="tab" :class="{ on: form.source === 'recording' }" @click="form.source = 'recording'">{{ t("wb.fromRecording") }}</text>
      </view>
      <text class="d-hint">{{ form.source === "topic" ? t("wb.topicHint") : t("wb.recordingHint") }}</text>

      <text class="label">{{ t("wb.topic") }}<text v-if="form.source === 'recording'" class="opt"> {{ t("wb.optional") }}</text></text>
      <input v-model="form.topic" class="input" :placeholder="t('wb.topicPh')" maxlength="200" />

      <template v-if="form.source === 'topic'">
        <text class="label">{{ t("wb.note") }} <text class="opt">{{ t("wb.optional") }}</text></text>
        <textarea v-model="form.note" class="area" :placeholder="t('wb.notePh')" maxlength="30000" />
        <text class="label">{{ t("wb.minutes") }}</text>
        <view class="chips">
          <text v-for="n in [3, 6, 10]" :key="n" class="pick" :class="{ on: form.minutes === n }" @click="form.minutes = n">{{ t("wb.min", { n }) }}</text>
        </view>
        <text class="label">{{ t("wb.voice") }}</text>
        <view v-if="voices.length" class="chips">
          <text v-for="v in voices" :key="v.id" class="pick" :class="{ on: form.voice === v.id }" @click="pickVoice(v)">{{ v.zh }}</text>
        </view>
        <text v-else class="d-hint">{{ voiceOn ? t("common.loading") : t("wb.noVoice") }}</text>
      </template>
      <template v-else>
        <text class="label">{{ t("wb.file") }}</text>
        <!-- #ifdef H5 -->
        <input type="file" class="file" accept="audio/*,video/mp4,.m4a,.mp3,.wav" @change="onFile" />
        <!-- #endif -->
        <text v-if="file" class="d-hint">{{ file.name }} · {{ Math.round(file.size / 1048576) }} MB</text>
      </template>

      <text class="label">{{ t("wb.media") }} <text class="opt">{{ t("wb.optional") }}</text></text>
      <picker :range="scopes" range-key="label" :value="scopeIdx" @change="(e: any) => (scopeIdx = +e.detail.value)">
        <view class="input pickbox">{{ scopes[scopeIdx]?.label }} ▾</view>
      </picker>

      <view v-if="formError" class="alert">{{ formError }}</view>
      <view class="d-actions">
        <text class="ghost" @click="dialog = false">{{ t("common.cancel") }}</text>
        <view class="primary" :class="{ disabled: busy }" @click="create">{{ busy || t("wb.start") }}</view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { api, ApiError, token, user, type Voice, type WbSummary } from "../../api";
import { errorText, formatDate, t } from "../../i18n";

defineOptions({ inheritAttrs: false });

const list = ref<WbSummary[]>([]);
const loading = ref(true);
const error = ref("");
const dialog = ref(false);
const busy = ref("");
const formError = ref("");
const voices = ref<Voice[]>([]);
const voiceOn = ref(true);
const file = ref<File | null>(null);
const form = ref({ source: "topic" as "topic" | "recording", topic: "", note: "", minutes: 6, voice: "zm_yunjian" });
const projects = ref<{ id: string; title: string }[]>([]);
const books = ref<{ book: string; title: string }[]>([]);
const scopeIdx = ref(0);
const scopes = computed(() => [
  { label: t("wb.allBooks"), course: "", book: "" },
  ...projects.value.map((p) => ({ label: t("wb.ofCourse", { name: p.title || t("studio.untitled") }), course: p.id, book: "" })),
  ...books.value.map((b) => ({ label: t("wb.ofBook", { name: b.title }), course: "", book: b.book })),
]);
let timer: ReturnType<typeof setTimeout> | null = null;

const mmss = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

async function load() {
  error.value = "";
  try {
    const r = await api.wbList();
    list.value = r.lessons;
    voiceOn.value = r.voice_on;
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
  if (timer) clearTimeout(timer);
  if (list.value.some((w) => w.job)) timer = setTimeout(load, 3000);
}

async function openNew() {
  dialog.value = true;
  formError.value = "";
  if (!voices.value.length) {
    api.studioVoices().then((r) => {
      voiceOn.value = r.available;
      voices.value = r.voices.filter((v) => v.lang === "zh");
      if (voices.value.length && !voices.value.some((v) => v.id === form.value.voice)) form.value.voice = voices.value[0].id;
    }).catch(() => (voiceOn.value = false));
  }
  if (!projects.value.length) api.studioProjects().then((ps) => (projects.value = ps.filter((p) => p.lessons).map((p) => ({ id: p.id, title: p.title })))).catch(() => {});
  if (!books.value.length) api.textbooks().then((r) => (books.value = r.books.filter((b) => b.labs).map((b) => ({ book: b.book, title: b.title })))).catch(() => {});
}

let sample: any = null;
function pickVoice(v: Voice) {
  form.value.voice = v.id;
  // #ifdef H5
  try { sample?.pause(); sample = new Audio(v.sample); sample.play(); } catch { /* no sound: fine */ }
  // #endif
}

function onFile(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0];
  file.value = f || null;
}

async function create() {
  if (busy.value) return;
  formError.value = "";
  const f = form.value;
  if (f.source === "topic" && !f.topic.trim()) return (formError.value = t("wb.needTopic"));
  if (f.source === "recording" && !file.value) return (formError.value = t("wb.needFile"));
  const sc = scopes.value[scopeIdx.value] || { course: "", book: "" };
  busy.value = t("wb.starting");
  try {
    const w = await api.wbCreate({ source: f.source, topic: f.topic.trim(), note: f.note, minutes: f.minutes, voice: f.voice,
                                   course_pid: sc.course, book: sc.book });
    if (f.source === "recording" && file.value) {
      await api.wbUploadRecording(w.id, file.value, (d) => (busy.value = t("wb.uploading", { n: Math.round(d * 100) })));
    }
    dialog.value = false;
    form.value = { ...form.value, topic: "", note: "" };
    file.value = null;
    await load();
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    busy.value = "";
  }
}

function edit(w: WbSummary) {
  // #ifdef H5
  window.location.href = `/wb-editor/?id=${w.id}`;
  // #endif
  // #ifndef H5
  uni.showToast({ title: t("wb.desktop"), icon: "none" });
  // #endif
}

async function play(w: WbSummary) {
  try {
    const d = await api.wbGet(w.id);
    // #ifdef H5
    window.open(d.play, "_blank");
    // #endif
    // #ifndef H5
    uni.setClipboardData({ data: d.play });
    // #endif
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  }
}

function remove(w: WbSummary) {
  uni.showModal({
    title: t("wb.delete"), content: t("wb.deleteAsk", { name: w.title.zh || t("wb.untitled") }),
    success: async (r) => {
      if (!r.confirm) return;
      try { await api.wbDelete(w.id); await load(); } catch (e) { error.value = e instanceof ApiError ? e.code : "unknown"; }
    },
  });
}

onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t("wb.title") });
  if (user.value && user.value.can_create_courses === false) error.value = "forbidden";
  load();
});
onUnmounted(() => { if (timer) clearTimeout(timer); });
</script>

<style scoped>
.wrap { max-width: 980px; }
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; margin-bottom: 18px; }
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); }
.lead { display: block; color: var(--wq-muted); margin-top: 6px; line-height: 1.7; max-width: 660px; }
.primary { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 10px 20px; border-radius: 8px; cursor: pointer; white-space: nowrap; text-align: center; }
.disabled { opacity: .6; pointer-events: none; }
.alert { background: #fdecea; color: var(--wq-danger); padding: 10px 14px; border-radius: 8px; margin: 10px 0; }
.muted, .empty { color: var(--wq-muted); }
.empty { background: #fff; border: 1px dashed var(--wq-line); border-radius: 8px; padding: 28px; text-align: center; line-height: 1.7; }
.list { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; overflow: hidden; }
.row { display: flex; align-items: center; gap: 10px; padding: 14px 16px; cursor: pointer; border-top: 1px solid var(--wq-line); flex-wrap: wrap; }
.row:first-child { border-top: 0; }
.row:hover { background: #f7f9f8; }
.r-main { flex: 1; min-width: 200px; }
.r-title { display: block; font-weight: 600; color: var(--wq-ink); }
.r-meta { display: block; font-size: 13px; color: var(--wq-muted); margin-top: 2px; }
.r-err { display: block; font-size: 13px; color: var(--wq-danger); margin-top: 2px; }
.chip { font-size: 12px; padding: 2px 8px; border-radius: 999px; white-space: nowrap; }
.chip.busy { background: #e7f1f5; color: var(--wq-link); }
.chip.warn { background: #fff3d6; color: #7a5a00; }
.chip.bad { background: #fdecea; color: var(--wq-danger); }
.chip.ok { background: #e6f4ea; color: #2e7d4f; }
.link { color: var(--wq-link); font-size: 14px; white-space: nowrap; }
.link.danger { color: var(--wq-muted); }
.chev { color: var(--wq-muted); }
.foot { display: block; color: var(--wq-muted); font-size: 13px; margin-top: 12px; }
.scrim { position: fixed; inset: 0; background: rgba(20,33,43,.4); z-index: 40; }
.dialog { position: fixed; z-index: 41; left: 50%; top: 50%; transform: translate(-50%, -50%); width: min(560px, calc(100vw - 32px));
  max-height: calc(100vh - 48px); overflow: auto; background: #fff; border-radius: 12px; padding: 20px; box-sizing: border-box;
  box-shadow: 0 20px 48px rgba(20,33,43,.25); display: flex; flex-direction: column; }
.d-title { font-size: 20px; font-weight: 700; color: var(--wq-ink); }
.d-hint { color: var(--wq-muted); font-size: 13px; line-height: 1.6; margin-top: 6px; }
.tabs { display: flex; gap: 6px; margin-top: 14px; background: #f1f3f2; border-radius: 8px; padding: 4px; }
.tab { flex: 1; text-align: center; padding: 7px; border-radius: 6px; cursor: pointer; color: var(--wq-muted); }
.tab.on { background: #fff; color: var(--wq-ink); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.label { font-weight: 600; color: var(--wq-ink); margin-top: 14px; margin-bottom: 6px; font-size: 14px; }
.opt { font-weight: 400; color: var(--wq-muted); font-size: 12px; }
.input { border: 1px solid var(--wq-line); border-radius: 8px; padding: 0 10px; height: 38px; line-height: 38px; font-size: 15px; box-sizing: border-box; width: 100%; }
.pickbox { color: var(--wq-ink); cursor: pointer; }
.area { border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 10px; height: 90px; width: 100%; box-sizing: border-box; font-size: 14px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.pick { border: 1px solid var(--wq-line); border-radius: 999px; padding: 5px 12px; cursor: pointer; font-size: 14px; }
.pick.on { background: var(--wq-ink); color: #fff; border-color: var(--wq-ink); }
.file { font-size: 14px; }
.d-actions { display: flex; justify-content: flex-end; align-items: center; gap: 16px; margin-top: 18px; }
.ghost { color: var(--wq-muted); cursor: pointer; }
</style>
