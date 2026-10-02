<template>
  <div class="page">
    <div class="page-title"><h1>仿真与分析</h1>
      <span class="muted">有限元强度校核：选零件 → 材料 → 在模型上点选面加约束和载荷 → 服务器计算 → 看应力、变形、安全系数</span></div>

    <div class="row">
      <!-- 左：设置 -->
      <section class="card side">
        <div class="step"><b>1</b> 零件</div>
        <div class="line">
          <select v-model="partSel" class="grow-in" aria-label="零件">
            <option value="" disabled>选择零件…</option>
            <option v-for="p in parts" :key="p.item" :value="p.item">{{ p.item }}{{ p.name ? ' · ' + p.name : '' }}</option>
          </select>
          <button class="btn" :disabled="!partSel || busy" @click="loadItem">读入</button>
        </div>
        <label class="small upload">或者上传 STEP（任何 CAD 导出）
          <input type="file" accept=".step,.stp,.STEP,.STP" :disabled="busy" @change="upload"></label>
        <div v-if="geo" class="small ok">{{ geo.name }} · {{ geo.solid.faces }} 个面 · 体积 {{ (geo.solid.volume_mm3 / 1000).toFixed(1) }} cm³</div>

        <template v-if="geo">
          <div class="step"><b>2</b> 材料</div>
          <select v-model="matId" class="full" aria-label="材料">
            <option v-for="m in materials" :key="m.id" :value="m.id">{{ m.name }}</option>
          </select>
          <div v-if="mat" class="small muted matline">
            E {{ (mat.E_mpa / 1000).toFixed(0) }} GPa · ν {{ mat.nu }} · {{ mat.yield_mpa ? '屈服 ' + mat.yield_mpa : '抗拉 ' + mat.ultimate_mpa }} MPa · σ₋₁ {{ mat.sigma_1 }} MPa
            <a href="#" @click.prevent="showSrc = !showSrc">出处</a>
            <div v-if="showSrc" class="src-box">{{ mat.note }}<br><span v-for="s in mat.sources" :key="s">· {{ s }}<br></span></div>
          </div>

          <div class="step"><b>3</b> 约束与载荷 <span class="muted small">先点“+”，再在右边模型上点面</span></div>
          <div class="adds">
            <button v-for="(k, key) in KINDS" :key="key" type="button" class="add" :style="{ '--c': k.color }" :title="k.hint" @click="addRow(key)">+ {{ k.label }}</button>
          </div>
          <button v-if="geo.item === 'SH-301'" type="button" class="btn ghost small-btn" @click="example">填入示范题：SH-301 受 350 N·m 扭矩</button>
          <div v-if="!rows.length" class="empty">还没有约束和载荷。</div>
          <div v-for="(r, i) in rows" :key="r.key" class="lrow" :class="{ active: active === i }" :style="{ '--c': KINDS[r.kind].color }" @click="active = i">
            <div class="lhead"><i></i><b>{{ KINDS[r.kind].label }}</b>
              <span class="small muted">{{ active === i ? '正在选面：在模型上点' : '点这里再选面' }}</span>
              <button type="button" class="x" title="删除" @click.stop="rows.splice(i, 1); active = Math.min(active, rows.length - 1)">×</button></div>
            <div class="chips">
              <span v-for="f in r.faces" :key="f" class="chip" :title="faceText(faceById[f])">面 {{ f }} <a href="#" @click.prevent.stop="toggleFace(i, f)">×</a></span>
              <span v-if="!r.faces.length" class="small muted">（还没选面）</span>
            </div>
            <div class="params small">
              <template v-if="r.kind === 'force'">
                <label>Fx <input v-model.number="r.fx" type="number"></label><label>Fy <input v-model.number="r.fy" type="number"></label><label>Fz <input v-model.number="r.fz" type="number"></label><span>N</span>
              </template>
              <template v-if="r.kind === 'pressure'"><label>压力 <input v-model.number="r.value" type="number" step="0.1"></label><span>MPa</span></template>
              <template v-if="r.kind === 'torque'"><label>扭矩 <input v-model.number="r.value" type="number"></label><span>N·m</span></template>
              <template v-if="['torque', 'bearing', 'coupling'].includes(r.kind)">
                <label class="wide">绕
                  <select v-model="r.axis"><option v-for="a in axes" :key="a.key" :value="a.key">{{ a.label }}</option></select></label>
              </template>
              <label v-if="r.kind === 'bearing'" class="chk"><input v-model="r.thrust" type="checkbox"> 止推（也限制轴向）</label>
            </div>
            <div v-if="rowErr(r)" class="small err">{{ rowErr(r) }}</div>
          </div>

          <div class="step"><b>4</b> 网格</div>
          <div class="seg">
            <button v-for="m in MESH" :key="m.k" type="button" :class="{ on: meshK === m.k }" @click="meshK = m.k">{{ m.label }}</button>
          </div>
          <div class="small muted">单元尺寸约 {{ meshSize.toFixed(1) }} mm，载荷面附近自动加密。网格越细越准、越慢；教学版上限约 20 万个单元、5 分钟。</div>

          <label class="small">这次计算的名称 <input v-model.trim="title" class="full" maxlength="80" placeholder="例如：SH-301 额定扭矩校核"></label>
          <button class="btn primary big-w" :disabled="!ready || submitting" @click="submit">{{ submitting ? '正在提交…' : '开始计算' }}</button>
          <div v-if="!ready && rows.length" class="small muted">{{ notReady }}</div>
        </template>
        <div v-if="err" class="err small">{{ err }}</div>
      </section>

      <!-- 右：模型与结果 -->
      <section class="card grow">
        <div class="card-head">
          <h2>{{ result ? '计算结果' : '模型' }}{{ job ? ' · ' + (job.title || job.item || '') : '' }}</h2>
          <template v-if="result">
            <div class="seg">
              <button type="button" :class="{ on: field === 'vm' }" @click="field = 'vm'">Von Mises 应力</button>
              <button type="button" :class="{ on: field === 'u' }" @click="field = 'u'">位移</button>
            </div>
            <label class="small deform">变形放大 <input v-model.number="deformK" type="range" min="0" max="1" step="0.01"> {{ deformX.toFixed(0) }}×</label>
            <button type="button" class="btn more" :disabled="reporting" @click="downloadReport">{{ reporting ? '正在生成报告…' : '下载计算报告（Word）' }}</button>
            <button type="button" class="btn ghost" @click="backToSetup">回到设置</button>
          </template>
        </div>
        <div v-if="job && job.status !== 'done'" class="jobbar" :class="job.status">
          <template v-if="job.status === 'queued'">排队中{{ job.position ? '：前面还有 ' + (job.position - 1) + ' 个任务' : '' }}…</template>
          <template v-else-if="job.status === 'running'">正在划分网格、求解…（已 {{ elapsed }} 秒）<div class="spin"></div></template>
          <template v-else-if="job.status === 'failed'">没算成：{{ job.error }}</template>
        </div>
        <div v-if="!geo && !result" class="empty big-empty">先在左边选一个零件（例如 SH-301 输出轴）或上传 STEP。</div>
        <CaeViewer v-else ref="viewer" :glb-url="result ? '' : geo?.model_url" :faces="geo?.faces || []" :face-colors="faceColors"
          :picking="!result && active >= 0" :surface="result?.surface" :field="field" :deform="deformX" :marks="marks" :peaks="{ vm: st.vm_peak_all_mpa, u: st.u_max_mm }" @pick="onPick" />

        <div v-if="result" class="stats">
          <div class="stat"><span>最大应力（Von Mises）</span><b>{{ st.vm_max_mpa.toFixed(1) }} <small>MPa</small></b>
            <small class="muted">面 {{ (st.vm_max_faces || []).join('、') || '—' }} · 粉色点</small></div>
          <div class="stat" :class="sfTone"><span>安全系数</span><b>{{ st.safety_factor?.toFixed(2) ?? '—' }}</b>
            <small>{{ st.strength_mpa ? strengthKind + ' ' + st.strength_mpa + ' MPa ÷ 最大应力' : '' }}</small></div>
          <div class="stat"><span>最大位移</span><b>{{ st.u_max_mm.toPrecision(3) }} <small>mm</small></b><small class="muted">青色点</small></div>
          <div class="stat"><span>网格</span><b>{{ (st.elements / 1000).toFixed(1) }}k <small>单元</small></b>
            <small class="muted">{{ st.nodes }} 节点 · {{ st.mesh_size_mm }} mm · {{ st.seconds }} 秒</small></div>
        </div>
        <div v-if="result" class="small muted notes">
          <p v-if="st.vm_peak_all_mpa > st.vm_max_mpa * 1.01">约束面附近最高 {{ st.vm_peak_all_mpa.toFixed(1) }} MPa：那是约束方式造成的（实际的支承没有那么“死”），评估时避开了约束面 {{ (1.5 * st.mesh_size_mm).toFixed(1) }} mm 以内的点。</p>
          <p>尖角（没有圆角的内角）处的应力理论上没有上限，网格越细数值越大——看到最大值在尖角，就要考虑加圆角，或者按规范的应力集中系数去校核。</p>
        </div>
      </section>
    </div>

    <section class="card">
      <div class="card-head"><h2>{{ teacher ? '本厂的计算记录' : '我的计算记录' }}</h2><span class="small muted">点一条看结果</span></div>
      <div v-if="!jobs.length" class="empty">还没有计算记录。</div>
      <table v-else class="t">
        <thead><tr><th>名称</th><th>零件</th><th v-if="teacher">提交人</th><th>时间</th><th>状态</th><th class="num">最大应力 MPa</th><th class="num">安全系数</th><th></th></tr></thead>
        <tbody><tr v-for="j in jobs" :key="j.id" :class="{ cur: job?.id === j.id }">
          <td>{{ j.title || '—' }}</td><td class="mono">{{ j.item || '上传的零件' }}</td><td v-if="teacher">{{ j.owner_name }}</td>
          <td class="small">{{ new Date(j.created * 1000).toLocaleString('zh-CN', { hour12: false }) }}</td>
          <td><span class="pill" :class="TONE[j.status]">{{ STATUS[j.status] }}</span></td>
          <td class="num">{{ j.stats ? j.stats.vm_max_mpa.toFixed(1) : '' }}</td>
          <td class="num">{{ j.stats?.safety_factor?.toFixed(2) ?? '' }}</td>
          <td><a v-if="j.status === 'done'" href="#" @click.prevent="openJob(j)">看结果 →</a>
            <span v-else-if="j.status === 'failed'" class="small err" :title="j.error">原因</span></td>
        </tr></tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { get, post, session, ApiError } from '../lib/api';
import { KINDS, toLoad, axesOf, faceText, fetchSurface } from '../lib/cae';
import CaeViewer from '../components/CaeViewer.vue';

const STATUS = { queued: '排队', running: '计算中', done: '完成', failed: '失败' };
const TONE = { queued: 'mute', running: 'info', done: 'good', failed: 'bad' };
const MESH = [{ k: 'coarse', label: '粗（快）', div: 20 }, { k: 'mid', label: '中', div: 32 }, { k: 'fine', label: '细（慢）', div: 48 }];

const teacher = computed(() => !!session.user?.teacher);
const parts = ref([]);
const materials = ref([]);
const partSel = ref('SH-301');
const geo = ref(null);
const matId = ref('45-QT');
const showSrc = ref(false);
const rows = ref([]);
const active = ref(-1);
const meshK = ref('mid');
const title = ref('');
const busy = ref(false);
const submitting = ref(false);
const err = ref('');
const job = ref(null);
const jobs = ref([]);
const result = ref(null);
const field = ref('vm');
const deformK = ref(0.3);
const elapsed = ref(0);
const viewer = ref(null);
let keyN = 0, pollT = null, listT = null;

const mat = computed(() => materials.value.find((m) => m.id === matId.value));
const faceById = computed(() => Object.fromEntries((geo.value?.faces || []).map((f) => [f.id, f])));
const axes = computed(() => axesOf(geo.value?.faces || []));
const diag = computed(() => { const b = geo.value?.solid.bbox_mm; return b ? Math.hypot(b[3] - b[0], b[4] - b[1], b[5] - b[2]) : 100; });
const meshSize = computed(() => diag.value / MESH.find((m) => m.k === meshK.value).div);
const faceColors = computed(() => {
  const out = {};
  rows.value.forEach((r) => r.faces.forEach((f) => { out[f] = KINDS[r.kind].color; }));
  return out;
});
const st = computed(() => result.value?.stats || {});
const strengthKind = computed(() => (materials.value.find((m) => m.id === job.value?.setup?.material_id)?.yield_mpa ? '屈服强度' : '抗拉强度'));
const sfTone = computed(() => { const s = st.value.safety_factor; return s == null ? '' : s < 1 ? 'bad' : s < 1.5 ? 'warn' : 'good'; });
const deformX = computed(() => {                    // 滑块 0–1 → 让最大位移看起来约为外形的 0–10%
  const um = st.value.u_max_mm || 0;
  return um > 0 ? Math.round((deformK.value * 0.1 * diag.value) / um) : 0;
});
const marks = computed(() => (result.value ? [
  { at: st.value.vm_max_at, color: 0xff2bd6 }, { at: st.value.u_max_at, color: 0x00d0ff }] : []));

function rowErr(r) {
  if (!r.faces.length) return '';
  if (KINDS[r.kind].cyl && r.faces.some((f) => faceById.value[f]?.kind !== 'cylinder')) return '轴承支承、限制转动只能选圆柱面';
  if (['torque', 'bearing', 'coupling'].includes(r.kind) && !axes.value.length) return '这个零件没有圆柱面，找不到轴线';
  if (r.kind === 'force' && !(+r.fx || +r.fy || +r.fz)) return '力的大小是 0';
  if (['pressure', 'torque'].includes(r.kind) && !+r.value) return '大小是 0';
  return '';
}
const notReady = computed(() => {
  if (!rows.value.some((r) => KINDS[r.kind].support && r.faces.length)) return '还缺约束：至少一个固定或支承面，否则零件会整体移动';
  if (!rows.value.some((r) => !KINDS[r.kind].support && r.faces.length)) return '还缺载荷';
  if (rows.value.some((r) => !r.faces.length)) return '有一行还没选面（选面或删掉这一行）';
  if (rows.value.some(rowErr)) return '有一行设置不对，看红字';
  return '';
});
const ready = computed(() => geo.value && mat.value && rows.value.length && !notReady.value);

function addRow(kind) {
  const r = { key: ++keyN, kind, faces: [], fx: 0, fy: 0, fz: 0, value: 0, axis: axes.value[0]?.key, thrust: false };
  if (kind === 'force') r.fy = -1000;
  if (kind === 'pressure') r.value = 1;
  if (kind === 'torque') r.value = 100;
  rows.value.push(r);
  active.value = rows.value.length - 1;
}
function toggleFace(i, f) {
  const r = rows.value[i];
  const k = r.faces.indexOf(f);
  if (k >= 0) { r.faces.splice(k, 1); return; }
  rows.value.forEach((o) => { const j = o.faces.indexOf(f); if (j >= 0) o.faces.splice(j, 1); });   // 一个面只放在一行里
  r.faces.push(f);
  if (KINDS[r.kind].cyl && faceById.value[f]?.kind === 'cylinder') {               // 圆柱支承：轴线就用这个面的
    const a = axes.value.find((x) => x.faces.includes(f));
    if (a) r.axis = a.key;
  }
}
function onPick(f) { if (active.value >= 0) toggleFace(active.value, f); }

// 示范题：两处轴承（Ø35）、输出端（Ø30，离键槽远的一端）限制转动、键槽一侧受 350 N·m
function example() {
  const F = geo.value.faces;
  const brg = F.filter((f) => f.radius_mm === 17.5).sort((a, b) => a.center[2] - b.center[2]);
  const out = F.filter((f) => f.radius_mm === 15).sort((a, b) => b.center[2] - a.center[2])[0];
  const wall = F.find((f) => f.kind === 'plane' && f.normal && Math.abs(Math.abs(f.normal[0]) - 1) < 1e-3);
  if (brg.length < 2 || !out || !wall) { err.value = '这个版本的 SH-301 和示范题的形状对不上，请手动设置'; return; }
  const ax = axes.value[0]?.key;
  rows.value = [
    { key: ++keyN, kind: 'bearing', faces: [brg[0].id], axis: ax, thrust: true },
    { key: ++keyN, kind: 'bearing', faces: [brg[1].id], axis: ax, thrust: false },
    { key: ++keyN, kind: 'coupling', faces: [out.id], axis: ax },
    { key: ++keyN, kind: 'torque', faces: [wall.id], axis: ax, value: 350 },
  ];
  active.value = -1;
  matId.value = '45-QT';
  title.value = 'SH-301 额定扭矩 350 N·m 校核';
}

async function loadItem() {
  await withBusy(() => post('/cae/geometry/item/' + encodeURIComponent(partSel.value)));
}
async function upload(ev) {
  const f = ev.target.files[0];
  if (!f) return;
  const fd = new FormData(); fd.append('step', f);
  await withBusy(async () => {
    const r = await fetch('/api/cae/geometry/upload', { method: 'POST', headers: { 'x-wq-token': session.token }, body: fd });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new ApiError(r.status, d.detail || '读不了这个文件');
    return d;
  });
  ev.target.value = '';
}
async function withBusy(fn) {
  busy.value = true; err.value = '';
  try {
    geo.value = await fn();
    rows.value = []; active.value = -1; result.value = null; job.value = null; title.value = '';
  } catch (e) { err.value = e.message; } finally { busy.value = false; }
}

async function submit() {
  submitting.value = true; err.value = '';
  try {
    const setup = { material_id: matId.value, mesh: { size_mm: +meshSize.value.toFixed(2) }, loads: rows.value.map((r) => toLoad(r, axes.value)) };
    job.value = await post('/cae/jobs', { step_sha: geo.value.sha, setup, item: geo.value.item, title: title.value || geo.value.name });
    result.value = null;
    poll();
    loadJobs();
  } catch (e) { err.value = e.message; } finally { submitting.value = false; }
}
function poll() {
  clearTimeout(pollT);
  if (!job.value || ['done', 'failed'].includes(job.value.status)) return;
  pollT = setTimeout(async () => {
    try {
      job.value = await get('/cae/jobs/' + job.value.id);
      if (job.value.started) elapsed.value = Math.round(Date.now() / 1000 - job.value.started);
      if (job.value.status === 'done') { await showResult(job.value); loadJobs(); return; }
      if (job.value.status === 'failed') { loadJobs(); return; }
    } catch (e) { /* 网络抖动：下次再问 */ }
    poll();
  }, 1500);
}
async function showResult(j) {
  const surface = await fetchSurface(j.id);
  result.value = { stats: j.stats, surface };
  field.value = 'vm';
}
async function openJob(j) {
  job.value = j;
  err.value = '';
  try { await showResult(j); window.scrollTo({ top: 0, behavior: 'smooth' }); } catch (e) { err.value = e.message; }
}
// 报告：自动截应力、位移两张云图，连同设置和结果生成 Word
const reporting = ref(false);
const frame = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
async function downloadReport() {
  reporting.value = true; err.value = '';
  const keep = field.value;
  try {
    const images = [];
    for (const [f, cap] of [['vm', 'Von Mises 应力云图（MPa）'], ['u', '位移云图（mm）']]) {
      field.value = f;
      await frame(); await frame();
      images.push({ data: viewer.value.snapshot(), caption: `${cap}，色标蓝 → 红 = 低 → 高（最高 ${f === 'vm' ? st.value.vm_peak_all_mpa.toFixed(1) + ' MPa' : st.value.u_max_mm.toPrecision(3) + ' mm'}），变形放大 ${deformX.value} 倍；粉点为最大应力位置，青点为最大位移位置` });
    }
    const r = await fetch(`/api/cae/jobs/${encodeURIComponent(job.value.id)}/report`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'x-wq-token': session.token }, body: JSON.stringify({ images }) });
    if (!r.ok) throw new ApiError(r.status, (await r.json().catch(() => ({}))).detail || '报告生成失败');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(await r.blob());
    a.download = `有限元报告-${job.value.item || job.value.id}.docx`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  } catch (e) { err.value = e.message; } finally { field.value = keep; reporting.value = false; }
}
function backToSetup() { result.value = null; job.value = null; }
async function loadJobs() { try { jobs.value = (await get('/cae/jobs')).jobs; } catch (e) { /* 计算服务没开时不挡页面 */ } }

watch(axes, (a) => rows.value.forEach((r) => { if (!a.find((x) => x.key === r.axis)) r.axis = a[0]?.key; }));

onMounted(async () => {
  try {
    const [p, m] = await Promise.all([get('/cae/parts'), get('/cae/materials')]);
    parts.value = p.items; materials.value = m.materials;
  } catch (e) { err.value = e.status === 503 ? '计算服务暂时连不上，请稍后再试' : e.message; }
  loadJobs();
  listT = setInterval(() => { if (jobs.value.some((j) => ['queued', 'running'].includes(j.status))) loadJobs(); }, 5000);
});
onUnmounted(() => { clearTimeout(pollT); clearInterval(listT); });
</script>

<style scoped>
.side { width: 380px; flex-shrink: 0; display: flex; flex-direction: column; gap: 9px; align-self: flex-start; }
.grow { flex: 1; min-width: 0; }
.step { display: flex; align-items: center; gap: 8px; font-weight: 600; margin-top: 6px; }
.step b { width: 22px; height: 22px; border-radius: 50%; background: var(--accent); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; }
.line { display: flex; gap: 8px; }
.grow-in, .full { flex: 1; height: 34px; border: 1px solid #C8CEC7; border-radius: 6px; padding: 0 8px; background: #fff; width: 100%; }
.upload { display: flex; flex-direction: column; gap: 4px; color: var(--muted); }
.matline { line-height: 1.6; }
.src-box { background: var(--surface-2); border: 1px solid var(--line); border-radius: 6px; padding: 6px 8px; margin-top: 4px; }
.adds { display: flex; flex-wrap: wrap; gap: 6px; }
.add { border: 1px solid var(--c); color: var(--c); background: #fff; border-radius: 14px; padding: 3px 10px; cursor: pointer; font-size: 12px; }
.add:hover { background: color-mix(in srgb, var(--c) 10%, #fff); }
.small-btn { height: 30px; font-size: 12px; }
.lrow { border: 1px solid var(--line); border-left: 4px solid var(--c); border-radius: 8px; padding: 8px 10px; cursor: pointer; display: flex; flex-direction: column; gap: 6px; }
.lrow.active { box-shadow: 0 0 0 2px color-mix(in srgb, var(--c) 35%, transparent); }
.lhead { display: flex; align-items: center; gap: 8px; }
.lhead i { width: 10px; height: 10px; border-radius: 2px; background: var(--c); }
.x { margin-left: auto; border: 0; background: none; font-size: 18px; line-height: 1; cursor: pointer; color: var(--muted); }
.chips { display: flex; flex-wrap: wrap; gap: 4px; }
.chip { font-size: 12px; background: var(--surface-2); border: 1px solid var(--line); border-radius: 10px; padding: 1px 8px; }
.chip a { color: var(--muted); margin-left: 2px; }
.params { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; }
.params input[type=number] { width: 74px; height: 28px; border: 1px solid #C8CEC7; border-radius: 5px; padding: 0 6px; }
.params select { height: 28px; border: 1px solid #C8CEC7; border-radius: 5px; max-width: 250px; }
.params .wide { flex-basis: 100%; }
.chk { display: flex; align-items: center; gap: 4px; }
.seg { display: inline-flex; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; align-self: flex-start; }
.seg button { border: 0; background: #fff; padding: 6px 12px; cursor: pointer; font-size: 13px; }
.seg button.on { background: var(--accent-bg); font-weight: 600; }
.big-w { height: 42px; font-size: 15px; margin-top: 6px; }
.card-head { flex-wrap: wrap; align-items: center; }
.deform { display: flex; align-items: center; gap: 6px; }
.jobbar { border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; background: var(--accent-bg); color: var(--accent); display: flex; align-items: center; gap: 10px; }
.jobbar.failed { background: var(--bad-bg); color: var(--bad); }
.spin { width: 14px; height: 14px; border: 2px solid currentColor; border-right-color: transparent; border-radius: 50%; animation: sp 0.8s linear infinite; }
@keyframes sp { to { transform: rotate(360deg); } }
.big-empty { padding: 120px 0; text-align: center; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 12px; }
.stat { border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 2px; }
.stat span { font-size: 12px; color: var(--muted); }
.stat b { font-size: 22px; font-family: var(--mono); }
.stat b small { font-size: 12px; font-weight: 400; }
.stat.good { background: var(--good-bg); } .stat.good b { color: var(--good); }
.stat.warn { background: var(--warn-bg); } .stat.warn b { color: var(--warn-ink); }
.stat.bad { background: var(--bad-bg); } .stat.bad b { color: var(--bad); }
.notes p { margin: 8px 0 0; }
tr.cur td { background: var(--accent-bg); }
@media (max-width: 1100px) { .side { width: 100%; } .stats { grid-template-columns: repeat(2, 1fr); } }
</style>
