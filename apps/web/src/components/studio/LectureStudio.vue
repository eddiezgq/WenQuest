<template>
  <view class="ls">
    <text class="h4">{{ t("lec.title") }}</text>
    <template v-if="file && file.lecture">
      <text class="muted-s">{{ file.source === "teacher" ? t("lec.fromTeacher") : t("lec.fromAi") }} · {{ mmss(file.seconds || 0) }}</text>
      <LecturePlayer :lecture="file.lecture" />
    </template>
    <text v-else class="muted-s">{{ t("lec.none") }}</text>

    <view v-if="!locked" class="acts">
      <view v-if="file" class="ghost small" @click="toggleRows">{{ rowsOpen ? t("lec.hideRows") : t("lec.showRows") }}</view>
      <!-- #ifdef H5 -->
      <view class="ghost small" :class="{ disabled: busy || uploading >= 0 }" @click="pick">
        {{ uploading >= 0 ? t("lec.uploading", { n: Math.round(uploading * 100) }) : t("lec.upload") }}
      </view>
      <!-- #endif -->
      <view class="ghost small" :class="{ disabled: busy }" @click="redo">{{ file ? t("lec.redoAi") : t("lec.makeAi") }}</view>
    </view>
    <text v-if="!locked" class="muted-s">{{ t("lec.uploadHint") }}</text>
    <text v-if="msg" class="err">{{ msg }}</text>

    <view v-if="rowsOpen" class="rows">
      <text class="muted-s">{{ view?.source === "teacher" ? t("lec.rowsTeacher") : t("lec.rowsAi") }}</text>
      <view v-for="r in rows" :key="r.n" class="row">
        <text class="at">{{ view?.source === "teacher" ? mmss(r.start) : t("lec.slide", { n: r.n + 1 }) }}<text v-if="r.edited" class="ed"> ✎</text></text>
        <view class="cols">
          <textarea v-if="has('zh')" v-model="r.zh" class="in" auto-height :disabled="locked" :maxlength="1500" />
          <text v-if="r.raw && r.raw !== r.zh" class="raw">{{ t("lec.heard") }}{{ r.raw }}</text>
          <textarea v-if="has('en')" v-model="r.en" class="in en" auto-height :disabled="locked" :maxlength="1500" />
        </view>
      </view>
      <view v-if="!locked" class="acts">
        <view class="primary small" :class="{ disabled: busy || !changed.length }" @click="save">{{ t("lec.save", { n: changed.length }) }}</view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
// 讲解视频 in the course builder (round 4, step 5): watch it (both voices, subtitles), check and edit its lines, upload
// the teacher's own recording, or have the AI lecturer make it again.
import { computed, ref, watch } from "vue";
import { api, type LectureRows, type StudioLesson } from "../../api";
import { t } from "../../i18n";
import LecturePlayer from "../LecturePlayer.vue";

const props = defineProps<{ pid: string; lesson: StudioLesson; busy: boolean }>();
const emit = defineEmits<{ (e: "act", fn: () => Promise<unknown>): void }>();

const file = computed(() => (props.lesson.files || []).find((f) => f.kind === "lecture") || null);
const locked = computed(() => props.lesson.status === "published");
const rowsOpen = ref(false);
const view = ref<LectureRows | null>(null);
const rows = ref<LectureRows["rows"]>([]);
const orig = ref<Record<number, { zh: string; en: string }>>({});
const uploading = ref(-1);
const msg = ref("");

function mmss(s: number) {
  const m = Math.floor(s / 60);
  return `${m}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
}
function has(lang: string) {
  return !view.value?.langs?.length || view.value.langs.includes(lang);
}
const changed = computed(() => rows.value.filter((r) => orig.value[r.n] && (r.zh !== orig.value[r.n].zh || r.en !== orig.value[r.n].en)));

async function loadRows() {
  try {
    const v = await api.studioLecture(props.pid, props.lesson.id);
    view.value = v;
    rows.value = v.rows.map((r) => ({ ...r }));
    orig.value = Object.fromEntries(v.rows.map((r) => [r.n, { zh: r.zh, en: r.en }]));
  } catch (e: any) { msg.value = e?.message || String(e); }
}
function toggleRows() {
  rowsOpen.value = !rowsOpen.value;
  if (rowsOpen.value) loadRows();
}
function save() {
  if (props.busy || !changed.value.length) return;
  const list = changed.value.map((r) => {
    const o = orig.value[r.n];
    return { n: r.n, ...(r.zh !== o.zh ? { zh: r.zh } : {}), ...(r.en !== o.en ? { en: r.en } : {}) };
  });
  rowsOpen.value = false;
  emit("act", () => api.studioEditLecture(props.pid, props.lesson.id, list));
}
function redo() {
  if (props.busy) return;
  if (file.value?.source === "teacher" && !confirm(t("lec.replaceRecording"))) return;
  emit("act", () => api.studioRedoLecture(props.pid, props.lesson.id));
}
function pick() {
  // #ifdef H5
  if (props.busy || uploading.value >= 0) return;
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "video/*,.mp4,.mov,.m4v,.webm,.mkv,.avi";
  input.onchange = () => {
    const f = input.files?.[0];
    if (!f) return;
    if (f.size > 3 * 1024 ** 3) { msg.value = t("lec.tooLarge"); return; }
    msg.value = "";
    uploading.value = 0;
    emit("act", async () => {
      try {
        return await api.studioUploadRecording(props.pid, props.lesson.id, f, (d) => { uploading.value = d; });
      } finally { uploading.value = -1; }
    });
  };
  input.click();
  // #endif
}
watch(() => file.value?.lecture?.video?.zh, () => { if (rowsOpen.value) loadRows(); });
</script>

<style scoped>
.ls { margin: 12px 0; padding: 12px; border: 1px solid #e3e8ee; border-radius: 8px; background: #fbfcfd; display: flex; flex-direction: column; gap: 8px; }
.h4 { font-weight: 600; font-size: 14px; }
.muted-s { color: #6b7b8b; font-size: 12px; }
.err { color: #b3261e; font-size: 12px; }
.acts { display: flex; flex-wrap: wrap; gap: 8px; }
.primary { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; border-radius: 8px; cursor: pointer; text-align: center; padding: 7px 14px; font-size: 14px; }
.ghost { border: 1px solid var(--wq-line); padding: 6px 12px; border-radius: 8px; cursor: pointer; color: var(--wq-ink); background: #fff; font-size: 13px; }
.disabled { opacity: .45; pointer-events: none; }
.rows { display: flex; flex-direction: column; gap: 10px; margin-top: 6px; }
.row { display: flex; gap: 10px; align-items: flex-start; border-top: 1px solid #eef1f4; padding-top: 8px; }
.at { width: 64px; flex-shrink: 0; font-size: 12px; color: #5b6b7b; font-variant-numeric: tabular-nums; }
.ed { color: #c47a1a; }
.cols { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.in { width: 100%; min-height: 36px; font-size: 13px; line-height: 1.5; padding: 6px 8px; border: 1px solid #d5dde5; border-radius: 6px; background: #fff; box-sizing: border-box; }
.in.en { color: #3a4a5a; }
.raw { font-size: 11px; color: #8a97a4; }
</style>
