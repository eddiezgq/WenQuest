<template>
  <!-- 第 62 轮：电控箱的热与流体。公式当场算（教材第 18 章：损耗 → 热阻网络 → 间歇负载 → 结温、电容寿命、开关时间折中），
       电流取本机的设计；“CAE 复核”交给数字工厂：流体（自然对流 / 风扇）算外壳每个面的散热系数 → 温度场 → 箱子到车间的热阻，代回公式。 -->
  <view class="ebox">
    <text class="bt">{{ t("sew.ebox.title") }}</text>
    <text class="hint">{{ t("sew.ebox.lead") }}</text>

    <view v-if="R" class="drv">
      <view class="tbl">
        <view class="tr th"><text class="td">{{ t("sew.ebox.drive") }}</text><text class="td">{{ t("sew.ebox.irun") }}</text>
          <text class="td">{{ t("sew.ebox.ipk") }}</text><text class="td">{{ t("sew.ebox.loss") }}</text><text class="td">{{ t("sew.ebox.tj") }}</text></view>
        <view v-for="d in R.drives" :key="d.key" class="tr">
          <text class="td">{{ L(d) }}<text class="muted small"> · {{ d.src === "design" ? t("sew.ebox.fromDesign") : t("sew.ebox.manual") }}</text></text>
          <text class="td">{{ n2(d.Irun) }} A</text><text class="td">{{ n2(d.Ipk) }} A</text>
          <text class="td">{{ n1(d.Pavg) }} W</text><text class="td">{{ n1(d.Tjpk) }} °C</text>
        </view>
      </view>
      <view class="kgrid">
        <view v-for="r in R.results" :key="r.zh" class="kc"><text class="kl">{{ L(r) }}</text><text class="kv">{{ r.value }} {{ unit(r.unit) }}</text></view>
      </view>
      <view v-for="c in R.checks" :key="c.key" class="chk">
        <text class="lamp" :class="c.state" />
        <view class="cbody"><view class="crow"><text class="cname">{{ L(c.name) }}</text><text class="cst" :class="c.state">{{ t("sew.state." + c.state) }}</text></view>
          <text class="cval">{{ L(c.value) }}<text class="muted">　{{ t("sew.criterion") }} {{ L(c.limit) }}</text></text>
          <text v-if="c.state !== 'ok'" class="cval muted">{{ L(c.advice) }}</text></view>
      </view>
      <view class="charts">
        <view v-for="c in R.charts" :key="c.key" class="chart">
          <text class="ctt">{{ L(c) }}</text>
          <svg class="svg" viewBox="0 0 300 150" v-html="line(c)" />
          <view class="legend"><text v-for="s in c.series" :key="s.zh" class="lg"><text class="sw" :style="{ background: s.color }" />{{ L(s) }}</text></view>
        </view>
      </view>
      <text class="st">{{ L(R.variants) }}</text>
      <view class="tbl">
        <view class="tr th"><text v-for="(h, i) in R.variants.cols" :key="i" class="td" :class="{ w2: i === 0 }" v-show="i !== 1">{{ lang === "en" ? h[1] : h[0] }}</text></view>
        <view v-for="(r, i) in R.variants.rows" :key="i" class="tr">
          <text v-for="(v, k) in r" :key="k" class="td" :class="{ w2: k === 0, badc: (k === 6 && v !== '0'), warnc: (k === 7 && v !== '0') }" v-show="k !== 1">
            {{ k === 0 ? (lang === "en" ? r[1] : r[0]) : v }}</text>
        </view>
      </view>
    </view>

    <!-- AI：一句话改电控箱参数（计算核心重算，人点“采用”） -->
    <view class="ai">
      <input class="ainp" :value="say" :placeholder="t('sew.ebox.aiPh')" maxlength="300" @input="(e: any) => (say = e.detail.value)" @confirm="draft" />
      <view class="btn ghost" :class="{ disabled: !say.trim() || aiBusy }" @click="draft">{{ aiBusy ? t("sew.making") : t("sew.ebox.aiGo") }}</view>
    </view>
    <view v-if="ai" class="aires">
      <text v-for="r in ai.changes" :key="r.key" class="para">{{ r.name }}：{{ r.old }} → <text class="strong">{{ r.new }}</text> {{ r.unit }}<text class="muted">　{{ r.why }}</text></text>
      <text v-for="(q, i) in ai.questions" :key="'q' + i" class="para muted">{{ q }}</text>
      <text v-if="ai.after_bad.length" class="para badc">{{ t("sew.ebox.aiBad", { n: ai.after_bad.length }) }}{{ ai.after_bad.map((x: any) => x.name).join("、") }}</text>
      <view v-if="ai.params" class="btn sm" @click="adopt">{{ t("sew.ebox.adopt") }}</view>
    </view>

    <!-- 参数 -->
    <view v-for="g in schema" :key="g.key" class="grp">
      <view class="gt" @click="open[g.key] = !open[g.key]"><text>{{ L(g) }}</text><text class="muted">{{ open[g.key] ? "−" : "+" }}</text></view>
      <view v-if="open[g.key]">
        <view v-for="p in g.params" :key="p.key" class="prm" v-show="visible(p.key)">
          <text class="pl">{{ L(p) }}<text v-if="p.unit" class="muted"> · {{ p.unit }}</text></text>
          <view v-if="p.choices.length" class="row">
            <text v-for="c in p.choices" :key="c.key" class="opt" :class="{ on: ep[p.key] === c.key }" @click="setv(p.key, c.key)">{{ L(c) }}</text>
          </view>
          <view v-else class="row">
            <input class="inp" type="digit" :value="String(ep[p.key])" @change="(e: any) => setv(p.key, Number(e.detail.value))" />
            <text class="muted small">{{ p.min }}–{{ p.max }}</text>
          </view>
        </view>
      </view>
    </view>
    <view class="row">
      <text class="link" @click="reset">{{ t("sew.ebox.reset") }}</text>
      <text class="link" @click="caseSix">{{ t("sew.ebox.summer") }}</text>
    </view>

    <!-- CAE 复核 -->
    <view class="cae">
      <text class="st">{{ t("sew.ebox.caeTitle") }}</text>
      <text class="hint">{{ ep.air === "fan" ? t("sew.ebox.caeFan") : t("sew.ebox.caeNatural") }}</text>
      <text class="hint">{{ t("sew.ebox.ownNote") }}</text>
      <view class="row">
        <view class="btn" :class="{ disabled: !canRun }" @click="runCae">{{ busy ? t("sew.making") : t("sew.ebox.runCae") }}</view>
        <!-- #ifdef H5 -->
        <view class="btn ghost" :class="{ disabled: !canRun }" @click="stepFile">{{ t("sew.ebox.step") }}</view>
        <view class="btn ghost" :class="{ disabled: !canRun }" @click="uploadOwn">{{ t("sew.ebox.own") }}</view>
        <!-- #endif -->
      </view>
    </view>
    <text v-if="msg" class="hint err">{{ msg }}</text>
  </view>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { ApiError, BASE, request, token } from "../../api";
import { errorText, locale, t } from "../../i18n";

const props = defineProps<{ machine: string; params: Record<string, number | string>; canRun: boolean; active: boolean }>();
const emit = defineEmits<{ (e: "submitted", jid: string): void; (e: "change", p: Record<string, number | string>): void }>();

interface Choice { key: string; zh: string; en: string }
interface Param { key: string; zh: string; en: string; unit: string; default: number | string; min: number; max: number; step: number; choices: Choice[] }
interface Group { key: string; zh: string; en: string; params: Param[] }
interface Chart { key: string; zh: string; en: string; x: number[]; series: { zh: string; en: string; color: string; y: number[] }[];
  ref?: number | null; zero?: boolean; xr?: [number, number]; xl?: { zh: string; en: string } }

const schema = ref<Group[]>([]);
const defaults = ref<Record<string, number | string>>({});
const ep = reactive<Record<string, number | string>>({});
const open = reactive<Record<string, boolean>>({ load: true });
const R = ref<any>(null);
const msg = ref("");
const busy = ref(false);
const lang = computed(() => (locale.value === "en" ? "en" : "zh"));
const L = (x: any) => (x ? (lang.value === "en" ? x.en || x.zh : x.zh || x.en) : "");
const n1 = (v: number | null | undefined) => (v == null ? "—" : Number(v).toFixed(1));
const n2 = (v: number | null | undefined) => (v == null ? "—" : Number(v).toFixed(2));
const unit = (u: string) => (lang.value === "en" ? u.replace("年 / years", "years") : u.replace("年 / years", "年"));
const fail = (e: unknown) => { msg.value = errorText(e instanceof ApiError ? e.code : "unknown"); };

// 手填电流时才显示运行电流；按尺寸算热阻时才显示给定热阻；风扇时才显示风速
function visible(k: string) {
  if (k === "Irun") return ep.src === "manual" || !["lockstitch", "overlock"].includes(props.machine);   // 绷缝、花样、刺绣机的主轴没有转矩模型，主轴电流手填
  if (k === "Rbox") return ep.rbox_src === "given";
  if (k === "vfan") return ep.air === "fan";
  return true;
}

async function loadSchema() {
  try {
    const s = await request<{ groups: Group[]; defaults: Record<string, number | string> }>("GET", `/api/v1/sewing/ebox/schema?machine=${props.machine}`);
    schema.value = s.groups;
    defaults.value = s.defaults;
    for (const k of Object.keys(ep)) delete ep[k];
    Object.assign(ep, s.defaults);
    await calc();
  } catch (e) { fail(e); }
}
let timer: ReturnType<typeof setTimeout> | null = null;
function later() {
  if (timer) clearTimeout(timer);
  timer = setTimeout(calc, 250);
}
function setv(k: string, v: number | string) {
  ep[k] = v;
  later();
}
let seq = 0;
async function calc() {
  msg.value = "";
  const n = ++seq;
  try {
    const r = await request("POST", "/api/v1/sewing/ebox/analyze", { machine: props.machine, params: { ...props.params }, ebox: { ...ep } });
    if (n !== seq) return;                         // 已经有更新的一次在算
    R.value = r;
    emit("change", { ...ep });                    // 设计页导出计算书、参数表时带上电控箱这一节
  } catch (e) { fail(e); }
}
function reset() { Object.assign(ep, defaults.value); calc(); }
// 教材 18.7 节：夏天午后车间 38 °C，散热片糊了一层飞絮（堵塞 0.5）
function caseSix() { Object.assign(ep, { Ta: 38, clog: 0.5 }); calc(); }

const say = ref("");
const ai = ref<any>(null);
const aiBusy = ref(false);
async function draft() {
  if (!say.value.trim() || aiBusy.value) return;
  aiBusy.value = true;
  msg.value = "";
  try {
    ai.value = await request("POST", "/api/v1/sewing/ai/draft", { machine: props.machine, params: { ...props.params }, target: "ebox", ebox: { ...ep },
      sentence: say.value.trim() });
  } catch (e) { fail(e); }
  aiBusy.value = false;
}
function adopt() {
  if (!ai.value?.params) return;
  Object.assign(ep, ai.value.params);
  ai.value = null;
  calc();
}

async function runCae() {
  if (!props.canRun || busy.value) return;
  busy.value = true;
  msg.value = "";
  try {
    const r = await request<{ id: string }>("POST", "/api/v1/sewing/cae/ebox", { machine: props.machine, params: { ...props.params }, ebox: { ...ep } });
    emit("submitted", r.id);
  } catch (e) { fail(e); }
  busy.value = false;
}

function uploadOwn() {
  if (!props.canRun) return;
  // #ifdef H5
  const inp = document.createElement("input");
  inp.type = "file";
  inp.accept = ".step,.stp";
  inp.onchange = async () => {
    const f = inp.files?.[0];
    if (!f) return;
    busy.value = true;
    msg.value = "";
    try {
      const fd = new FormData();
      fd.append("file", f);
      fd.append("machine", props.machine);
      fd.append("params", JSON.stringify({ ...props.params }));
      fd.append("ebox", JSON.stringify({ ...ep }));
      const res = await fetch(`${BASE}/api/v1/sewing/cae/ebox/upload`, { method: "POST", headers: { Authorization: `Bearer ${token.value}` }, body: fd });
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new ApiError(j.error || `http_${res.status}`, res.status);
      emit("submitted", j.id);
    } catch (e) { fail(e); }
    busy.value = false;
  };
  inp.click();
  // #endif
}

async function stepFile() {
  if (!props.canRun) return;
  // #ifdef H5
  try {
    const res = await fetch(`${BASE}/api/v1/sewing/cae/ebox/step`, { method: "POST", headers: { Authorization: `Bearer ${token.value}`, "Content-Type": "application/json" },
      body: JSON.stringify({ machine: props.machine, params: { ...props.params }, ebox: { ...ep } }) });
    if (!res.ok) {
      let code = `http_${res.status}`;
      try { code = (await res.json()).error || code; } catch { /* not json */ }
      throw new ApiError(code, res.status);
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(await res.blob());
    a.download = `ebox-${ep.L}x${ep.W}x${ep.H}.step`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } catch (e) { fail(e); }
  // #endif
}

const esc = (x: string) => String(x).replace(/&/g, "&amp;").replace(/</g, "&lt;");
function line(c: Chart) {
  const xs = c.x, ref = c.ref == null ? undefined : c.ref;
  const all = c.series.map((s) => s.y).flat().concat(ref != null ? [ref] : []).concat(c.zero ? [0] : []);
  let lo = Math.min(...all), hi = Math.max(...all);
  if (hi - lo < 1e-6) hi = lo + 1;
  const [x0, x1] = c.xr || [xs[0], xs[xs.length - 1]];
  const X = (a: number) => 34 + (258 * (a - x0)) / (x1 - x0 || 1), Y = (v: number) => 132 - (120 * (v - lo)) / (hi - lo);
  let s = `<rect x="34" y="12" width="258" height="120" fill="#fff" stroke="#e1e6ea"/>`;
  for (const q of [0, 0.25, 0.5, 0.75, 1]) {
    const a = x0 + q * (x1 - x0);
    s += `<text x="${X(a)}" y="146" font-size="9" text-anchor="middle" fill="#6b7b88">${x1 - x0 < 10 ? a.toFixed(1) : Math.round(a)}</text>`;
  }
  if (c.xl) s += `<text x="292" y="10" font-size="9" text-anchor="end" fill="#6b7b88">${esc(L(c.xl))} →</text>`;
  s += `<text x="30" y="${Y(hi) + 4}" font-size="9" text-anchor="end" fill="#6b7b88">${hi.toFixed(hi > 100 ? 0 : 1)}</text>`;
  s += `<text x="30" y="${Y(lo) + 3}" font-size="9" text-anchor="end" fill="#6b7b88">${lo.toFixed(1)}</text>`;
  if (ref != null) s += `<line x1="34" x2="292" y1="${Y(ref)}" y2="${Y(ref)}" stroke="#c0392b" stroke-dasharray="4 3" stroke-width="0.8"/>`;
  for (const se of c.series) s += `<polyline fill="none" stroke="${se.color}" stroke-width="1.6" points="${se.y.map((v, j) => `${X(xs[j]).toFixed(1)},${Y(v).toFixed(1)}`).join(" ")}"/>`;
  return s;
}

// 换机型才重新载入（恢复这台机型的默认）；切走页签再回来，改过的电控箱参数还在
let loadedFor = "";
watch(() => [props.machine, props.active], () => {
  if (props.active && loadedFor !== props.machine) { loadedFor = props.machine; loadSchema(); }
}, { immediate: true });
watch(() => JSON.stringify(props.params), () => { if (props.active && schema.value.length) later(); });     // 设计改了，电流跟着变
</script>

<style scoped>
.ebox { border-top: 1px solid var(--wq-line); padding: 12px 0; }
.bt { display: block; font-weight: 700; color: var(--wq-ink); font-size: 15px; }
.st { display: block; font-weight: 600; color: var(--wq-ink); margin-top: 12px; }
.hint { display: block; color: var(--wq-muted); font-size: 13px; line-height: 1.6; margin-top: 4px; }
.hint.err { color: var(--wq-danger); }
.row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 6px 0; }
.opt { font-size: 13px; padding: 4px 10px; border: 1px solid var(--wq-line); border-radius: 999px; cursor: pointer; background: #fff; }
.opt.on { background: #1d4e75; border-color: #1d4e75; color: #fff; }
.btn { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 7px 14px; border-radius: 6px; cursor: pointer; white-space: nowrap; font-size: 14px; display: inline-block; margin-top: 6px; }
.btn.disabled { opacity: .5; cursor: not-allowed; }
.btn.ghost { background: #fff; border: 1px solid var(--wq-line); }
.link { color: var(--wq-link); font-size: 13px; cursor: pointer; }
.muted { color: var(--wq-muted); }
.small { font-size: 12px; }
.grp { border-top: 1px solid var(--wq-line); }
.gt { display: flex; justify-content: space-between; padding: 9px 2px; font-weight: 600; color: var(--wq-ink); cursor: pointer; font-size: 14px; }
.prm { padding: 2px 0 6px; }
.pl { display: block; font-size: 13px; }
.inp { width: 110px; border: 1px solid var(--wq-line); border-radius: 6px; padding: 4px 8px; font-size: 14px; background: #fff; }
.tbl { border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; font-size: 13px; margin-top: 8px; }
.tr { display: flex; border-top: 1px solid var(--wq-line); }
.tr:first-child { border-top: 0; }
.tr.th { background: #eaf2fa; font-weight: 600; }
.td { flex: 1; padding: 5px 8px; min-width: 0; }
.td.w2 { flex: 2.4; }
.kgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 8px; margin-top: 8px; }
.kc { border: 1px solid var(--wq-line); border-radius: 6px; padding: 8px 10px; }
.kl { display: block; font-size: 12px; color: var(--wq-muted); }
.kv { display: block; font-size: 15px; font-weight: 600; color: var(--wq-ink); margin-top: 2px; }
.chk { display: flex; gap: 10px; padding: 8px 0; border-top: 1px solid var(--wq-line); }
.lamp { width: 12px; height: 12px; border-radius: 50%; margin-top: 5px; flex: none; background: #2e9e6a; }
.lamp.warn, .cst.warn { background: #e8913a; }
.lamp.bad, .cst.bad { background: #c0392b; }
.cbody { flex: 1; min-width: 0; }
.crow { display: flex; justify-content: space-between; gap: 10px; }
.cname { font-weight: 600; color: var(--wq-ink); }
.cst { font-size: 12px; color: #fff; background: #2e9e6a; border-radius: 999px; padding: 1px 8px; white-space: nowrap; height: 18px; }
.cval { display: block; font-size: 13px; margin-top: 2px; }
.charts { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; margin-top: 10px; }
.ctt { display: block; font-size: 13px; font-weight: 600; color: var(--wq-ink); }
.svg { width: 100%; height: auto; display: block; margin-top: 4px; }
.legend { display: flex; gap: 10px; flex-wrap: wrap; font-size: 12px; color: var(--wq-muted); }
.lg { display: inline-flex; align-items: center; gap: 4px; }
.sw { display: inline-block; width: 10px; height: 3px; border-radius: 2px; }
.badc { color: var(--wq-danger); font-weight: 700; }
.warnc { color: #b66a12; font-weight: 700; }
.cae { margin-top: 10px; }
.ai { display: flex; gap: 8px; align-items: center; margin-top: 12px; }
.ainp { flex: 1; border: 1px solid var(--wq-line); border-radius: 6px; padding: 6px 10px; font-size: 14px; background: #fff; }
.aires { background: #f6f9fc; border-radius: 6px; padding: 8px 10px; margin-top: 6px; }
.para { display: block; font-size: 13px; line-height: 1.7; }
.strong { font-weight: 600; color: var(--wq-ink); }
.btn.sm { padding: 4px 10px; font-size: 13px; }
</style>
