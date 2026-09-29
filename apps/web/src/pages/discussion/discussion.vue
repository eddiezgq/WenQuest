<template>
  <AppShell nav="courses" :course="d" :tab="kind" :crumb="th ? th.subject : ''" :title="t('menu.discussions')">
    <text v-if="loading && !th" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error && !th" class="wq-error">{{ errorText(error) }}</text>

    <template v-else-if="th">
      <view class="wq-head">
        <view class="wq-row">
          <text class="wq-link" @click="back">‹ {{ t(kind === "announcements" ? "menu.announcements" : "disc.allTopics") }}</text>
        </view>
        <view v-if="teacher && meta" class="wq-row">
          <view class="wq-btn small" @click="toggle('pin')">{{ meta.pinned ? t("disc.unpin") : t("disc.pin") }}</view>
          <view class="wq-btn small" @click="toggle('lock')">{{ meta.locked ? t("disc.unlock") : t("disc.lock") }}</view>
        </view>
      </view>
      <text class="wq-h1">{{ th.subject }}</text>
      <view v-if="meta && meta.locked" class="wq-card locked-note">🔒 {{ t("disc.lockedNote") }}</view>

      <view v-for="p in ordered" :key="p.post.id" class="post" :style="{ marginLeft: Math.min(p.depth, 3) * 28 + 'px' }">
        <view class="p-head">
          <view class="wq-avatar">{{ initials(p.post.author) }}</view>
          <view class="p-meta">
            <text class="p-author">{{ p.post.author }}</text>
            <text class="wq-muted">{{ formatDate(p.post.time) }}</text>
          </view>
          <text v-if="p.post.unread" class="wq-tag live">{{ t("ann.new") }}</text>
        </view>
        <view v-if="editId === p.post.id" class="p-edit">
          <textarea v-model="editText" class="wq-textarea" auto-height :maxlength="-1" />
          <view class="wq-row">
            <view class="wq-btn primary small" :class="{ disabled: busy }" @click="saveEdit(p.post)">{{ t("common.save") }}</view>
            <view class="wq-btn small" @click="editId = 0">{{ t("common.cancel") }}</view>
          </view>
        </view>
        <view v-else class="p-body">
          <text v-if="p.post.deleted" class="wq-muted">{{ t("disc.deleted") }}</text>
          <MathContent v-else :html="p.post.message" />
        </view>
        <view v-if="p.post.attachments.length" class="files">
          <text v-for="f in p.post.attachments" :key="f.url" class="wq-link" @click="openFile(f.url)">📎 {{ f.name }}</text>
        </view>
        <view class="wq-row p-actions">
          <text v-if="p.post.can_reply && !(meta && meta.locked)" class="wq-link" @click="startReply(p.post.id)">{{ t("disc.reply") }}</text>
          <text v-if="p.post.can_edit && !p.post.deleted" class="wq-link" @click="startEdit(p.post)">{{ t("common.edit") }}</text>
          <text v-if="p.post.can_delete && !p.post.deleted" class="wq-link danger" @click="remove(p.post)">{{ t("common.delete") }}</text>
        </view>
        <view v-if="replyTo === p.post.id" class="reply-box">
          <textarea v-model="replyText" class="wq-textarea" auto-height :maxlength="-1" :focus="true" :placeholder="t('disc.replyHint', { name: p.post.author })" />
          <text v-if="formError" class="wq-error">{{ formError }}</text>
          <view class="wq-row">
            <view class="wq-btn primary small" :class="{ disabled: busy || !replyText.trim() }" @click="sendReply(p.post.id)">{{ busy ? t("common.saving") : t("disc.send") }}</view>
            <view class="wq-btn small" @click="replyTo = 0">{{ t("common.cancel") }}</view>
          </view>
        </view>
      </view>

      <!-- quick reply to the first post -->
      <view v-if="first && first.can_reply && !(meta && meta.locked) && replyTo !== first.id" class="wq-card quick" @click="startReply(first.id)">
        <text class="wq-muted">{{ t("disc.writeReply") }}</text>
      </view>
    </template>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import MathContent from "../../components/MathContent.vue";
import { absolute, ApiError, token } from "../../api";
import { confirmAction, courseApi, type Discussion, initials, openOutside, type Post, type Thread } from "../../courseApi";
import { errorText, formatDate, t } from "../../i18n";
import { type CourseData, isTeacher, loadCourse } from "../../store";

defineOptions({ inheritAttrs: false });

const id = ref(0);
const cid = ref(0);
const kind = ref("discussions");
const d = ref<CourseData | null>(null);
const th = ref<Thread | null>(null);
const meta = ref<Discussion | null>(null);
const loading = ref(true);
const error = ref("");
const replyTo = ref(0);
const replyText = ref("");
const editId = ref(0);
const editText = ref("");
const busy = ref(false);
const formError = ref("");

const teacher = computed(() => isTeacher(d.value));
const first = computed(() => th.value?.posts[0] || null);
/** Replies under the post they answer, oldest first. */
const ordered = computed(() => {
  const posts = th.value?.posts || [];
  const kids = new Map<number, Post[]>();
  for (const p of posts) kids.set(p.parent, [...(kids.get(p.parent) || []), p]);
  const out: { post: Post; depth: number }[] = [];
  const walk = (parent: number, depth: number) => {
    for (const p of kids.get(parent) || []) {
      out.push({ post: p, depth });
      walk(p.id, depth + 1);
    }
  };
  walk(0, 0);
  const seen = new Set(out.map((x) => x.post.id));
  for (const p of posts) if (!seen.has(p.id)) out.push({ post: p, depth: 1 });
  return out;
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    if (!d.value) d.value = await loadCourse(cid.value);
    th.value = await courseApi.thread(id.value);
    if (isTeacher(d.value) && th.value.forum) {
      meta.value = (await courseApi.discussions(th.value.forum)).items.find((x) => x.id === id.value) || null;
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

function startReply(pid: number) {
  replyTo.value = pid;
  replyText.value = "";
  formError.value = "";
  editId.value = 0;
}
function startEdit(p: Post) {
  editId.value = p.id;
  editText.value = p.message.replace(/<br\s*\/?>/g, "\n").replace(/<\/p>\s*<p>/g, "\n\n").replace(/<[^>]+>/g, "");
  replyTo.value = 0;
}
async function sendReply(pid: number) {
  busy.value = true;
  formError.value = "";
  try {
    await courseApi.reply(pid, replyText.value);
    replyTo.value = 0;
    await load();
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    busy.value = false;
  }
}
async function saveEdit(p: Post) {
  busy.value = true;
  try {
    await courseApi.editPost(p.id, "", editText.value);
    editId.value = 0;
    await load();
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  } finally {
    busy.value = false;
  }
}
async function remove(p: Post) {
  const whole = p.id === first.value?.id;
  if (!(await confirmAction(t(whole ? "disc.confirmDeleteTopic" : "disc.confirmDelete"), t("common.delete"), t("common.cancel")))) return;
  try {
    await courseApi.deletePost(p.id);
    if (whole) return back();
    await load();
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  }
}
async function toggle(what: "pin" | "lock") {
  if (!meta.value) return;
  try {
    if (what === "pin") await courseApi.pin(id.value, !meta.value.pinned);
    else await courseApi.lock(id.value, !meta.value.locked);
    await load();
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  }
}
const openFile = (url: string) => openOutside(absolute(url), t("activity.linkCopied"));
function back() {
  const pages = getCurrentPages();
  if (pages.length > 1) uni.navigateBack();
  else uni.redirectTo({ url: `/pages/course/course?id=${cid.value}&tab=${kind.value}` });
}

onLoad((q: any) => {
  id.value = Number(q?.id || 0);
  cid.value = Number(q?.course || 0);
  kind.value = q?.kind === "announcements" ? "announcements" : "discussions";
});
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  load();
});
</script>

<style scoped>
.locked-note { color: var(--wq-muted); }
.post { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; }
.p-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.p-meta { flex: 1; display: flex; flex-direction: column; }
.p-author { font-weight: 600; color: var(--wq-ink); }
.p-body { line-height: 1.75; color: var(--wq-text); }
.p-edit { display: flex; flex-direction: column; gap: 8px; }
.files { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
.p-actions { margin-top: 8px; gap: 16px; }
.reply-box { margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }
.quick { cursor: text; }
</style>
