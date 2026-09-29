<template>
  <view>
    <view class="wq-head">
      <text class="wq-h1">{{ t("menu.grades") }}</text>
      <input v-if="teacher" v-model="q" class="wq-input search" :placeholder="t('people.search')" />
    </view>
    <text v-if="loading && !items.length" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error" class="wq-error">{{ errorText(error) }}</text>
    <view v-else-if="!work.length" class="wq-empty">{{ t("grades.none") }}</view>

    <!-- student: my grades -->
    <view v-else-if="!teacher" class="mine">
      <view v-if="total && cells[String(total.id)]" class="wq-card total">
        <text class="wq-muted">{{ t("grades.total") }}</text>
        <text class="t-n">{{ cells[String(total.id)].text }}</text>
        <text class="wq-muted">{{ cells[String(total.id)].percent }}</text>
      </view>
      <view class="table">
        <view class="tr th"><text class="c-name">{{ t("grades.item") }}</text><text class="c-g">{{ t("grades.grade") }}</text><text class="c-p">{{ t("grades.percent") }}</text></view>
        <view v-for="i in work" :key="i.id" class="tr-wrap">
          <view class="tr" @click="toggle(i.id)">
            <view class="c-name">
              <text class="kind">{{ t("type." + (i.module || "other")) }}</text>
              <text class="wq-link" @click.stop="openItem(i)">{{ i.name }}</text>
            </view>
            <text class="c-g">{{ cell(i).text || "—" }}<text class="wq-muted"> / {{ i.max }}</text></text>
            <text class="c-p">{{ cell(i).percent }}</text>
          </view>
          <view v-if="cell(i).feedback && (open[i.id] ?? true)" class="fb"><text class="wq-label">{{ t("work.teacherFeedback") }}</text><MathContent :html="cell(i).feedback" /></view>
        </view>
      </view>
    </view>

    <!-- teacher: the class grade book -->
    <scroll-view v-else scroll-x class="book">
      <view class="grid" :style="{ gridTemplateColumns: `180px repeat(${work.length + (total ? 1 : 0)}, 110px)` }">
        <text class="h sticky">{{ t("grades.student") }}</text>
        <text v-for="i in work" :key="'h' + i.id" class="h link" @click="openItem(i)">{{ i.name }}<text class="wq-muted"> /{{ i.max }}</text></text>
        <text v-if="total" class="h">{{ t("grades.total") }}</text>
        <template v-for="r in shownRows" :key="r.id">
          <text class="n sticky">{{ r.fullname }}</text>
          <text v-for="i in work" :key="r.id + '-' + i.id" class="v" :class="{ empty: !r.cells[String(i.id)] || r.cells[String(i.id)].raw === null }">
            {{ r.cells[String(i.id)]?.raw !== null && r.cells[String(i.id)] ? r.cells[String(i.id)].text : "–" }}
          </text>
          <text v-if="total" class="v tot">{{ r.cells[String(total.id)]?.text || "–" }}</text>
        </template>
        <template v-if="averages">
          <text class="n sticky avg">{{ t("grades.average") }}</text>
          <text v-for="i in work" :key="'a' + i.id" class="v avg">{{ averages[i.id] }}</text>
          <text v-if="total" class="v avg">{{ averages[total.id] }}</text>
        </template>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import MathContent from "../MathContent.vue";
import { ApiError } from "../../api";
import { type GradeCell, type GradeItem, workApi } from "../../courseApi";
import { errorText, t } from "../../i18n";

const props = defineProps<{ courseId: number }>();
const items = ref<GradeItem[]>([]);
const cells = ref<Record<string, GradeCell>>({});
const rows = ref<{ id: number; fullname: string; cells: Record<string, GradeCell> }[]>([]);
const teacher = ref(false);
const loading = ref(true);
const error = ref("");
const q = ref("");
const open = ref<Record<number, boolean>>({});

const work = computed(() => items.value.filter((i) => i.type !== "course" && i.type !== "category"));
const total = computed(() => items.value.find((i) => i.type === "course") || null);
const shownRows = computed(() => rows.value.filter((r) => !q.value.trim() || r.fullname.toLowerCase().includes(q.value.trim().toLowerCase())));
const cell = (i: GradeItem): GradeCell => cells.value[String(i.id)] || { raw: null, text: "", percent: "", feedback: "", hidden: false, graded_at: 0 };
const averages = computed(() => {
  if (!rows.value.length) return null;
  const out: Record<number, string> = {};
  for (const i of [...work.value, ...(total.value ? [total.value] : [])]) {
    const vals = rows.value.map((r) => r.cells[String(i.id)]?.raw).filter((v): v is number => v !== null && v !== undefined);
    out[i.id] = vals.length ? (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(1) : "–";
  }
  return out;
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const r = await workApi.grades(props.courseId);
    teacher.value = r.teacher;
    items.value = r.items;
    cells.value = r.cells || {};
    rows.value = r.rows || [];
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}
const toggle = (id: number) => (open.value = { ...open.value, [id]: !(open.value[id] ?? true) });
function openItem(i: GradeItem) {
  if (i.cmid) uni.navigateTo({ url: `/pages/activity/activity?id=${i.cmid}&course=${props.courseId}` });
}

onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.search { max-width: 260px; }
.total { display: flex; align-items: baseline; gap: 14px; border-left: 4px solid var(--wq-ok); }
.t-n { font-size: 28px; font-weight: 800; color: var(--wq-ok); font-family: "IBM Plex Mono", Menlo, monospace; }
.table { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; overflow: hidden; }
.tr { display: flex; align-items: center; gap: 10px; padding: 10px 16px; border-top: 1px solid var(--wq-line); }
.tr.th { border-top: 0; background: #f3f5f5; font-size: 13px; color: var(--wq-muted); }
.tr-wrap:first-of-type .tr { border-top: 1px solid var(--wq-line); }
.c-name { flex: 1; min-width: 0; display: flex; align-items: center; gap: 8px; }
.kind { font-size: 12px; color: var(--wq-muted); background: #eef2f1; border-radius: 4px; padding: 0 6px; }
.c-g { width: 120px; text-align: right; font-family: "IBM Plex Mono", Menlo, monospace; }
.c-p { width: 90px; text-align: right; color: var(--wq-muted); }
.fb { padding: 4px 16px 12px 16px; background: #fafbfb; }
.book { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; }
.grid { display: grid; }
.h, .n, .v { padding: 8px 10px; border-bottom: 1px solid var(--wq-line); border-right: 1px solid #eef1f0; font-size: 13px; background: #fff; }
.h { background: #f3f5f5; font-weight: 600; color: var(--wq-ink); position: sticky; top: 0; }
.h.link { color: var(--wq-link); cursor: pointer; }
.sticky { position: sticky; left: 0; z-index: 1; }
.n { color: var(--wq-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.v { text-align: center; font-family: "IBM Plex Mono", Menlo, monospace; }
.v.empty { color: #b8c2c6; }
.v.tot { font-weight: 700; }
.avg { background: #fafbfb; font-weight: 600; }
</style>
