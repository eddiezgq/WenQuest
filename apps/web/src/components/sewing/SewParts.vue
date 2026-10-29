<template>
  <!-- 第 49 轮：本单位零件库。一个单位一个库，同单位共享。三种入库：手填、表格批量（零件族）、AI 整理样本（待复核 → 人确认才可用）。
       设计里“从本单位零件库选”、CAE 电机选型和机壳模态都用这里“可用”的零件。 -->
  <view class="lib">
    <view v-if="!licensed" class="note">{{ t("sew.lib.locked") }}</view>
    <template v-else>
      <view class="top">
        <text class="lead">{{ t("sew.lib.lead", { org, n: total, r: review }) }}</text>
      </view>
      <view class="row">
        <view class="btn" @click="startNew">{{ t("sew.lib.add") }}</view>
        <view class="btn ghost" @click="mode = mode === 'table' ? '' : 'table'">{{ t("sew.lib.table") }}</view>
        <view class="btn ghost" @click="mode = mode === 'ai' ? '' : 'ai'">{{ t("sew.lib.ai") }}</view>
        <view class="btn ghost" @click="download('/api/v1/sewing/parts/erp.xlsx')">{{ t("sew.lib.erp") }}</view>
        <view class="btn ghost" @click="mode = mode === 'key' ? '' : 'key'; loadKey()">{{ t("sew.lib.key") }}</view>
      </view>
      <text v-if="msg" class="err">{{ msg }}</text>

      <!-- 表格批量 -->
      <view v-if="mode === 'table'" class="box">
        <text class="bt">{{ t("sew.lib.table") }}</text>
        <text class="hint">{{ t("sew.lib.tableNote") }}</text>
        <view class="row"><text v-for="c in cats" :key="c.key" class="opt" :class="{ on: tcat === c.key }" @click="tcat = c.key; preview = null">{{ c.zh }}</text></view>
        <view class="row">
          <view class="btn ghost sm" @click="download(`/api/v1/sewing/parts/template.xlsx?cat=${tcat}`)">① {{ t("sew.lib.tpl") }}</view>
          <view class="btn ghost sm" @click="pickFile('.xlsx', (f) => importTable(f, false))">② {{ t("sew.lib.upTable") }}</view>
          <view v-if="preview && !preview.bad && preview.rows.length" class="btn sm" @click="importTable(tfile, true)">③ {{ t("sew.lib.commit", { n: preview.rows.length }) }}</view>
        </view>
        <view v-if="preview" class="tbl">
          <view class="tr th"><text class="td">{{ t("sew.lib.row") }}</text><text class="td">{{ t("sew.lib.code") }}</text><text class="td">{{ t("sew.lib.name") }}</text><text class="td w3">{{ t("sew.lib.check") }}</text></view>
          <view v-for="r in preview.rows" :key="r.row" class="tr"><text class="td">{{ r.row }}</text><text class="td">{{ r.code }}</text><text class="td">{{ r.name }}</text>
            <text class="td w3" :class="r.errors.length ? 'badc' : 'okc'">{{ r.errors.length ? r.errors.join("；") : "✓" }}</text></view>
        </view>
        <text v-if="preview && preview.imported" class="hint okc">{{ t("sew.lib.imported", { n: preview.imported }) }}</text>
      </view>

      <!-- AI 整理样本 -->
      <view v-if="mode === 'ai'" class="box">
        <text class="bt">{{ t("sew.lib.ai") }}</text>
        <text class="hint">{{ t("sew.lib.aiNote") }}</text>
        <view class="row"><text v-for="c in cats" :key="c.key" class="opt" :class="{ on: acat === c.key }" @click="acat = c.key">{{ c.zh }}</text></view>
        <view class="btn" :class="{ disabled: busy }" @click="pickFile('.pdf', extract)">{{ busy ? t("sew.ai.thinking") : t("sew.lib.upPdf") }}</view>
        <text v-if="aiDone" class="hint">{{ aiDone }}</text>
      </view>

      <!-- FreeCAD 钥匙 -->
      <view v-if="mode === 'key'" class="box">
        <text class="bt">{{ t("sew.lib.key") }}</text>
        <text class="hint">{{ t("sew.lib.keyNote") }}</text>
        <text class="hint">{{ keyInfo.has_key ? t("sew.lib.keyHas", { d: day(keyInfo.created) }) : t("sew.lib.keyNone") }}</text>
        <view class="row">
          <view class="btn sm" @click="newKey">{{ keyInfo.has_key ? t("sew.lib.keyRenew") : t("sew.lib.keyMake") }}</view>
          <text v-if="keyInfo.has_key" class="link" @click="dropKey">{{ t("sew.lib.keyDrop") }}</text>
        </view>
        <view v-if="newKeyText" class="keybox"><text class="mono">{{ newKeyText }}</text><text class="hint warnc">{{ t("sew.lib.keyOnce") }}</text></view>
      </view>

      <!-- 查找 -->
      <view class="row">
        <input v-model="q" class="input" :placeholder="t('sew.lib.search')" @confirm="load" @blur="load" />
        <text class="opt" :class="{ on: !fcat }" @click="fcat = ''; load()">{{ t("sew.lib.all") }}</text>
        <text v-for="c in cats" :key="c.key" class="opt" :class="{ on: fcat === c.key }" @click="fcat = c.key; load()">{{ c.zh }}</text>
        <text class="opt" :class="{ on: fstatus === 'review' }" @click="fstatus = fstatus === 'review' ? '' : 'review'; load()">{{ t("sew.lib.review") }}</text>
      </view>
      <text v-if="!parts.length" class="hint">{{ t("sew.lib.empty") }}</text>
      <view v-for="p in parts" :key="p.id" class="item" :class="{ on: cur && cur.id === p.id }" @click="open(p)">
        <text class="st" :class="p.status">{{ p.status === "ok" ? t("sew.lib.ok") : t("sew.lib.review") }}</text>
        <text class="code">{{ p.code }}</text><text class="name">{{ p.name }}</text>
        <text class="muted small">{{ catName(p.cat) }} · {{ summary(p) }}<text v-if="p.erp"> · ERP {{ p.erp }}</text> · {{ t("sew.lib.src." + p.source) }}</text>
      </view>

      <!-- 新增 / 详情 -->
      <view v-if="cur" class="box detail">
        <view class="dh"><text class="bt">{{ cur.id ? cur.code : t("sew.lib.add") }}</text><text class="link" @click="cur = null">{{ t("sew.lib.close") }}</text></view>
        <view v-if="!cur.id" class="row"><text v-for="c in cats" :key="c.key" class="opt" :class="{ on: cur.cat === c.key }" @click="cur.cat = c.key">{{ c.zh }}</text></view>
        <view v-if="cur.status === 'review'" class="note">{{ t("sew.lib.reviewNote") }}<text v-if="cur.evidence && cur.evidence._file"> · {{ cur.evidence._file }}</text>
          <text v-if="cur.evidence && cur.evidence._errors && cur.evidence._errors.length" class="badc">　{{ t("sew.lib.aiErrors") }}{{ cur.evidence._errors.join("；") }}</text></view>
        <view class="grid">
          <view class="f"><text class="fl">{{ t("sew.lib.code") }} *</text><input v-model="cur.code" class="input" maxlength="60" /></view>
          <view class="f"><text class="fl">{{ t("sew.lib.name") }} *</text><input v-model="cur.name" class="input" maxlength="80" /></view>
          <view class="f"><text class="fl">{{ t("sew.lib.erpNo") }}</text><input v-model="cur.erp" class="input" maxlength="60" /></view>
          <view v-for="f in catOf(cur.cat).fields" :key="f.key" class="f">
            <text class="fl">{{ f.zh }}<text v-if="f.unit" class="muted"> · {{ f.unit }}</text>{{ f.required ? " *" : "" }}</text>
            <input v-model="cur.fields[f.key]" class="input" :type="f.text ? 'text' : 'digit'" />
            <text v-if="cur.evidence && cur.evidence[f.key]" class="ev" :class="cur.evidence[f.key].found ? 'okc' : 'warnc'">
              {{ cur.evidence[f.key].found ? "✓" : "？" }} {{ cur.evidence[f.key].quote || t("sew.lib.noQuote") }}</text>
          </view>
        </view>
        <view class="row">
          <view class="btn" @click="saveCur(false)">{{ t("sew.save") }}</view>
          <view v-if="cur.status === 'review'" class="btn" @click="saveCur(true)">{{ t("sew.lib.confirm") }}</view>
          <view v-if="cur.id" class="btn ghost" @click="pickFile('.step,.stp', uploadStep)">{{ t("sew.lib.upStep") }}</view>
          <view v-if="cur.id && cur.has_step" class="btn ghost" @click="download(`/api/v1/sewing/parts/${cur.id}/step`)">{{ t("sew.lib.downStep") }}</view>
          <text v-if="cur.id" class="link danger" @click="del">{{ t("sew.delete") }}</text>
        </view>
        <text v-if="catOf(cur.cat).cae" class="hint">{{ t("sew.lib.caeUse") }}{{ catOf(cur.cat).cae }}</text>
        <view v-if="cur.id && uses.length" class="uses">
          <text class="hint">{{ t("sew.lib.useHere") }}</text>
          <view v-for="u in uses" :key="u.label" class="btn ghost sm" @click="emit('apply', u.params)">{{ u.label }}：{{ fmt(u.params) }}</view>
        </view>
        <!-- #ifdef H5 -->
        <view v-if="cur.id && cur.has_step" class="view3d"><view ref="v3" class="v3" /><text class="hint">{{ meshNote }}</text></view>
        <!-- #endif -->
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import { ApiError, BASE, request, token } from "../../api";
import { errorText, t } from "../../i18n";

interface Field { key: string; zh: string; unit: string; required: boolean; text: boolean }
interface Cat { key: string; zh: string; fields: Field[]; cae: string; need_step: boolean; shape: boolean }
const props = defineProps<{ machine: string; licensed: boolean; active: boolean }>();
const emit = defineEmits<{ (e: "apply", p: Record<string, number | string>): void; (e: "changed"): void }>();
const cats = ref<Cat[]>([]);
const parts = ref<any[]>([]);
const total = ref(0);
const review = ref(0);
const org = ref("");
const q = ref("");
const fcat = ref("");
const fstatus = ref("");
const mode = ref("");
const msg = ref("");
const busy = ref(false);
const cur = ref<any>(null);
const uses = ref<any[]>([]);
const tcat = ref("link");
const acat = ref("motor");
const preview = ref<any>(null);
const tfile = ref<File | null>(null);
const aiDone = ref("");
const keyInfo = ref<{ has_key: boolean; created: number | null }>({ has_key: false, created: null });
const newKeyText = ref("");
const v3 = ref<any>(null);
const meshNote = ref("");

const catOf = (k: string) => cats.value.find((c) => c.key === k) || { key: k, zh: k, fields: [], cae: "", need_step: false, shape: false };
const catName = (k: string) => catOf(k).zh;
const day = (ts: number | null) => (ts ? new Date(ts * 1000).toLocaleDateString() : "");
const fmt = (p: Record<string, any>) => Object.entries(p).map(([k, v]) => `${k} = ${v}`).join("，");
function summary(p: any) {
  const c = catOf(p.cat);
  return c.fields.filter((f) => p.fields[f.key] != null && p.fields[f.key] !== "").slice(0, 3).map((f) => `${f.zh} ${p.fields[f.key]}${f.unit ? " " + f.unit : ""}`).join("，");
}
const fail = (e: unknown) => { msg.value = e instanceof ApiError ? (e.detail && ["bad_fields", "bad_table", "no_text", "duplicate", "bad_file"].includes(e.code) ? e.detail : errorText(e.code)) : errorText("unknown"); };

async function loadCats() {
  if (cats.value.length) return;
  cats.value = (await request<{ cats: Cat[] }>("GET", "/api/v1/sewing/parts/cats")).cats;
}
async function load() {
  if (!props.licensed) return;
  try {
    await loadCats();
    const qs = new URLSearchParams({ q: q.value, cat: fcat.value, status: fstatus.value }).toString();
    const r = await request<any>("GET", `/api/v1/sewing/parts?${qs}`);
    parts.value = r.parts; total.value = r.total; review.value = r.review; org.value = r.org;
  } catch (e) { fail(e); }
}
function startNew() {
  cur.value = { id: 0, cat: fcat.value || "motor", code: "", name: "", erp: "", fields: {}, status: "ok", evidence: {} };
  uses.value = [];
}
async function open(p: any) {
  msg.value = "";
  try {
    const full = await request<any>("GET", `/api/v1/sewing/parts/${p.id}?machine=${props.machine}`);
    full.fields = { ...full.fields };
    cur.value = full;
    uses.value = full.uses || [];
    await nextTick();
    if (full.has_step) show3d(full.id);
  } catch (e) { fail(e); }
}
async function saveCur(confirm: boolean) {
  const c = cur.value;
  if (!c) return;
  msg.value = "";
  const fields: Record<string, any> = {};
  for (const f of catOf(c.cat).fields) {
    const v = c.fields[f.key];
    if (v !== undefined && v !== null && String(v).trim() !== "") fields[f.key] = f.text ? String(v) : Number(v);
  }
  const body = { cat: c.cat, code: String(c.code || "").trim(), name: String(c.name || "").trim(), erp: String(c.erp || "").trim(), fields, confirm };
  try {
    const r = c.id ? await request<any>("PUT", `/api/v1/sewing/parts/${c.id}`, body) : await request<any>("POST", "/api/v1/sewing/parts", body);
    await load();
    await open(r);
    msg.value = confirm ? t("sew.lib.confirmed") : t("sew.saved");
    emit("changed");
  } catch (e) { fail(e); }
}
function del() {
  const c = cur.value;
  if (!c?.id) return;
  uni.showModal({ title: t("sew.delete"), content: t("sew.deleteAsk", { name: c.code }), success: async (r) => {
    if (!r.confirm) return;
    try { await request("DELETE", `/api/v1/sewing/parts/${c.id}`); cur.value = null; await load(); emit("changed"); } catch (e) { fail(e); }
  } });
}

// ---------- 文件 ----------
function pickFile(accept: string, then: (f: File) => void) {
  // #ifdef H5
  const el = document.createElement("input");
  el.type = "file";
  el.accept = accept;
  el.onchange = () => { const f = el.files?.[0]; if (f) then(f); };
  el.click();
  // #endif
}
async function post(path: string, fd: FormData) {
  const res = await fetch(`${BASE}${path}`, { method: "POST", headers: { Authorization: `Bearer ${token.value}` }, body: fd });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(body.error || `http_${res.status}`, res.status, body.detail || "");
  return body;
}
async function download(path: string) {
  // #ifdef H5
  try {
    const res = await fetch(`${BASE}${path}`, { headers: { Authorization: `Bearer ${token.value}` } });
    if (!res.ok) { const b = await res.json().catch(() => ({})); throw new ApiError(b.error || `http_${res.status}`, res.status, b.detail || ""); }
    const m = /filename\*=UTF-8''([^;]+)/.exec(res.headers.get("content-disposition") || "");
    const url = URL.createObjectURL(await res.blob());
    const a = document.createElement("a");
    a.href = url;
    a.download = m ? decodeURIComponent(m[1]) : "download";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  } catch (e) { fail(e); }
  // #endif
}
async function importTable(f: File | null, commit: boolean) {
  if (!f) return;
  tfile.value = f;
  msg.value = "";
  const fd = new FormData();
  fd.append("file", f);
  fd.append("cat", tcat.value);
  fd.append("commit", commit ? "true" : "false");
  try {
    preview.value = await post("/api/v1/sewing/parts/import", fd);
    if (preview.value.imported) { await load(); emit("changed"); }
  } catch (e) { fail(e); preview.value = null; }
}
async function extract(f: File) {
  busy.value = true;
  msg.value = aiDone.value = "";
  const fd = new FormData();
  fd.append("file", f);
  fd.append("cat", acat.value);
  try {
    const r = await post("/api/v1/sewing/parts/extract", fd);
    aiDone.value = t("sew.lib.aiDone", { n: r.parts.length }) + (r.notes.length ? " " + r.notes.join(" ") : "");
    fstatus.value = "review";
    await load();
  } catch (e) { fail(e); }
  busy.value = false;
}
async function uploadStep(f: File) {
  const fd = new FormData();
  fd.append("file", f);
  try { const r = await post(`/api/v1/sewing/parts/${cur.value.id}/step`, fd); await open(r); emit("changed"); } catch (e) { fail(e); }
}

// ---------- FreeCAD 钥匙 ----------
async function loadKey() { try { keyInfo.value = await request("GET", "/api/v1/sewing/keys"); } catch (e) { fail(e); } newKeyText.value = ""; }
async function newKey() { try { newKeyText.value = (await request<{ key: string }>("POST", "/api/v1/sewing/keys")).key; keyInfo.value = { has_key: true, created: Date.now() / 1000 }; } catch (e) { fail(e); } }
async function dropKey() { try { await request("DELETE", "/api/v1/sewing/keys"); await loadKey(); } catch (e) { fail(e); } }

// ---------- 三维预览（three.js，和网页版教材同一份 /vendor） ----------
let stop: (() => void) | null = null;
function three(): Promise<any> {
  const w = window as any;
  if (w.THREE) return Promise.resolve(w.THREE);
  return new Promise((ok, no) => {
    const s = document.createElement("script");
    s.src = "/vendor/three/r128/three.min.js";
    s.onload = () => ok(w.THREE);
    s.onerror = no;
    document.head.appendChild(s);
  });
}
async function show3d(id: number) {
  // #ifdef H5
  stop?.();
  meshNote.value = t("sew.lib.meshLoading");
  try {
    const [mesh, THREE] = await Promise.all([request<any>("GET", `/api/v1/sewing/parts/${id}/mesh`), three()]);
    const el: HTMLElement = (v3.value?.$el || v3.value) as HTMLElement;
    if (!el || cur.value?.id !== id) return;
    el.innerHTML = "";
    const W = el.clientWidth || 480, H = 260;
    const r = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    r.setSize(W, H);
    r.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    el.appendChild(r.domElement);
    const scene = new THREE.Scene();
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(mesh.v, 3));
    g.setIndex(mesh.f);
    g.computeVertexNormals();
    g.center();
    const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0x8aa4bd, metalness: 0.35, roughness: 0.45 }));
    const grp = new THREE.Group();
    grp.add(m);
    scene.add(grp);
    scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 0.9));
    const dl = new THREE.DirectionalLight(0xffffff, 0.8);
    dl.position.set(1, 2, 3);
    scene.add(dl);
    const size = Math.max(...mesh.size, 1);
    const cam = new THREE.PerspectiveCamera(35, W / H, size / 100, size * 50);
    cam.position.set(size * 0.95, size * 0.65, size * 1.15);
    cam.lookAt(0, 0, 0);
    let rx = -0.4, ry = 0.6, drag = false, px = 0, py = 0, raf = 0;
    const cv = r.domElement as HTMLCanvasElement;
    cv.onpointerdown = (e) => { drag = true; px = e.clientX; py = e.clientY; };
    window.addEventListener("pointerup", () => (drag = false));
    cv.onpointermove = (e) => { if (!drag) return; ry += (e.clientX - px) * 0.01; rx += (e.clientY - py) * 0.01; px = e.clientX; py = e.clientY; };
    const tick = () => { if (!drag) ry += 0.004; grp.rotation.set(rx, ry, 0); r.render(scene, cam); raf = requestAnimationFrame(tick); };
    tick();
    stop = () => { cancelAnimationFrame(raf); r.dispose(); };
    meshNote.value = t("sew.lib.meshSize", { x: mesh.size[0], y: mesh.size[1], z: mesh.size[2] });
  } catch { meshNote.value = t("sew.lib.meshNone"); }
  // #endif
}

watch(() => [props.active, props.licensed], () => { if (props.active && props.licensed) load(); }, { immediate: true });
watch(() => props.machine, async () => { if (cur.value?.id) { const r = await request<any>("GET", `/api/v1/sewing/parts/${cur.value.id}?machine=${props.machine}`); uses.value = r.uses || []; } });
watch(cur, (v) => { if (!v) stop?.(); });
</script>

<style scoped>
.note { background: #fff3d6; color: #7a5a00; padding: 10px 12px; border-radius: 8px; font-size: 13px; line-height: 1.6; margin-bottom: 8px; }
.top { margin-bottom: 8px; }
.lead { font-size: 13px; color: var(--wq-muted); line-height: 1.7; }
.row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 8px 0; }
.btn { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; white-space: nowrap; display: inline-block; }
.btn.ghost { background: #fff; border: 1px solid var(--wq-line); }
.btn.sm { padding: 4px 10px; font-size: 12.5px; }
.btn.disabled { opacity: .5; }
.opt { font-size: 12.5px; padding: 3px 10px; border: 1px solid var(--wq-line); border-radius: 999px; cursor: pointer; background: #fff; }
.opt.on { background: #1d4e75; border-color: #1d4e75; color: #fff; }
.input { border: 1px solid var(--wq-line); border-radius: 6px; padding: 0 8px; height: 32px; line-height: 32px; font-size: 13.5px; background: #fff; box-sizing: border-box; min-width: 160px; }
.box { border: 1px solid var(--wq-line); border-radius: 8px; padding: 10px 12px; margin: 8px 0; background: #fbfcfd; }
.bt { display: block; font-weight: 700; font-size: 14px; color: var(--wq-ink); }
.hint { display: block; font-size: 13px; color: var(--wq-muted); line-height: 1.6; margin-top: 4px; }
.err { display: block; color: var(--wq-danger); font-size: 13px; }
.item { display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; padding: 8px 6px; border-top: 1px solid var(--wq-line); cursor: pointer; font-size: 14px; }
.item:hover, .item.on { background: #f3f7fb; }
.st { font-size: 11.5px; padding: 1px 8px; border-radius: 999px; background: #e6f4ea; color: #2e7d4f; }
.st.review { background: #fff3d6; color: #7a5a00; }
.code { font-weight: 700; font-family: ui-monospace, Menlo, Consolas, monospace; }
.name { color: var(--wq-ink); }
.muted { color: var(--wq-muted); } .small { font-size: 12px; }
.detail { background: #fff; }
.dh { display: flex; justify-content: space-between; align-items: center; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px 12px; margin-top: 8px; }
.f { display: flex; flex-direction: column; gap: 3px; }
.fl { font-size: 12.5px; color: var(--wq-ink); }
.ev { font-size: 11.5px; line-height: 1.4; }
.okc { color: #2e7d4f; } .badc { color: var(--wq-danger); } .warnc { color: #8a4b00; }
.link { color: var(--wq-link); font-size: 13px; cursor: pointer; }
.link.danger { color: var(--wq-muted); }
.uses { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; margin-top: 8px; }
.tbl { border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; font-size: 12.5px; margin-top: 8px; }
.tr { display: flex; border-top: 1px solid var(--wq-line); }
.tr:first-child { border-top: 0; }
.th { background: #eaf2fa; font-weight: 600; }
.td { flex: 1; padding: 4px 8px; min-width: 0; }
.w3 { flex: 3; }
.keybox { margin-top: 8px; padding: 8px; background: #0f1720; border-radius: 6px; }
.mono { font-family: ui-monospace, Menlo, Consolas, monospace; color: #e6edf3; font-size: 13px; word-break: break-all; display: block; }
.view3d { margin-top: 10px; }
.v3 { width: 100%; height: 260px; background: #0b1220; border-radius: 6px; overflow: hidden; touch-action: none; }
</style>
