<template>
  <view class="qcard" :class="review ? 'r-' + (q.result || 'none') : ''">
    <view class="q-head">
      <text class="q-no">{{ t("quiz.question", { n: q.number }) }}</text>
      <text class="wq-muted">{{ t("quiz.type." + typeKey) }}</text>
      <text v-if="q.maxmark" class="wq-muted">· {{ t("quiz.marks", { n: q.maxmark }) }}</text>
      <text v-if="review" class="verdict" :class="q.result">{{ verdict }}</text>
    </view>
    <view class="q-text"><MathContent :html="q.text" /></view>

    <!-- choices -->
    <view v-if="q.kind === 'choice' || q.kind === 'multi'" class="opts">
      <view v-for="(o, i) in q.options" :key="o.name + o.value" class="opt"
        :class="{ on: isOn(o), right: review && o.result === 'correct', wrong: review && o.result === 'incorrect', ro: review }"
        @click="toggle(o)">
        <text class="mark" :class="q.kind">{{ isOn(o) ? (q.kind === "multi" ? "✓" : "●") : letter(i) }}</text>
        <view class="o-label">
          <MathContent v-if="q.type !== 'truefalse'" :html="o.label" />
          <text v-else>{{ t("quiz." + o.label) }}</text>
          <text v-if="review && o.feedback" class="o-fb">{{ strip(o.feedback) }}</text>
        </view>
      </view>
    </view>

    <!-- fill in / number -->
    <view v-else-if="q.kind === 'text'" class="fill">
      <input class="wq-input" :class="review ? q.result : ''" :type="q.numeric ? 'digit' : 'text'" :value="answer as string" :disabled="review"
        :placeholder="q.numeric ? t('quiz.numberHint') : t('quiz.textHint')" @input="(e: any) => emit('update', e.detail.value)" />
    </view>

    <view v-else class="unsupported">
      <MathContent :html="q.html || ''" />
      <text class="wq-muted block">{{ t("quiz.unsupported") }}</text>
    </view>

    <view v-if="review && (q.rightanswer || q.feedback)" class="explain">
      <view v-if="q.rightanswer && q.result !== 'correct'" class="right">
        <text class="e-k">{{ t("quiz.rightAnswer") }}</text>
        <text v-if="q.type === 'truefalse'">{{ t("quiz." + q.rightanswer) }}</text>
        <MathContent v-else :html="q.rightanswer" />
      </view>
      <view v-if="q.feedback" class="fb">
        <text class="e-k">{{ t("quiz.explanation") }}</text>
        <MathContent :html="q.feedback" />
      </view>
      <text v-if="q.mark !== null && q.mark !== undefined" class="wq-muted">{{ t("quiz.got", { n: Number(q.mark), m: q.maxmark || 0 }) }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import MathContent from "../MathContent.vue";
import type { QuizOption, QuizQuestion } from "../../courseApi";
import { t } from "../../i18n";

const props = defineProps<{ q: QuizQuestion; answer?: unknown; review?: boolean }>();
const emit = defineEmits<{ (e: "update", v: unknown): void }>();

const typeKey = computed(() => (props.q.type === "multichoice" ? (props.q.kind === "multi" ? "multi" : "single") : props.q.type));
const verdict = computed(() => t("quiz.result." + (props.q.result || "none")));
const letter = (i: number) => String.fromCharCode(65 + i);
const strip = (h: string) => h.replace(/<[^>]+>/g, "");

function isOn(o: QuizOption): boolean {
  if (props.review) return o.checked;
  if (props.q.kind === "multi") return Array.isArray(props.answer) && (props.answer as string[]).includes(o.name);
  return props.answer === o.value;
}
function toggle(o: QuizOption) {
  if (props.review) return;
  if (props.q.kind === "multi") {
    const cur = Array.isArray(props.answer) ? [...(props.answer as string[])] : [];
    emit("update", cur.includes(o.name) ? cur.filter((x) => x !== o.name) : [...cur, o.name]);
  } else {
    emit("update", o.value);
  }
}
</script>

<style scoped>
.qcard { background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; padding: 18px 22px; }
.qcard.r-correct { border-left: 5px solid var(--wq-ok); }
.qcard.r-incorrect { border-left: 5px solid var(--wq-danger); }
.qcard.r-partiallycorrect { border-left: 5px solid var(--wq-accent); }
.q-head { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
.q-no { font-weight: 800; color: var(--wq-ink); font-size: 16px; }
.verdict { margin-left: auto; font-weight: 700; }
.verdict.correct { color: var(--wq-ok); }
.verdict.incorrect { color: var(--wq-danger); }
.verdict.partiallycorrect { color: #9a6b00; }
.q-text { font-size: 16px; line-height: 1.8; color: var(--wq-ink); margin-bottom: 14px; }
.opts { display: flex; flex-direction: column; gap: 8px; }
.opt { display: flex; align-items: flex-start; gap: 12px; padding: 10px 14px; border: 1px solid var(--wq-line); border-radius: 8px; cursor: pointer; }
.opt:hover:not(.ro) { border-color: var(--wq-link); }
.opt.on { border-color: var(--wq-ink); background: #f3f6f7; }
.opt.right { border-color: var(--wq-ok); background: #eef8f2; }
.opt.wrong { border-color: var(--wq-danger); background: #fdf0ef; }
.opt.ro { cursor: default; }
.mark { width: 26px; height: 26px; border-radius: 50%; border: 1px solid var(--wq-line); display: inline-flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: var(--wq-muted); flex-shrink: 0; }
.mark.multi { border-radius: 6px; }
.opt.on .mark { background: var(--wq-ink); border-color: var(--wq-ink); color: #fff; }
.o-label { flex: 1; min-width: 0; padding-top: 2px; }
.o-fb { display: block; font-size: 13px; color: var(--wq-muted); margin-top: 4px; }
.fill { max-width: 420px; }
.fill .correct { border-color: var(--wq-ok); background: #eef8f2; }
.fill .incorrect { border-color: var(--wq-danger); background: #fdf0ef; }
.explain { margin-top: 14px; background: #f7f9fa; border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; gap: 8px; }
.e-k { display: block; font-size: 12px; color: var(--wq-muted); margin-bottom: 2px; }
.block { display: block; }
</style>
