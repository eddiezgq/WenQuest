<template>
  <AppShell nav="courses" :title="title">
    <view class="dp">
      <!-- top bar -->
      <view class="bar">
        <view class="b-title">
          <text class="b-name">{{ title }}</text>
          <text v-if="eng" class="wq-tag accent">{{ t("doc.engKind." + (est?.kind || "report")) }}</text>
          <text v-else class="wq-tag" :class="st?.published ? 'ok' : 'accent'">{{ st?.published ? t("doc.publishedN", { n: st.published }) : t("doc.draft") }}</text>
          <text v-if="st?.published && !eng" class="wq-tag">{{ t("doc.aud." + st.audience) }}</text>
          <text v-if="!viewing" class="wq-muted save">{{ saveText }}</text>
        </view>
        <view class="b-actions">
          <!-- #ifdef H5 -->
          <view v-if="!viewing && !eng" class="wq-btn small" :class="{ disabled: busy }" @click="openDraft">✦ {{ t("doc.aiDraft") }}</view>
          <!-- #endif -->
          <view class="wq-btn small" :class="{ disabled: busy }" @click="exportAs('docx')">{{ t("report.exportWord") }}</view>
          <view v-if="st?.pdf" class="wq-btn small" :class="{ disabled: busy }" @click="exportAs('pdf')">{{ t("report.exportPdf") }}</view>
          <view v-if="!eng" class="wq-btn small" :class="{ disabled: busy }" @click="exportMany">{{ t("doc.exportMany") }}</view>
          <view v-if="!viewing && !eng" class="wq-btn primary small" :class="{ disabled: busy }" @click="publish">{{ t("doc.publish") }}</view>
        </view>
      </view>
      <text v-if="error" class="wq-error block">{{ error }}</text>
      <view v-if="viewing" class="banner">
        <text>{{ t("report.viewingVersion", { n: viewing }) }}</text>
        <text class="wq-link" @click="restore">{{ t("doc.restore") }}</text>
        <text class="wq-link" @click="backToDraft">{{ t("report.backToCurrent") }}</text>
      </view>
      <view v-else-if="eng" class="banner muted">{{ t("doc.engNote") }}</view>
      <view v-else class="banner muted">{{ t("doc.draftNote") }}<!-- #ifndef H5 --> {{ t("doc.mobileNote") }}<!-- #endif --></view>
      <view v-if="eng && est?.stale" class="banner">
        <text>{{ t("doc.stale") }}</text>
        <text class="wq-link" @click="regenerate">{{ t("doc.regenerate") }}</text>
      </view>
      <view v-if="eng && est?.project_gone" class="banner muted">{{ t("doc.projectGone") }}</view>
      <view v-if="fresh && !viewing" class="banner">
        <text>{{ t("doc.freshHint") }}</text>
        <!-- #ifdef H5 -->
        <text class="wq-link" @click="openDraft">✦ {{ t("doc.aiDraft") }}</text>
        <!-- #endif -->
      </view>
      <view v-if="st?.versions.length && !eng" class="versions">
        <text class="wq-muted">{{ t("doc.versions") }}</text>
        <text v-for="v in st.versions" :key="v.ver" class="vchip" :class="{ on: viewing === v.ver }" @click="viewVersion(v.ver)">
          {{ t("report.versionN", { n: v.ver }) }} · {{ t("doc.aud." + v.audience) }} · {{ formatDate(v.at) }}
        </text>
      </view>

      <!-- a published version, read only -->
      <view v-if="viewing && shown" class="paper"><MathContent :html="previewHtml(shown)" /></view>

      <!-- the draft -->
      <view v-else-if="doc" class="paper">
        <input v-model="doc.title[0]" class="d-title" :placeholder="t('doc.askTitle')" @input="changed" />
        <input v-model="doc.sub" class="d-sub" :placeholder="t('doc.subPh')" @input="changed" />
        <view v-for="(b, bi) in doc.blocks" :key="keys[bi]" class="blk" :class="'k-' + b.t">
          <!-- block tools -->
          <view v-if="b.lock" class="tools">
            <text class="lock-l">🔒 {{ t("doc.locked") }}</text>
            <!-- #ifdef H5 -->
            <text class="tl" @click="insertMenu(bi)">＋</text>
            <!-- #endif -->
          </view>
          <view v-if="b.lock" class="locked"><MathContent :html="blocksHtml([b])" /></view>
          <template v-else>
          <view class="tools">
            <!-- #ifdef H5 -->
            <text class="tl" :title="t('doc.up')" @click="move(bi, -1)">↑</text>
            <text class="tl" :title="t('doc.down')" @click="move(bi, 1)">↓</text>
            <text class="tl" @click="insertMenu(bi)">＋</text>
            <text v-if="!eng && ['h', 'para', 'list', 'table', 'callout'].includes(b.t)" class="tl ai" @click="aiMenu(bi)">✦ {{ t("doc.ai") }}</text>
            <text v-if="b.t === 'table'" class="tl" @click="openChart(bi)">📈</text>
            <!-- #endif -->
            <text v-if="b.t === 'h' || b.t === 'para'" class="tl" :class="{ on: showEn[bi] || !!(b as any).en }" @click="showEn[bi] = !showEn[bi]">{{ t("doc.bilingual") }}</text>
            <text class="tl danger" :title="t('doc.remove')" @click="remove(bi)">✕</text>
          </view>

          <view v-if="b.t === 'h'" class="row-h">
            <picker :range="['H1', 'H2', 'H3']" :value="b.level - 1" @change="(e: any) => { b.level = (+e.detail.value + 1) as 1 | 2 | 3; changed(); }">
              <text class="lv">H{{ b.level }}</text>
            </picker>
            <input v-model="b.text" class="h-in" :class="'lv' + b.level" @input="changed" />
          </view>
          <input v-if="b.t === 'h' && (showEn[bi] || b.en)" v-model="b.en" class="en-in" :placeholder="t('doc.enPh')" @input="changed" />

          <template v-if="b.t === 'para'">
            <textarea v-model="b.text" class="area" auto-height :maxlength="20000" :placeholder="t('doc.paraPh')" @input="changed" />
            <textarea v-if="showEn[bi] || b.en" v-model="b.en" class="area en" auto-height :maxlength="20000" :placeholder="t('doc.enPh')" @input="changed" />
            <view v-if="hasMath(b.text) || hasMath(b.en)" class="preview"><MathContent :html="mathHtml(b.text) + (b.en ? '<br>' + mathHtml(b.en) : '')" /></view>
          </template>

          <view v-else-if="b.t === 'list'" class="lst">
            <view v-for="(it, ii) in b.items" :key="ii" class="li">
              <text class="mark">{{ b.ordered ? ii + 1 + "." : "•" }}</text>
              <view class="li-in">
                <input v-model="it.text" class="f-in" @input="changed" />
                <input v-if="it.en || showEn[bi]" v-model="it.en" class="f-in en" :placeholder="t('doc.enPh')" @input="changed" />
              </view>
              <text class="wq-link danger x" @click="b.items.splice(ii, 1); changed()">✕</text>
            </view>
            <view class="sub-acts">
              <text class="wq-link" @click="b.items.push({ text: '', en: '' }); changed()">＋ {{ t("doc.addItem") }}</text>
              <text class="ck" @click="b.ordered = !b.ordered; changed()"><text class="box">{{ b.ordered ? "☑" : "□" }}</text>{{ t("doc.ordered") }}</text>
              <text class="ck" @click="showEn[bi] = !showEn[bi]"><text class="box">{{ showEn[bi] ? "☑" : "□" }}</text>{{ t("doc.bilingual") }}</text>
            </view>
          </view>

          <view v-else-if="b.t === 'table'" class="tbl">
            <input v-model="b.caption" class="cap-in" :placeholder="t('doc.captionPh')" @input="changed" />
            <view class="tb-scroll">
              <view class="tb">
                <view class="tr th"><input v-for="(h, j) in b.head" :key="j" v-model="b.head[j]" class="td cell head" @input="changed" /></view>
                <view v-for="(r, i) in b.rows" :key="i" class="tr">
                  <input v-for="(c, j) in r" :key="j" v-model="b.rows[i][j]" class="td cell" @input="changed" />
                </view>
              </view>
            </view>
            <view class="sub-acts">
              <text class="wq-link" @click="b.rows.push(b.head.map(() => '')); changed()">＋ {{ t("doc.addRow") }}</text>
              <text v-if="b.head.length < 12" class="wq-link" @click="addCol(b)">＋ {{ t("doc.addCol") }}</text>
              <text v-if="b.rows.length" class="wq-link danger" @click="b.rows.pop(); changed()">{{ t("doc.delRow") }}</text>
              <text v-if="b.head.length > 1" class="wq-link danger" @click="delCol(b)">{{ t("doc.delCol") }}</text>
            </view>
          </view>

          <view v-else-if="b.t === 'image'" class="img">
            <image class="pic" :src="docImageUrl(b.img)" mode="widthFix" />
            <input v-model="b.caption" class="cap-in center" :placeholder="t('doc.captionPh')" @input="changed" />
          </view>

          <textarea v-else-if="b.t === 'callout'" v-model="b.text" class="area callout" auto-height :maxlength="20000" @input="changed" />
          <view v-else-if="b.t === 'hr'" class="hr" />
          </template>
        </view>

        <!-- add at the end -->
        <view class="add-row">
          <text class="wq-muted">{{ t("doc.add") }}：</text>
          <text v-for="k in addKinds" :key="k" class="add-k" @click="insert(doc.blocks.length, k)">{{ t("doc.blk." + k) }}</text>
        </view>
      </view>
      <text v-else-if="!error" class="wq-muted">{{ t("common.loading") }}</text>

      <!-- AI: a whole first draft -->
      <view v-if="draft.open" class="mask" @click.self="!draft.busy && (draft.open = false)">
        <view class="dialog">
          <text class="d-head">✦ {{ t("doc.aiDraft") }}</text>
          <template v-if="!draft.result">
            <text class="wq-muted block">{{ t("doc.aiDraftHint") }}</text>
            <textarea v-model="draft.prompt" class="area" auto-height :maxlength="4000" :placeholder="t('doc.aiPromptPh')" />
            <text class="wq-label">{{ t("doc.aiSources") }}</text>
            <view class="srcs">
              <text v-if="!sources.length" class="wq-muted">{{ t("doc.aiNoSources") }}</text>
              <view v-for="s in sources" :key="s.cmid" class="ck" @click="pickSource(s.cmid)">
                <text class="box">{{ draft.sources.includes(s.cmid) ? "☑" : "□" }}</text><text>{{ s.name }}</text><text class="wq-muted"> · {{ s.section }}</text>
              </view>
            </view>
            <text v-if="draft.busy" class="wq-muted block">{{ t("doc.aiWorking") }}</text>
            <view class="wq-row actions">
              <view class="wq-btn primary" :class="{ disabled: draft.busy || draft.prompt.trim().length < 2 }" @click="runDraft">{{ t("doc.aiGo") }}</view>
              <view class="wq-btn" :class="{ disabled: draft.busy }" @click="draft.open = false">{{ t("common.cancel") }}</view>
            </view>
          </template>
          <template v-else>
            <view class="proposal"><MathContent :html="previewHtml(draft.result)" /></view>
            <view class="wq-row actions">
              <view class="wq-btn primary" @click="takeDraft">{{ t("doc.aiTake") }}</view>
              <view class="wq-btn" @click="draft.result = null">{{ t("doc.aiDrop") }}</view>
            </view>
          </template>
        </view>
      </view>

      <!-- AI: one block -->
      <view v-if="blockAi.open" class="mask" @click.self="!blockAi.busy && (blockAi.open = false)">
        <view class="dialog">
          <text class="d-head">✦ {{ t("doc.ai." + blockAi.action) }}</text>
          <text v-if="blockAi.busy" class="wq-muted block">{{ t("doc.aiWorking") }}</text>
          <template v-else-if="blockAi.result">
            <text class="wq-label">{{ t("doc.aiProposal") }}</text>
            <view class="proposal"><MathContent :html="blocksHtml([blockAi.result])" /></view>
            <view class="wq-row actions">
              <view class="wq-btn primary" @click="takeBlock">{{ t("doc.aiTake") }}</view>
              <view class="wq-btn" @click="blockAi.open = false">{{ t("doc.aiDrop") }}</view>
            </view>
          </template>
        </view>
      </view>

      <!-- chart from a table -->
      <view v-if="chart.open" class="mask" @click.self="chart.open = false">
        <view class="dialog">
          <text class="d-head">{{ t("doc.chartFrom") }}</text>
          <view class="wq-row">
            <view class="half"><text class="wq-label">{{ t("report.chartX") }}</text>
              <picker :range="chartCols" :value="chart.x" @change="(e: any) => { chart.x = +e.detail.value; draw(); }"><view class="pick">{{ chartCols[chart.x] }}</view></picker></view>
            <view class="half"><text class="wq-label">{{ t("report.chartY") }}</text>
              <picker :range="chartCols" :value="chart.y" @change="(e: any) => { chart.y = +e.detail.value; draw(); }"><view class="pick">{{ chartCols[chart.y] }}</view></picker></view>
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
            <view class="wq-btn primary" :class="{ disabled: !chart.ok || busy }" @click="addChart">{{ t("doc.chartAdd") }}</view>
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
import { type AiSource, type CBlock, type CDoc, type CDocState, confirmAction, docApi, docImageUrl, downloadAuthed, engDocApi,
  type EngDocState } from "../../courseApi";
import { drawChart } from "../../chart";
import { errorText, formatDate, locale, t } from "../../i18n";

type TableB = Extract<CBlock, { t: "table" }>;
const id = ref(0);
const eng = ref(false);                   // 第 128 轮：工程师的网页文档（缝纫机计算书、调机卡）
const est = ref<EngDocState | null>(null);
const st = ref<CDocState | null>(null);
const doc = ref<CDoc | null>(null);
const keys = ref<number[]>([]);          // stable keys for v-for while blocks move
let nextKey = 1;
const showEn = reactive<Record<number, boolean>>({});
const viewing = ref(0);
const shown = ref<CDoc | null>(null);
const error = ref("");
const busy = ref(false);
const saving = ref(false);
const dirty = ref(false);
const savedAt = ref(0);
const sources = ref<AiSource[]>([]);
const section = ref(-1);
let timer: ReturnType<typeof setTimeout> | null = null;
let h5 = false;
// #ifdef H5
h5 = true;
// #endif
const addKinds = h5 ? ["h", "para", "list", "table", "image", "callout", "hr"] : ["h", "para", "list", "table", "callout"];

const title = computed(() => (doc.value?.title[0] || (locale.value === "en" ? doc.value?.title[1] : "") || t("doc.title")));
const saveText = computed(() => (saving.value ? t("common.saving") : dirty.value ? t("report.unsaved") : savedAt.value ? t("report.savedAt", { time: formatDate(savedAt.value) }) : ""));
const fresh = computed(() => !eng.value && !!st.value && !st.value.published && !st.value.versions.length);
const fail = (e: unknown) => { error.value = errorText(e instanceof ApiError ? e.code : "unknown"); };

// ---------- rendering helpers (a read-only preview, the same shape as the course page) ----------
const esc = (s: string) => String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const hasMath = (s: string) => /\$[^$]+\$/.test(s || "");
const mathHtml = (s: string) => esc(s).replace(/\$\$([^$]+)\$\$/g, "\\[$1\\]").replace(/\$([^$\n]+)\$/g, "\\($1\\)").replace(/\n/g, "<br>");
function words(d: CDoc | null) {
  if (!d) return 0;
  let n = 0;
  for (const b of d.blocks) {
    if (b.t === "para" || b.t === "callout") n += b.text.trim().length;
    else if (b.t === "list") n += b.items.reduce((a, it) => a + it.text.trim().length, 0);
    else if (b.t === "table") n += b.rows.reduce((a, r) => a + r.join("").trim().length, 0);
  }
  return n;
}
function blocksHtml(blocks: CBlock[]) {
  return blocks.map((b) => {
    if (b.t === "h") return `<h${b.level + 1}>${esc(b.text)}${b.en ? ` <small style="color:#5b6b75">${esc(b.en)}</small>` : ""}</h${b.level + 1}>`;
    if (b.t === "para") return `<p>${mathHtml(b.text)}</p>${b.en ? `<p style="color:#5b6b75">${mathHtml(b.en)}</p>` : ""}`;
    if (b.t === "list") return `<${b.ordered ? "ol" : "ul"}>${b.items.map((it) => `<li>${mathHtml(it.text)}${it.en ? `<br><span style="color:#5b6b75">${mathHtml(it.en)}</span>` : ""}</li>`).join("")}</${b.ordered ? "ol" : "ul"}>`;
    if (b.t === "table") return `${b.caption ? `<p><b>${esc(b.caption)}</b></p>` : ""}<table border="1" style="border-collapse:collapse"><tr>${b.head.map((h) => `<th>${esc(h)}</th>`).join("")}</tr>${b.rows.map((r) => `<tr>${r.map((c) => `<td>${mathHtml(c)}</td>`).join("")}</tr>`).join("")}</table>`;
    if (b.t === "image") return `<p style="text-align:center"><img src="${docImageUrl(b.img)}" style="max-width:100%"></p>${b.caption ? `<p style="text-align:center;color:#555">${esc(b.caption)}</p>` : ""}`;
    if (b.t === "callout") return `<blockquote>${mathHtml(b.text)}</blockquote>`;
    return "<hr>";
  }).join("");
}
const previewHtml = (d: CDoc) => `<h2 style="text-align:center">${esc(d.title[0])}</h2>${d.sub ? `<p style="text-align:center;color:#555">${esc(d.sub)}</p>` : ""}${blocksHtml(d.blocks)}`;

// ---------- load and save ----------
function take(s: CDocState) {
  st.value = s;
  doc.value = s.doc;
  keys.value = s.doc.blocks.map(() => nextKey++);
  savedAt.value = s.updated;
  dirty.value = false;
}
function fromEng(e: EngDocState): CDocState {
  est.value = e;
  return { id: e.id, course: 0, cmid: 0, template: "blank", doc: e.doc, audience: "teachers", published: 0, updated: e.updated, versions: [], pdf: e.pdf };
}
async function load() {
  error.value = "";
  try {
    if (eng.value) { take(fromEng(await engDocApi.get(id.value))); return; }
    take(await docApi.get(id.value));
    viewing.value = 0;
    shown.value = null;
    docApi.list(st.value!.course).then((r) => { section.value = r.docs.find((x) => x.id === id.value)?.section ?? -1; }).catch(() => {});
  } catch (e) { fail(e); }
}
function changed() {
  if (viewing.value) return;
  dirty.value = true;
  if (timer) clearTimeout(timer);
  timer = setTimeout(save, 1500);
}
async function save() {
  if (!dirty.value || !doc.value || !st.value) return;
  saving.value = true;
  try {
    const r = await (eng.value ? engDocApi.save : docApi.save)(id.value, doc.value, st.value.updated);
    st.value.updated = r.updated;
    savedAt.value = r.updated;
    dirty.value = false;
  } catch (e) {
    if (e instanceof ApiError && e.code === "doc_changed") {
      if (await confirmAction(t("doc.changedElsewhere"), t("report.reload"), t("common.cancel"))) await load();
    } else fail(e);
  } finally { saving.value = false; }
}
async function flush() { if (timer) clearTimeout(timer); await save(); }
onUnmounted(() => { if (timer) clearTimeout(timer); if (dirty.value) save(); });

// ---------- blocks ----------
function blank(k: string): CBlock | null {
  if (k === "h") return { t: "h", level: 1, text: "", en: "" };
  if (k === "para") return { t: "para", text: "", en: "" };
  if (k === "list") return { t: "list", ordered: false, items: [{ text: "", en: "" }] };
  if (k === "table") return { t: "table", id: `t${Date.now() % 1e8}`, caption: "", head: ["", "", ""], rows: [["", "", ""], ["", "", ""]] };
  if (k === "callout") return { t: "callout", text: "" };
  if (k === "hr") return { t: "hr" };
  return null;
}
function put(at: number, b: CBlock) {
  doc.value!.blocks.splice(at, 0, b);
  keys.value.splice(at, 0, nextKey++);
  changed();
}
async function insert(at: number, k: string) {
  if (!doc.value) return;
  if (k === "image") return addImage(at);
  const b = blank(k);
  if (b) put(at, b);
}
function insertMenu(bi: number) {
  const kinds = addKinds;
  uni.showActionSheet({ itemList: kinds.map((k) => t("doc.blk." + k)), success: (r) => insert(bi + 1, kinds[r.tapIndex]) });
}
function move(bi: number, d: number) {
  const bl = doc.value!.blocks, j = bi + d;
  if (j < 0 || j >= bl.length) return;
  [bl[bi], bl[j]] = [bl[j], bl[bi]];
  [keys.value[bi], keys.value[j]] = [keys.value[j], keys.value[bi]];
  changed();
}
async function regenerate() {
  if (busy.value) return;
  busy.value = true;
  try { await flush(); take(fromEng(await engDocApi.regenerate(id.value))); uni.showToast({ title: t("doc.regenerated"), icon: "none" }); }
  catch (e) { fail(e); } finally { busy.value = false; }
}
async function remove(bi: number) {
  if (!(await confirmAction(t("doc.removeAsk"), t("doc.remove"), t("common.cancel")))) return;
  doc.value!.blocks.splice(bi, 1);
  keys.value.splice(bi, 1);
  changed();
}
function addCol(b: TableB) { b.head.push(""); b.rows.forEach((r) => r.push("")); changed(); }
function delCol(b: TableB) { b.head.pop(); b.rows.forEach((r) => r.pop()); changed(); }

// ---------- pictures (H5): a photo, made smaller in the browser when large; the server checks it ----------
async function readImage(path: string): Promise<string> {
  // #ifdef H5
  const blob = await (await fetch(path)).blob();
  const url = URL.createObjectURL(blob);
  try {
    const img = await new Promise<HTMLImageElement>((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = no; i.src = url; });
    if (blob.size <= 1_500_000 && img.width <= 1600 && /png|jpe?g/.test(blob.type)) {
      return await new Promise<string>((ok) => { const r = new FileReader(); r.onload = () => ok(String(r.result)); r.readAsDataURL(blob); });
    }
    const s = Math.min(1, 1600 / img.width);
    const cv = document.createElement("canvas");
    cv.width = Math.round(img.width * s); cv.height = Math.round(img.height * s);
    const g = cv.getContext("2d")!;
    g.fillStyle = "#fff"; g.fillRect(0, 0, cv.width, cv.height);
    g.drawImage(img, 0, 0, cv.width, cv.height);
    return cv.toDataURL("image/jpeg", 0.85);
  } finally { URL.revokeObjectURL(url); }
  // #endif
  return "";
}
function addImage(at: number) {
  uni.chooseImage({
    count: 1,
    success: async (r) => {
      busy.value = true;
      try {
        const data = await readImage(r.tempFilePaths[0]);
        if (data.length > 4_000_000) { uni.showToast({ title: t("doc.imageTooBig"), icon: "none" }); return; }
        const up = await (eng.value ? engDocApi.image : docApi.image)(id.value, data);
        put(at, { t: "image", img: up.img, caption: "" });
      } catch (e) { fail(e); } finally { busy.value = false; }
    },
  });
}

// ---------- chart from a table (H5) ----------
const chart = reactive({ open: false, at: 0, x: 0, y: 1, line: false, fit: true, caption: "", note: "", ok: false, png: "" });
const chartTable = computed(() => (doc.value?.blocks[chart.at] as TableB | undefined));
const chartCols = computed(() => chartTable.value?.head || []);
function openChart(bi: number) {
  Object.assign(chart, { open: true, at: bi, x: 0, y: 1, caption: "" });
  setTimeout(draw, 50);
}
function draw() {
  const tb = chartTable.value;
  if (!tb || tb.t !== "table") return;
  const r = drawChart(tb.head, tb.rows, { x: chart.x, y: chart.y, line: chart.line, fit: chart.fit });
  chart.ok = r.ok; chart.png = r.png;
  if (!chart.caption || chart.caption.includes(" — ")) chart.caption = r.ok ? `${r.yLabel} — ${r.xLabel}` : "";
  chart.note = !r.ok ? t("report.chartNeedData") : r.fit ? t("report.chartFitResult", r.fit) : "";
}
async function addChart() {
  if (!chart.ok || busy.value) return;
  busy.value = true;
  try {
    const up = await (eng.value ? engDocApi.image : docApi.image)(id.value, "data:image/png;base64," + chart.png);
    put(chart.at + 1, { t: "image", img: up.img, caption: chart.caption });
    chart.open = false;
  } catch (e) { fail(e); } finally { busy.value = false; }
}

// ---------- AI ----------
const draft = reactive({ open: false, busy: false, prompt: "", sources: [] as number[], result: null as CDoc | null });
async function openDraft() {
  if (busy.value || !st.value) return;
  Object.assign(draft, { open: true, result: null });
  if (!draft.prompt && doc.value) draft.prompt = doc.value.title[0] + (doc.value.sub ? `（${doc.value.sub}）` : "");
  try { sources.value = (await docApi.sources(st.value.course)).sources; } catch { sources.value = []; }
}
function pickSource(c: number) {
  if (draft.sources.includes(c)) draft.sources = draft.sources.filter((x) => x !== c);
  else if (draft.sources.length < 6) draft.sources = [...draft.sources, c];
}
async function runDraft() {
  if (draft.busy || draft.prompt.trim().length < 2) return;
  draft.busy = true;
  error.value = "";
  try { draft.result = (await docApi.aiDraft(id.value, draft.prompt.trim(), draft.sources)).doc; } catch (e) { fail(e); draft.open = false; } finally { draft.busy = false; }
}
async function takeDraft() {
  if (!draft.result || !doc.value) return;
  if (!fresh.value && !(await confirmAction(t("doc.aiReplaceAsk"), t("doc.aiTake"), t("common.cancel")))) return;
  doc.value.blocks = draft.result.blocks;
  if (draft.result.sub) doc.value.sub = draft.result.sub;
  keys.value = doc.value.blocks.map(() => nextKey++);
  draft.open = false;
  changed();
}
const blockAi = reactive({ open: false, busy: false, at: 0, action: "rewrite", result: null as CBlock | null });
function aiMenu(bi: number) {
  const acts = ["rewrite", "expand", "shorten", "bilingual"];
  uni.showActionSheet({
    itemList: acts.map((a) => t("doc.ai." + a)),
    success: async (r) => {
      Object.assign(blockAi, { open: true, busy: true, at: bi, action: acts[r.tapIndex], result: null });
      try { blockAi.result = (await docApi.aiBlock(id.value, bi, blockAi.action, doc.value!.blocks[bi])).block; } catch (e) { fail(e); blockAi.open = false; } finally { blockAi.busy = false; }
    },
  });
}
function takeBlock() {
  if (!blockAi.result || !doc.value) return;
  doc.value.blocks.splice(blockAi.at, 1, blockAi.result);
  blockAi.open = false;
  changed();
}

// ---------- publish, versions, export ----------
async function publish() {
  if (busy.value || !st.value) return;
  const i = await new Promise<number>((res) => uni.showActionSheet({
    itemList: [t("doc.publishStudents"), t("doc.publishTeachers")], success: (r) => res(r.tapIndex), fail: () => res(-1) }));
  if (i < 0) return;
  busy.value = true;
  try {
    await flush();
    take(await docApi.publish(id.value, i === 0 ? "students" : "teachers"));
    uni.showToast({ title: t("doc.published"), icon: "success" });
  } catch (e) { fail(e); } finally { busy.value = false; }
}
async function viewVersion(v: number) {
  try {
    await flush();
    shown.value = (await docApi.version(id.value, v)).doc;
    viewing.value = v;
  } catch (e) { fail(e); }
}
function backToDraft() { viewing.value = 0; shown.value = null; }
async function restore() {
  try {
    take(await docApi.restore(id.value, viewing.value));
    backToDraft();
    uni.showToast({ title: t("doc.restored"), icon: "none" });
  } catch (e) { fail(e); }
}
const fname = () => (doc.value?.title[0] || t("doc.title")).replace(/\s+/g, "");
async function exportAs(fmt: "docx" | "pdf") {
  if (busy.value) return;
  busy.value = true;
  error.value = "";
  try {
    await flush();
    const base = eng.value ? `/api/v1/engdocs/${id.value}` : `/api/v1/webdocs/${id.value}`;
    await downloadAuthed(`${base}/export?fmt=${fmt}${viewing.value ? `&ver=${viewing.value}` : ""}`, `${fname()}.${fmt}`);
  } catch (e) { fail(e); } finally { busy.value = false; }
}
function exportMany() {
  if (busy.value || !st.value || section.value < 0) return;
  const opts: [string, string, string][] = [["plan", "docx", t("doc.exportChapterPlans")], ["plan", "pdf", t("doc.exportChapterPlansPdf")], ["", "docx", t("doc.exportChapterAll")]];
  uni.showActionSheet({
    itemList: opts.map((o) => o[2]),
    success: async (r) => {
      const [tpl, fmt, label] = opts[r.tapIndex];
      busy.value = true;
      try {
        await flush();
        await downloadAuthed(`/api/v1/courses/${st.value!.course}/webdocs.zip?section=${section.value}&fmt=${fmt}${tpl ? `&template=${tpl}` : ""}`, `${label}.zip`);
      } catch (e) { fail(e); } finally { busy.value = false; }
    },
  });
}

onLoad(async (q: any) => {
  eng.value = !!q.eng;
  id.value = +(q.id || q.eng || 0);
  if (!id.value) { error.value = errorText("not_found"); return; }
  await load();
  if (q.ai && fresh.value && h5) openDraft();      // just made from the course editor
});
</script>

<style scoped>
.dp { max-width: 980px; margin: 0 auto; padding: 16px; }
.bar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.b-title { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.b-name { font-size: 18px; font-weight: 600; }
.b-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.save { font-size: 13px; }
.block { display: block; }
.banner { background: #fff7e0; border: 1px solid #ecd9a0; border-radius: 8px; padding: 8px 12px; margin: 6px 0; display: flex; gap: 12px; flex-wrap: wrap; }
.banner.muted { background: #f3f4f6; border-color: #e3e5e8; color: #555; font-size: 13px; }
.versions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 6px 0 10px; }
.vchip { font-size: 13px; padding: 3px 10px; border-radius: 12px; border: 1px solid #d9dde1; cursor: pointer; }
.vchip.on { background: #1f2d3a; color: #fff; border-color: #1f2d3a; }
.paper { background: #fff; border: 1px solid #e3e5e8; border-radius: 10px; padding: 28px 32px; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
.d-title { width: 100%; text-align: center; font-size: 22px; font-weight: 700; border: none; height: 40px; }
.d-sub { width: 100%; text-align: center; font-size: 14px; color: #555; border: none; margin-bottom: 14px; }
.blk { position: relative; padding: 6px 8px; margin: 4px -8px; border-radius: 6px; border: 1px solid transparent; }
.blk:hover { border-color: #e3e5e8; background: #fcfdfd; }
.tools { display: flex; gap: 4px; justify-content: flex-end; flex-wrap: wrap; opacity: .35; margin-bottom: 2px; }
.blk:hover .tools { opacity: 1; }
.tl { font-size: 12px; padding: 1px 7px; border: 1px solid #d9dde1; border-radius: 10px; cursor: pointer; background: #fff; }
.tl.on { background: #e8eef0; }
.tl.ai { color: #6a3fb5; border-color: #d6c8ef; }
.tl.danger { color: #b3261e; }
.row-h { display: flex; gap: 8px; align-items: center; }
.lv { font-size: 12px; color: #5b6b75; border: 1px solid #d9dde1; border-radius: 4px; padding: 1px 5px; }
.h-in { flex: 1; font-weight: 700; border: none; border-bottom: 2px solid #1f2d3a; }
.h-in.lv1 { font-size: 18px; height: 34px; }
.h-in.lv2 { font-size: 16px; height: 30px; border-bottom-width: 1px; }
.h-in.lv3 { font-size: 15px; height: 28px; border-bottom: 1px dashed #b8c4c8; }
.en-in { width: 100%; font-size: 13px; color: #5b6b75; border: none; border-bottom: 1px dashed #d9dde1; margin-top: 4px; }
.area { width: 100%; box-sizing: border-box; border: 1px solid #e3e5e8; border-radius: 6px; padding: 8px 10px; font-size: 15px; line-height: 1.7; min-height: 44px; }
.area.en { color: #5b6b75; font-size: 14px; margin-top: 4px; }
.area.callout { background: #eef6f8; border-left: 4px solid #1f6f8b; }
.preview { margin-top: 6px; padding: 6px 10px; background: #f7f9fa; border-radius: 6px; font-size: 14px; }
.lst .li { display: flex; gap: 8px; align-items: flex-start; margin: 4px 0; }
.mark { width: 22px; text-align: right; padding-top: 4px; color: #333; }
.li-in { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.f-in { border: none; border-bottom: 1px solid #d9dde1; padding: 3px 4px; font-size: 15px; min-width: 0; }
.f-in.en { font-size: 13px; color: #5b6b75; }
.f-in.wide { width: 100%; }
.x { padding-top: 4px; }
.sub-acts { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 6px; font-size: 14px; align-items: center; }
.ck { display: inline-flex; gap: 4px; align-items: center; cursor: pointer; }
.box { font-size: 16px; }
.cap-in { width: 100%; font-size: 14px; border: none; border-bottom: 1px dashed #d9dde1; margin-bottom: 6px; }
.cap-in.center { text-align: center; }
.tb-scroll { overflow-x: auto; }
.tb { display: table; border-collapse: collapse; min-width: 100%; }
.tr { display: table-row; }
.td { display: table-cell; border: 1px solid #c9d1d6; padding: 4px 6px; font-size: 13px; min-width: 70px; height: 30px; }
.td.head { background: #e8eef0; font-weight: 600; }
.img { text-align: center; display: flex; flex-direction: column; align-items: center; }
.pic { max-width: 640px; width: 100%; }
.hr { border-top: 1px solid #c9d1d6; margin: 10px 0; }
.locked { background: #f7f8f9; border-radius: 6px; padding: 4px 10px; color: #333; }
.lock-l { font-size: 11px; color: #8a959c; margin-right: auto; }
.add-row { margin-top: 18px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; border-top: 1px dashed #d9dde1; padding-top: 12px; }
.add-k { font-size: 13px; padding: 3px 10px; border: 1px solid #d9dde1; border-radius: 12px; cursor: pointer; background: #fff; }
.mask { position: fixed; inset: 0; background: rgba(0,0,0,.35); display: flex; align-items: center; justify-content: center; z-index: 50; }
.dialog { background: #fff; border-radius: 12px; padding: 18px; width: min(760px, 94vw); max-height: 92vh; overflow: auto; display: flex; flex-direction: column; gap: 8px; }
.d-head { font-size: 17px; font-weight: 600; }
.srcs { display: flex; flex-direction: column; gap: 4px; max-height: 200px; overflow: auto; border: 1px solid #eef0f2; border-radius: 6px; padding: 6px 8px; }
.proposal { border: 1px solid #e3e5e8; border-radius: 8px; padding: 12px 16px; max-height: 60vh; overflow: auto; background: #fcfdfd; }
.pick { border: 1px solid #d9dde1; border-radius: 6px; padding: 6px 10px; }
.half { flex: 1; }
.chart { width: 100%; max-width: 640px; height: auto; aspect-ratio: 640 / 420; border: 1px solid #eee; }
.actions { gap: 8px; margin-top: 6px; }
@media (max-width: 900px) {
  .paper { padding: 18px 14px; }
  .tools { opacity: 1; }
}
</style>
