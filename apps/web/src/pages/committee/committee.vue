<template>
  <AppShell nav="committee" :title="t('rev.committee')">
    <view class="wrap">
      <view class="wq-head">
        <text class="wq-h1">{{ t("rev.committee") }}</text>
        <text v-if="me" class="wq-muted">{{ me.chair ? t("rev.youChair") : t("rev.youMember") }}</text>
      </view>
      <text v-if="denied" class="wq-error">{{ t("rev.notMember") }}</text>
      <view v-else class="cols">
        <view class="list">
          <view class="wq-tabs">
            <text class="wq-tab" :class="{ on: !done }" @click="setDone(false)">{{ t("rev.todo") }}</text>
            <text class="wq-tab" :class="{ on: done }" @click="setDone(true)">{{ t("rev.handled") }}</text>
          </view>
          <text v-if="!items.length" class="wq-empty">{{ done ? t("rev.noneHandled") : t("rev.noneWaiting") }}</text>
          <view v-for="x in items" :key="x.lid" class="row" :class="{ on: sel && sel.lid === x.lid }" @click="open(x)">
            <text class="r-t">{{ x.no }} {{ disp(x.title) }}</text>
            <text class="r-s">{{ disp(x.course) }} · {{ x.teacher }}</text>
            <text class="r-v" :class="x.verdict">{{ x.verdict ? t("rev.verdict." + x.verdict) : "" }}<text v-if="done"> · {{ t("rev.state." + x.state) }}</text></text>
          </view>
        </view>
        <view v-if="item" class="detail">
          <text class="d-course">{{ disp(item.course) }} · {{ disp(item.chapter) }}</text>
          <text class="d-title">{{ item.no }} {{ disp(item.lesson.title) }}</text>
          <text class="wq-muted">{{ t("rev.by", { name: item.teacher }) }}</text>
          <text v-if="item.flow.note" class="d-note">{{ t("rev.teacherNote") }}{{ item.flow.note }}</text>
          <ReviewOpinion :flow="item.flow" />
          <view v-if="item.flow.state === 'submitted'" class="decide">
            <textarea v-model="comment" class="c-in" auto-height :placeholder="t('rev.commentHint')" />
            <view class="btns">
              <view v-if="item.role.chair" class="primary" :class="{ disabled: working }" @click="approve">{{ working ? t("create.publishing") : t("rev.approve") }}</view>
              <view class="ghost" :class="{ disabled: working || !comment.trim() }" @click="sendBack">{{ t("rev.return") }}</view>
            </view>
            <text v-if="item.role.chair && item.owner === myId" class="wq-muted">{{ t("rev.selfNote") }}</text>
            <text v-if="!item.role.chair" class="wq-muted">{{ t("rev.chairOnly") }}</text>
          </view>
          <text v-if="msg" class="wq-error">{{ msg }}</text>
          <text class="h4">{{ t("rev.deliverables") }}</text>
          <view class="files">
            <text v-for="f in item.lesson.files || []" :key="f.name" class="file" @click="download(f.url)">{{ t("studio.kind." + f.kind) }} · {{ f.name }} ↓</text>
          </view>
          <text class="h4">{{ t("rev.notes") }}</text>
          <view class="paper"><MathContent :html="disp(item.lesson.content)" /></view>
          <text class="h4">{{ t("studio.exercises") }}</text>
          <view class="paper"><MathContent :html="disp(item.lesson.exercises)" /></view>
          <text class="h4">{{ t("studio.answers") }}</text>
          <view class="paper"><MathContent :html="disp(item.lesson.answers)" /></view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
// 课程委员会 (round 6): lessons waiting for the committee, the AI pre-review, the whole lesson as students get it;
// the chair approves (published at once) or any member returns it with comments.
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import MathContent from "../../components/MathContent.vue";
import ReviewOpinion from "../../components/studio/ReviewOpinion.vue";
import { absolute, api, ApiError, type CommitteeItem, type ReviewFlow, type StudioLesson, type Text, user } from "../../api";
import { errorText, locale, t } from "../../i18n";

const me = ref<{ member: boolean; chair: boolean } | null>(null);
const denied = ref(false);
const done = ref(false);
const items = ref<CommitteeItem[]>([]);
const sel = ref<CommitteeItem | null>(null);
const item = ref<{ course: Text; chapter: Text; no: string; teacher: string; owner: number; lesson: StudioLesson; flow: ReviewFlow;
  role: { chair: boolean } } | null>(null);
const comment = ref("");
const working = ref(false);
const msg = ref("");
const myId = ref(0);

const disp = (x?: Text | null) => (x ? (locale.value === "en" ? x.en || x.zh : x.zh || x.en) || "" : "");

async function load() {
  try {
    me.value = await api.committeeMe();
    if (!me.value.member) { denied.value = true; return; }
    myId.value = (user.value as any)?.id || 0;
    items.value = (await api.committeeQueue(done.value)).items;
  } catch { denied.value = true; }
}
function setDone(v: boolean) { done.value = v; item.value = null; sel.value = null; load(); }
async function open(x: CommitteeItem) {
  sel.value = x; msg.value = ""; comment.value = "";
  item.value = await api.committeeItem(x.pid, x.lid);
}
async function approve() {
  if (!sel.value || working.value) return;
  working.value = true; msg.value = "";
  try {
    await api.committeeApprove(sel.value.pid, sel.value.lid, comment.value.trim());
    item.value = null; sel.value = null; await load();
  } catch (e) { msg.value = errorText(e instanceof ApiError ? e.code : "unknown"); }
  working.value = false;
}
async function sendBack() {
  if (!sel.value || !comment.value.trim() || working.value) return;
  working.value = true; msg.value = "";
  try {
    await api.committeeReturn(sel.value.pid, sel.value.lid, comment.value.trim());
    item.value = null; sel.value = null; await load();
  } catch (e) { msg.value = errorText(e instanceof ApiError ? e.code : "unknown"); }
  working.value = false;
}
function download(url: string) {
  // #ifdef H5
  window.open(absolute(url), "_blank");
  // #endif
}
onShow(load);
</script>

<style scoped>
.wrap { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.cols { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
.list { flex: 0 0 320px; max-width: 100%; display: flex; flex-direction: column; gap: 8px; }
.row { border: 1px solid var(--wq-line); border-radius: 8px; padding: 10px 12px; background: #fff; display: flex; flex-direction: column; gap: 2px; cursor: pointer; }
.row.on { border-color: var(--wq-accent); background: #fffaf0; }
.r-t { font-weight: 600; font-size: 14px; }
.r-s, .r-v { font-size: 12px; color: var(--wq-muted); }
.detail { flex: 1 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 8px; background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; padding: 16px; }
.d-course { font-size: 13px; color: var(--wq-muted); }
.d-title { font-size: 20px; font-weight: 700; }
.d-note { font-size: 14px; background: #f4f7fa; padding: 8px 10px; border-radius: 6px; }
.decide { display: flex; flex-direction: column; gap: 8px; border-top: 1px solid var(--wq-line); padding-top: 10px; }
.c-in { width: 100%; min-height: 60px; border: 1px solid var(--wq-line); border-radius: 6px; padding: 8px; font-size: 14px; box-sizing: border-box; }
.btns { display: flex; gap: 10px; flex-wrap: wrap; }
.primary { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 8px 16px; border-radius: 8px; cursor: pointer; }
.ghost { border: 1px solid var(--wq-line); padding: 7px 14px; border-radius: 8px; cursor: pointer; background: #fff; }
.disabled { opacity: .45; pointer-events: none; }
.h4 { font-weight: 600; margin-top: 8px; }
.files { display: flex; flex-direction: column; gap: 4px; }
.file { font-size: 13px; color: var(--wq-link); cursor: pointer; }
.paper { border: 1px solid var(--wq-line); border-radius: 8px; padding: 12px; }
</style>
