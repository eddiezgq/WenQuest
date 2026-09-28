<template>
  <view class="page">
    <TopBar />
    <view class="wrap">
      <view class="back" @click="leave">‹ {{ t("nav.courses") }}</view>
      <text class="h1">{{ t("create.title") }}</text>

      <!-- steps -->
      <view class="steps">
        <view v-for="(label, i) in stepLabels" :key="i" class="step" :class="{ on: step === i + 1, done: step > i + 1 }">
          <text class="num">{{ step > i + 1 ? "✓" : i + 1 }}</text>
          <text class="label">{{ label }}</text>
        </view>
      </view>

      <view v-if="error" class="alert" role="alert">{{ errorText(error) }}</view>

      <!-- 1. brief -->
      <view v-if="step === 1" class="card">
        <view class="field">
          <text class="lbl">{{ t("create.topic") }} *</text>
          <input class="input" v-model="brief.topic" :placeholder="t('create.topicHint')" />
        </view>
        <view class="field">
          <text class="lbl">{{ t("create.audience") }}</text>
          <input class="input" v-model="brief.audience" :placeholder="t('create.audienceHint')" />
        </view>
        <view class="row">
          <view class="field grow">
            <text class="lbl">{{ t("create.level") }}</text>
            <view class="chips">
              <view v-for="lv in levels" :key="lv" class="chip" :class="{ sel: brief.level === t('create.level.' + lv) }"
                    @click="brief.level = t('create.level.' + lv)">{{ t("create.level." + lv) }}</view>
            </view>
          </view>
          <view class="field grow">
            <text class="lbl">{{ t("create.languages") }}</text>
            <view class="chips">
              <view v-for="lg in langs" :key="lg" class="chip" :class="{ sel: brief.languages === lg }"
                    @click="brief.languages = lg">{{ t("create.lang." + lg) }}</view>
            </view>
          </view>
        </view>
        <view class="row">
          <view class="field">
            <text class="lbl">{{ t("create.sections") }}</text>
            <view class="stepper">
              <view class="sb" @click="brief.sections = Math.max(1, brief.sections - 1)">−</view>
              <text class="sv">{{ brief.sections }}</text>
              <view class="sb" @click="brief.sections = Math.min(12, brief.sections + 1)">＋</view>
            </view>
          </view>
          <view class="field">
            <text class="lbl">{{ t("create.lessons") }}</text>
            <view class="stepper">
              <view class="sb" @click="brief.lessons_per_section = Math.max(1, brief.lessons_per_section - 1)">−</view>
              <text class="sv">{{ brief.lessons_per_section }}</text>
              <view class="sb" @click="brief.lessons_per_section = Math.min(5, brief.lessons_per_section + 1)">＋</view>
            </view>
          </view>
          <view class="field">
            <text class="lbl">{{ t("create.assignments") }}</text>
            <switch :checked="brief.assignments" color="#f2b705" @change="(e: any) => (brief.assignments = e.detail.value)" />
          </view>
        </view>
        <view class="field">
          <text class="lbl">{{ t("create.notes") }}</text>
          <textarea class="area" v-model="brief.notes" :maxlength="30000" :placeholder="t('create.notesHint')" />
        </view>
        <view class="actions">
          <view class="primary" :class="{ disabled: busy || brief.topic.trim().length < 2 }" @click="makeOutline">
            {{ busy ? t("create.thinking") : "✨ " + t("create.makeOutline") }}
          </view>
        </view>
      </view>

      <!-- 2. outline -->
      <view v-if="step === 2 && outline" class="card">
        <view class="field">
          <text class="lbl">{{ t("create.courseTitle") }}</text>
          <view v-for="k in keys" :key="'t' + k" class="lang-line">
            <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
            <input class="input" v-model="outline.title[k]" />
          </view>
        </view>
        <view class="field">
          <text class="lbl">{{ t("create.summary") }}</text>
          <view v-for="k in keys" :key="'s' + k" class="lang-line">
            <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
            <textarea class="area small" v-model="outline.summary[k]" :maxlength="2000" />
          </view>
        </view>

        <view v-for="(sec, si) in outline.sections" :key="si" class="sec">
          <view class="sec-head">
            <text class="sec-no">{{ si + 1 }}</text>
            <view class="grow">
              <view v-for="k in keys" :key="'st' + k" class="lang-line">
                <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
                <input class="input strong" v-model="sec.title[k]" />
              </view>
            </view>
            <text class="link danger" @click="outline.sections.splice(si, 1)">{{ t("create.remove") }}</text>
          </view>
          <view v-for="(les, li) in sec.lessons" :key="li" class="lesson">
            <text class="dot">•</text>
            <view class="grow">
              <view v-for="k in keys" :key="'lt' + k" class="lang-line">
                <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
                <input class="input" v-model="les.title[k]" />
              </view>
              <text v-if="les.goal && disp(les.goal)" class="goal">{{ disp(les.goal) }}</text>
            </view>
            <text class="link danger" @click="sec.lessons.splice(li, 1)">✕</text>
          </view>
          <text class="link" @click="addLesson(sec)">{{ t("create.addLesson") }}</text>
          <view v-if="sec.assignment" class="assign">
            <text class="lbl">✎ {{ t("create.assignment") }}</text>
            <view v-for="k in keys" :key="'at' + k" class="lang-line">
              <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
              <input class="input" v-model="sec.assignment.title[k]" />
            </view>
            <view v-for="k in keys" :key="'ab' + k" class="lang-line">
              <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
              <textarea class="area small" v-model="sec.assignment.brief[k]" :maxlength="3000" />
            </view>
          </view>
        </view>

        <view class="actions">
          <view class="ghost" @click="step = 1">{{ t("create.back") }}</view>
          <view class="ghost" :class="{ disabled: busy }" @click="makeOutline">{{ busy ? t("create.thinking") : t("create.regenOutline") }}</view>
          <view class="primary" :class="{ disabled: !lessonCount }" @click="writeAll">✨ {{ t("create.writeAll") }}</view>
        </view>
      </view>

      <!-- 3. writing -->
      <view v-if="step === 3 && outline" class="card">
        <text class="progress-text">{{ t("create.writing", { done: doneCount, total: lessonCount }) }}</text>
        <view class="bar"><view class="fill" :style="{ width: (lessonCount ? (doneCount / lessonCount) * 100 : 0) + '%' }" /></view>
        <view v-for="(sec, si) in outline.sections" :key="si" class="w-sec">
          <text class="w-sec-title">{{ disp(sec.title) }}</text>
          <view v-for="(les, li) in sec.lessons" :key="li" class="w-row">
            <text class="w-name">{{ disp(les.title) }}</text>
            <text class="w-status" :class="status[key(si, li)] || 'wait'">{{ t("create.status." + (status[key(si, li)] || "wait")) }}</text>
            <text v-if="status[key(si, li)] === 'fail'" class="link" @click="writeOne(si, li)">{{ t("create.retry") }}</text>
          </view>
        </view>
        <view class="actions">
          <view class="ghost" @click="step = 2">{{ t("create.back") }}</view>
          <view class="primary" :class="{ disabled: doneCount < lessonCount }" @click="step = 4">{{ t("create.preview") }} →</view>
        </view>
      </view>

      <!-- 4. review and publish -->
      <view v-if="step === 4 && outline" class="card">
        <text class="course-title">{{ disp(outline.title) }}</text>
        <text class="course-summary">{{ disp(outline.summary) }}</text>
        <view v-for="(sec, si) in outline.sections" :key="si" class="r-sec">
          <text class="w-sec-title">{{ disp(sec.title) }}</text>
          <view v-for="(les, li) in sec.lessons" :key="li" class="r-lesson">
            <view class="r-head" @click="toggle(key(si, li))">
              <text class="r-arrow">{{ open[key(si, li)] ? "▾" : "▸" }}</text>
              <text class="w-name">{{ disp(les.title) }}</text>
              <text class="link" @click.stop="writeOne(si, li)">
                {{ status[key(si, li)] === "busy" ? t("create.status.busy") : t("create.rewrite") }}
              </text>
            </view>
            <view v-if="open[key(si, li)]" class="r-body"><RichContent :html="disp(les.content)" /></view>
          </view>
          <view v-if="sec.assignment" class="r-assign">✎ {{ disp(sec.assignment.title) }}</view>
        </view>
        <view class="actions">
          <view class="ghost" @click="step = 2">{{ t("create.back") }}</view>
          <view class="primary" :class="{ disabled: busy }" @click="publish">
            {{ busy ? t("create.publishing") : t("create.publish") }}
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import TopBar from "../../components/TopBar.vue";
import RichContent from "../../components/RichContent.vue";
import { api, ApiError, type Brief, type Outline, type OutlineSection, type Text, token, user } from "../../api";
import { errorText, locale, t } from "../../i18n";

const step = ref(1);
const busy = ref(false);
const error = ref("");
const outline = ref<Outline | null>(null);
const status = reactive<Record<string, "wait" | "busy" | "done" | "fail">>({});
const open = reactive<Record<string, boolean>>({});

const levels = ["intro", "mid", "adv"];
const langs = ["zh", "en", "both"] as const;
const stepLabels = computed(() => [t("create.step1"), t("create.step2"), t("create.step3"), t("create.step4")]);

const brief = reactive<Brief>({
  topic: "",
  audience: "",
  level: "",
  sections: 4,
  lessons_per_section: 2,
  assignments: true,
  languages: locale.value === "zh" ? "zh" : "en",
  notes: "",
});

const keys = computed<("zh" | "en")[]>(() =>
  outline.value?.languages === "both" ? ["zh", "en"] : [(outline.value?.languages as "zh" | "en") || "zh"],
);
const key = (si: number, li: number) => `${si}-${li}`;
const disp = (tx?: Text) => (tx ? tx[locale.value] || tx.zh || tx.en || "" : "");
const lessonCount = computed(() => outline.value?.sections.reduce((n, s) => n + s.lessons.length, 0) || 0);
const doneCount = computed(() => {
  let n = 0;
  outline.value?.sections.forEach((s, si) => s.lessons.forEach((_, li) => status[key(si, li)] === "done" && n++));
  return n;
});

function fail(e: unknown) {
  error.value = e instanceof ApiError ? e.code : "unknown";
}

async function makeOutline() {
  if (busy.value || brief.topic.trim().length < 2) return;
  busy.value = true;
  error.value = "";
  try {
    outline.value = await api.aiOutline({ ...brief, topic: brief.topic.trim() });
    Object.keys(status).forEach((k) => delete status[k]);
    step.value = 2;
  } catch (e) {
    fail(e);
  } finally {
    busy.value = false;
  }
}

function addLesson(sec: OutlineSection) {
  const empty = () => Object.fromEntries(keys.value.map((k) => [k, ""])) as Text;
  sec.lessons.push({ title: empty(), goal: empty(), content: empty() });
}

async function writeOne(si: number, li: number) {
  const o = outline.value;
  if (!o) return;
  const sec = o.sections[si];
  const les = sec.lessons[li];
  const k = key(si, li);
  if (status[k] === "busy") return;
  status[k] = "busy";
  try {
    const r = await api.aiLesson({
      course_title: disp(o.title),
      section_title: disp(sec.title),
      lesson_title: disp(les.title),
      goal: disp(les.goal),
      audience: brief.audience,
      level: brief.level,
      languages: o.languages,
      notes: brief.notes,
    });
    les.content = r.content;
    status[k] = "done";
  } catch (e) {
    status[k] = "fail";
    fail(e);
  }
}

async function writeAll() {
  const o = outline.value;
  if (!o || !lessonCount.value) return;
  error.value = "";
  step.value = 3;
  const jobs: [number, number][] = [];
  o.sections.forEach((s, si) => s.lessons.forEach((_, li) => status[key(si, li)] !== "done" && jobs.push([si, li])));
  // Three at a time: fast enough, and gentle on the model's rate limits.
  const worker = async () => {
    while (jobs.length) {
      const [si, li] = jobs.shift()!;
      await writeOne(si, li);
    }
  };
  await Promise.all([worker(), worker(), worker()]);
  if (doneCount.value === lessonCount.value) step.value = 4;
}

function toggle(k: string) {
  open[k] = !open[k];
}

async function publish() {
  const o = outline.value;
  if (!o || busy.value) return;
  if (doneCount.value < lessonCount.value) {
    error.value = "";
    uni.showToast({ title: t("create.needAll"), icon: "none" });
    return;
  }
  busy.value = true;
  error.value = "";
  try {
    const r = await api.publish(o);
    uni.showToast({ title: t("create.published"), icon: "success" });
    setTimeout(() => uni.reLaunch({ url: `/pages/course/course?id=${r.course_id}` }), 800);
  } catch (e) {
    fail(e);
  } finally {
    busy.value = false;
  }
}

function leave() {
  uni.reLaunch({ url: "/pages/courses/courses" });
}

onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t("create.title") });
  if (user.value && user.value.can_create_courses === false) error.value = "forbidden";
});
</script>

<style scoped>
.page { min-height: 100vh; background: var(--wq-bg); }
.wrap { max-width: 860px; margin: 0 auto; padding: 16px 16px 64px; }
.back { color: var(--wq-link); font-size: 14px; cursor: pointer; margin-bottom: 8px; display: inline-block; }
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); margin-bottom: 16px; }
.steps { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.step { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; background: #e8ecea; color: var(--wq-muted); font-size: 13px; }
.step.on { background: var(--wq-ink); color: #fff; }
.step.done { background: #dcefe5; color: var(--wq-ok); }
.num { font-weight: 700; }
.alert { background: #fdecea; color: var(--wq-danger); padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; font-size: 14px; }
.card { background: #fff; border: 1px solid var(--wq-line); border-radius: 12px; padding: 20px 18px; }
.field { display: flex; flex-direction: column; margin-bottom: 16px; }
.row { display: flex; gap: 20px; flex-wrap: wrap; }
.grow { flex: 1; min-width: 0; }
.lbl { font-size: 14px; color: var(--wq-text); margin-bottom: 6px; font-weight: 600; }
.input { height: 40px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 0 10px; font-size: 15px; background: #fafbfa; flex: 1; }
.input.strong { font-weight: 600; }
.area { width: 100%; min-height: 120px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 10px; font-size: 14px; background: #fafbfa; box-sizing: border-box; }
.area.small { min-height: 60px; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { padding: 6px 14px; border-radius: 999px; border: 1px solid var(--wq-line); font-size: 14px; cursor: pointer; background: #fff; }
.chip.sel { background: var(--wq-ink); color: #fff; border-color: var(--wq-ink); }
.stepper { display: flex; align-items: center; gap: 10px; }
.sb { width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--wq-line); display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 18px; }
.sv { min-width: 24px; text-align: center; font-size: 16px; font-weight: 600; }
.actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; flex-wrap: wrap; }
.primary { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 10px 20px; border-radius: 8px; cursor: pointer; text-align: center; }
.ghost { border: 1px solid var(--wq-line); padding: 10px 18px; border-radius: 8px; cursor: pointer; color: var(--wq-ink); background: #fff; }
.disabled { opacity: 0.5; pointer-events: none; }
.lang-line { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.tag { font-size: 11px; font-weight: 700; color: var(--wq-muted); width: 22px; flex-shrink: 0; }
.sec { border-top: 1px solid var(--wq-line); padding-top: 14px; margin-top: 14px; }
.sec-head { display: flex; gap: 10px; align-items: flex-start; }
.sec-no { width: 28px; height: 28px; border-radius: 8px; background: var(--wq-ink); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0; margin-top: 6px; }
.lesson { display: flex; gap: 8px; align-items: flex-start; margin: 6px 0 6px 38px; }
.dot { color: var(--wq-muted); margin-top: 10px; }
.goal { display: block; font-size: 12px; color: var(--wq-muted); margin: -2px 0 4px; }
.link { color: var(--wq-link); font-size: 13px; cursor: pointer; margin-left: 38px; flex-shrink: 0; }
.lesson .link, .sec-head .link, .w-row .link, .r-head .link { margin-left: 0; margin-top: 10px; }
.link.danger { color: var(--wq-danger); }
.assign { margin: 10px 0 0 38px; padding: 10px 12px; background: #fff8e0; border-radius: 8px; }
.progress-text { display: block; font-size: 15px; color: var(--wq-ink); margin-bottom: 8px; }
.bar { height: 8px; background: #e8ecea; border-radius: 4px; overflow: hidden; margin-bottom: 16px; }
.fill { height: 100%; background: var(--wq-accent); transition: width .3s ease; }
.w-sec, .r-sec { margin-bottom: 14px; }
.w-sec-title { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 6px; }
.w-row { display: flex; align-items: center; gap: 10px; padding: 6px 0 6px 12px; border-bottom: 1px solid #f0f2f1; }
.w-name { flex: 1; font-size: 14px; color: var(--wq-text); }
.w-status { font-size: 12px; color: var(--wq-muted); }
.w-status.busy { color: #7a5a00; }
.w-status.done { color: var(--wq-ok); }
.w-status.fail { color: var(--wq-danger); }
.course-title { display: block; font-size: 22px; font-weight: 700; color: var(--wq-ink); }
.course-summary { display: block; font-size: 14px; color: var(--wq-muted); margin: 6px 0 16px; }
.r-lesson { border: 1px solid var(--wq-line); border-radius: 8px; margin: 6px 0; }
.r-head { display: flex; align-items: center; gap: 8px; padding: 8px 12px; cursor: pointer; }
.r-head .link { margin-top: 0; }
.r-arrow { color: var(--wq-muted); width: 12px; }
.r-body { padding: 4px 16px 12px; border-top: 1px solid #f0f2f1; }
.r-assign { font-size: 14px; color: #7a5a00; padding: 6px 12px; }
</style>
