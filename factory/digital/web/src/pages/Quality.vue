<template>
  <div class="page">
    <TaskBar v-if="teachStatus" :t="teachStatus" />
    <div class="page-title"><h1>质量</h1><span class="muted">质检员工作区 · 三坐标测量值、控制图、不合格品评审</span></div>
    <div class="row">
      <section class="card grow">
        <div class="card-head">
          <h2>控制图</h2>
          <select v-model="ch" @change="load">
            <option v-for="c in CHARS" :key="c.key" :value="c.key">{{ c.name }}</option>
          </select>
          <span class="muted small">quality/qc-01/measurement · 最近 {{ rows.length }} 件</span>
        </div>
        <ControlChart v-if="chart.points.length" :chart="chart" :height="220" />
        <div v-else class="empty">还没有这个特性的测量值。</div>
        <p v-if="chart.points.length" class="small">最近 5 件均值 <b class="mono">{{ mean5.toFixed(4) }}</b> mm，偏离公差中值
          <b class="mono">{{ ((mean5 - chart.center) * 1000).toFixed(1) }}</b> µm，距上限 <b class="mono">{{ ((chart.upper - max5) * 1000).toFixed(1) }}</b> µm。</p>
        <table class="t">
          <thead><tr><th>时间</th><th>零件</th><th>工单</th><th class="num">实测 mm</th><th class="num">公差</th><th>判定</th></tr></thead>
          <tbody><tr v-for="r in rows.slice().reverse().slice(0, 30)" :key="r.id">
            <td class="small">{{ timeOf(r.ts) }}</td><td class="mono small">{{ r.part_serial }}</td><td class="mono small">{{ r.work_order }}</td>
            <td class="num">{{ r.value_mm.toFixed(4) }}</td><td class="num small">{{ r.lower_tol_mm }}–{{ r.upper_tol_mm }}</td>
            <td><span class="pill" :class="r.result === 'pass' ? 'good' : 'bad'">{{ r.result === 'pass' ? '合格' : '超差' }}</span></td>
          </tr></tbody>
        </table>
      </section>
      <section class="card side">
        <div class="card-head"><h2>不合格品</h2><span class="muted small">超差零件自动开单（quality/qc-01/ncr）</span></div>
        <div v-if="!ncr.length" class="empty">没有不合格品。</div>
        <div v-for="n in ncr" :key="n.ncr_id" class="ncr">
          <div><b class="mono">{{ n.ncr_id }}</b> <span class="mono small">{{ n.part_serial }}</span>
            <span class="pill" :class="n.status === 'open' ? 'bad' : 'good'">{{ DISP[n.status] }}</span></div>
          <div class="small muted">{{ n.detail.name }} 实测 {{ n.detail.value_mm }} mm（{{ n.detail.lower_tol_mm }}–{{ n.detail.upper_tol_mm }}）</div>
          <div v-if="n.status === 'open'" class="acts">
            <button class="btn" @click="decide(n, 'rework')">返修</button>
            <button class="btn danger" @click="decide(n, 'scrap')">报废</button>
            <button class="btn ghost" @click="decide(n, 'use_as_is')">让步接收</button>
          </div>
          <div v-else class="small muted">由 {{ n.decided_by }} 评审</div>
        </div>
        <div class="card-head" style="margin-top: 18px;"><h2>砂轮</h2></div>
        <p class="small">磨床 GRD-01 砂轮剩余寿命 <b class="mono">{{ grdLife }}</b>。砂轮越磨损，磨出的轴承位直径越偏大；寿命低于 8% 时自动修整。</p>
        <template v-if="teachStatus">
          <div class="card-head" style="margin-top: 18px;"><h2>任务 5 问答</h2></div>
          <p class="small">轴承位直径为什么会逐渐变大？</p>
          <label v-for="c in teachStatus.t5_choices" :key="c" class="choice small"><input v-model="t5" type="radio" :value="c"> {{ c }}</label>
          <button class="btn primary" :disabled="!t5" @click="answer">提交</button>
          <div v-if="fb" class="small" :class="fbOk ? 'ok' : 'err'">{{ fb }}</div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { get, post, session } from '../lib/api';
import { bus } from '../lib/bus';
import { timeOf } from '../lib/fmt';
import ControlChart from '../components/ControlChart.vue';
import TaskBar from '../components/TaskBar.vue';

const CHARS = [
  { key: 'bearing_seat_d35', name: '轴承位直径 Ø35 k6' },
  { key: 'gear_seat_d40', name: '齿轮位直径 Ø40 k6' },
  { key: 'keyway_width_12', name: '键槽宽 12 N9' },
];
const DISP = { open: '待评审', rework: '返修', scrap: '报废', use_as_is: '让步接收' };
const ch = ref('bearing_seat_d35');
const rows = ref([]);
const ncr = ref([]);
const t5 = ref('');
const fb = ref('');
const fbOk = ref(true);
const teachStatus = ref(null);
const chart = computed(() => {
  const r = rows.value.slice(-30);
  if (!r.length) return { points: [] };
  const lo = r[0].lower_tol_mm, hi = r[0].upper_tol_mm;
  return { lower: lo, upper: hi, center: (lo + hi) / 2,
    points: r.map((x) => ({ id: x.id, value: x.value_mm, serial: x.part_serial, result: x.result })) };
});
const last5 = computed(() => rows.value.slice(-5).map((r) => r.value_mm));
const mean5 = computed(() => last5.value.reduce((a, b) => a + b, 0) / Math.max(1, last5.value.length));
const max5 = computed(() => Math.max(...last5.value));
const grdLife = computed(() => {
  const g = bus.machines['grd-01'];
  return g ? Math.round(g.tool_life_left * 100) + '%' : '—';
});
async function load() {
  [rows.value, ncr.value] = await Promise.all([get('/quality/measurements?characteristic=' + ch.value + '&limit=60'), get('/ncr')]);
}
async function decide(n, d) {
  await post('/ncr/' + n.ncr_id, { disposition: d });
  load();
}
async function answer() {
  const r = await post('/teach/t5', { reason: t5.value });
  fb.value = `${r.feedback}（本题得 ${r.score} / ${r.of}）`;
  fbOk.value = r.score >= 8;
  teachStatus.value = await get('/teach');
}
onMounted(async () => {
  load();
  if (session.user.mode === 'teach') teachStatus.value = await get('/teach');
});
</script>

<style scoped>
.grow { flex-grow: 1; min-width: 0; }
.side { width: 380px; flex-shrink: 0; }
.card-head select { height: 32px; border: 1px solid var(--line); border-radius: 6px; }
.ncr { padding: 10px 0; border-top: 1px solid var(--line-soft); display: flex; flex-direction: column; gap: 4px; }
.acts { display: flex; gap: 6px; margin-top: 4px; }
.choice { display: block; padding: 4px 0; }
@media (max-width: 1100px) { .side { width: auto; } }
</style>
