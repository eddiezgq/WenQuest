<template>
  <view>
    <view class="wq-head">
      <text class="wq-h1">{{ t("menu.announcements") }}</text>
      <view v-if="canPost && !editing" class="wq-btn primary" @click="startNew">＋ {{ t("ann.publish") }}</view>
    </view>

    <view v-if="editing" class="wq-card editor">
      <text class="wq-label">{{ t("ann.title") }}</text>
      <input v-model="form.subject" class="wq-input" :placeholder="t('ann.titleHint')" />
      <text class="wq-label">{{ t("ann.body") }}</text>
      <textarea v-model="form.message" class="wq-textarea" auto-height :maxlength="-1" :placeholder="t('ann.bodyHint')" />
      <text v-if="formError" class="wq-error">{{ formError }}</text>
      <view class="wq-row actions">
        <view class="wq-btn primary" :class="{ disabled: saving }" @click="save">{{ saving ? t("common.saving") : editingId ? t("common.save") : t("ann.publish") }}</view>
        <view class="wq-btn" @click="editing = false">{{ t("common.cancel") }}</view>
      </view>
    </view>

    <text v-if="loading && !items.length" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error" class="wq-error">{{ errorText(error) }}</text>
    <view v-else-if="!items.length" class="wq-empty">{{ t("ann.none") }}</view>

    <view v-for="a in items" :key="a.id" class="wq-card ann" :class="{ unread: a.unread }">
      <view class="a-head">
        <view class="wq-avatar">{{ initials(a.author) }}</view>
        <view class="a-meta">
          <text class="a-title">{{ a.subject }}</text>
          <text class="wq-muted">{{ a.author }} · {{ formatDate(a.created) }}</text>
        </view>
        <text v-if="a.pinned" class="wq-tag accent">{{ t("disc.pinned") }}</text>
        <text v-if="a.unread" class="wq-tag live">{{ t("ann.new") }}</text>
      </view>
      <view class="a-body" :class="{ clipped: !open[a.id] && long(a) }"><MathContent :html="a.message" /></view>
      <view class="wq-row">
        <text v-if="long(a)" class="wq-link" @click="open = { ...open, [a.id]: !open[a.id] }">
          {{ open[a.id] ? t("common.collapse") : t("common.readMore") }}
        </text>
        <text v-if="a.replies" class="wq-muted">{{ t("disc.replies", { n: a.replies }) }}</text>
        <text class="wq-link" @click="thread(a)">{{ t("ann.comments") }} ›</text>
        <template v-if="canPost">
          <text class="wq-link" @click="startEdit(a)">{{ t("common.edit") }}</text>
          <text class="wq-link danger" @click="remove(a)">{{ t("common.delete") }}</text>
        </template>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import MathContent from "../MathContent.vue";
import { ApiError } from "../../api";
import { confirmAction, courseApi, type Discussion, initials } from "../../courseApi";
import { errorText, formatDate, t } from "../../i18n";

const props = defineProps<{ courseId: number }>();
const items = ref<Discussion[]>([]);
const canPost = ref(false);
const loading = ref(true);
const error = ref("");
const open = ref<Record<number, boolean>>({});
const editing = ref(false);
const editingId = ref(0);
const saving = ref(false);
const formError = ref("");
const form = reactive({ subject: "", message: "" });

const long = (a: Discussion) => a.message.length > 600;

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const r = await courseApi.announcements(props.courseId);
    items.value = r.items;
    canPost.value = r.can_post;
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

function startNew() {
  Object.assign(form, { subject: "", message: "" });
  editingId.value = 0;
  formError.value = "";
  editing.value = true;
}
function startEdit(a: Discussion) {
  Object.assign(form, { subject: a.subject, message: a.message.replace(/<br\s*\/?>/g, "\n").replace(/<\/p>\s*<p>/g, "\n\n").replace(/<[^>]+>/g, "") });
  editingId.value = a.postid;
  formError.value = "";
  editing.value = true;
}
async function save() {
  if (!form.subject.trim() || !form.message.trim()) {
    formError.value = t("ann.needBoth");
    return;
  }
  saving.value = true;
  formError.value = "";
  try {
    if (editingId.value) await courseApi.editPost(editingId.value, form.subject, form.message);
    else await courseApi.announce(props.courseId, form.subject, form.message);
    editing.value = false;
    await load();
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    saving.value = false;
  }
}
async function remove(a: Discussion) {
  if (!(await confirmAction(t("ann.confirmDelete", { name: a.subject }), t("common.delete"), t("common.cancel")))) return;
  try {
    await courseApi.deletePost(a.postid);
    await load();
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  }
}
function thread(a: Discussion) {
  uni.navigateTo({ url: `/pages/discussion/discussion?id=${a.id}&course=${props.courseId}&kind=announcements` });
}

onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.editor .actions { margin-top: 12px; }
.ann.unread { border-left: 4px solid var(--wq-accent); }
.a-head { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.a-meta { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.a-title { font-size: 17px; font-weight: 700; color: var(--wq-ink); }
.a-body { color: var(--wq-text); line-height: 1.75; margin-bottom: 8px; }
.a-body.clipped { max-height: 220px; overflow: hidden; -webkit-mask-image: linear-gradient(#000 70%, transparent); mask-image: linear-gradient(#000 70%, transparent); }
</style>
