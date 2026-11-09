<template>
  <AppShell nav="textbook" :title="title">
    <view class="rp" :class="{ split: labOpen && !!st?.lab_url }">
      <!-- top bar -->
      <view class="bar">
        <view class="b-title">
          <text class="b-name">{{ title }}</text>
          <text class="wq-tag" :class="statusClass">{{ statusText }}</text>
          <text v-if="!readonly" class="wq-muted save">{{ saveText }}</text>
        </view>
        <view class="b-actions">
          <!-- #ifdef H5 -->
          <view v-if="st?.lab_url && !teacherView" class="wq-btn small" @click="labOpen = !labOpen">{{ labOpen ? t("report.hideLab") : t("report.showLab") }}</view>
          <!-- #endif -->
          <view v-if="!teacherView" class="wq-btn small" :class="{ disabled: busy }" @click="exportAs('docx')">{{ t("report.exportWord") }}</view>
          <view v-if="st?.pdf && !teacherView" class="wq-btn small" :class="{ disabled: busy }" @click="exportAs('pdf')">{{ t("report.exportPdf") }}</view>
          <view v-if="!teacherView && !viewing" class="wq-btn primary small" :class="{ disabled: busy || readonly }" @click="submit">{{ t("report.submit") }}</view>
        </view>
      </view>
      <text v-if="error" class="wq-error block">{{ error }}</text>
      <view v-if="viewing" class="banner">
        <text>{{ t("report.viewingVersion", { n: viewing }) }}</text>
        <text v-if="!teacherView" class="wq-link" @click="backToCurrent">{{ t("report.backToCurrent") }}</text>
      </view>
      <view v-else-if="st && st.status === 'submitted' && !teacherView" class="banner ok">{{ t("report.submittedNote") }}</view>
      <view v-if="st && !teacherView && !st.assignments.length && !viewing" class="banner muted">{{ t("report.noAssignment") }}</view>
      <view v-if="versions.length" class="versions">
        <text class="wq-muted">{{ t("report.versions") }}</text>
        <text v-for="v in versions" :key="v.ver" class="vchip" :class="{ on: viewing === v.ver }" @click="viewVersion(v.ver)">
          {{ t("report.versionN", { n: v.ver }) }} · {{ formatDate(v.at) }}
        </text>
      </view>

      <view class="cols">
        <!-- the report -->
        <view v-if="doc" class="paper">
          <template v-for="(b, bi) in doc.blocks" :key="bi">
            <view v-if="b.t === 'title'" class="d-title"><text class="zh">{{ b.zh }}</text><text class="en">{{ b.en }}</text></view>
            <view v-else-if="b.t === 'fields'" class="fields">
              <view v-for="it in b.items" :key="it.k" class="field">
                <text class="f-l">{{ it.label }}</text>
                <input v-model="it.v" class="f-in" :disabled="readonly || it.fixed" @input="changed" />
              </view>
            </view>
            <text v-else-if="b.t === 'note'" class="note">{{ b.text }}</text>
            <view v-else-if="b.t === 'h'" class="d-h"><text class="zh">{{ b.zh }}</text><text class="en">{{ b.en }}</text></view>
            <view v-else-if="b.t === 'p'" class="d-p"><text>{{ b.zh }}</text><text class="en block">{{ b.en }}</text></view>
            <text v-else-if="b.t === 'strong'" class="d-strong">{{ b.text }}</text>
            <text v-else-if="b.t === 'label'" class="d-label">{{ b.text }}</text>
            <view v-else-if="b.t === 'prompt'" class="d-prompt"><text>{{ b.zh }}</text><text class="en block">{{ b.en }}</text></view>
            <view v-else-if="b.t === 'text'" class="d-text">
              <textarea v-model="b.v" class="area" :class="{ ro: readonly }" auto-height :maxlength="20000" :disabled="readonly"
                        :style="{ minHeight: `${Math.max(2, b.lines) * 26}px` }" :placeholder="readonly ? '' : t('report.writeHere')" @input="changed" />
              <view v-if="hasMath(b.v)" class="preview"><MathContent :html="mathHtml(b.v)" /></view>
              <view v-if="b.id === 'process' && !readonly && canDraw" class="wq-btn small fig-btn" @click="openChart">＋ {{ t("report.addChart") }}</view>
            </view>
            <view v-else-if="b.t === 'table'" class="d-table">
              <text class="tb-title">{{ b.title[0] }}<text class="en"> {{ b.title[1] }}</text></text>
              <view class="tb-scroll">
                <view class="tb">
                  <view class="tr th"><text v-for="(h, j) in b.head" :key="j" class="td">{{ h }}</text><text v-if="b.grow && !readonly" class="td x" /></view>
                  <view v-for="(r, i) in b.rows" :key="i" class="tr">
                    <template v-for="(c, j) in r" :key="j">
                      <input v-if="cellEditable(b, i, j)" v-model="b.rows[i][j]" class="td cell" :disabled="readonly" @input="changed" />
                      <text v-else class="td fixed">{{ c }}</text>
                    </template>
                    <text v-if="b.grow && !readonly" class="td x wq-link" @click="dropRow(b, i)">✕</text>
                  </view>
                  <text v-if="b.records && !b.rows.length" class="tb-empty wq-muted">{{ st?.lab_url ? t("report.recordsHint") : t("report.recordsHintNoLab") }}</text>
                </view>
              </view>
              <text v-if="b.grow && !readonly" class="wq-link add-row" @click="addRow(b)">＋ {{ t("report.addRow") }}</text>
            </view>
            <view v-else-if="b.t === 'check'" class="d-check">
              <view v-for="(o, i) in b.options" :key="i" class="ck" @click="toggle(b, i)">
                <text class="box">{{ b.v.includes(i) ? "☑" : "□" }}</text><text>{{ o[0] }}</text><text class="en"> {{ o[1] }}</text>
              </view>
              <view class="ck other"><text>{{ t("report.other") }}</text><input v-model="b.other" class="f-in" :disabled="readonly" @input="changed" /></view>
            </view>
            <view v-else-if="b.t === 'figure'" class="d-fig">
              <image class="fig-img" :src="'data:image/png;base64,' + b.png" mode="widthFix" />
              <input v-model="b.caption" class="cap" :disabled="readonly" @input="changed" />
              <text v-if="!readonly" class="wq-link danger" @click="dropFigure(bi)">{{ t("report.removeChart") }}</text>
            </view>
            <view v-else-if="b.t === 'rubric'" class="d-table rubric">
              <view class="tb">
                <view class="tr th"><text v-for="(h, j) in b.head" :key="j" class="td">{{ h }}</text></view>
                <view v-for="(r, i) in b.rows" :key="i" class="tr"><text v-for="(c, j) in r" :key="j" class="td fixed">{{ c }}</text></view>
              </view>
            </view>
          </template>
        </view>
        <text v-else-if="!error" class="wq-muted">{{ t("common.loading") }}</text>

        <!-- the virtual lab beside the report (H5) -->
        <!-- #ifdef H5 -->
        <view v-if="labOpen && st?.lab_url && !teacherView" class="labpane">
          <iframe ref="frame" class="labframe" :src="st.lab_url" :title="title" @load="hello"></iframe>
        </view>
        <!-- #endif -->
      </view>

      <!-- make a chart from two columns of a table -->
      <view v-if="chart.open" class="mask" @click.self="chart.open = false">
        <view class="dialog">
          <text class="wq-label">{{ t("report.chartTable") }}</text>
          <picker :range="tables.map((x) => x.title[0])" :value="chart.table" @change="(e: any) => { chart.table = +e.detail.value; chart.x = 0; chart.y = 1; draw(); }">
            <view class="pick">{{ tables[chart.table]?.title[0] }}</view>
          </picker>
          <text v-if="chart.byRow" class="wq-muted block">{{ t("report.chartByRow") }}</text>
          <view v-else class="wq-row">
            <view class="half"><text class="wq-label">{{ t("report.chartX") }}</text>
              <picker :range="cols" :value="chart.x" @change="(e: any) => { chart.x = +e.detail.value; draw(); }"><view class="pick">{{ cols[chart.x] }}</view></picker></view>
            <view class="half"><text class="wq-label">{{ t("report.chartY") }}</text>
              <picker :range="cols" :value="chart.y" @change="(e: any) => { chart.y = +e.detail.value; draw(); }"><view class="pick">{{ cols[chart.y] }}</view></picker></view>
          </view>
          <view class="wq-row">
            <text class="ck" @click="chart.line = !chart.line; draw()"><text class="box">{{ chart.line ? "☑" : "□" }}</text>{{ t("report.chartLine") }}</text>
            <text class="ck" @click="chart.fit = !chart.fit; draw()"><text class="box">{{ chart.fit ? "☑" : "□" }}</text>{{ t("report.chartFit") }}</text>
          </view>
          <image v-if="chart.ok" class="chart" :src="'data:image/png;base64,' + chart.png" mode="widthFix" />
          <text class="wq-muted block">{{ chart.note }}</text>
          <text class="wq-label">{{ t("report.chartCaption") }}</text>
          <input v-model="chart.caption" class="f-in wide" />
          <view class="wq-row actions">
            <view class="wq-btn primary" :class="{ disabled: !chart.ok }" @click="addChart">{{ t("report.chartAdd") }}</view>
            <view class="wq-btn" @click="chart.open = false">{{ t("common.cancel") }}</view>
          </view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onUnmounted, reactive, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import MathContent from "../../components/MathContent.vue";
import { ApiError } from "../../api";
import { confirmAction, downloadAuthed, type ReportBlock, type ReportDoc, type ReportState, type ReportVersion, reportApi } from "../../courseApi";
import { errorText, formatDate, locale, t } from "../../i18n";

type TableBlock = Extract<ReportBlock, { t: "table" }>;
const book = ref("");
const lab = ref("");
const wantCmid = ref(0);
const teacherView = ref(false);
const teacherUid = ref(0);
const st = ref<ReportState | null>(null);
const doc = ref<ReportDoc | null>(null);
const versions = ref<ReportVersion[]>([]);
const viewing = ref(0);
const error = ref("");
const busy = ref(false);
const saving = ref(false);
const dirty = ref(false);
const savedAt = ref(0);
const labOpen = ref(true);
const frame = ref<any>(null);
let timer: ReturnType<typeof setTimeout> | null = null;
let canDraw = false;
// #ifdef H5
canDraw = true;
// #endif

const title = computed(() => (doc.value ? (locale.value === "en" ? doc.value.title[1] : doc.value.title[0]) : t("report.title")));
const readonly = computed(() => teacherView.value || !!viewing.value || st.value?.status === "submitted");
const statusText = computed(() => (teacherView.value ? t("report.teacherView") : t("report.status." + (st.value?.status || "new"))));
const statusClass = computed(() => (st.value?.status === "submitted" ? "ok" : "accent"));
const saveText = computed(() => (saving.value ? t("common.saving") : dirty.value ? t("report.unsaved") : savedAt.value ? t("report.savedAt", { time: formatDate(savedAt.value) }) : ""));
const tables = computed(() => (doc.value?.blocks.filter((b) => b.t === "table" && !(b as TableBlock).records) || []) as TableBlock[]);

const fail = (e: unknown) => { error.value = errorText(e instanceof ApiError ? e.code : "unknown"); };
const hasMath = (s: string) => /\$[^$]+\$/.test(s || "");
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const mathHtml = (s: string) => esc(s).replace(/\$\$([^$]+)\$\$/g, "\\[$1\\]").replace(/\$([^$]+)\$/g, "\\($1\\)").replace(/\n/g, "<br>");

/** The template decides which cells are fillable: its empty and {{name}} cells, and every row added later. */
function cellEditable(b: TableBlock, i: number, j: number) {
  if (readonly.value) return false;
  const mask = st.value?.editable?.[b.id];
  if (!mask || i >= mask.length) return true;
  return !!mask[i][j];
}

async function load() {
  error.value = "";
  try {
    const s = await reportApi.get(book.value, lab.value);
    st.value = s;
    doc.value = s.doc;
    versions.value = s.versions;
    savedAt.value = s.updated;
    viewing.value = 0;
    dirty.value = false;
  } catch (e) { fail(e); }
}

async function loadTeacher(cmid: number, uid: number, ver = 0) {
  try {
    const r = await reportApi.studentReport(cmid, uid, ver);
    doc.value = r.doc;
    versions.value = r.versions;
    viewing.value = r.ver;
  } catch (e) { fail(e); }
}

function changed() {
  if (readonly.value) return;
  dirty.value = true;
  if (timer) clearTimeout(timer);
  timer = setTimeout(save, 1500);
}
async function save() {
  if (!dirty.value || !doc.value || readonly.value) return;
  saving.value = true;
  try {
    const r = await reportApi.save(book.value, lab.value, doc.value, st.value?.updated || 0);
    if (st.value) { st.value.updated = r.updated; st.value.status = "draft"; }
    savedAt.value = r.updated;
    dirty.value = false;
  } catch (e) {
    if (e instanceof ApiError && e.code === "report_changed") {
      if (await confirmAction(t("report.changedElsewhere"), t("report.reload"), t("common.cancel"))) await load();
    } else fail(e);
  } finally {
    saving.value = false;
  }
}

function addRow(b: TableBlock) { b.rows.push(b.head.map(() => "")); changed(); }
function dropRow(b: TableBlock, i: number) {
  if ((st.value?.editable?.[b.id]?.length || 0) > i) return;      // rows of the template stay
  b.rows.splice(i, 1); changed();
}
function toggle(b: Extract<ReportBlock, { t: "check" }>, i: number) {
  if (readonly.value) return;
  b.v = b.v.includes(i) ? b.v.filter((x) => x !== i) : [...b.v, i].sort();
  changed();
}
function dropFigure(i: number) { doc.value?.blocks.splice(i, 1); changed(); }

// ---------- the lab beside the report ----------
function hello() {
  // the lab page listens once its kit has started (3D labs load models first): say hello a few times
  [0, 1000, 3000, 8000].forEach((ms) => setTimeout(() => {
    try { frame.value?.contentWindow?.postMessage({ type: "wq-report-host" }, "*"); } catch { /* frame gone */ }
  }, ms));
}
function onMessage(e: MessageEvent) {
  const d: any = e.data || {};
  if (d.type !== "wq-lab-record" || !doc.value) return;
  if (frame.value && e.source !== frame.value.contentWindow) return;
  if (readonly.value) { uni.showToast({ title: t("report.cannotRecord"), icon: "none" }); return; }
  const rec = doc.value.blocks.find((b) => b.t === "table" && (b as TableBlock).records) as TableBlock | undefined;
  if (rec && rec.rows.length < 200) rec.rows.push([String(d.time || ""), String(d.scene || ""), String(d.params || ""), String(d.readings || "")].map((x) => x.slice(0, 200)));
  let n = 0;
  for (const [name, v] of Object.entries(d.values || {})) {
    const slot = st.value?.slots[name];
    if (!slot) continue;
    const tb = doc.value.blocks.find((b) => b.t === "table" && (b as TableBlock).id === slot[0]) as TableBlock | undefined;
    if (tb && tb.rows[slot[1]]) { tb.rows[slot[1]][slot[2]] = String(v).slice(0, 200); n++; }
  }
  uni.showToast({ title: n ? t("report.recordedFilled", { n }) : t("report.recorded"), icon: "none" });
  changed();
}
// #ifdef H5
window.addEventListener("message", onMessage);
onUnmounted(() => window.removeEventListener("message", onMessage));
// #endif
onUnmounted(() => { if (timer) clearTimeout(timer); });

// ---------- hand in, export, versions ----------
async function submit() {
  if (busy.value || readonly.value || !st.value) return;
  const list = st.value.assignments;
  if (!list.length) { uni.showToast({ title: t("report.noAssignment"), icon: "none" }); return; }
  let pick = list.find((a) => a.cmid === wantCmid.value) || list[0];
  if (list.length > 1 && !list.some((a) => a.cmid === wantCmid.value)) {
    const i = await new Promise<number>((res) => uni.showActionSheet({ itemList: list.map((a) => a.name), success: (r) => res(r.tapIndex), fail: () => res(-1) }));
    if (i < 0) return;
    pick = list[i];
  }
  if (!(await confirmAction(t("report.confirmSubmit", { name: pick.name }), t("report.submit"), t("common.cancel")))) return;
  busy.value = true;
  try {
    if (timer) clearTimeout(timer);
    await save();
    const r = await reportApi.submit(book.value, lab.value, pick.cmid);
    st.value.status = "submitted";
    versions.value = r.versions;
    uni.showToast({ title: t("report.submitted"), icon: "success" });
  } catch (e) { fail(e); } finally { busy.value = false; }
}

async function exportAs(fmt: "docx" | "pdf") {
  if (busy.value || !doc.value) return;
  busy.value = true;
  error.value = "";
  try {
    if (timer) clearTimeout(timer);
    await save();
    const name = `${doc.value.title[0].replace(/\s+/g, "")}-${t("report.title")}.${fmt}`;
    await downloadAuthed(`/api/v1/reports/${book.value}/${lab.value}/export?fmt=${fmt}${viewing.value ? `&ver=${viewing.value}` : ""}`, name);
  } catch (e) { fail(e); } finally { busy.value = false; }
}

async function viewVersion(v: number) {
  if (teacherView.value) { await loadTeacher(wantCmid.value, teacherUid.value, v); return; }
  try {
    const r = await reportApi.version(book.value, lab.value, v);
    doc.value = r.doc;
    viewing.value = v;
  } catch (e) { fail(e); }
}
function backToCurrent() { load(); }

// ---------- charts (H5) ----------
const chart = reactive({ open: false, table: 0, x: 0, y: 1, line: false, fit: true, caption: "", note: "", ok: false, png: "",
  byRow: false, xLabel: "", yLabel: "" });
const cols = computed(() => tables.value[chart.table]?.head || []);
function openChart() {
  chart.open = true;
  chart.table = Math.max(0, tables.value.findIndex((b) => b.rows.some((r) => r.filter((c) => num(c) !== null).length >= 2)));
  chart.x = 0; chart.y = 1; chart.caption = "";
  setTimeout(draw, 50);
}
const num = (c: string) => { const v = parseFloat(String(c).replace(/,/g, "").replace(/[−–]/g, "-")); return Number.isFinite(v) ? v : null; };
function draw() {
  // #ifdef H5
  const tb = tables.value[chart.table];
  if (!tb) return;
  const cv = document.createElement("canvas");      // off-screen: uni-app's <canvas> resizes and clears itself
  cv.width = 640; cv.height = 420;
  // a table is read by columns; a one-row table like 表 1 (位置 1…10) is read along its row
  let pts: [number, number][] = tb.rows.map((r) => [num(r[chart.x]), num(r[chart.y])]).filter((p) => p[0] !== null && p[1] !== null) as [number, number][];
  let xLabel = tb.head[chart.x] || "", yLabel = tb.head[chart.y] || "";
  chart.byRow = false;
  if (pts.length < 2 && tb.rows.length === 1) {      // 表 1 那样只有一行（位置 1…10）：沿着这一行画
    pts = tb.head.map((h, j) => [num(h), num(tb.rows[0][j])]).filter((p) => p[0] !== null && p[1] !== null) as [number, number][];
    xLabel = tb.head[0] || ""; yLabel = tb.rows[0][0] || "";
    chart.byRow = true;
  }
  const g = cv.getContext("2d")!;
  const W = cv.width, H = cv.height, L = 70, R = 20, T = 20, B = 50;
  g.fillStyle = "#fff"; g.fillRect(0, 0, W, H);
  chart.ok = pts.length >= 2;
  chart.note = chart.ok ? "" : t("report.chartNeedData");
  if (!chart.ok) return;
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  const pad = (a: number, b: number) => { const d = (b - a) || Math.abs(a) || 1; return [a - d * 0.08, b + d * 0.08]; };
  const [x0, x1] = pad(Math.min(...xs), Math.max(...xs)), [y0, y1] = pad(Math.min(...ys), Math.max(...ys));
  const X = (x: number) => L + (x - x0) / (x1 - x0) * (W - L - R), Y = (y: number) => H - B - (y - y0) / (y1 - y0) * (H - T - B);
  g.strokeStyle = "#333"; g.lineWidth = 1; g.beginPath(); g.moveTo(L, T); g.lineTo(L, H - B); g.lineTo(W - R, H - B); g.stroke();
  g.fillStyle = "#333"; g.font = "13px sans-serif"; g.textAlign = "center";
  // tick labels with enough decimals for the step (62.94 … 63.00 needs two)
  const dec = (a: number, b: number) => Math.min(6, Math.max(0, Math.ceil(-Math.log10((b - a) / 5)) + 1));
  const dx = dec(x0, x1), dy = dec(y0, y1);
  for (let i = 0; i <= 5; i++) {
    const xv = x0 + (x1 - x0) * i / 5, yv = y0 + (y1 - y0) * i / 5;
    g.fillText(xv.toFixed(dx), X(xv), H - B + 18);
    g.textAlign = "right"; g.fillText(yv.toFixed(dy), L - 6, Y(yv) + 4); g.textAlign = "center";
    g.strokeStyle = "#e5e5e5"; g.beginPath(); g.moveTo(L, Y(yv)); g.lineTo(W - R, Y(yv)); g.stroke();
  }
  g.fillText(xLabel, (L + W - R) / 2, H - 10);
  g.save(); g.translate(16, (T + H - B) / 2); g.rotate(-Math.PI / 2); g.fillText(yLabel, 0, 0); g.restore();
  chart.xLabel = xLabel; chart.yLabel = yLabel;
  const sorted = pts.slice().sort((a, b) => a[0] - b[0]);
  if (chart.line) { g.strokeStyle = "#1f6f8b"; g.lineWidth = 1.5; g.beginPath(); sorted.forEach((p, i) => (i ? g.lineTo(X(p[0]), Y(p[1])) : g.moveTo(X(p[0]), Y(p[1])))); g.stroke(); }
  g.fillStyle = "#1f6f8b"; pts.forEach((p) => { g.beginPath(); g.arc(X(p[0]), Y(p[1]), 4, 0, Math.PI * 2); g.fill(); });
  if (chart.fit && new Set(xs).size >= 2) {
    const n = pts.length, mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n;
    let sxy = 0, sxx = 0; pts.forEach(([x, y]) => { sxy += (x - mx) * (y - my); sxx += (x - mx) * (x - mx); });
    const k = sxy / sxx, b = my - k * mx;
    g.strokeStyle = "#b8860b"; g.setLineDash([6, 4]); g.beginPath(); g.moveTo(X(x0), Y(k * x0 + b)); g.lineTo(X(x1), Y(k * x1 + b)); g.stroke(); g.setLineDash([]);
    chart.note = t("report.chartFitResult", { k: +k.toPrecision(4), b: +b.toPrecision(4) });
  }
  chart.png = cv.toDataURL("image/png").split(",")[1];
  // #endif
}
function addChart() {
  if (!chart.ok || !doc.value) return;
  const figs = doc.value.blocks.filter((b) => b.t === "figure").length;
  if (figs >= 8) { uni.showToast({ title: t("report.tooManyCharts"), icon: "none" }); return; }
  const tb = tables.value[chart.table];
  const fig: ReportBlock = { t: "figure", id: `fig${Date.now() % 1e8}`, png: chart.png, caption: chart.caption || `${chart.yLabel} — ${chart.xLabel}`,
    src: { table: tb.id, x: String(chart.x), y: String(chart.y) } };
  const at = doc.value.blocks.findIndex((b) => b.t === "text" && (b as any).id === "process");
  let i = at + 1;
  while (doc.value.blocks[i]?.t === "figure") i++;
  doc.value.blocks.splice(i, 0, fig);
  chart.open = false;
  changed();
}

onLoad(async (q: any) => {
  book.value = String(q.b || "");
  lab.value = String(q.l || "");
  wantCmid.value = +(q.cmid || 0);
  if (q.u && q.cmid) { teacherView.value = true; teacherUid.value = +q.u; await loadTeacher(+q.cmid, +q.u); return; }
  if (!book.value || !lab.value) { error.value = errorText("not_found"); return; }
  await load();
});
</script>

<style scoped>
.rp { max-width: 980px; margin: 0 auto; padding: 16px; }
.rp.split { max-width: 1600px; }
.bar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.b-title { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.b-name { font-size: 18px; font-weight: 600; }
.b-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.save { font-size: 13px; }
.banner { background: #fff7e0; border: 1px solid #ecd9a0; border-radius: 8px; padding: 8px 12px; margin: 6px 0; display: flex; gap: 12px; flex-wrap: wrap; }
.banner.ok { background: #e9f6ee; border-color: #b7dfc4; }
.banner.muted { background: #f3f4f6; border-color: #e3e5e8; color: #555; }
.versions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 6px 0 10px; }
.vchip { font-size: 13px; padding: 3px 10px; border-radius: 12px; border: 1px solid #d9dde1; cursor: pointer; }
.vchip.on { background: #1f2d3a; color: #fff; border-color: #1f2d3a; }
.cols { display: flex; gap: 16px; align-items: flex-start; }
.paper { flex: 1 1 0; min-width: 0; background: #fff; border: 1px solid #e3e5e8; border-radius: 10px; padding: 28px 32px; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
.labpane { flex: 1 1 0; min-width: 0; position: sticky; top: 12px; }
.labframe { width: 100%; height: calc(100vh - 120px); border: 1px solid #e3e5e8; border-radius: 10px; background: #fff; }
.d-title { text-align: center; margin-bottom: 14px; display: flex; flex-direction: column; }
.d-title .zh { font-size: 22px; font-weight: 700; }
.en { color: #5b6b75; font-size: 13px; }
.block { display: block; }
.fields { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px 14px; margin: 8px 0 6px; }
.field { display: flex; align-items: center; gap: 6px; }
.f-l { font-size: 13px; color: #333; white-space: nowrap; }
.f-in { flex: 1; border: none; border-bottom: 1px solid #b8c4c8; padding: 3px 4px; font-size: 14px; min-width: 0; }
.f-in.wide { width: 100%; }
.note { display: block; font-size: 12px; color: #5b6b75; margin-bottom: 8px; }
.d-h { margin: 22px 0 8px; border-bottom: 2px solid #1f2d3a; padding-bottom: 4px; display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }
.d-h .zh { font-size: 17px; font-weight: 700; }
.d-p, .d-prompt { margin: 8px 0 4px; line-height: 1.6; }
.d-prompt { font-weight: 500; }
.d-strong { display: block; font-weight: 700; margin: 8px 0 4px; }
.d-label { display: block; margin: 8px 0 4px; }
.area { width: 100%; box-sizing: border-box; border: 1px solid #d9dde1; border-radius: 6px; padding: 8px 10px; font-size: 15px; line-height: 26px; background: repeating-linear-gradient(#fff, #fff 25px, #eef1f3 26px); }
.area.ro { background: #fafbfc; }
.preview { margin-top: 6px; padding: 6px 10px; background: #f7f9fa; border-radius: 6px; font-size: 14px; }
.fig-btn { margin-top: 8px; display: inline-block; }
.d-table { margin: 12px 0; }
.tb-title { display: block; font-size: 14px; margin-bottom: 6px; }
.tb-scroll { overflow-x: auto; }
.tb { display: table; border-collapse: collapse; min-width: 100%; }
.tr { display: table-row; }
.td { display: table-cell; border: 1px solid #c9d1d6; padding: 5px 6px; font-size: 13px; min-width: 52px; vertical-align: middle; }
.th .td { background: #e8eef0; font-weight: 600; }
.td.cell { background: #fffdf3; width: auto; height: 30px; }
.td.fixed { background: #fff; }
.td.x { width: 28px; min-width: 28px; text-align: center; border: none; }
.tb-empty { display: block; padding: 8px 4px; font-size: 13px; }
.add-row { display: inline-block; margin-top: 6px; font-size: 14px; }
.d-check { margin: 8px 0; display: flex; flex-direction: column; gap: 6px; }
.ck { display: flex; gap: 6px; align-items: center; cursor: pointer; }
.box { font-size: 17px; }
.ck.other { cursor: default; }
.d-fig { margin: 12px 0; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.fig-img { max-width: 560px; width: 100%; }
.cap { text-align: center; font-size: 13px; color: #555; border: none; border-bottom: 1px dashed #c9d1d6; width: 80%; }
.rubric .td { font-size: 12.5px; }
.mask { position: fixed; inset: 0; background: rgba(0,0,0,.35); display: flex; align-items: center; justify-content: center; z-index: 50; }
.dialog { background: #fff; border-radius: 12px; padding: 18px; width: min(700px, 94vw); max-height: 92vh; overflow: auto; display: flex; flex-direction: column; gap: 8px; }
.pick { border: 1px solid #d9dde1; border-radius: 6px; padding: 6px 10px; }
.half { flex: 1; }
.chart { width: 100%; max-width: 640px; height: auto; aspect-ratio: 640 / 420; border: 1px solid #eee; }
.actions { gap: 8px; margin-top: 6px; }
@media (max-width: 900px) {
  .cols { flex-direction: column; }
  .labpane { position: static; width: 100%; }
  .labframe { height: 70vh; }
  .paper { padding: 18px 14px; }
  .fields { grid-template-columns: 1fr; }
}
</style>
