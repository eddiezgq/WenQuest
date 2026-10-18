<template>
  <!-- 第 41 轮：缝纫机设计软件接入问渠 CAE。零件强度与疲劳、机壳固有频率、机构动力学、主轴电机选型交给数字工厂计算服务；
       设计优化（本软件公式）在网关里秒级算完，“采用”一键回填参数。只给已开通的单位用。 -->
  <view class="cae">
    <view v-if="!licensed" class="note">{{ t("sew.cae.locked") }}</view>
    <template v-else>
      <view class="top">
        <text class="lead">{{ t("sew.cae.lead") }}</text>
        <text v-if="opt && !opt.connected" class="chip bad">{{ t("sew.cae.offline") }}</text>
        <text v-else-if="opt && opt.quota" class="chip">{{ t("sew.cae.quota", { used: opt.quota.used, limit: opt.quota.limit }) }}</text>
      </view>

      <!-- 零件强度与疲劳 -->
      <view v-if="opt && opt.parts.length" class="box">
        <text class="bt">{{ t("sew.cae.fea") }}</text>
        <text class="hint">{{ t("sew.cae.feaNote") }}</text>
        <view class="row">
          <text v-for="p in opt.parts" :key="p.key" class="opt" :class="{ on: part === p.key }" @click="part = p.key">{{ L(p) }}</text>
        </view>
        <text class="hint">{{ t("sew.cae.material", { m: String(params.mat || "45-QT") }) }}</text>
        <view class="btn" :class="{ disabled: !canRun }" @click="submit('fea')">{{ t("sew.cae.run") }}</view>
      </view>

      <!-- 机壳固有频率 -->
      <view class="box">
        <text class="bt">{{ t("sew.cae.frame") }}</text>
        <text class="hint">{{ t("sew.cae.frameNote") }}</text>
        <!-- #ifdef H5 -->
        <view class="row">
          <view class="btn ghost sm" @click="chooseFile">{{ t("sew.cae.choose") }}</view>
          <text class="file">{{ frameFile ? frameFile.name : t("sew.cae.noFile") }}</text>
          <text v-for="m in FRAME_MATS" :key="m" class="opt" :class="{ on: fmat === m }" @click="fmat = m">{{ m }}</text>
        </view>
        <view class="btn" :class="{ disabled: !canRun || !frameFile }" @click="submitFrame">{{ t("sew.cae.run") }}</view>
        <!-- #endif -->
      </view>

      <!-- 机构动力学 + 主轴电机 -->
      <view v-if="opt && (opt.kinds.mbd || opt.kinds.motor)" class="box">
        <text class="bt">{{ t("sew.cae.drive") }}</text>
        <text class="hint">{{ t("sew.cae.driveNote") }}</text>
        <view class="row">
          <view v-if="opt.kinds.mbd" class="btn" :class="{ disabled: !canRun }" @click="submit('mbd')">{{ t("sew.cae.runMbd") }}</view>
          <view v-if="opt.kinds.motor" class="btn ghost" :class="{ disabled: !canRun }" @click="pickMotor">{{ busy === "motor" ? t("sew.making") : t("sew.cae.runMotor") }}</view>
        </view>
        <view v-if="motor" class="res">
          <text class="para">{{ t("sew.cae.motorSum", { peak: motor.peak_nm.toFixed(2), rms: motor.rms_nm.toFixed(2), p: Math.round(motor.power_w), n: motor.n, s: motor.safety }) }}</text>
          <text class="para strong">{{ motor.pick ? t("sew.cae.motorPick", { name: motor.pick.name }) : t("sew.cae.motorNone") }}</text>
          <view class="tbl">
            <view class="tr th"><text class="td">{{ t("sew.cae.motorName") }}</text><text class="td">{{ t("sew.cae.motorRated") }}</text>
              <text class="td">{{ t("sew.cae.motorPeak") }}</text><text class="td">{{ t("sew.cae.motorMax") }}</text><text class="td" /></view>
            <view v-for="r in motor.rows" :key="r.name" class="tr"><text class="td">{{ r.name }}</text><text class="td">{{ r.rated_nm }} N·m</text>
              <text class="td">{{ r.peak_nm }} N·m</text><text class="td">{{ r.max_rpm }}</text><text class="td" :class="r.ok ? 'okc' : 'badc'">{{ r.ok ? "✓" : "✕" }}</text></view>
          </view>
          <svg class="svg" viewBox="0 0 300 120" v-html="spark(motor.torque, 'N·m')" />
          <text class="hint">{{ t("sew.cae.motorSrc", { s: motor.source }) }}</text>
        </view>
      </view>

      <!-- 设计优化 -->
      <view v-if="opt && opt.goals.length" class="box">
        <text class="bt">{{ t("sew.cae.opt") }}</text>
        <text class="hint">{{ t("sew.cae.optNote") }}</text>
        <view class="row">
          <text v-for="g in opt.goals" :key="g.key" class="opt" :class="{ on: goal === g.key }" @click="runOpt(g.key)">{{ L(g) }}</text>
        </view>
        <text v-if="busy === 'opt'" class="hint">{{ t("sew.computing") }}</text>
        <view v-if="optRes && !busy" class="res">
          <text v-if="!optRes.candidates.length" class="hint">{{ t("sew.cae.optNone") }}</text>
          <view v-for="(c, i) in optRes.candidates" :key="i" class="cand">
            <view class="cbody">
              <text class="para strong">{{ i + 1 }}. {{ fmtParams(c.params) }}</text>
              <text class="para muted">{{ L(optRes.unit) }}：{{ c.value }}<text v-if="noteText(c.note)"> · {{ noteText(c.note) }}</text>
                · {{ t("sew.cae.lamps", { b: c.bad, w: c.warn }) }}</text>
            </view>
            <view class="btn ghost sm" @click="emit('apply', c.params)">{{ t("sew.cae.apply") }}</view>
          </view>
        </view>
      </view>

      <!-- 任务与结果 -->
      <view class="box">
        <view class="bh"><text class="bt">{{ t("sew.cae.jobs") }}</text><text class="link" @click="loadJobs">{{ t("sew.cae.refresh") }}</text></view>
        <text v-if="!jobs.length" class="hint">{{ t("sew.cae.noJobs") }}</text>
        <view v-for="j in jobs" :key="j.jid" class="job" :class="{ on: sel && sel.id === j.jid }" @click="openJob(j.jid)">
          <text class="jt">{{ j.title }}</text>
          <text class="js" :class="j.status">{{ statusText(j) }}</text>
        </view>
        <view v-if="sel" class="res">
          <text class="ct">{{ sel.title }}</text>
          <text v-if="sel.status !== 'done'" class="hint">{{ statusText(sel) }}<text v-if="sel.error"> · {{ sel.error }}</text></text>
          <template v-if="sel.result">
            <view v-for="c in sel.result.checks" :key="c.key" class="chk">
              <text class="lamp" :class="c.state" />
              <view class="cbody"><view class="crow"><text class="cname">{{ lang === "en" ? c.en : c.zh }}</text>
                <text class="cst" :class="c.state">{{ t("sew.state." + c.state) }}</text></view>
                <text class="cval">{{ c.value }}<text class="muted">　{{ t("sew.criterion") }} {{ c.limit }}</text></text></view>
            </view>
            <view v-if="sel.kind === 'fea'" class="kgrid">
              <view class="kc"><text class="kl">{{ t("sew.cae.vm") }}</text><text class="kv">{{ n1(sel.result.vm_max_mpa) }} MPa</text></view>
              <view class="kc"><text class="kl">{{ t("sew.cae.umax") }}</text><text class="kv">{{ n3(sel.result.u_max_mm) }} mm</text></view>
              <view v-if="sel.result.analytic" class="kc"><text class="kl">{{ L(sel.result.analytic) }}</text>
                <text class="kv">{{ sel.result.analytic.value }} {{ sel.result.analytic.unit }}</text></view>
              <view class="kc"><text class="kl">{{ t("sew.cae.phi") }}</text><text class="kv">{{ sel.result.phi }}°</text></view>
            </view>
            <view v-if="sel.kind === 'frame'" class="res">
              <text class="para">{{ t("sew.cae.freqs") }}：{{ (sel.result.freqs_hz || []).map((x: number) => x.toFixed(0)).join(" / ") }} Hz</text>
              <view v-if="sel.result.apply" class="row">
                <text class="para">{{ t("sew.cae.fnApply", { f: sel.result.apply.fn }) }}</text>
                <view class="btn ghost sm" @click="emit('apply', sel.result.apply)">{{ t("sew.cae.apply") }}</view>
              </view>
            </view>
            <view v-if="sel.kind === 'mbd'" class="res">
              <text class="para">{{ t("sew.cae.mbdSum", { a: n3(sel.result.torque_peak_mbd), b: n3(sel.result.torque_peak_formula) }) }}</text>
              <svg class="svg" viewBox="0 0 300 120" v-html="spark(sel.result.series, 'N·m')" />
            </view>
            <!-- #ifdef H5 -->
            <image v-if="img" class="img" :src="img" mode="widthFix" />
            <!-- #endif -->
            <view class="row">
              <view class="btn ghost" @click="getReport">{{ busy === "report" ? t("sew.making") : t("sew.cae.report") }}</view>
              <text class="hint">{{ t("sew.cae.inCalc") }}</text>
            </view>
          </template>
        </view>
      </view>
      <text v-if="msg" class="hint err">{{ msg }}</text>
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { ApiError, BASE, request, token } from "../../api";
import { errorText, locale, t } from "../../i18n";

const props = defineProps<{ machine: string; params: Record<string, number | string>; licensed: boolean; active: boolean; labels?: Record<string, string> }>();
const emit = defineEmits<{ (e: "apply", p: Record<string, number | string>): void }>();

interface Opt { connected: boolean; parts: { key: string; zh: string; en: string }[]; goals: { key: string; zh: string; en: string }[];
  quota: { used: number; limit: number } | null; kinds: Record<string, boolean> }
const FRAME_MATS = ["HT200", "QT500-7", "Q235", "6061-T6"];
const opt = ref<Opt | null>(null);
const part = ref("");
const goal = ref("");
const optRes = ref<any>(null);
const motor = ref<any>(null);
const jobs = ref<any[]>([]);
const sel = ref<any>(null);
const img = ref("");
const msg = ref("");
const busy = ref("");
const fmat = ref("HT200");
const frameFile = ref<File | null>(null);
const lang = computed(() => (locale.value === "en" ? "en" : "zh"));
const L = (x: { zh: string; en: string }) => (lang.value === "en" ? x.en || x.zh : x.zh || x.en);
const canRun = computed(() => !!opt.value?.connected && !busy.value);
const n1 = (v: number | null | undefined) => (v == null ? "—" : Number(v).toFixed(1));
const n3 = (v: number | null | undefined) => (v == null ? "—" : Number(v).toFixed(3));
const fail = (e: unknown) => { msg.value = errorText(e instanceof ApiError ? e.code : "unknown"); };

async function load() {
  if (!props.licensed) return;
  msg.value = "";
  try {
    opt.value = await request<Opt>("GET", `/api/v1/sewing/cae/options?machine=${props.machine}`);
    part.value = opt.value.parts[0]?.key || "";
  } catch (e) { fail(e); }
  goal.value = "";
  optRes.value = motor.value = sel.value = null;
  await loadJobs();
}
async function loadJobs() {
  try { jobs.value = (await request<{ jobs: any[] }>("GET", `/api/v1/sewing/cae/jobs?machine=${props.machine}`)).jobs; } catch { jobs.value = []; }
  if (jobs.value.some((j) => j.status === "queued" || j.status === "running")) poll();
}

async function submit(kind: "fea" | "mbd") {
  if (!canRun.value) return;
  busy.value = kind;
  msg.value = "";
  try {
    const r = await request<{ id: string }>("POST", `/api/v1/sewing/cae/${kind}`, { machine: props.machine, params: { ...props.params }, part: part.value }, 120000);
    await loadJobs();
    await openJob(r.id);
    refreshQuota();
  } catch (e) { fail(e); }
  busy.value = "";
}
// uni-app 的 <input> 在网页上不是文件框，这里临时建一个原生的
function chooseFile() {
  // #ifdef H5
  const el = document.createElement("input");
  el.type = "file";
  el.accept = ".step,.stp";
  el.onchange = () => { frameFile.value = el.files?.[0] || null; };
  el.click();
  // #endif
}
async function submitFrame() {
  if (!canRun.value || !frameFile.value) return;
  busy.value = "frame";
  msg.value = "";
  // #ifdef H5
  try {
    const fd = new FormData();
    fd.append("file", frameFile.value);
    fd.append("machine", props.machine);
    fd.append("params", JSON.stringify(props.params));
    fd.append("material", fmat.value);
    const res = await fetch(`${BASE}/api/v1/sewing/cae/frame`, { method: "POST", headers: { Authorization: `Bearer ${token.value}` }, body: fd });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new ApiError(body.error || `http_${res.status}`, res.status);
    await loadJobs();
    await openJob(body.id);
    refreshQuota();
  } catch (e) { fail(e); }
  // #endif
  busy.value = "";
}
async function refreshQuota() {
  try { const o = await request<Opt>("GET", `/api/v1/sewing/cae/options?machine=${props.machine}`); if (opt.value) opt.value.quota = o.quota; } catch { /* keep */ }
}
async function pickMotor() {
  if (!canRun.value) return;
  busy.value = "motor";
  msg.value = "";
  try { motor.value = await request("POST", "/api/v1/sewing/cae/motor", { machine: props.machine, params: { ...props.params } }); } catch (e) { fail(e); }
  busy.value = "";
}
async function runOpt(k: string) {
  if (busy.value) return;
  goal.value = k;
  busy.value = "opt";
  msg.value = "";
  optRes.value = null;
  try { optRes.value = await request("POST", "/api/v1/sewing/optimize", { machine: props.machine, params: { ...props.params }, goal: k }, 120000); } catch (e) { fail(e); }
  busy.value = "";
}

// ---------- 任务 ----------
let timer: any = null;
function poll() {
  clearTimeout(timer);
  timer = setTimeout(async () => {
    if (!props.active) return poll();
    await loadJobs();
    if (sel.value && sel.value.status !== "done" && sel.value.status !== "failed") await openJob(sel.value.id, true);
  }, 4000);
}
async function openJob(id: string, quiet = false) {
  try {
    const j = await request<any>("GET", `/api/v1/sewing/cae/jobs/${id}`, undefined, 180000);
    const changed = !sel.value || sel.value.id !== id || (sel.value.status !== "done" && j.status === "done");
    sel.value = j;
    if (changed) { img.value = ""; if (j.status === "done" && (j.kind === "fea" || j.kind === "frame")) loadImage(id); }
    if (j.status === "done" && quiet) loadJobs();
    if (j.status !== "done" && j.status !== "failed") poll();
  } catch (e) { if (!quiet) fail(e); }
}
async function authed(path: string) {
  const res = await fetch(`${BASE}${path}`, { headers: { Authorization: `Bearer ${token.value}` } });
  if (!res.ok) {
    let code = `http_${res.status}`;
    try { code = (await res.json()).error || code; } catch { /* not json */ }
    throw new ApiError(code, res.status);
  }
  return res;
}
async function loadImage(id: string) {
  // #ifdef H5
  try {
    const b = await (await authed(`/api/v1/sewing/cae/jobs/${id}/image.png`)).blob();
    if (sel.value?.id === id) { if (img.value) URL.revokeObjectURL(img.value); img.value = URL.createObjectURL(b); }
  } catch { img.value = ""; }
  // #endif
}
async function getReport() {
  if (!sel.value || busy.value) return;
  busy.value = "report";
  // #ifdef H5
  try {
    const res = await authed(`/api/v1/sewing/cae/jobs/${sel.value.id}/report.docx`);
    const m = /filename\*=UTF-8''([^;]+)/.exec(res.headers.get("content-disposition") || "");
    const url = URL.createObjectURL(await res.blob());
    const a = document.createElement("a");
    a.href = url;
    a.download = m ? decodeURIComponent(m[1]) : "CAE.docx";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  } catch (e) { fail(e); }
  // #endif
  busy.value = "";
}
function statusText(j: any) {
  if (j.status === "queued") return j.position ? t("sew.cae.queued", { n: j.position }) : t("sew.cae.st.queued");
  return t("sew.cae.st." + (["running", "done", "failed"].includes(j.status) ? j.status : "unknown"));
}

// ---------- 显示 ----------
function fmtParams(p: Record<string, number | string>) {
  return Object.entries(p).map(([k, v]) => `${props.labels?.[k] || k} = ${v}`).join("，");
}
const NOTES = ["fmax", "mu_min", "margin", "pre", "neg", "gamma_min", "swing", "arc", "eps_pct", "window"];
function noteText(n: Record<string, unknown>) {
  return Object.entries(n || {}).map(([k, v]) => `${NOTES.includes(k) ? t("sew.cae.note." + k) : k} ${Array.isArray(v) ? v.join("…") : v}`).join("，");
}
function spark(ys: number[], unit: string) {
  if (!ys || !ys.length) return "";
  let lo = Math.min(...ys, 0), hi = Math.max(...ys, 0);
  if (hi - lo < 1e-9) hi = lo + 1;
  const X = (i: number) => 34 + (258 * i) / Math.max(1, ys.length - 1), Y = (v: number) => 104 - (92 * (v - lo)) / (hi - lo);
  let s = `<rect x="34" y="12" width="258" height="92" fill="#fff" stroke="#e1e6ea"/>`;
  s += `<line x1="34" x2="292" y1="${Y(0)}" y2="${Y(0)}" stroke="#8a9aa8" stroke-width="0.6"/>`;
  s += `<text x="30" y="${Y(hi) + 4}" font-size="9" text-anchor="end" fill="#6b7b88">${hi.toFixed(2)}</text>`;
  s += `<text x="30" y="${Y(lo) + 3}" font-size="9" text-anchor="end" fill="#6b7b88">${lo.toFixed(2)}</text>`;
  s += `<text x="292" y="116" font-size="9" text-anchor="end" fill="#6b7b88">${unit}</text>`;
  s += `<polyline fill="none" stroke="#2d6fb3" stroke-width="1.5" points="${ys.map((v, i) => `${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(" ")}"/>`;
  return s;
}

watch(() => [props.machine, props.licensed], load, { immediate: true });
onBeforeUnmount(() => clearTimeout(timer));
</script>

<style scoped>
.cae { font-size: 14px; }
.top { display: flex; gap: 10px; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; }
.lead { flex: 1; min-width: 240px; color: var(--wq-muted); line-height: 1.7; font-size: 13px; }
.chip { font-size: 12px; padding: 3px 10px; border-radius: 999px; background: #eaf2fa; color: #1d4e75; white-space: nowrap; }
.chip.bad { background: #fdecea; color: var(--wq-danger); }
.note { background: #fff3d6; color: #7a5a00; padding: 10px 14px; border-radius: 8px; line-height: 1.6; }
.box { border-top: 1px solid var(--wq-line); padding: 12px 0; }
.bh { display: flex; justify-content: space-between; align-items: center; }
.bt { display: block; font-weight: 700; color: var(--wq-ink); font-size: 15px; }
.hint { display: block; color: var(--wq-muted); font-size: 13px; line-height: 1.6; margin-top: 4px; }
.hint.err { color: var(--wq-danger); }
.row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 8px 0; }
.opt { font-size: 13px; padding: 4px 10px; border: 1px solid var(--wq-line); border-radius: 999px; cursor: pointer; background: #fff; }
.opt.on { background: #1d4e75; border-color: #1d4e75; color: #fff; }
.btn { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 7px 14px; border-radius: 6px; cursor: pointer; white-space: nowrap; font-size: 14px; display: inline-block; margin-top: 6px; }
.btn.ghost { background: #fff; border: 1px solid var(--wq-line); }
.btn.sm { padding: 4px 10px; font-size: 13px; margin-top: 0; }
.btn.disabled { opacity: .5; cursor: not-allowed; }
.file { font-size: 13px; }
.link { color: var(--wq-link); font-size: 13px; cursor: pointer; }
.res { margin-top: 8px; }
.para { display: block; font-size: 13px; line-height: 1.7; }
.strong { font-weight: 600; color: var(--wq-ink); }
.muted { color: var(--wq-muted); }
.cand { display: flex; gap: 10px; align-items: center; padding: 6px 0; border-top: 1px dashed var(--wq-line); }
.cbody { flex: 1; min-width: 0; }
.job { display: flex; justify-content: space-between; gap: 10px; padding: 7px 8px; border-radius: 6px; cursor: pointer; }
.job:hover, .job.on { background: #f3f6f9; }
.jt { flex: 1; min-width: 0; }
.js { font-size: 12px; color: var(--wq-muted); white-space: nowrap; }
.js.done { color: #2e7d4f; }
.js.failed { color: var(--wq-danger); }
.ct { display: block; font-weight: 600; color: var(--wq-ink); margin: 10px 0 4px; }
.chk { display: flex; gap: 10px; padding: 8px 0; border-top: 1px solid var(--wq-line); }
.lamp { width: 12px; height: 12px; border-radius: 50%; margin-top: 5px; flex: none; background: #2e9e6a; }
.lamp.warn, .cst.warn { background: #e8913a; }
.lamp.bad, .cst.bad { background: #c0392b; }
.crow { display: flex; justify-content: space-between; gap: 10px; }
.cname { font-weight: 600; color: var(--wq-ink); }
.cst { font-size: 12px; color: #fff; background: #2e9e6a; border-radius: 999px; padding: 1px 8px; white-space: nowrap; height: 18px; }
.cval { display: block; font-size: 13px; margin-top: 2px; }
.kgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 8px; margin-top: 8px; }
.kc { border: 1px solid var(--wq-line); border-radius: 6px; padding: 8px 10px; }
.kl { display: block; font-size: 12px; color: var(--wq-muted); }
.kv { display: block; font-size: 15px; font-weight: 600; color: var(--wq-ink); margin-top: 2px; }
.img { width: 100%; max-width: 620px; margin-top: 10px; border: 1px solid var(--wq-line); border-radius: 6px; }
.svg { width: 100%; max-width: 560px; height: auto; display: block; margin-top: 6px; }
.tbl { border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; font-size: 13px; margin-top: 6px; }
.tr { display: flex; border-top: 1px solid var(--wq-line); }
.tr:first-child { border-top: 0; }
.tr.th { background: #eaf2fa; font-weight: 600; }
.td { flex: 1; padding: 5px 8px; min-width: 0; }
.okc { color: #2e7d4f; font-weight: 700; }
.badc { color: var(--wq-danger); }
</style>
