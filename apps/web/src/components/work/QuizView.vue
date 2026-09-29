<template>
  <view>
    <text v-if="loading && !q" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error && !q" class="wq-error">{{ errorText(error) }}</text>
    <template v-else-if="q">
      <view class="facts">
        <view class="fact"><text class="f-k">{{ t("quiz.limit") }}</text><text class="f-v">{{ q.timelimit ? t("quiz.minutes", { n: Math.round(q.timelimit / 60) }) : t("quiz.noLimit") }}</text></view>
        <view class="fact"><text class="f-k">{{ t("quiz.attemptsAllowed") }}</text><text class="f-v">{{ q.attempts_allowed || t("quiz.unlimited") }}</text></view>
        <view class="fact"><text class="f-k">{{ t("work.points") }}</text><text class="f-v">{{ q.max_grade }}</text></view>
        <view v-if="q.closes" class="fact"><text class="f-k">{{ t("quiz.closes") }}</text><text class="f-v">{{ formatDate(q.closes) }}</text></view>
        <view v-if="q.opens && q.opens * 1000 > Date.now()" class="fact"><text class="f-k">{{ t("quiz.opens") }}</text><text class="f-v">{{ formatDate(q.opens) }}</text></view>
      </view>
      <view v-if="q.intro" class="paper"><MathContent :html="q.intro" /></view>

      <view v-if="q.best !== null" class="wq-card best">
        <text class="wq-muted">{{ t("quiz.best") }}</text>
        <text class="b-num">{{ q.best }} / {{ q.max_grade }}</text>
      </view>

      <view v-if="q.attempts.length" class="attempts">
        <view v-for="x in q.attempts" :key="x.id" class="att">
          <text class="a-no">{{ t("quiz.attemptNo", { n: x.number }) }}</text>
          <text class="wq-muted">{{ formatDate(x.start) }}</text>
          <text class="wq-tag" :class="x.state === 'finished' ? 'ok' : 'accent'">{{ t("quiz.state." + x.state) }}</text>
          <text class="a-grade">{{ x.grade !== null ? `${x.grade} / ${q.max_grade}` : "" }}</text>
          <text v-if="x.state === 'finished'" class="wq-link" @click="review(x.id)">{{ t("quiz.review") }} ›</text>
          <text v-else class="wq-link" @click="go(x.id)">{{ t("quiz.continue") }} ›</text>
        </view>
      </view>

      <view v-if="!q.questions" class="wq-empty">{{ t("quiz.noQuestions") }}</view>
      <view v-else-if="unfinished" class="wq-row"><view class="wq-btn primary" @click="go(unfinished.id)">{{ t("quiz.continue") }}</view></view>
      <view v-else-if="q.can_attempt" class="wq-row start">
        <view class="wq-btn primary" :class="{ disabled: starting }" @click="start">{{ q.attempts.length ? t("quiz.again") : t("quiz.start") }}</view>
        <text v-if="q.timelimit" class="wq-muted">{{ t("quiz.timerNote", { n: Math.round(q.timelimit / 60) }) }}</text>
      </view>
      <view v-else-if="q.blocked.length" class="wq-card blocked">
        <text v-for="b in q.blocked" :key="b" class="wq-muted block">{{ b }}</text>
      </view>
      <text v-if="q.teacher" class="wq-muted block teacher">{{ t("quiz.teacherNote") }}</text>
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import MathContent from "../MathContent.vue";
import { ApiError } from "../../api";
import { type QuizInfo, workApi } from "../../courseApi";
import { errorText, formatDate, t } from "../../i18n";

const props = defineProps<{ cmid: number; courseId: number }>();
const q = ref<QuizInfo | null>(null);
const loading = ref(true);
const error = ref("");
const starting = ref(false);
const unfinished = computed(() => q.value?.attempts.find((x) => x.state === "inprogress" || x.state === "overdue") || null);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    q.value = await workApi.quiz(props.cmid);
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}
async function start() {
  starting.value = true;
  try {
    const r = await workApi.startAttempt(props.cmid);
    go(r.attempt);
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  } finally {
    starting.value = false;
  }
}
const go = (aid: number) => uni.navigateTo({ url: `/pages/quiz/attempt?id=${aid}&course=${props.courseId}` });
const review = (aid: number) => uni.navigateTo({ url: `/pages/quiz/attempt?id=${aid}&course=${props.courseId}&review=1` });

onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.facts { display: flex; flex-wrap: wrap; background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; margin-bottom: 14px; }
.fact { flex: 1; min-width: 130px; padding: 10px 16px; border-left: 1px solid var(--wq-line); display: flex; flex-direction: column; }
.fact:first-child { border-left: 0; }
.f-k { font-size: 12px; color: var(--wq-muted); }
.f-v { font-weight: 600; color: var(--wq-ink); }
.paper { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 18px 22px; margin-bottom: 14px; line-height: 1.8; }
.best { display: flex; align-items: baseline; gap: 12px; border-left: 4px solid var(--wq-ok); }
.b-num { font-size: 24px; font-weight: 800; color: var(--wq-ok); font-family: "IBM Plex Mono", Menlo, monospace; }
.attempts { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; margin-bottom: 14px; }
.att { display: flex; align-items: center; gap: 12px; padding: 10px 16px; border-top: 1px solid var(--wq-line); flex-wrap: wrap; }
.att:first-child { border-top: 0; }
.a-no { font-weight: 600; color: var(--wq-ink); }
.a-grade { flex: 1; text-align: right; font-family: "IBM Plex Mono", Menlo, monospace; }
.start { margin-top: 4px; }
.block { display: block; }
.teacher { margin-top: 14px; }
</style>
