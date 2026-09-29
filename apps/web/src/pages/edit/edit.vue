<template>
  <AppShell nav="courses" :course="d" tab="modules" :crumb="heading" :title="heading">
    <text v-if="loading" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error" class="wq-error">{{ errorText(error) }}</text>
    <view v-else class="editor">
      <text class="wq-h1">{{ heading }}</text>
      <view class="wq-card">
        <BiField v-model="f.name" :label="t('edit.name')" :placeholder="t('edit.nameHint.' + type)" />

        <!-- reading page -->
        <BiField v-if="type === 'page'" v-model="f.content" :label="t('edit.pageContent')" kind="rich" :placeholder="t('edit.pageHint')" />

        <!-- link -->
        <template v-if="type === 'url'">
          <text class="wq-label">{{ t("edit.url") }}</text>
          <input v-model="f.url" class="wq-input" placeholder="https://" />
        </template>

        <!-- description / instructions -->
        <BiField v-if="type !== 'page'" v-model="f.intro" :label="type === 'assign' ? t('edit.requirements') : t('edit.description')" kind="rich"
          :placeholder="type === 'assign' ? t('edit.requirementsHint') : ''" />

        <!-- assignment settings -->
        <template v-if="type === 'assign'">
          <view class="grid">
            <view>
              <text class="wq-label">{{ t("edit.dueDate") }}</text>
              <view class="wq-row">
                <picker mode="date" :value="due.date" @change="(e: any) => (due.date = e.detail.value)"><view class="wq-input pk">{{ due.date || t("edit.none") }}</view></picker>
                <picker mode="time" :value="due.time" @change="(e: any) => (due.time = e.detail.value)"><view class="wq-input pk">{{ due.time }}</view></picker>
                <text v-if="due.date" class="wq-link" @click="due.date = ''">✕</text>
              </view>
            </view>
            <view>
              <text class="wq-label">{{ t("work.points") }}</text>
              <input v-model.number="f.grade" type="digit" class="wq-input" />
            </view>
          </view>
          <text class="wq-label">{{ t("work.submitAs") }}</text>
          <view class="wq-row">
            <text class="chk" :class="{ on: f.allowtext }" @click="f.allowtext = !f.allowtext">{{ f.allowtext ? "☑" : "☐" }} {{ t("work.asText") }}</text>
            <text class="chk" :class="{ on: f.allowfiles }" @click="f.allowfiles = !f.allowfiles">{{ f.allowfiles ? "☑" : "☐" }} {{ t("work.asFiles") }}</text>
            <template v-if="f.allowfiles">
              <text class="wq-muted">{{ t("edit.maxFiles") }}</text>
              <input v-model.number="f.maxfiles" type="number" class="wq-input tiny" />
            </template>
          </view>
        </template>

        <view v-if="!cmid" class="wq-row sw" @click="f.visible = !f.visible">
          <text class="chk" :class="{ on: f.visible }">{{ f.visible ? "☑" : "☐" }} {{ t("edit.visibleNow") }}</text>
        </view>
        <text v-if="formError" class="wq-error">{{ formError }}</text>
        <view class="wq-row acts">
          <view class="wq-btn primary" :class="{ disabled: saving }" @click="save">{{ saving ? t("common.saving") : t("common.save") }}</view>
          <view class="wq-btn" @click="back">{{ t("common.cancel") }}</view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import BiField from "../../components/edit/BiField.vue";
import { ApiError, token } from "../../api";
import { type Bi, editApi } from "../../courseApi";
import { errorText, t } from "../../i18n";
import { type CourseData, loadCourse } from "../../store";

defineOptions({ inheritAttrs: false });

const cid = ref(0);
const cmid = ref(0);
const section = ref(0);
const type = ref("page");
const d = ref<CourseData | null>(null);
const loading = ref(true);
const error = ref("");
const saving = ref(false);
const formError = ref("");
const f = reactive<{ name: Bi; content: Bi; intro: Bi; url: string; grade: number; allowtext: boolean; allowfiles: boolean; maxfiles: number; visible: boolean }>({
  name: { text: "" }, content: { text: "" }, intro: { text: "" }, url: "", grade: 100, allowtext: true, allowfiles: true, maxfiles: 5, visible: true,
});
const due = reactive({ date: "", time: "23:59" });
const heading = computed(() => t(cmid.value ? "edit.editKind" : "edit.newKind", { kind: t("edit.kind." + type.value) }));
const pad = (n: number) => String(n).padStart(2, "0");
const filled = (b: Bi) => !!(b.text || b.zh || b.en || "").trim();

async function load() {
  loading.value = true;
  error.value = "";
  try {
    d.value = await loadCourse(cid.value);
    if (cmid.value) {
      const c = await editApi.content(cid.value, cmid.value);
      type.value = c.type;
      Object.assign(f, {
        name: c.name, content: c.content || { text: "" }, intro: c.intro || { text: "" }, url: c.url || "",
        grade: c.grade || 100, allowtext: !!c.allowtext, allowfiles: !!c.allowfiles, maxfiles: c.maxfiles || 5,
      });
      if (c.duedate) {
        const x = new Date(c.duedate * 1000);
        due.date = `${x.getFullYear()}-${pad(x.getMonth() + 1)}-${pad(x.getDate())}`;
        due.time = `${pad(x.getHours())}:${pad(x.getMinutes())}`;
      }
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

function dueTs(): number {
  if (!due.date) return 0;
  const [y, m, dd] = due.date.split("-").map(Number);
  const [h, mi] = due.time.split(":").map(Number);
  return Math.round(new Date(y, m - 1, dd, h, mi).getTime() / 1000);
}

async function save() {
  if (!filled(f.name)) return (formError.value = t("error.name_required"));
  if (type.value === "url" && !f.url.trim()) return (formError.value = t("error.url_required"));
  if (type.value === "assign" && !f.allowtext && !f.allowfiles) return (formError.value = t("edit.needSubmitType"));
  saving.value = true;
  formError.value = "";
  const body: Record<string, unknown> = { name: f.name };
  if (type.value === "page") body.content = f.content;
  else body.intro = f.intro;
  if (type.value === "url") body.url = f.url;
  if (type.value === "assign") Object.assign(body, { duedate: dueTs(), grade: Number(f.grade) || 100, allowtext: f.allowtext, allowfiles: f.allowfiles, maxfiles: Number(f.maxfiles) || 5 });
  try {
    if (cmid.value) await editApi.saveContent(cid.value, cmid.value, body);
    else await editApi.addActivity(cid.value, section.value, { ...body, type: type.value, visible: f.visible } as any);
    await loadCourse(cid.value, true);
    uni.showToast({ title: t("work.saved"), icon: "none" });
    back();
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    saving.value = false;
  }
}
function back() {
  if (getCurrentPages().length > 1) uni.navigateBack();
  else uni.redirectTo({ url: `/pages/course/course?id=${cid.value}&tab=modules&edit=1` });
}

onLoad((q: any) => {
  cid.value = Number(q?.course || 0);
  cmid.value = Number(q?.cmid || 0);
  section.value = Number(q?.section || 0);
  if (q?.type) type.value = String(q.type);
});
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  if (loading.value) load();
});
</script>

<style scoped>
.editor { max-width: 980px; }
.grid { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; }
.pk { display: flex; align-items: center; min-width: 110px; cursor: pointer; }
.chk { cursor: pointer; padding: 4px 8px; border-radius: 6px; }
.chk.on { color: var(--wq-ink); font-weight: 600; }
.tiny { width: 70px; }
.sw { margin-top: 12px; }
.acts { margin-top: 16px; }
@media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }
</style>
