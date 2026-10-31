<template>
  <!-- 缝纫机设计与制造软件（第 39 轮平缝机，第 40 轮加包缝机、绷缝机，第 41 轮接入问渠 CAE）。机型在上，参数在左，三维样机 / 校核 / 时序 / 零件与制造 / CAE 分析 / 导出在右。来宾可试算，开通后可保存与导出。 -->
  <view class="sew">
    <view class="head">
      <text class="h1">{{ t("sew.title") }}</text>
      <text class="lead">{{ t("sew.lead") }}</text>
      <view class="who">
        <!-- #ifdef H5 -->
        <text class="link help" @click="help">？{{ t("sew.help") }}</text>
        <!-- #endif -->
        <text v-if="me.licensed" class="chip ok">{{ t("sew.licensed", { org: me.org || "" }) }}</text>
        <template v-else>
          <text class="chip">{{ me.login ? t("sew.notLicensed") : t("sew.guest") }}</text>
          <text v-if="!me.login" class="link" @click="toLogin">{{ t("sew.login") }}</text>
          <text class="link" @click="contact">{{ t("sew.contact") }} →</text>
        </template>
      </view>
    </view>

    <!-- 机型 -->
    <view class="mbar">
      <text v-for="m in machines" :key="m.key" class="mopt" :class="{ on: machine === m.key }" @click="switchMachine(m.key)">{{ L(m) }}</text>
    </view>

    <!-- 项目条（已开通） -->
    <view v-if="me.licensed" class="pbar">
      <picker :range="projectNames" :value="pIndex" @change="pickProject">
        <view class="psel">{{ t("sew.project") }}：<text class="pname">{{ current ? current.name : t("sew.untitled") }}</text> ▾</view>
      </picker>
      <input v-model="pname" class="input pn" :placeholder="t('sew.namePh')" maxlength="80" />
      <view class="btn" @click="save(false)">{{ t("sew.save") }}</view>
      <view v-if="current" class="btn" @click="save(true)">{{ t("sew.saveAs") }}</view>
      <view class="btn ghost" @click="newProject">{{ t("sew.new") }}</view>
      <text v-if="current" class="link danger" @click="removeProject">{{ t("sew.delete") }}</text>
      <text v-if="msg" class="hint">{{ msg }}</text>
    </view>

    <view class="cols">
      <!-- 参数 -->
      <view class="left">
        <view class="lhead">
          <text class="h2">{{ t("sew.params") }}</text>
          <text class="link" @click="reset">{{ t("sew.reset") }}</text>
        </view>
        <view v-for="g in schema" :key="g.key" class="grp">
          <view class="gt" @click="open[g.key] = !open[g.key]">
            <text>{{ L(g) }}</text><text class="muted">{{ open[g.key] ? "−" : "+" }}</text>
          </view>
          <view v-if="open[g.key] && libFor(g).length" class="libpick">
            <text class="link small" @click="libOpen[g.key] = !libOpen[g.key]">{{ t("sew.lib.pick", { n: libFor(g).length }) }} {{ libOpen[g.key] ? "▴" : "▾" }}</text>
            <view v-if="libOpen[g.key]">
              <text v-for="it in libFor(g)" :key="it.id + it.label" class="libitem" @click="applyParams(it.params)">{{ it.code }} {{ it.name }} · {{ it.label }}</text>
            </view>
          </view>
          <view v-if="open[g.key]">
            <view v-for="p in g.params" :key="p.key" class="prm">
              <text class="pl">{{ L(p) }}<text v-if="p.unit" class="muted"> · {{ p.unit }}</text></text>
              <view v-if="p.choices.length" class="chips">
                <text v-for="c in p.choices" :key="c.key" class="opt" :class="{ on: params[p.key] === c.key }" @click="setv(p.key, c.key)">{{ L(c) }}</text>
              </view>
              <view v-if="p.key === 'pat' && params.pat === 'csv'" class="csv">
                <view class="btn ghost" @click="pickCsv">{{ t("sew.csvPick") }}</view>
                <text class="hint">{{ csvInfo || t("sew.csvHint") }}</text>
              </view>
              <view v-else-if="!p.choices.length" class="num">
                <slider class="sl" :min="p.min" :max="p.max" :step="p.step" :value="Number(params[p.key])" block-size="16"
                  activeColor="#1d6fa5" @changing="(e: any) => setv(p.key, e.detail.value)" @change="(e: any) => setv(p.key, e.detail.value)" />
                <input class="input ni" type="digit" :value="String(params[p.key])" @blur="(e: any) => typed(p, e.detail.value)"
                  @confirm="(e: any) => typed(p, e.detail.value)" />
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 结果 -->
      <view class="right">
        <SewAi :machine="machine" :params="params" :licensed="me.licensed" @apply="applyParams" @desc="(s: string[]) => { desc = s; tab = 'export'; msg = t('sew.ai.descReady'); }" />
        <view class="summary" :class="R ? (R.ok ? (warns ? 'warn' : 'ok') : 'bad') : ''">
          <text v-if="!R">{{ t("sew.computing") }}</text>
          <text v-else-if="R.ok && !warns">✓ {{ t("sew.allOk", { n: R.checks.length }) }}</text>
          <text v-else>{{ R.ok ? "!" : "✕" }} {{ t("sew.someBad", { b: bads, w: warns, n: R.checks.length }) }}</text>
          <text v-if="busy" class="muted small"> · {{ t("sew.computing") }}</text>
        </view>
        <view class="tabs">
          <text v-for="k in tabs" :key="k" class="tab" :class="{ on: tab === k }" @click="tab = k">{{ t("sew.tab." + k) }}</text>
        </view>

        <!-- 三维样机 -->
        <view v-show="tab === 'proto'" class="pane">
          <!-- #ifdef H5 -->
          <view class="frame" :class="{ flat: R && ['looper', 'embroid'].includes(R.view.page) }">
            <iframe v-if="protoOk" :key="protoSrc" ref="frame" class="proto" :src="protoSrc" title="3D" @load="syncProto" />
            <view v-else class="empty">{{ t("sew.protoMissing") }}</view>
          </view>
          <!-- #endif -->
          <text class="hint">{{ t("sew.protoNote." + machine) }}</text>
          <view v-if="R" class="kgrid">
            <view v-for="(k, i) in R.results" :key="i" class="kc"><text class="kl">{{ lang === "en" ? k.en : k.zh }}</text>
              <text class="kv">{{ k.value }} <text class="muted small">{{ k.unit }}</text></text></view>
          </view>
        </view>

        <!-- 校核 -->
        <view v-if="R" v-show="tab === 'checks'" class="pane">
          <view v-if="R.trial" class="trial">
            <text class="kl">{{ t("sew.trial") }}</text>
            <view class="dots"><text v-for="(s, i) in R.trial.res" :key="i" class="dot" :class="s" /></view>
            <text class="hint">{{ t("sew.trialSum", { ok: R.trial.counts.ok, skip: R.trial.counts.skip, hit: R.trial.counts.hit, cut: R.trial.counts.cut, brk: R.trial.counts.break }) }}</text>
          </view>
          <view v-for="c in R.checks" :key="c.key" class="chk">
            <text class="lamp" :class="c.state" />
            <view class="cbody">
              <view class="crow">
                <text class="cname">{{ c.name[lang] }}</text>
                <text class="cst" :class="c.state">{{ t("sew.state." + c.state) }}</text>
              </view>
              <text class="cval">{{ c.value[lang] }}<text class="muted">　{{ t("sew.criterion") }} {{ c.limit[lang] }} · {{ t("sew.lecture", { n: c.lecture }) }}</text></text>
              <text v-if="c.advice[lang]" class="cadv">{{ c.advice[lang] }}</text>
            </view>
          </view>
        </view>

        <!-- 时序与曲线 -->
        <view v-if="R" v-show="tab === 'timing'" class="pane">
          <text class="ct">{{ R.timing_x === "pass" ? t("sew.chart.timingPass") : t("sew.chart.timing") }}</text>
          <svg class="svg" :viewBox="`0 0 640 ${timingH()}`" v-html="timingSvg()" />
          <text class="hint">{{ R.timing_x === "pass" ? t("sew.chart.pass") : t("sew.chart.angle") }}</text>
          <view class="charts">
            <view v-for="c in R.charts" :key="c.key" class="chart"><text class="ct">{{ lang === "en" ? c.en : c.zh }}</text>
              <svg class="svg" viewBox="0 0 300 150" v-html="c.kind === 'xy' ? path(c) : line(c)" /></view>
          </view>
        </view>

        <!-- 零件与制造 -->
        <view v-if="R" v-show="tab === 'parts'" class="pane">
          <text class="ct">{{ t("sew.parts") }}</text>
          <view v-for="pt in R.parts" :key="pt.key" class="part">
            <text class="pt">{{ lang === "en" ? pt.en : pt.zh }}</text>
            <view v-for="(d, i) in pt.dims" :key="i" class="dim"><text>{{ lang === "en" ? d[1] : d[0] }}</text><text class="dv">{{ d[2] }} {{ d[3] }}</text></view>
          </view>
          <view v-for="tb in R.tables || []" :key="tb.key">
            <text class="ct">{{ lang === "en" ? tb.en : tb.zh }}</text>
            <view class="tbl">
              <view class="tr th"><text v-for="(h, i) in tb.head" :key="i" class="td">{{ lang === "en" ? h[1] : h[0] }}</text></view>
              <view v-for="(r, j) in tb.rows" :key="j" class="tr"><text v-for="(c, i) in r" :key="i" class="td">{{ Array.isArray(c) ? (lang === "en" ? c[1] : c[0]) : c }}</text></view>
            </view>
          </view>
          <text v-if="R.chain" class="ct">{{ t("sew.chain") }}</text>
          <text v-if="R.chain" class="para">{{ t("sew.chainText", { w: R.chain.worst.toFixed(3), yi: (R.chain.y_int * 100).toFixed(1), ya: (R.chain.y_adj * 100).toFixed(2), ys: (R.chain.y_swap * 100).toFixed(1) }) }}</text>
          <text class="ct">{{ t("sew.card") }}</text>
          <view v-for="(s, i) in R.card" :key="i" class="step"><text class="sn">{{ i + 1 }}</text>
            <view><text class="pt">{{ lang === "en" ? s.en : s.zh }}</text><text class="para">{{ lang === "en" ? s.do_en : s.do_zh }}</text></view></view>
        </view>

        <!-- CAE 分析（第 41 轮） -->
        <view v-show="tab === 'cae'" class="pane">
          <SewCae :machine="machine" :params="params" :licensed="me.licensed" :active="tab === 'cae'" :labels="plabels" @apply="applyParams"
            @ebox="(e: Record<string, number | string>) => (eboxP = e)" />
        </view>

        <!-- 本单位零件库（第 49 轮） -->
        <view v-show="tab === 'lib'" class="pane">
          <SewParts :machine="machine" :licensed="me.licensed" :active="tab === 'lib'" @apply="applyParams" @changed="loadLib" />
        </view>

        <!-- 导出 -->
        <view v-show="tab === 'export'" class="pane">
          <view v-if="!me.licensed" class="note">{{ t("sew.expLocked") }} <text class="link" @click="contact">{{ t("sew.contact") }} →</text></view>
          <view class="lrow"><text class="muted">{{ t("sew.lang") }}</text>
            <text class="opt" :class="{ on: flang === 'zh' }" @click="flang = 'zh'">中文</text>
            <text class="opt" :class="{ on: flang === 'en' }" @click="flang = 'en'">English</text></view>
          <view v-if="desc.length" class="lrow"><text class="opt" :class="{ on: withDesc }" @click="withDesc = !withDesc">{{ withDesc ? "✓ " : "" }}{{ t("sew.ai.withDesc") }}</text>
            <text class="muted small">{{ desc.join("").slice(0, 60) }}…</text></view>
          <view v-for="k in kinds" :key="k" class="exp" :class="{ locked: !me.licensed }" @click="download(k)">
            <text>{{ t("sew.exp." + k) }}</text><text class="muted">{{ making === k ? t("sew.making") : "↓" }}</text>
          </view>
          <!-- 第 56 轮：按这台设计一键出三维讲解片（有三维零件的平缝机、包缝机） -->
          <view v-if="machine === 'lockstitch' || machine === 'overlock'" class="fc">
            <text class="pt">{{ t("sew.video") }}</text>
            <text class="para">{{ t("sew.videoText") }}</text>
            <view class="btn" :class="{ disabled: !me.licensed }" @click="makeVideo">{{ making === "video" ? t("sew.videoMaking") : t("sew.videoBtn") }}</view>
          </view>
          <view class="fc">
            <text class="pt">{{ t("sew.freecad") }}</text>
            <text class="para">{{ t("sew.freecadText") }}</text>
            <text class="para muted">{{ t("sew.freecadSteps") }}</text>
            <view class="btn" :class="{ disabled: !me.licensed }" @click="download('freecad')">{{ making === "freecad" ? t("sew.making") : t("sew.freecadBtn") }}</view>
          </view>
          <text v-if="msg" class="hint">{{ msg }}</text>
        </view>
      </view>
    </view>

    <!-- 管理员：手动开通 -->
    <view v-if="me.admin" class="adm">
      <text class="h2">{{ t("sew.admin") }}</text>
      <view class="grant">
        <input v-model="g.who" class="input" :placeholder="t('sew.grantWho')" maxlength="120" />
        <input v-model="g.org" class="input" :placeholder="t('sew.grantOrg')" maxlength="80" />
        <input v-model="g.note" class="input" :placeholder="t('sew.grantNote')" maxlength="200" />
        <view class="btn" @click="grant">{{ t("sew.grant") }}</view>
      </view>
      <text v-if="adminMsg" class="hint">{{ adminMsg }}</text>
      <text v-if="!licenses.length" class="hint">{{ t("sew.noLicenses") }}</text>
      <view v-for="x in licenses" :key="x.user_id" class="g-row">
        <text>{{ x.name || x.user_id }} · {{ x.org }}<text v-if="x.note" class="muted"> · {{ x.note }}</text></text>
        <text class="link danger" @click="revoke(x.user_id)">{{ t("sew.revoke") }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { ApiError, BASE, request, token } from "../../api";
import { siteUrl } from "../../accountApi";
import { errorText, locale, t } from "../../i18n";
import SewAi from "./SewAi.vue";
import SewCae from "./SewCae.vue";
import SewParts from "./SewParts.vue";

interface Choice { key: string; zh: string; en: string }
interface Param { key: string; zh: string; en: string; unit: string; default: number | string; min: number; max: number; step: number; choices: Choice[] }
interface Group { key: string; zh: string; en: string; params: Param[] }
interface Check { key: string; group: string; name: { zh: string; en: string }; value: { zh: string; en: string }; limit: { zh: string; en: string }; state: "ok" | "warn" | "bad"; lecture: number;
  advice: { zh: string; en: string } }
interface Project { id: number; name: string; note?: string; machine?: string; params?: Record<string, number | string>; updated?: number }
interface Chart { key: string; kind: "line" | "xy"; zh: string; en: string; x: number[]; series: { zh: string; en: string; color: string; y: number[] }[];
  ref?: number | null; zero?: boolean; ref_zh?: string; ref_en?: string; xr?: [number, number]; xl?: { zh: string; en: string }; open?: boolean }

const props = defineProps<{ startTab?: string; startMachine?: string; startParams?: string }>();
const kinds = ref<string[]>(["report", "card", "params", "step", "macro", "dxf", "json"]);
const machines = ref<Choice[]>([]);
const machine = ref("lockstitch");
const COLORS = ["#2d6fb3", "#7d5ba6", "#c0392b", "#2e9e6a", "#e8913a"];
const tabs = ["proto", "checks", "timing", "parts", "cae", "lib", "export"];

const schema = ref<Group[]>([]);
const params = reactive<Record<string, number | string>>({});
const defaults: Record<string, number | string> = {};
const open = reactive<Record<string, boolean>>({ basic: true, needle: true, looper: true });
const R = ref<any>(null);
const busy = ref(false);
const tab = ref("proto");
watch(() => props.startTab, (v) => { if (v && tabs.includes(v)) tab.value = v; }, { immediate: true });
const me = ref<{ login: boolean; licensed: boolean; admin: boolean; org?: string }>({ login: false, licensed: false, admin: false });
const projects = ref<Project[]>([]);
const current = ref<Project | null>(null);
const pname = ref("");
const msg = ref("");
const making = ref("");
const flang = ref<"zh" | "en">(locale.value === "en" ? "en" : "zh");
const protoOk = ref(true);
const frame = ref<any>(null);
const licenses = ref<any[]>([]);
const g = reactive({ who: "", org: "", note: "" });
const adminMsg = ref("");

const lang = computed(() => (locale.value === "en" ? "en" : "zh"));
const L = (x: { zh: string; en: string }) => (lang.value === "en" ? x.en || x.zh : x.zh || x.en);
const bads = computed(() => (R.value ? R.value.checks.filter((c: Check) => c.state === "bad").length : 0));
const warns = computed(() => (R.value ? R.value.checks.filter((c: Check) => c.state === "warn").length : 0));
const mname = (k?: string) => { const m = machines.value.find((x) => x.key === (k || "lockstitch")); return m ? L(m) : ""; };
const projectNames = computed(() => projects.value.map((p) => `${p.name}（${mname(p.machine)}）`));
const plabels = computed(() => { const o: Record<string, string> = {}; for (const grp of schema.value) for (const x of grp.params) { o[x.key] = L(x); for (const c of x.choices || []) o[`${x.key}:${c.key}`] = L(c); } return o; });
const pIndex = computed(() => Math.max(0, projects.value.findIndex((p) => p.id === current.value?.id)));
const PAGES: Record<string, string> = { lockstitch: "proto-lockstitch", overlock: "model-overlock", cover: "looper", pattern: "model-pattern", embroid: "embroid", flatknit: "model-flatknit" };
const MACHINE_KEYS = Object.keys(PAGES);
const protoSrc = computed(() => `${BASE}/api/v1/sewing/proto?lang=${lang.value}&page=${PAGES[machine.value] || PAGES.lockstitch}`);

// ---------- 计算 ----------
let timer: any = null;
let seq = 0;
function schedule() {
  clearTimeout(timer);
  timer = setTimeout(compute, 250);
}
async function compute() {
  const my = ++seq;
  busy.value = true;
  try {
    const r = await request<any>("POST", "/api/v1/sewing/analyze", { machine: machine.value, params: { ...params } });
    if (my !== seq) return;
    R.value = r;
    syncProto();
  } catch (e) {
    msg.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    if (my === seq) busy.value = false;
  }
}
function setv(k: string, v: number | string) {
  params[k] = v;
  schedule();
}
function typed(p: Param, raw: string) {
  const v = Number(raw);
  if (!isFinite(v)) return;
  setv(p.key, Math.min(p.max, Math.max(p.min, v)));
}
// CAE 分析 / 设计优化的“采用”：回填参数（夹在参数范围里）再算
function applyParams(p: Record<string, number | string>) {
  const lim: Record<string, Param> = {};
  for (const grp of schema.value) for (const x of grp.params) lim[x.key] = x;
  for (const [k, v] of Object.entries(p)) {
    const d = lim[k];
    if (!d) continue;
    params[k] = typeof v === "number" && !d.choices.length ? Math.min(d.max, Math.max(d.min, v)) : v;
  }
  msg.value = t("sew.cae.applied", { p: Object.entries(p).map(([k, v]) => `${plabels.value[k] || k} = ${v}`).join("，") });
  compute();
}
function reset() {
  delete params.pts;
  csvInfo.value = "";
  Object.assign(params, defaults);
  compute();
}

// 花样机：上传针位表（CSV：每行 x, y，单位 mm；最多 3000 针）。原文交给后端整理，存项目时一起存
const csvInfo = ref("");
function pickCsv() {
  // #ifdef H5
  const inp = document.createElement("input");
  inp.type = "file";
  inp.accept = ".csv,.txt,text/csv,text/plain";
  inp.onchange = async () => {
    const f = inp.files && inp.files[0];
    if (!f) return;
    if (f.size > 200000) { csvInfo.value = t("sew.csvBig"); return; }
    const txt = await f.text();
    params.pts = txt;
    csvInfo.value = t("sew.csvLoaded", { name: f.name });
    compute();
  };
  inp.click();
  // #endif
}
watch(R, (r) => {
  if (r && machine.value === "pattern" && params.pat === "csv" && r.params?.pts) csvInfo.value = t("sew.csvCount", { n: r.params.pts.length });
});

// 三维样机 / 动画：同源页面。平缝机调 __api.setCfg；绷缝机弯针动画改 __api.ST 再 changed()；包缝机三维结构模型不用同步
function syncProto() {
  // #ifdef H5
  try {
    const w = frame.value?.contentWindow || (frame.value?.$el as HTMLIFrameElement | undefined)?.contentWindow;
    const v = R.value?.view;
    if (!w || !w.__api || !v) return;
    if (v.sync === "setCfg") w.__api.setCfg(v.cfg);
    else if (v.sync === "ST") { Object.assign(w.__api.ST, v.cfg); w.__api.changed(); }
    else if (v.sync === "A") { Object.assign(w.__api.A, v.cfg); w.__api.changedA(); }   // 刺绣机：头数、框驱动力、针距、转速
  } catch { /* the page is still loading */ }
  // #endif
}

// 换机型：参数表、默认值、导出种类都跟着换；当前项目清空
async function loadSchema() {
  const s = await request<{ groups: Group[]; machines: Choice[]; kinds: Record<string, string> }>("GET", `/api/v1/sewing/schema?machine=${machine.value}`);
  schema.value = s.groups;
  machines.value = s.machines;
  kinds.value = Object.keys(s.kinds);
  for (const k of Object.keys(defaults)) delete defaults[k];
  for (const k of Object.keys(params)) delete params[k];
  for (const grp of s.groups) for (const p of grp.params) defaults[p.key] = p.default;
  Object.assign(params, defaults);
  open[s.groups[0]?.key || "basic"] = true;
  if (s.groups[1]) open[s.groups[1].key] = true;
  if (machine.value === "cover" && s.groups[2]) open[s.groups[2].key] = true;     // 耗线计划是绷缝机的卖点，默认展开
}
async function switchMachine(m: string, keepProject = false) {
  if (m === machine.value && R.value) return;
  machine.value = m;
  R.value = null;
  msg.value = "";
  if (!keepProject) { current.value = null; pname.value = ""; }
  await loadSchema();
  compute();
}

// ---------- 图 ----------
const tx = (a: number) => 168 + (462 * a) / 360;
function segs(r: { a: number; b: number }) {
  if (r.a === r.b) return [[r.a - 1, r.a + 1]];
  return r.b >= r.a ? [[r.a, r.b]] : [[r.a, 360], [0, r.b]];
}
// 时序图高度随行数变（花样机、刺绣机只有两行）
const timingH = () => 30 + 28 * Math.max(2, (R.value?.timing || []).length);
function timingSvg() {
  let s = "";
  const h = timingH();
  for (const a of [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]) {
    s += `<line x1="${tx(a)}" x2="${tx(a)}" y1="8" y2="${h - 22}" stroke="#e1e6ea"/><text x="${tx(a)}" y="${h - 6}" font-size="10" text-anchor="middle" fill="#6b7b88">${R.value?.timing_x === "pass" ? Math.round(a / 3.6) + "%" : a}</text>`;
  }
  (R.value.timing as any[]).forEach((r, i) => {
    s += `<text x="4" y="${24 + i * 28}" font-size="10.5" fill="#1f2a33">${esc(r[lang.value])}</text>`;
    for (const g of segs(r)) s += `<rect x="${tx(g[0])}" y="${10 + i * 28}" width="${Math.max(2, tx(g[1]) - tx(g[0]))}" height="16" rx="3" fill="${COLORS[i % 5]}"/>`;
    if (r.mark != null) s += `<line x1="${tx(r.mark)}" x2="${tx(r.mark)}" y1="${7 + i * 28}" y2="${29 + i * 28}" stroke="#000" stroke-width="2"/>`;
  });
  return s;
}
const esc = (x: string) => String(x).replace(/&/g, "&amp;").replace(/</g, "&lt;");
function line(c: Chart) {
  const phi = c.x, zero = !!c.zero, ref = c.ref == null ? undefined : c.ref;
  const series = c.series.map((x) => x.y), colors = c.series.map((x) => x.color);
  const all = series.flat().concat(ref != null ? [ref] : []).concat(zero ? [0] : []);
  let lo = Math.min(...all), hi = Math.max(...all);
  if (hi - lo < 1e-6) hi = lo + 1;
  const [x0, x1] = c.xr || [0, 360];
  const X = (a: number) => 34 + (258 * (a - x0)) / (x1 - x0 || 1), Y = (v: number) => 132 - (120 * (v - lo)) / (hi - lo);
  let s = `<rect x="34" y="12" width="258" height="120" fill="#fff" stroke="#e1e6ea"/>`;
  const ticks = c.xr ? [0, 0.25, 0.5, 0.75, 1].map((q) => x0 + q * (x1 - x0)) : [0, 90, 180, 270, 360];
  const fine = c.xr && x1 - x0 < 10;            // 横轴范围小（例如横机机头速度 0.4–2.0 m/s）：标一位小数
  for (const a of ticks) s += `<text x="${X(a)}" y="146" font-size="9" text-anchor="middle" fill="#6b7b88">${fine ? a.toFixed(1) : Math.round(a)}</text>`;
  if (c.xl) s += `<text x="292" y="10" font-size="9" text-anchor="end" fill="#6b7b88">${esc(lang.value === "en" ? c.xl.en : c.xl.zh)} →</text>`;
  s += `<text x="30" y="${Y(hi) + 4}" font-size="9" text-anchor="end" fill="#6b7b88">${hi.toFixed(hi > 100 ? 0 : 1)}</text>`;
  s += `<text x="30" y="${Y(lo) + 3}" font-size="9" text-anchor="end" fill="#6b7b88">${lo.toFixed(lo < -100 ? 0 : 1)}</text>`;
  if (zero && lo < 0 && hi > 0) s += `<line x1="34" x2="292" y1="${Y(0)}" y2="${Y(0)}" stroke="#8a9aa8" stroke-width="0.6"/>`;
  if (ref != null) s += `<line x1="34" x2="292" y1="${Y(ref)}" y2="${Y(ref)}" stroke="#c0392b" stroke-dasharray="4 3" stroke-width="0.8"/>`;
  series.forEach((ys, i) => {
    s += `<polyline fill="none" stroke="${colors[i]}" stroke-width="1.6" points="${ys.map((v, j) => `${X(phi[j]).toFixed(1)},${Y(v).toFixed(1)}`).join(" ")}"/>`;
  });
  return s;
}
function path(c: Chart) {
  const xs = c.x, ys = c.series[0].y;
  const xl = Math.min(...xs), xh = Math.max(...xs), yl = Math.min(...ys, 0), yh = Math.max(...ys, 0);
  const sc = Math.min(250 / (xh - xl || 1), 115 / (yh - yl || 1));
  const X = (v: number) => 150 + (v - (xl + xh) / 2) * sc, Y = (v: number) => 75 - (v - (yl + yh) / 2) * sc;
  let s = `<rect x="4" y="4" width="292" height="142" fill="#fff" stroke="#e1e6ea"/>`;
  s += `<line x1="8" x2="292" y1="${Y(0)}" y2="${Y(0)}" stroke="#8a9aa8" stroke-width="0.8"/>`;
  s += `<text x="290" y="${Y(0) - 3}" font-size="9" text-anchor="end" fill="#6b7b88">${esc(lang.value === "en" ? c.ref_en || "" : c.ref_zh || "")}</text>`;
  s += `<${c.open ? "polyline" : "polygon"} fill="none" stroke="#2e9e6a" stroke-width="1.6" points="${xs.map((v, j) => `${X(v).toFixed(1)},${Y(ys[j]).toFixed(1)}`).join(" ")}"/>`;
  return s;
}

// ---------- 第 49 轮：AI 设计说明、本单位零件库、帮助 ----------
const desc = ref<string[]>([]);
const eboxP = ref<Record<string, number | string> | null>(null);       // 第 62 轮：看过“电控箱”后，计算书和参数表带上这一节
watch(() => machine.value, () => { eboxP.value = null; });
const withDesc = ref(true);
watch(machine, () => { desc.value = []; });
const libItems = ref<{ id: number; code: string; name: string; label: string; params: Record<string, number> }[]>([]);
const libOpen = reactive<Record<string, boolean>>({});
async function loadLib() {
  if (!me.value.licensed) { libItems.value = []; return; }
  try { libItems.value = (await request<{ items: any[] }>("GET", `/api/v1/sewing/parts/for?machine=${machine.value}`)).items; } catch { libItems.value = []; }
}
watch(machine, loadLib);
function libFor(g: Group) {
  const keys = new Set(g.params.map((p) => p.key));
  return libItems.value.filter((it) => Object.keys(it.params).some((k) => keys.has(k)));
}
const HELP: Record<string, string> = { proto: "proto", checks: "checks", timing: "timing", parts: "parts", cae: "cae", lib: "lib", export: "export" };
function help() {
  // #ifdef H5
  window.open(`/static/help/sewing/index.html#${HELP[tab.value] || ""}`, "_blank", "noopener");
  // #endif
}

// ---------- 账号、项目 ----------
async function loadMe() {
  try { me.value = await request("GET", "/api/v1/sewing/me"); } catch { /* guest */ }
  if (me.value.licensed) { await loadProjects(); loadLib(); }
  if (me.value.admin) await loadLicenses();
}
async function loadProjects() {
  try { projects.value = (await request<{ projects: Project[] }>("GET", "/api/v1/sewing/projects")).projects; } catch { projects.value = []; }
}
async function pickProject(e: any) {
  const p = projects.value[Number(e.detail.value)];
  if (!p) return;
  const full = await request<Project>("GET", `/api/v1/sewing/projects/${p.id}`);
  await switchMachine(full.machine || "lockstitch", true);
  current.value = full;
  pname.value = full.name;
  Object.assign(params, defaults, full.params || {});
  compute();
}
function newProject() {
  current.value = null;
  pname.value = "";
  reset();
}
async function save(asNew: boolean) {
  const name = pname.value.trim() || (current.value && !asNew ? current.value.name : "");
  if (!name) return (msg.value = t("sew.namePh"));
  try {
    const body = { name, machine: machine.value, params: { ...params } };
    const p = current.value && !asNew
      ? await request<Project>("PUT", `/api/v1/sewing/projects/${current.value.id}`, body)
      : await request<Project>("POST", "/api/v1/sewing/projects", body);
    current.value = p;
    pname.value = p.name;
    msg.value = t("sew.saved");
    await loadProjects();
  } catch (e) {
    msg.value = errorText(e instanceof ApiError ? e.code : "unknown");
  }
}
function removeProject() {
  const p = current.value;
  if (!p) return;
  uni.showModal({ title: t("sew.delete"), content: t("sew.deleteAsk", { name: p.name }), success: async (r) => {
    if (!r.confirm) return;
    await request("DELETE", `/api/v1/sewing/projects/${p.id}`);
    newProject();
    await loadProjects();
  } });
}

// ---------- 导出（H5：带登录凭证取文件再存盘） ----------
async function download(kind: string) {
  if (!me.value.licensed) return (msg.value = t("sew.expLocked"));
  if (making.value) return;
  making.value = kind;
  msg.value = "";
  // #ifdef H5
  try {
    const isZip = kind === "freecad";
    const res = await fetch(`${BASE}${isZip ? "/api/v1/sewing/freecad.zip" : `/api/v1/sewing/export/${kind}`}`, {
      method: isZip ? "GET" : "POST",
      headers: { Authorization: `Bearer ${token.value}`, "Content-Type": "application/json" },
      body: isZip ? undefined : JSON.stringify({ machine: machine.value, params: { ...params }, project: current.value?.name || pname.value || "", lang: flang.value,
        desc: kind === "report" && withDesc.value ? desc.value : [],
        ebox: (kind === "report" || kind === "params") && eboxP.value ? eboxP.value : null }),
    });
    if (!res.ok) {
      let code = `http_${res.status}`;
      try { code = (await res.json()).error || code; } catch { /* not json */ }
      throw new ApiError(code, res.status);
    }
    const cd = res.headers.get("content-disposition") || "";
    const m = /filename\*=UTF-8''([^;]+)/.exec(cd);
    const name = m ? decodeURIComponent(m[1]) : `${kind}.bin`;
    const url = URL.createObjectURL(await res.blob());
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  } catch (e) {
    msg.value = errorText(e instanceof ApiError ? e.code : "unknown");
  }
  // #endif
  making.value = "";
}

// ---------- 三维讲解片（第 56 轮）：网关按设计写好场景、开始出关键画面，跳到三维视频页 ----------
async function makeVideo() {
  if (!me.value.licensed) return (msg.value = t("sew.expLocked"));
  if (making.value) return;
  making.value = "video";
  msg.value = "";
  try {
    const r = await request<{ id: string }>("POST", "/api/v1/sewing/video", { machine: machine.value, params: { ...params }, project: current.value?.name || pname.value || "", lang: flang.value });
    uni.navigateTo({ url: `/pages/video3d/edit?id=${encodeURIComponent(r.id)}` });
  } catch (e) {
    msg.value = errorText(e instanceof ApiError ? e.code : "unknown");
  }
  making.value = "";
}

// ---------- 管理员 ----------
async function loadLicenses() {
  try { licenses.value = (await request<{ licenses: any[] }>("GET", "/api/v1/admin/sewing/licenses")).licenses; } catch { licenses.value = []; }
}
async function grant() {
  adminMsg.value = "";
  if (!g.who.trim() || !g.org.trim()) return;
  try {
    const r = await request<{ name: string }>("POST", "/api/v1/admin/sewing/licenses", { username: g.who.trim(), org: g.org.trim(), note: g.note.trim() });
    adminMsg.value = t("sew.granted", { name: r.name, org: g.org.trim() });
    g.who = g.note = "";
    await loadLicenses();
  } catch (e) {
    adminMsg.value = errorText(e instanceof ApiError ? e.code : "unknown");
  }
}
async function revoke(uid: number) {
  try { await request("DELETE", `/api/v1/admin/sewing/licenses/${uid}`); await loadLicenses(); } catch { /* shown on reload */ }
}

function toLogin() {
  uni.navigateTo({ url: `/pages/login/login?back=${encodeURIComponent("/pages/sewing/sewing")}` });
}
function contact() {
  // #ifdef H5
  window.location.href = siteUrl("/#contact");
  // #endif
}

// 帮助里的“试一试”：?p= 后面是参数 JSON（例 {"n":6000}），夹到范围里再算
function startWith(raw?: string) {
  if (!raw) return;
  try {
    const p = JSON.parse(decodeURIComponent(raw));
    for (const grp of schema.value) for (const x of grp.params) {
      if (!(x.key in p)) continue;
      const v = p[x.key];
      params[x.key] = x.choices.length ? v : Math.min(x.max, Math.max(x.min, Number(v)));
      open[grp.key] = true;
    }
  } catch { /* not JSON: ignore */ }
}
async function init() {
  if (props.startMachine && MACHINE_KEYS.includes(props.startMachine)) machine.value = props.startMachine;
  await loadSchema();
  startWith(props.startParams);
  compute();
  loadMe();
  // #ifdef H5
  fetch(protoSrc.value, { method: "GET" }).then((r) => (protoOk.value = r.ok)).catch(() => (protoOk.value = false));
  // #endif
}
watch(lang, () => setTimeout(syncProto, 800));
defineExpose({ init, loadMe });
init();
</script>

<style scoped>
.sew { max-width: 1280px; }
.head { margin-bottom: 12px; }
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); }
.h2 { display: block; font-size: 17px; font-weight: 700; color: var(--wq-ink); }
.lead { display: block; color: var(--wq-muted); margin-top: 6px; line-height: 1.7; max-width: 860px; }
.who { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-top: 10px; }
.chip { font-size: 13px; padding: 4px 10px; border-radius: 999px; background: #f1f3f2; color: var(--wq-muted); }
.chip.ok { background: #e6f4ea; color: #2e7d4f; }
.link { color: var(--wq-link); font-size: 14px; cursor: pointer; white-space: nowrap; }
.link.danger { color: var(--wq-muted); }
.link.help { font-weight: 600; }
.libpick { margin: -2px 0 6px; }
.libitem { display: block; font-size: 12.5px; padding: 4px 8px; margin-top: 4px; border: 1px dashed #b9cfe4; border-radius: 6px; cursor: pointer; color: #1d4e75; }
.libitem:hover { background: #f3f7fb; }
.muted { color: var(--wq-muted); }
.small { font-size: 12px; }
.hint { display: block; color: var(--wq-muted); font-size: 13px; line-height: 1.6; margin-top: 8px; }
.pbar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px; }
.psel { font-size: 14px; cursor: pointer; padding: 6px 4px; }
.pname { font-weight: 600; color: var(--wq-ink); }
.input { border: 1px solid var(--wq-line); border-radius: 6px; padding: 0 8px; height: 34px; line-height: 34px; font-size: 14px; box-sizing: border-box; background: #fff; }
.pn { flex: 1; min-width: 180px; }
.btn { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 7px 14px; border-radius: 6px; cursor: pointer; white-space: nowrap; font-size: 14px; display: inline-block; text-align: center; }
.btn.ghost { background: #fff; border: 1px solid var(--wq-line); }
.btn.disabled { opacity: .5; }
.cols { display: flex; gap: 16px; align-items: flex-start; }
.left { width: 340px; flex: none; background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 12px; max-height: calc(100vh - 120px); overflow-y: auto; position: sticky; top: 12px; }
.right { flex: 1; min-width: 0; }
.lhead { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.grp { border-top: 1px solid var(--wq-line); }
.gt { display: flex; justify-content: space-between; padding: 9px 2px; font-weight: 600; color: var(--wq-ink); cursor: pointer; font-size: 14px; }
.prm { padding: 4px 0 8px; }
.pl { display: block; font-size: 13px; color: var(--wq-ink); }
.num { display: flex; align-items: center; gap: 6px; }
.sl { flex: 1; margin: 4px 6px 4px 0; }
.ni { width: 74px; flex: none; text-align: right; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.opt { font-size: 13px; padding: 4px 10px; border: 1px solid var(--wq-line); border-radius: 999px; cursor: pointer; background: #fff; }
.opt.on { background: #1d4e75; border-color: #1d4e75; color: #fff; }
.summary { padding: 10px 14px; border-radius: 8px; font-weight: 600; margin-bottom: 8px; background: #f1f3f2; }
.summary.ok { background: #e6f4ea; color: #2e7d4f; }
.summary.warn { background: #fff3d6; color: #7a5a00; }
.summary.bad { background: #fdecea; color: var(--wq-danger); }
.tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--wq-line); flex-wrap: wrap; }
.tab { padding: 8px 14px; cursor: pointer; font-size: 14px; color: var(--wq-muted); border-bottom: 2px solid transparent; }
.tab.on { color: var(--wq-ink); font-weight: 600; border-bottom-color: #1d4e75; }
.pane { background: #fff; border: 1px solid var(--wq-line); border-top: 0; border-radius: 0 0 8px 8px; padding: 14px; }
.mbar { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.mopt { padding: 8px 18px; border-radius: 8px; border: 1px solid var(--wq-line); background: #fff; cursor: pointer; font-weight: 600; font-size: 15px; }
.mopt.on { background: #1d4e75; color: #fff; border-color: #1d4e75; }
.tbl { border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; font-size: 13px; }
.tr { display: flex; border-top: 1px solid var(--wq-line); }
.tr:first-child { border-top: 0; }
.tr.th { background: #eaf2fa; font-weight: 600; }
.td { flex: 1; padding: 6px 8px; min-width: 0; }
.tr:last-child { font-weight: 600; }
.frame.flat { aspect-ratio: 4 / 3; }
.csv { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 6px; }
.frame { position: relative; width: 100%; aspect-ratio: 16 / 10; background: #0b1220; border-radius: 6px; overflow: hidden; }
.proto { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
.empty { color: #c9d4d8; padding: 40px; text-align: center; }
.kgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 8px; margin-top: 12px; }
.kc { border: 1px solid var(--wq-line); border-radius: 6px; padding: 8px 10px; }
.kl { display: block; font-size: 12px; color: var(--wq-muted); }
.kv { display: block; font-size: 15px; font-weight: 600; color: var(--wq-ink); margin-top: 2px; }
.trial { margin-bottom: 10px; }
.dots { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px; }
.dot { width: 14px; height: 14px; border-radius: 50%; background: #2e9e6a; display: inline-block; }
.dot.skip { background: #e8913a; }
.dot.hit, .dot.cut, .dot.break { background: #c0392b; }
.chk { display: flex; gap: 10px; padding: 9px 0; border-top: 1px solid var(--wq-line); }
.lamp { width: 12px; height: 12px; border-radius: 50%; margin-top: 5px; flex: none; background: #2e9e6a; }
.lamp.warn, .cst.warn { background: #e8913a; }
.lamp.bad, .cst.bad { background: #c0392b; }
.cbody { flex: 1; min-width: 0; }
.crow { display: flex; justify-content: space-between; gap: 10px; }
.cname { font-weight: 600; color: var(--wq-ink); font-size: 14px; }
.cst { font-size: 12px; color: #fff; background: #2e9e6a; border-radius: 999px; padding: 1px 8px; white-space: nowrap; height: 18px; }
.cval { display: block; font-size: 13px; margin-top: 2px; }
.cadv { display: block; font-size: 13px; color: #8a4b00; margin-top: 2px; }
.ct { display: block; font-weight: 600; color: var(--wq-ink); font-size: 14px; margin: 12px 0 6px; }
.svg { width: 100%; height: auto; display: block; }
.charts { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }
.part { border-top: 1px solid var(--wq-line); padding: 6px 0; }
.pt { display: block; font-weight: 600; font-size: 14px; color: var(--wq-ink); }
.dim { display: flex; justify-content: space-between; font-size: 13px; padding: 2px 0; gap: 10px; }
.dv { font-variant-numeric: tabular-nums; }
.para { display: block; font-size: 13px; line-height: 1.7; }
.step { display: flex; gap: 10px; padding: 6px 0; border-top: 1px solid var(--wq-line); }
.sn { width: 22px; height: 22px; border-radius: 50%; background: #1d4e75; color: #fff; font-size: 12px; text-align: center; line-height: 22px; flex: none; }
.note { background: #fff3d6; color: #7a5a00; padding: 10px 14px; border-radius: 8px; margin-bottom: 10px; line-height: 1.6; font-size: 14px; }
.lrow { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; font-size: 13px; }
.exp { display: flex; justify-content: space-between; padding: 10px 12px; border: 1px solid var(--wq-line); border-radius: 6px; margin-bottom: 6px; cursor: pointer; font-size: 14px; }
.exp:hover { background: #f7f9f8; }
.exp.locked { opacity: .55; }
.fc { margin-top: 14px; border-top: 1px solid var(--wq-line); padding-top: 12px; }
.fc .btn { margin-top: 8px; }
.adm { margin-top: 20px; background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 14px; }
.grant { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; }
.grant .input { flex: 1; min-width: 150px; }
.g-row { display: flex; justify-content: space-between; gap: 10px; padding: 8px 0; border-top: 1px solid var(--wq-line); font-size: 14px; flex-wrap: wrap; }
@media (max-width: 900px) {
  .cols { flex-direction: column; }
  .left { width: 100%; box-sizing: border-box; position: static; max-height: none; }
}
</style>
