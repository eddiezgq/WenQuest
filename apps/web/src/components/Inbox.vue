<template>
  <view>
    <view class="wq-head">
      <text class="wq-h1">{{ t("shell.inbox") }}</text>
      <view class="wq-btn primary" @click="startNew">✎ {{ t("inbox.new") }}</view>
    </view>
    <view class="wq-tabs">
      <view class="wq-tab" :class="{ on: view === 'messages' }" @click="view = 'messages'">{{ t("inbox.messages") }}<text v-if="unreadMsgs"> · {{ unreadMsgs }}</text></view>
      <view class="wq-tab" :class="{ on: view === 'notices' }" @click="view = 'notices'">{{ t("inbox.notices") }}<text v-if="unreadNotes"> · {{ unreadNotes }}</text></view>
    </view>
    <text v-if="error" class="wq-error">{{ errorText(error) }}</text>

    <!-- compose -->
    <view v-if="composing" class="wq-card compose">
      <text class="wq-label">{{ t("inbox.to") }}</text>
      <view class="chips">
        <text v-for="p in chosen" :key="p.id" class="chip" @click="toggle(p)">{{ p.fullname }} ✕</text>
        <text v-if="!chosen.length" class="wq-muted">{{ t("inbox.pickHint") }}</text>
      </view>
      <view class="picker">
        <view v-for="c in contacts" :key="c.id" class="pc">
          <view class="wq-row pc-h">
            <text class="pc-name">{{ c.name }}</text>
            <text class="wq-link" @click="addAll(c, true)">{{ t("inbox.allTeachers") }}</text>
            <text class="wq-link" @click="addAll(c, false)">{{ t("inbox.allStudents") }}</text>
            <text v-for="g in groupsOf(c)" :key="g" class="wq-link" @click="addGroup(c, g)">{{ g }}</text>
          </view>
          <view class="pc-people">
            <text v-for="p in c.people" :key="p.id" class="person" :class="{ on: isChosen(p.id), teacher: p.teacher }" @click="toggle(p)">{{ p.fullname }}</text>
          </view>
        </view>
        <text v-if="!contacts.length" class="wq-muted">{{ t("common.loading") }}</text>
      </view>
      <textarea v-model="draft" class="wq-textarea" auto-height :maxlength="-1" :placeholder="t('inbox.write')" />
      <text v-if="formError" class="wq-error">{{ formError }}</text>
      <view class="wq-row acts">
        <view class="wq-btn primary" :class="{ disabled: busy || !chosen.length || !draft.trim() }" @click="sendNew">{{ busy ? t("common.saving") : t("disc.send") }}</view>
        <view class="wq-btn" @click="composing = false">{{ t("common.cancel") }}</view>
        <text v-if="chosen.length > 1" class="wq-muted">{{ t("inbox.separate", { n: chosen.length }) }}</text>
      </view>
    </view>

    <!-- conversations -->
    <view v-else-if="view === 'messages'" class="split" :class="{ open: !!openId }">
      <view class="convs">
        <text v-if="loading && !convs.length" class="wq-muted pad">{{ t("common.loading") }}</text>
        <view v-else-if="!convs.length" class="wq-muted pad">{{ t("inbox.none") }}</view>
        <view v-for="c in convs" :key="c.id" class="conv" :class="{ on: c.id === openId, unread: c.unread }" @click="openConv(c.id)">
          <view class="wq-avatar">{{ initials(c.name) }}</view>
          <view class="c-main">
            <view class="wq-row c-top"><text class="c-name">{{ c.name || t("inbox.self") }}</text><text class="wq-muted">{{ when(c.time) }}</text></view>
            <text class="c-last">{{ c.from_me ? t("inbox.me") + "：" : "" }}{{ c.last }}</text>
          </view>
          <text v-if="c.unread" class="badge">{{ c.unread }}</text>
        </view>
      </view>
      <view class="thread">
        <view v-if="!openId" class="wq-muted pad">{{ t("inbox.pick") }}</view>
        <template v-else>
          <view class="t-head"><text class="wq-link back" @click="openId = 0">‹</text><text class="t-name">{{ threadName }}</text></view>
          <scroll-view scroll-y class="msgs" :scroll-into-view="bottomId">
            <view v-for="msg in messages" :id="'m' + msg.id" :key="msg.id" class="msg" :class="{ mine: msg.mine }">
              <text v-if="!msg.mine" class="m-author">{{ msg.author }}</text>
              <view class="bubble"><MathContent :html="msg.text" /></view>
              <text class="m-time">{{ when(msg.time) }}</text>
            </view>
          </scroll-view>
          <view class="reply">
            <textarea v-model="reply" class="wq-textarea r-in" auto-height :maxlength="-1" :placeholder="t('inbox.write')" />
            <view class="wq-btn primary" :class="{ disabled: busy || !reply.trim() }" @click="sendReply">{{ t("disc.send") }}</view>
          </view>
        </template>
      </view>
    </view>

    <!-- notifications -->
    <view v-else class="notes">
      <view v-if="!notes.length" class="wq-empty">{{ t("inbox.noNotices") }}</view>
      <view v-for="n in notes" :key="n.id" class="wq-card note" :class="{ unread: !n.read }">
        <view class="wq-row"><text class="n-subj">{{ n.subject }}</text><text class="wq-muted">{{ when(n.time) }}</text></view>
        <text class="n-text">{{ n.text }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from "vue";
import MathContent from "./MathContent.vue";
import { ApiError } from "../api";
import { type ChatMessage, type ContactCourse, type Conversation, initials, type Notice, workApi } from "../courseApi";
import { errorText, formatDate, t } from "../i18n";

const view = ref<"messages" | "notices">("messages");
const convs = ref<Conversation[]>([]);
const notes = ref<Notice[]>([]);
const openId = ref(0);
const threadName = ref("");
const messages = ref<ChatMessage[]>([]);
const bottomId = ref("");
const reply = ref("");
const loading = ref(true);
const error = ref("");
const busy = ref(false);
const composing = ref(false);
const contacts = ref<ContactCourse[]>([]);
const chosen = ref<{ id: number; fullname: string }[]>([]);
const draft = ref("");
const formError = ref("");
let poll: ReturnType<typeof setInterval> | null = null;

const unreadMsgs = computed(() => convs.value.reduce((a, c) => a + (c.unread || 0), 0));
const unreadNotes = computed(() => notes.value.filter((n) => !n.read).length);
function when(ts: number) {
  if (!ts) return "";
  const d = new Date(ts * 1000);
  return d.toDateString() === new Date().toDateString() ? formatDate(ts).slice(11) : formatDate(ts).slice(5, 10);
}

async function load() {
  try {
    const r = await workApi.inbox();
    convs.value = r.conversations;
    notes.value = r.notifications;
    error.value = "";
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}
async function openConv(id: number) {
  openId.value = id;
  try {
    const r = await workApi.conversation(id);
    threadName.value = r.name;
    messages.value = r.messages;
    await nextTick();
    bottomId.value = messages.value.length ? "m" + messages.value[messages.value.length - 1].id : "";
    const c = convs.value.find((x) => x.id === id);
    if (c) c.unread = 0;
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  }
}
async function sendReply() {
  if (!reply.value.trim() || !openId.value) return;
  busy.value = true;
  try {
    await workApi.send(openId.value, reply.value);
    reply.value = "";
    await openConv(openId.value);
    load();
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  } finally {
    busy.value = false;
  }
}

async function startNew() {
  composing.value = true;
  chosen.value = [];
  draft.value = "";
  formError.value = "";
  if (!contacts.value.length) {
    try {
      contacts.value = (await workApi.contacts()).courses;
    } catch (e) {
      formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
    }
  }
}
const isChosen = (id: number) => chosen.value.some((p) => p.id === id);
function toggle(p: { id: number; fullname: string }) {
  chosen.value = isChosen(p.id) ? chosen.value.filter((x) => x.id !== p.id) : [...chosen.value, { id: p.id, fullname: p.fullname }];
}
function addAll(c: ContactCourse, teachers: boolean) {
  for (const p of c.people) if (p.teacher === teachers && !isChosen(p.id)) chosen.value.push({ id: p.id, fullname: p.fullname });
}
const groupsOf = (c: ContactCourse) => [...new Set(c.people.flatMap((p) => p.groups))];
function addGroup(c: ContactCourse, g: string) {
  for (const p of c.people) if (p.groups.includes(g) && !isChosen(p.id)) chosen.value.push({ id: p.id, fullname: p.fullname });
}
async function sendNew() {
  busy.value = true;
  formError.value = "";
  try {
    const r = await workApi.newMessage(chosen.value.map((p) => p.id), draft.value);
    if (r.failed.length) formError.value = t("inbox.someFailed", { n: r.failed.length }) + " " + r.failed.join("；");
    else composing.value = false;
    await load();
    if (r.conversation && !r.failed.length) openConv(r.conversation);
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    busy.value = false;
  }
}

onMounted(() => {
  load();
  poll = setInterval(() => {
    load();
    if (openId.value && !busy.value) openConv(openId.value);
  }, 20000);
});
onUnmounted(() => poll && clearInterval(poll));
</script>

<style scoped>
.pad { padding: 18px; display: block; }
.split { display: grid; grid-template-columns: 320px minmax(0, 1fr); background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; min-height: 520px; overflow: hidden; }
.convs { border-right: 1px solid var(--wq-line); overflow: auto; max-height: 640px; }
.conv { display: flex; align-items: center; gap: 10px; padding: 12px 14px; border-bottom: 1px solid #eef1f0; cursor: pointer; }
.conv:hover, .conv.on { background: #f1f6f8; }
.conv.unread .c-name { font-weight: 800; }
.c-main { flex: 1; min-width: 0; }
.c-top { justify-content: space-between; flex-wrap: nowrap; }
.c-name { color: var(--wq-ink); font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.c-last { display: block; font-size: 13px; color: var(--wq-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.badge { background: var(--wq-danger); color: #fff; border-radius: 999px; font-size: 12px; min-width: 20px; text-align: center; padding: 0 6px; }
.thread { display: flex; flex-direction: column; min-width: 0; }
.t-head { padding: 12px 16px; border-bottom: 1px solid var(--wq-line); display: flex; gap: 10px; align-items: center; }
.back { display: none; font-size: 20px; }
.t-name { font-weight: 700; color: var(--wq-ink); }
.msgs { flex: 1; height: 440px; padding: 12px 16px; box-sizing: border-box; }
.msg { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 12px; }
.msg.mine { align-items: flex-end; }
.m-author { font-size: 12px; color: var(--wq-muted); margin-bottom: 2px; }
.bubble { max-width: 76%; background: #f1f4f5; border-radius: 12px; padding: 8px 12px; line-height: 1.6; }
.msg.mine .bubble { background: #fff3cc; }
.m-time { font-size: 11px; color: #9aa7ad; margin-top: 2px; }
.reply { display: flex; gap: 10px; align-items: flex-end; padding: 10px 14px; border-top: 1px solid var(--wq-line); }
.r-in { min-height: 44px; flex: 1; }
.compose .chips { display: flex; flex-wrap: wrap; gap: 6px; min-height: 28px; }
.chip { background: var(--wq-ink); color: #fff; border-radius: 999px; padding: 2px 10px; font-size: 13px; cursor: pointer; }
.picker { max-height: 260px; overflow: auto; border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 12px; margin: 10px 0; }
.pc { padding: 6px 0; border-bottom: 1px dashed var(--wq-line); }
.pc-h { gap: 12px; }
.pc-name { font-weight: 700; color: var(--wq-ink); }
.pc-people { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.person { border: 1px solid var(--wq-line); border-radius: 999px; padding: 2px 10px; font-size: 13px; cursor: pointer; }
.person.teacher { border-color: var(--wq-accent); }
.person.on { background: var(--wq-ink); color: #fff; border-color: var(--wq-ink); }
.acts { margin-top: 10px; }
.note.unread { border-left: 4px solid var(--wq-accent); }
.n-subj { font-weight: 700; color: var(--wq-ink); flex: 1; }
.n-text { display: block; margin-top: 4px; color: var(--wq-text); }
@media (max-width: 760px) {
  .split { grid-template-columns: 1fr; }
  .split.open .convs { display: none; }
  .split:not(.open) .thread { display: none; }
  .back { display: inline; }
}
</style>
