<template>
  <!-- 第 49 轮：AI 助手。AI 起草，计算核心把关（红灯变多就退回），人点“采用”才回填参数。只给已开通的单位用。 -->
  <view class="ai" :class="{ open }">
    <view class="bar" @click="open = !open">
      <text class="bt">✦ {{ t("sew.ai.title") }}</text>
      <text class="muted small">{{ open ? "−" : t("sew.ai.hint") }}</text>
    </view>
    <view v-if="open" class="body">
      <view v-if="!licensed" class="note">{{ t("sew.ai.locked") }}</view>
      <template v-else>
        <textarea v-model="sentence" class="ta" maxlength="600" :placeholder="t('sew.ai.ph.' + machine)" auto-height />
        <view class="row">
          <view class="btn" :class="{ disabled: !!busy }" @click="draft">{{ busy === "draft" ? t("sew.ai.thinking") : t("sew.ai.draft") }}</view>
          <view class="btn ghost" :class="{ disabled: !!busy }" @click="explain">{{ busy === "explain" ? t("sew.ai.thinking") : t("sew.ai.explain") }}</view>
          <view class="btn ghost" :class="{ disabled: !!busy }" @click="describe">{{ busy === "describe" ? t("sew.ai.thinking") : t("sew.ai.describe") }}</view>
          <text v-if="left != null" class="muted small">{{ t("sew.ai.left", { n: left }) }}<text v-if="model"> · {{ model === "rules" ? t("sew.ai.rules") : model }}</text></text>
        </view>
        <text v-if="msg" class="err">{{ msg }}</text>

        <!-- 起草 -->
        <view v-if="D" class="res">
          <view class="verdict" :class="D.status">
            <text>{{ D.status === "ok" ? t("sew.ai.passed") : t("sew.ai.rejected") }}</text>
            <text class="small cnt">{{ t("sew.ai.counts", { b0: D.before.bad, w0: D.before.warn, b1: D.after.bad, w1: D.after.warn }) }}<text v-if="D.rounds > 1"> · {{ t("sew.ai.rounds") }}</text></text>
          </view>
          <view v-if="D.changes.length" class="tbl">
            <view class="tr th"><text class="td w2">{{ t("sew.ai.param") }}</text><text class="td">{{ t("sew.ai.old") }}</text><text class="td">{{ t("sew.ai.new") }}</text><text class="td w3">{{ t("sew.ai.why") }}</text></view>
            <view v-for="c in D.changes" :key="c.key" class="tr">
              <text class="td w2">{{ c.name }}<text class="muted"> {{ c.unit }}</text></text><text class="td">{{ c.old }}</text>
              <text class="td strong">{{ c.new }}</text><text class="td w3">{{ c.why }}<text v-if="c.note" class="warnc"> （{{ c.note }}）</text></text>
            </view>
          </view>
          <text v-else class="hint">{{ t("sew.ai.noChange") }}</text>
          <view v-if="D.status !== 'ok' && D.new_bad.length" class="hint badc">{{ t("sew.ai.newBad") }}{{ D.new_bad.map((x: any) => x.name).join("、") }}</view>
          <text v-for="(a, i) in D.assumptions" :key="'a' + i" class="hint">· {{ a }}</text>
          <text v-for="(q, i) in D.questions" :key="'q' + i" class="hint warnc">？{{ q }}</text>
          <view v-if="D.status === 'ok' && D.changes.length" class="btn" @click="adopt(only(D.changes))">{{ t("sew.ai.adopt") }}</view>
        </view>

        <!-- 解释红黄灯 -->
        <view v-if="E" class="res">
          <text v-if="E.all_ok" class="hint okc">{{ t("sew.ai.allOk") }}</text>
          <view v-for="it in E.items" :key="it.check" class="item">
            <text class="lamp" :class="it.state" /><text class="strong">{{ it.name }}</text>
            <text class="muted small"> {{ it.value }} · {{ t("sew.criterion") }} {{ it.limit }}</text>
            <text class="para">{{ it.why }}</text>
            <view v-for="(f, j) in it.fixes" :key="j" class="fix">
              <text class="para">→ {{ f.name }} {{ f.old }} → <text class="strong">{{ f.new }}</text> {{ f.unit }}：{{ f.how }}</text>
              <text class="small" :class="f.clears && f.params ? 'okc' : 'badc'">{{ f.clears ? (f.params ? t("sew.ai.clears") : t("sew.ai.clearsBut", { n: f.new_bad.join("、") })) : t("sew.ai.notClears") }}</text>
              <text v-if="f.params" class="link" @click="adopt(only([f]))">{{ t("sew.ai.adopt") }}</text>
            </view>
          </view>
        </view>

        <!-- 设计说明 -->
        <view v-if="S" class="res">
          <text class="para">{{ S.sentences.join("") }}</text>
          <text v-if="S.dropped.length" class="hint warnc">{{ t("sew.ai.dropped", { n: S.dropped.length }) }}</text>
          <view v-if="S.sentences.length" class="btn ghost inl" @click="emit('desc', S.sentences)">{{ t("sew.ai.toReport") }}</view>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { ApiError, request } from "../../api";
import { errorText, t } from "../../i18n";

const props = defineProps<{ machine: string; params: Record<string, number | string>; licensed: boolean }>();
const emit = defineEmits<{ (e: "apply", p: Record<string, number | string>): void; (e: "desc", s: string[]): void }>();
const open = ref(false);
const sentence = ref("");
const busy = ref("");
const msg = ref("");
const left = ref<number | null>(null);
const model = ref("");
const D = ref<any>(null);
const E = ref<any>(null);
const S = ref<any>(null);
watch(() => props.machine, () => { D.value = E.value = S.value = null; msg.value = ""; });

async function call(kind: string) {
  if (busy.value) return null;
  busy.value = kind;
  msg.value = "";
  try {
    const r = await request<any>("POST", `/api/v1/sewing/ai/${kind}`, { machine: props.machine, params: { ...props.params }, sentence: sentence.value });
    if (r.left_today != null) left.value = r.left_today;
    model.value = r.model || "";
    return r;
  } catch (e) {
    msg.value = errorText(e instanceof ApiError ? e.code : "unknown");
    return null;
  } finally {
    busy.value = "";
  }
}
async function draft() {
  if (sentence.value.trim().length < 2) return (msg.value = t("sew.ai.writeFirst"));
  const r = await call("draft");
  if (r) { D.value = r; E.value = S.value = null; }
}
async function explain() {
  const r = await call("explain");
  if (r) { E.value = r; D.value = S.value = null; }
}
async function describe() {
  const r = await call("describe");
  if (r) { S.value = r; D.value = E.value = null; }
}
// 只回填改了的那几个参数
const only = (rows: { key: string; new: number | string; note?: string }[]) =>
  Object.fromEntries(rows.filter((r) => r.note !== "不是可选的值，没改").map((r) => [r.key, r.new])) as Record<string, number | string>;
function adopt(p: Record<string, number | string>) {
  emit("apply", p);
  D.value = E.value = null;
}
defineExpose({ open });
</script>

<style scoped>
.ai { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; margin-bottom: 8px; }
.ai.open { border-color: #b9cfe4; }
.bar { display: flex; justify-content: space-between; align-items: center; padding: 9px 14px; cursor: pointer; }
.bt { font-weight: 700; color: #1d4e75; font-size: 14px; }
.body { padding: 0 14px 12px; }
.ta { width: 100%; box-sizing: border-box; min-height: 52px; border: 1px solid var(--wq-line); border-radius: 6px; padding: 8px; font-size: 14px; line-height: 1.6; background: #fff; }
.row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 8px; }
.btn { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.btn.ghost { background: #fff; border: 1px solid var(--wq-line); }
.btn.disabled { opacity: .5; }
.btn.inl { display: inline-block; margin-top: 8px; }
.res { margin-top: 10px; border-top: 1px dashed var(--wq-line); padding-top: 10px; }
.verdict { padding: 6px 10px; border-radius: 6px; font-weight: 600; font-size: 14px; margin-bottom: 8px; }
.cnt { display: block; font-weight: 400; margin-top: 2px; }
.verdict.ok { background: #e6f4ea; color: #2e7d4f; }
.verdict.rejected { background: #fdecea; color: var(--wq-danger); }
.tbl { border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; font-size: 13px; margin-bottom: 8px; }
.tr { display: flex; border-top: 1px solid var(--wq-line); }
.tr:first-child { border-top: 0; }
.th { background: #eaf2fa; font-weight: 600; }
.td { flex: 1; padding: 5px 8px; min-width: 0; }
.w2 { flex: 2; } .w3 { flex: 3; }
.item { padding: 8px 0; border-top: 1px solid var(--wq-line); }
.item:first-child { border-top: 0; }
.fix { padding: 4px 0 4px 14px; display: flex; flex-wrap: wrap; gap: 6px; align-items: baseline; }
.lamp { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; background: #2e9e6a; }
.lamp.warn { background: #e8913a; } .lamp.bad { background: #c0392b; }
.para { display: block; font-size: 13px; line-height: 1.7; }
.hint { display: block; font-size: 13px; color: var(--wq-muted); line-height: 1.6; margin-top: 4px; }
.note { background: #fff3d6; color: #7a5a00; padding: 10px 12px; border-radius: 8px; font-size: 13px; line-height: 1.6; }
.err { display: block; color: var(--wq-danger); font-size: 13px; margin-top: 6px; }
.muted { color: var(--wq-muted); } .small { font-size: 12px; } .strong { font-weight: 600; }
.okc { color: #2e7d4f; } .badc { color: var(--wq-danger); } .warnc { color: #8a4b00; }
.link { color: var(--wq-link); font-size: 13px; cursor: pointer; }
</style>
