<template>
  <view>
    <view class="wq-head">
      <view class="wq-row">
        <text v-if="forum" class="wq-link back" @click="forum = null">‹ {{ t("disc.allForums") }}</text>
        <text class="wq-h1">{{ forum ? forum.name : t("menu.discussions") }}</text>
      </view>
      <view v-if="forum && canPost && !writing" class="wq-btn primary" @click="startNew">＋ {{ t("disc.newTopic") }}</view>
      <view v-if="!forum && canManage && !creating" class="wq-btn primary" @click="startForum">＋ {{ t("disc.newForum") }}</view>
    </view>

    <view v-if="creating" class="wq-card">
      <text class="wq-label">{{ t("disc.forumName") }}</text>
      <input v-model="forumForm.name" class="wq-input" :placeholder="t('disc.forumNameHint')" />
      <text class="wq-label">{{ t("disc.forumIntro") }}</text>
      <input v-model="forumForm.intro" class="wq-input" :placeholder="t('disc.forumIntroHint')" />
      <text v-if="formError" class="wq-error">{{ formError }}</text>
      <view class="wq-row actions">
        <view class="wq-btn primary" :class="{ disabled: saving }" @click="createForum">{{ saving ? t("common.saving") : t("common.save") }}</view>
        <view class="wq-btn" @click="creating = false">{{ t("common.cancel") }}</view>
      </view>
    </view>

    <text v-if="loading" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error" class="wq-error">{{ errorText(error) }}</text>

    <!-- forums of the course -->
    <template v-else-if="!forum">
      <view v-if="!forums.length" class="wq-empty">
        <text class="block">{{ canManage ? t("disc.noForumsTeacher") : t("disc.noForums") }}</text>
        <view v-if="canManage && !creating" class="wq-btn primary one" :class="{ disabled: saving }" @click="quickForum">＋ {{ t("disc.quickForum") }}</view>
      </view>
      <view v-for="f in forums" :key="f.id" class="wq-card forum" @click="openForum(f)">
        <view class="f-icon">✉</view>
        <view class="f-body">
          <text class="f-name">{{ f.name }}</text>
          <view v-if="f.intro" class="f-intro"><MathContent :html="f.intro" /></view>
        </view>
        <view class="f-side">
          <text v-if="f.discussions !== null" class="wq-muted">{{ t("disc.topics", { n: f.discussions }) }}</text>
          <text v-if="f.unread" class="wq-tag live">{{ t("disc.unread", { n: f.unread }) }}</text>
        </view>
        <text class="chev">›</text>
      </view>
    </template>

    <!-- topics of one forum -->
    <template v-else>
      <view v-if="forum.intro" class="intro"><MathContent :html="forum.intro" /></view>
      <view v-if="writing" class="wq-card">
        <text class="wq-label">{{ t("disc.topicTitle") }}</text>
        <input v-model="form.subject" class="wq-input" :placeholder="t('disc.topicTitleHint')" />
        <text class="wq-label">{{ t("disc.topicBody") }}</text>
        <textarea v-model="form.message" class="wq-textarea" auto-height :maxlength="-1" :placeholder="t('disc.topicBodyHint')" />
        <text v-if="formError" class="wq-error">{{ formError }}</text>
        <view class="wq-row actions">
          <view class="wq-btn primary" :class="{ disabled: saving }" @click="post">{{ saving ? t("common.saving") : t("disc.post") }}</view>
          <view class="wq-btn" @click="writing = false">{{ t("common.cancel") }}</view>
        </view>
      </view>
      <view v-if="!topics.length && !writing" class="wq-empty">{{ t("disc.noTopics") }}</view>
      <view v-if="topics.length" class="topics">
        <view v-for="d in topics" :key="d.id" class="topic" @click="openThread(d)">
          <view class="wq-avatar">{{ initials(d.author) }}</view>
          <view class="t-body">
            <view class="wq-row t-line">
              <text v-if="d.pinned" class="wq-tag accent">{{ t("disc.pinned") }}</text>
              <text v-if="d.locked" class="wq-tag">{{ t("disc.locked") }}</text>
              <text class="t-title" :class="{ unread: d.unread }">{{ d.subject }}</text>
            </view>
            <text class="wq-muted">{{ d.author }} · {{ formatDate(d.modified || d.created) }}</text>
          </view>
          <view class="t-count">
            <text class="n">{{ d.replies }}</text>
            <text class="wq-muted">{{ t("disc.repliesShort") }}</text>
            <text v-if="d.unread" class="wq-tag live">{{ t("disc.unread", { n: d.unread }) }}</text>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import MathContent from "../MathContent.vue";
import { ApiError } from "../../api";
import { courseApi, type Discussion, type Forum, initials } from "../../courseApi";
import { errorText, formatDate, t } from "../../i18n";

const props = defineProps<{ courseId: number; forumCmid?: number }>();
const forums = ref<Forum[]>([]);
const forum = ref<Forum | null>(null);
const topics = ref<Discussion[]>([]);
const canPost = ref(false);
const canManage = ref(false);
const creating = ref(false);
const forumForm = reactive({ name: "", intro: "" });
const loading = ref(true);
const error = ref("");
const writing = ref(false);
const saving = ref(false);
const formError = ref("");
const form = reactive({ subject: "", message: "" });

async function run(fn: () => Promise<void>) {
  loading.value = true;
  error.value = "";
  try {
    await fn();
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

const load = () => run(async () => {
  const fr = await courseApi.forums(props.courseId);
  forums.value = fr.forums;
  canManage.value = fr.can_manage;
  const wanted = props.forumCmid ? forums.value.find((f) => f.cmid === props.forumCmid) : null;
  if (wanted && !forum.value) await openForum(wanted);
  else if (forums.value.length === 1 && !forum.value) await openForum(forums.value[0]);
  else if (forum.value) await openForum(forum.value);
});

async function openForum(f: Forum) {
  forum.value = f;
  writing.value = false;
  const r = await courseApi.discussions(f.id);
  topics.value = r.items;
  canPost.value = r.can_post;
}

function startNew() {
  Object.assign(form, { subject: "", message: "" });
  formError.value = "";
  writing.value = true;
}
async function post() {
  if (!forum.value) return;
  if (!form.subject.trim() || !form.message.trim()) {
    formError.value = t("ann.needBoth");
    return;
  }
  saving.value = true;
  try {
    const r = await courseApi.startDiscussion(forum.value.id, form.subject, form.message);
    writing.value = false;
    await openForum(forum.value);
    openThread({ id: r.id } as Discussion);
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    saving.value = false;
  }
}
function startForum() {
  Object.assign(forumForm, { name: "", intro: "" });
  formError.value = "";
  creating.value = true;
}
async function makeForum(name: string, intro: string) {
  saving.value = true;
  formError.value = "";
  try {
    await courseApi.addForum(props.courseId, name, intro);
    creating.value = false;
    forum.value = null;
    await load();
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
    uni.showToast({ title: formError.value, icon: "none" });
  } finally {
    saving.value = false;
  }
}
const createForum = () => (forumForm.name.trim() ? makeForum(forumForm.name.trim(), forumForm.intro) : (formError.value = t("error.name_required")));
const quickForum = () => makeForum(t("disc.defaultForum"), t("disc.defaultForumIntro"));
function openThread(d: Discussion) {
  uni.navigateTo({ url: `/pages/discussion/discussion?id=${d.id}&course=${props.courseId}` });
}

onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.back { font-size: 14px; }
.block { display: block; }
.one { margin-top: 12px; }
.actions { margin-top: 12px; }
.intro { color: var(--wq-text); margin: -6px 0 14px; }
.forum { display: flex; align-items: center; gap: 14px; cursor: pointer; }
.forum:hover { border-color: var(--wq-link); }
.f-icon { width: 42px; height: 42px; border-radius: 10px; background: #0d1a20; color: var(--wq-accent); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.f-body { flex: 1; min-width: 0; }
.f-name { display: block; font-size: 17px; font-weight: 700; color: var(--wq-link); }
.f-intro { color: var(--wq-muted); font-size: 13px; max-height: 44px; overflow: hidden; }
.f-side { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.chev { color: var(--wq-muted); font-size: 18px; }
.topics { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; overflow: hidden; }
.topic { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-top: 1px solid var(--wq-line); cursor: pointer; }
.topic:first-child { border-top: 0; }
.topic:hover { background: #f5f8f9; }
.t-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.t-line { gap: 6px; }
.t-title { color: var(--wq-ink); font-size: 15px; }
.t-title.unread { font-weight: 700; }
.t-count { display: flex; flex-direction: column; align-items: center; min-width: 48px; }
.n { font-family: "IBM Plex Mono", Menlo, monospace; font-size: 17px; color: var(--wq-ink); }
</style>
