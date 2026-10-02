<template>
  <div class="page">
    <div class="page-title"><h1>运动与动力分析</h1>
      <span class="muted">多体动力学（MuJoCo）：选机构或机械臂 → 加驱动和负载 → 服务器计算 → 动画、运动曲线、关节受力、驱动力矩与功率</span></div>

    <div class="row">
      <section class="card side">
        <div class="step"><b>1</b> 模型</div>
        <div class="seg">
          <button v-for="s in SRC" :key="s.k" type="button" :class="{ on: src === s.k }" @click="src = s.k">{{ s.label }}</button>
        </div>
        <template v-if="src === 'mech'">
          <select v-model="mechId" class="full" aria-label="机构">
            <option v-for="m in mechs" :key="m.id" :value="m.id">{{ m.name }}</option>
          </select>
          <details v-if="mech" class="small">
            <summary>参数（零件库默认值，可改）</summary>
            <div class="grid2">
              <label v-for="(v, k) in mechParams" :key="k">{{ k }} <input v-model.number="mechParams[k]" type="number" step="any"></label>
            </div>
          </details>
        </template>
        <select v-else-if="src === 'robot'" v-model="robotId" class="full" aria-label="机械臂">
          <option v-for="r in robots" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
        <label v-else class="small upload">MJCF（.xml）、URDF（.urdf），或带网格的 zip
          <input type="file" accept=".xml,.urdf,.mjcf,.zip" @change="pickFile"></label>
        <button class="btn" :disabled="busy || (src === 'upload' && !file)" @click="loadModel">{{ busy ? '正在读入…' : '读入' }}</button>
        <div v-if="info" class="small ok">{{ info.bodies.length }} 个构件 · {{ info.joints.length }} 个可驱动关节 · 总质量 {{ info.total_mass_kg.toFixed(2) }} kg</div>

        <template v-if="info">
          <div class="step"><b>2</b> 驱动 <span class="muted small">{{ src === 'mech' ? '主动件：' + jlabel(driver) : '每个关节一行；“自由”= 不驱动' }}</span></div>
          <div v-for="j in driveJoints" :key="j.name" class="jrow">
            <div class="jname">{{ jlabel(j.name) }}<span class="muted small"> {{ j.type === 'hinge' ? '转动' : '移动' }}</span></div>
            <div class="jctl small">
              <label>初值 <input v-model.number="dv[j.name].init" type="number" step="any"> {{ au(j) }}</label>
              <select v-model="dv[j.name].kind">
                <option v-for="o in kindsFor(j)" :key="o.k" :value="o.k">{{ o.label }}</option>
              </select>
              <template v-if="dv[j.name].kind === 'speed'"><label><input v-model.number="dv[j.name].speed" type="number" step="any"> {{ j.type === 'hinge' ? 'r/min' : 'mm/s' }}</label></template>
              <template v-if="dv[j.name].kind === 'move'">
                <label>到 <input v-model.number="dv[j.name].to" type="number" step="any"> {{ au(j) }}</label>
                <label><input v-model.number="dv[j.name].t0" type="number" step="0.1" min="0"> 到 <input v-model.number="dv[j.name].t1" type="number" step="0.1"> 秒</label>
              </template>
              <template v-if="dv[j.name].kind === 'sine'">
                <label>幅值 <input v-model.number="dv[j.name].amp" type="number" step="any"> {{ au(j) }}</label>
                <label><input v-model.number="dv[j.name].freq" type="number" step="0.1"> Hz</label>
              </template>
              <template v-if="dv[j.name].kind === 'torque'"><label><input v-model.number="dv[j.name].torque" type="number" step="any"> {{ j.type === 'hinge' ? 'N·m' : 'N' }}</label></template>
            </div>
          </div>
          <div v-if="src === 'mech' && loadJoints.length" class="small">
            <div class="muted">工作阻力 / 负载力矩（加在从动件上，方向与运动相反时填负值）</div>
            <div v-for="j in loadJoints" :key="j.name" class="jrow inline">
              <span>{{ jlabel(j.name) }}</span>
              <label><input v-model.number="loads[j.name]" type="number" step="any"> {{ j.type === 'hinge' ? 'N·m' : 'N' }}</label>
            </div>
          </div>

          <div class="step"><b>3</b> 负载与重力</div>
          <label class="small chk"><input v-model="gravity" type="checkbox"> 计重力</label>
          <div v-for="(p, i) in payloads" :key="'p' + i" class="jrow inline small">
            <span>负载</span>
            <select v-model="p.body"><option v-for="b in info.bodies" :key="b.name" :value="b.name">{{ jlabel(b.name) }}</option></select>
            <label><input v-model.number="p.mass" type="number" step="0.1" min="0"> kg</label>
            <label>偏移 <input v-model.number="p.y" type="number" step="10"> mm</label>
            <button class="x" @click="payloads.splice(i, 1)">×</button>
          </div>
          <div v-for="(f, i) in forces" :key="'f' + i" class="jrow inline small">
            <span>外力</span>
            <select v-model="f.body"><option v-for="b in info.bodies" :key="b.name" :value="b.name">{{ jlabel(b.name) }}</option></select>
            <label>X <input v-model.number="f.fx" type="number"></label><label>Z <input v-model.number="f.fz" type="number"></label> N
            <button class="x" @click="forces.splice(i, 1)">×</button>
          </div>
          <div class="line">
            <button class="btn ghost small-btn" @click="payloads.push({ body: endBody, mass: 1, y: 0 })">+ 末端负载（质量）</button>
            <button class="btn ghost small-btn" @click="forces.push({ body: endBody, fx: 0, fz: -100 })">+ 外力</button>
          </div>

          <div class="step"><b>4</b> 记录点与时长</div>
          <div v-for="(p, i) in points" :key="'pt' + i" class="jrow inline small">
            <input v-model="p.name" class="pname" maxlength="8">
            <select v-model="p.body"><option v-for="b in info.bodies" :key="b.name" :value="b.name">{{ jlabel(b.name) }}</option></select>
            <label>x <input v-model.number="p.x" type="number"></label><label>y <input v-model.number="p.y" type="number"></label><label>z <input v-model.number="p.z" type="number"></label> mm
            <button class="x" @click="points.splice(i, 1)">×</button>
          </div>
          <button class="btn ghost small-btn" @click="points.push({ name: 'P' + (points.length + 1), body: endBody, x: 0, y: 0, z: 0 })">+ 记录一个点的轨迹</button>
          <label class="small">仿真时长 <input v-model.number="duration" type="number" min="0.1" max="60" step="0.5"> 秒（最多 60）</label>
          <label class="small">名称 <input v-model.trim="title" class="full" maxlength="80"></label>
          <button class="btn primary big-w" :disabled="submitting || !driveCount" @click="submit">{{ submitting ? '正在提交…' : '开始计算' }}</button>
          <div v-if="!driveCount" class="small muted">至少给一个关节加驱动（或给它“保持”）。</div>
        </template>
        <div v-if="err" class="err small">{{ err }}</div>
      </section>

      <section class="card grow">
        <div class="card-head"><h2>{{ result ? '结果' : '模型' }}{{ job ? ' · ' + (job.title || '') : '' }}</h2>
          <template v-if="result">
            <button class="btn ghost more" @click="downloadCsv">导出曲线（CSV）</button>
            <button class="btn ghost" @click="backToSetup">回到设置</button>
          </template></div>
        <div v-if="job && job.status !== 'done'" class="jobbar" :class="job.status">
          <template v-if="job.status === 'queued'">排队中{{ job.position ? '：前面还有 ' + (job.position - 1) + ' 个任务' : '' }}…</template>
          <template v-else-if="job.status === 'running'">正在计算…</template>
          <template v-else>没算成：{{ job.error }}</template>
        </div>
        <div v-if="!info && !result" class="empty big-empty">先在左边选一个机构或机械臂，点“读入”。</div>
        <template v-else>
          <MbdViewer :model-url="modelUrl" :anim="result?.anim" :time="time" :trails="trails" />
          <div v-if="result" class="player">
            <button class="btn ghost" @click="toggle">{{ playing ? '暂停' : '播放' }}</button>
            <input v-model.number="time" type="range" :min="0" :max="tmax" step="0.001" aria-label="时间">
            <span class="mono small">{{ time.toFixed(2) }} / {{ tmax.toFixed(2) }} s</span>
            <select v-model.number="speed" class="small"><option :value="0.1">0.1×</option><option :value="0.25">0.25×</option><option :value="0.5">0.5×</option><option :value="1">1×</option><option :value="2">2×</option></select>
          </div>
        </template>

        <template v-if="result">
          <table class="t sum">
            <thead><tr><th>驱动</th><th class="num">峰值</th><th class="num">均方根</th><th class="num">最高速度</th><th class="num">峰值功率 W</th><th class="num">平均功率 W</th></tr></thead>
            <tbody><tr v-for="d in result.stats.drives" :key="d.joint">
              <td>{{ jlabel(d.joint) }}<span class="muted small"> {{ KIND_NAME[d.kind] }}</span></td>
              <td class="num">{{ d.peak.toFixed(2) }} {{ tu(d.joint) }}</td><td class="num">{{ d.rms.toFixed(2) }}</td>
              <td class="num">{{ spd(d) }}</td><td class="num">{{ d.power_peak.toFixed(1) }}</td><td class="num">{{ d.power_mean.toFixed(1) }}</td></tr></tbody>
          </table>
          <div class="chips">
            <span class="small muted">曲线：</span>
            <button v-for="(lab, g) in GROUPS" v-show="groupHas(g)" :key="g" type="button" class="chip" :class="{ on: shown.includes(g) }" @click="toggleGroup(g)">{{ lab }}</button>
          </div>
          <div class="charts">
            <TimeChart v-for="c in charts" :key="c.group" :title="c.title" :unit="c.unit" :t="series.t" :series="c.series" :cursor="time" @seek="time = $event" />
          </div>
          <div v-if="charts.some((c) => c.more)" class="small muted">反力曲线只画受力最大的 6 个构件；全部数据在 CSV 里。</div>
        </template>
      </section>
    </div>

    <section class="card">
      <div class="card-head"><h2>{{ teacher ? '本厂的计算记录' : '我的计算记录' }}</h2></div>
      <div v-if="!jobs.length" class="empty">还没有计算记录。</div>
      <table v-else class="t">
        <thead><tr><th>名称</th><th v-if="teacher">提交人</th><th>时间</th><th>状态</th><th class="num">用时 s</th><th></th></tr></thead>
        <tbody><tr v-for="j in jobs" :key="j.id">
          <td>{{ j.title || '—' }}</td><td v-if="teacher">{{ j.owner_name }}</td>
          <td class="small">{{ new Date(j.created * 1000).toLocaleString('zh-CN', { hour12: false }) }}</td>
          <td><span class="pill" :class="TONE[j.status]">{{ STATUS[j.status] }}</span></td>
          <td class="num">{{ j.stats?.seconds ?? '' }}</td>
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
import { fetchSeries, fetchAnim, describe, GROUPS, SERIES, toCSV } from '../lib/mbd';
import MbdViewer from '../components/MbdViewer.vue';
import TimeChart from '../components/TimeChart.vue';

const SRC = [{ k: 'mech', label: '零件库机构' }, { k: 'robot', label: '机械臂' }, { k: 'upload', label: '上传模型' }];
const STATUS = { queued: '排队', running: '计算中', done: '完成', failed: '失败' };
const TONE = { queued: 'mute', running: 'info', done: 'good', failed: 'bad' };
const KIND_NAME = { speed: '匀速', move: '点到点', sine: '正弦', hold: '保持', torque: '给定力矩', coupled: '机构带动' };
const DEG = Math.PI / 180;

const teacher = computed(() => !!session.user?.teacher);
const src = ref('mech');
const mechs = ref([]), robots = ref([]);
const mechId = ref('C-LNK-SLIDER'), robotId = ref('B-ARM-UR5E');
const mechParams = ref({});
const file = ref(null);
const info = ref(null), ref_ = ref(null);
const busy = ref(false), submitting = ref(false), err = ref('');
const dv = ref({}), loads = ref({});
const gravity = ref(true), payloads = ref([]), forces = ref([]), points = ref([]);
const duration = ref(2), title = ref('');
const job = ref(null), jobs = ref([]), result = ref(null), series = ref(null);
const time = ref(0), playing = ref(false), speed = ref(0.25);
const shown = ref(['drive', 'q']);
let pollT = null, raf = null;

const mech = computed(() => mechs.value.find((m) => m.id === mechId.value));
watch(mech, (m) => { if (m) mechParams.value = { ...m.params }; });
const labels = computed(() => (src.value === 'mech' || ref_.value?.source === 'mech' ? mech.value?.labels || {} : {}));
const jlabel = (n) => (labels.value[n] ? `${labels.value[n]}` : n);
const jtypes = computed(() => Object.fromEntries((info.value?.joints || []).map((j) => [j.name, j.type])));
const driver = computed(() => (ref_.value?.source === 'mech' ? mechs.value.find((m) => m.id === ref_.value.id)?.driver : null));
const driveJoints = computed(() => (info.value?.joints || []).filter((j) => !driver.value || j.name === driver.value));
const loadJoints = computed(() => (driver.value ? (info.value?.joints || []).filter((j) => j.name !== driver.value) : []));
const endBody = computed(() => {
  const r = robots.value.find((x) => x.id === ref_.value?.id);
  return r?.end_body || info.value?.bodies[info.value.bodies.length - 1]?.name;
});
const modelUrl = computed(() => info.value?.model_url || '');
const au = (j) => (j.type === 'hinge' ? '°' : 'mm');
const toSI = (j, v) => (j.type === 'hinge' ? v * DEG : v / 1000);
const kindsFor = () => [{ k: 'free', label: '自由' }, { k: 'hold', label: '保持' }, { k: 'speed', label: '匀速' }, { k: 'move', label: '点到点' },
  { k: 'sine', label: '正弦' }, { k: 'torque', label: '给定力矩' }];
const driveCount = computed(() => driveJoints.value.filter((j) => dv.value[j.name] && dv.value[j.name].kind !== 'free').length);
const tu = (n) => (jtypes.value[n] === 'slide' ? 'N' : 'N·m');
const spd = (d) => (jtypes.value[d.joint] === 'slide' ? (d.speed_max * 1000).toFixed(0) + ' mm/s' : (d.speed_max / (2 * Math.PI) * 60).toFixed(1) + ' r/min');

function pickFile(ev) { file.value = ev.target.files[0] || null; }
async function loadModel() {
  busy.value = true; err.value = '';
  try {
    let r;
    if (src.value === 'upload') {
      const fd = new FormData(); fd.append('file', file.value);
      const res = await fetch('/api/mbd/models/upload', { method: 'POST', headers: { 'x-wq-token': session.token }, body: fd });
      r = await res.json().catch(() => ({}));
      if (!res.ok) throw new ApiError(res.status, r.detail || '读不了这个模型');
    } else {
      const ref = src.value === 'mech' ? { source: 'mech', id: mechId.value, params: mechParams.value } : { source: 'library', id: robotId.value };
      r = await post('/mbd/models/load', ref);
    }
    info.value = r; ref_.value = r.ref; result.value = null; job.value = null;
    resetForm();
  } catch (e) { err.value = e.message; } finally { busy.value = false; }
}

function resetForm() {
  const home = info.value.home || {};
  const out = {};
  for (const j of info.value.joints) {
    const v0 = home[j.name] || 0;
    out[j.name] = { init: +(j.type === 'hinge' ? v0 / DEG : v0 * 1000).toFixed(2), kind: driver.value ? 'speed' : 'hold', speed: 60, to: 0, t0: 0.2, t1: 1.5, amp: 20, freq: 0.5, torque: 0 };
  }
  dv.value = out; loads.value = {};
  payloads.value = []; forces.value = []; points.value = [];
  gravity.value = true; duration.value = driver.value ? 2 : 2;
  const id = ref_.value?.id;
  title.value = (src.value === 'mech' ? mech.value?.name : robots.value.find((r) => r.id === id)?.name) || '上传的模型';
  if (id === 'C-LNK-4BAR') points.value = [{ name: 'P', body: 'coupler', x: (mechParams.value.coupler_m || 0.12) * 500, y: 0, z: 0 }];
  if (id === 'C-LNK-SLIDER') forces.value = [{ body: 'slider', fx: -200, fz: 0 }];
  if (robots.value.some((r) => r.id === id)) {                       // 机械臂示范：肩、肘 1.3 秒内各转一个角度，带 3 kg
    payloads.value = [{ body: endBody.value, mass: 3, y: 100 }];
    const js = info.value.joints;
    if (js[0]) Object.assign(out[js[0].name], { kind: 'move', to: out[js[0].name].init + 90 });
    if (js[1]) Object.assign(out[js[1].name], { kind: 'move', to: out[js[1].name].init + 30 });
    points.value = [{ name: 'TCP', body: endBody.value, x: 0, y: 100, z: 0 }];
  }
}

function buildSetup() {
  const drives = [], initial = {};
  for (const j of info.value.joints) {
    const v = dv.value[j.name];
    if (!v) continue;
    if (!driver.value || j.name === driver.value) initial[j.name] = toSI(j, v.init || 0);
    if (driver.value && j.name !== driver.value) continue;
    if (v.kind === 'free') continue;
    const d = { joint: j.name, kind: v.kind };
    if (v.kind === 'speed') d.value = j.type === 'hinge' ? v.speed * 2 * Math.PI / 60 : v.speed / 1000;
    if (v.kind === 'move') Object.assign(d, { to: toSI(j, v.to), t0: v.t0, t1: v.t1 });
    if (v.kind === 'sine') Object.assign(d, { amp: toSI(j, v.amp), freq: v.freq });
    if (v.kind === 'torque') d.value = v.torque;
    drives.push(d);
  }
  for (const [jn, val] of Object.entries(loads.value)) if (+val) drives.push({ joint: jn, kind: 'torque', value: +val });
  return {
    duration_s: duration.value, gravity: gravity.value, initial, drives, sample_hz: 100,
    payloads: payloads.value.filter((p) => p.mass > 0).map((p) => ({ body: p.body, mass: p.mass, pos: [0, (p.y || 0) / 1000, 0] })),
    forces: forces.value.map((f) => ({ body: f.body, force: [+f.fx || 0, 0, +f.fz || 0] })),
    points: points.value.map((p) => ({ name: p.name || 'P', body: p.body, pos: [p.x / 1000, p.y / 1000, p.z / 1000] })),
  };
}

async function submit() {
  submitting.value = true; err.value = '';
  try {
    job.value = await post('/mbd/jobs', { model: ref_.value, setup: buildSetup(), title: title.value, item: ref_.value.id });
    result.value = null; poll(); loadJobs();
  } catch (e) { err.value = e.message; } finally { submitting.value = false; }
}
function poll() {
  clearTimeout(pollT);
  if (!job.value || ['done', 'failed'].includes(job.value.status)) return;
  pollT = setTimeout(async () => {
    try {
      job.value = await get('/mbd/jobs/' + job.value.id);
      if (job.value.status === 'done') { await showResult(job.value); loadJobs(); return; }
      if (job.value.status === 'failed') { loadJobs(); return; }
    } catch (e) { /* 下次再问 */ }
    poll();
  }, 1200);
}
async function showResult(j) {
  const [s, a] = await Promise.all([fetchSeries(j.id), fetchAnim(j.id)]);
  for (const d of j.stats.drives) {                                 // 功率 = 力矩 × 速度
    const tau = s['drive.' + d.joint], w = s['qd.' + d.joint], p = new Float32Array(tau.length);
    for (let i = 0; i < p.length; i++) p[i] = tau[i] * w[i];
    s['power.' + d.joint] = p;
  }
  series.value = s; result.value = { stats: j.stats, anim: a }; time.value = 0;
}
async function openJob(j) {
  err.value = '';
  try {
    if (!info.value || info.value.key !== j.model_key) {
      const r = await post('/mbd/models/load', j.model).catch(() => null);
      if (r) {
        const m = j.model || {};
        src.value = m.source === 'mech' ? 'mech' : m.source === 'library' ? 'robot' : 'upload';
        if (m.source === 'mech') { mechId.value = m.id; mechParams.value = { ...(m.params || {}) }; }
        if (m.source === 'library') robotId.value = m.id;
        info.value = r; ref_.value = r.ref;
        resetForm();
        duration.value = j.setup?.duration_s || duration.value;
        title.value = j.title || title.value;
      }
    }
    job.value = j; await showResult(j); window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (e) { err.value = e.message; }
}
function backToSetup() { result.value = null; job.value = null; playing.value = false; }

// ---- 播放
const tmax = computed(() => (result.value ? result.value.anim.t[result.value.anim.frames - 1] : 0));
function toggle() {
  playing.value = !playing.value;
  if (!playing.value) return;
  let last = performance.now();
  const step = (now) => {
    if (!playing.value) return;
    time.value += (now - last) / 1000 * speed.value; last = now;
    if (time.value > tmax.value) time.value = 0;
    raf = requestAnimationFrame(step);
  };
  raf = requestAnimationFrame(step);
}

// ---- 曲线
function groupHas(g) { return series.value && Object.keys(series.value).some((n) => n !== 't' && describe(n, jtypes.value).group === g); }
function toggleGroup(g) { const i = shown.value.indexOf(g); if (i >= 0) shown.value.splice(i, 1); else shown.value.push(g); }
const charts = computed(() => {
  const s = series.value;
  if (!s) return [];
  const drivenJ = new Set((result.value.stats.drives || []).map((d) => d.joint));
  const out = [];
  for (const g of shown.value) {
    let names = Object.keys(s).filter((n) => n !== 't' && describe(n, jtypes.value).group === g);
    if (['q', 'qd', 'qdd'].includes(g) && names.length > 6) names = names.filter((n) => drivenJ.has(n.split('.')[1]));
    if (['rf', 'rm'].includes(g)) names = names.filter((n) => !n.includes('wq_payload'));
    let more = false;
    if (names.length > 6) {                                        // 只画最大的 6 条（颜色按固定顺序，不循环）
      names.sort((a, b) => Math.max(...s[b].map(Math.abs)) - Math.max(...s[a].map(Math.abs)));
      names = names.slice(0, 6); more = true;
    }
    // 位置、速度：转动和移动单位不同，分开画
    const byUnit = {};
    for (const n of names) { const d = describe(n, jtypes.value, labels.value); (byUnit[d.unit] ||= []).push([n, d]); }
    for (const [unit, list] of Object.entries(byUnit)) {
      out.push({ group: g + unit, title: GROUPS[g], unit, more,
        series: list.map(([n, d], i) => ({ name: n, label: d.label, color: SERIES[i % SERIES.length], values: s[n].map((v) => v * d.k) })) });
    }
  }
  return out;
});
const trails = computed(() => {
  const s = series.value;
  if (!s) return [];
  const names = [...new Set(Object.keys(s).filter((n) => n.startsWith('pt.')).map((n) => n.split('.')[1]))];
  return names.map((p, i) => ({ color: SERIES[(i + 1) % SERIES.length], points: Array.from(s['pt.' + p + '.x'], (x, k) => [x, s['pt.' + p + '.y'][k], s['pt.' + p + '.z'][k]]) }));
});
function downloadCsv() {
  const names = Object.keys(series.value).filter((n) => n !== 't');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([toCSV(series.value, names)], { type: 'text/csv' }));
  a.download = `动力学-${job.value?.title || job.value?.id}.csv`;
  document.body.appendChild(a); a.click(); a.remove();
}
async function loadJobs() { try { jobs.value = (await get('/mbd/jobs')).jobs; } catch (e) { /* */ } }

onMounted(async () => {
  try {
    const [m, r] = await Promise.all([get('/mbd/mechs'), get('/mbd/robots')]);
    mechs.value = m.mechs; robots.value = r.robots;
    if (mech.value) mechParams.value = { ...mech.value.params };
  } catch (e) { err.value = e.status === 503 ? '计算服务暂时连不上，请稍后再试' : e.message; }
  loadJobs();
});
onUnmounted(() => { clearTimeout(pollT); cancelAnimationFrame(raf); playing.value = false; });
</script>

<style scoped>
.side { width: 400px; flex-shrink: 0; display: flex; flex-direction: column; gap: 9px; align-self: flex-start; }
.grow { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 10px; }
.step { display: flex; align-items: center; gap: 8px; font-weight: 600; margin-top: 6px; }
.step b { width: 22px; height: 22px; border-radius: 50%; background: var(--accent); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; }
.seg { display: inline-flex; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; align-self: flex-start; }
.seg button { border: 0; background: #fff; padding: 6px 12px; cursor: pointer; font-size: 13px; }
.seg button.on { background: var(--accent-bg); font-weight: 600; }
.full { width: 100%; height: 34px; border: 1px solid #C8CEC7; border-radius: 6px; padding: 0 8px; background: #fff; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 10px; margin-top: 6px; }
.grid2 input { width: 80px; }
.upload { display: flex; flex-direction: column; gap: 4px; color: var(--muted); }
.jrow { border: 1px solid var(--line); border-radius: 8px; padding: 6px 8px; display: flex; flex-direction: column; gap: 4px; }
.jrow.inline { flex-direction: row; align-items: center; gap: 6px; flex-wrap: wrap; }
.jname { font-weight: 500; }
.jctl { display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: center; }
input[type=number] { width: 64px; height: 26px; border: 1px solid #C8CEC7; border-radius: 5px; padding: 0 4px; }
select { height: 26px; border: 1px solid #C8CEC7; border-radius: 5px; }
.pname { width: 48px; height: 26px; border: 1px solid #C8CEC7; border-radius: 5px; padding: 0 4px; }
.x { border: 0; background: none; font-size: 16px; cursor: pointer; color: var(--muted); margin-left: auto; }
.chk { display: flex; gap: 6px; align-items: center; }
.line { display: flex; gap: 8px; flex-wrap: wrap; }
.small-btn { height: 28px; font-size: 12px; }
.big-w { height: 42px; font-size: 15px; margin-top: 6px; }
.card-head { flex-wrap: wrap; align-items: center; }
.jobbar { border-radius: 8px; padding: 10px 14px; background: var(--accent-bg); color: var(--accent); }
.jobbar.failed { background: var(--bad-bg); color: var(--bad); }
.big-empty { padding: 120px 0; text-align: center; }
.player { display: flex; align-items: center; gap: 10px; }
.player input[type=range] { flex: 1; }
.sum { margin-top: 4px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.chip { border: 1px solid var(--line); background: #fff; border-radius: 14px; padding: 3px 10px; cursor: pointer; font-size: 12px; }
.chip.on { background: var(--accent-bg); border-color: var(--accent); color: var(--accent); font-weight: 600; }
.charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 14px; }
@media (max-width: 1100px) { .side { width: 100%; } .charts { grid-template-columns: 1fr; } }
</style>
