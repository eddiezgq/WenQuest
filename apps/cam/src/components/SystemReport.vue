<script setup>
// The calculation sheet of a cam system (round 39, step 4): drive and cams, timing, checks, torque, vibration, and
// the CAE results (the example's, computed beforehand). Printed from the browser to PDF.
import { computed } from 'vue'
import { system, sysResult, caeExample } from '../sysstore'
import { laws } from '../store'
import { t, lang } from '../i18n'
import Checks from './Checks.vue'
import LineChart from './LineChart.vue'
import TimingDiagram from './TimingDiagram.vue'

const emit = defineEmits(['close'])
const doPrint = () => window.print()
const r = computed(() => sysResult.value)
const zh = computed(() => lang.value === 'zh')
const today = new Date().toISOString().slice(0, 10)
const nm = (n) => (zh.value ? n?.zh : n?.en) || ''
const fmt = (v, d = 2) => (v == null || !Number.isFinite(+v) ? (zh.value ? '未填' : 'not given') : (+v).toFixed(d))
const lawOf = (k) => laws.value.find((l) => l.key === k)
const cs = computed(() => system.camshaft || {})
const dr = computed(() => system.drive || {})
const status = (checks) => (checks.some((c) => c.status === 'fail') ? 'fail' : checks.some((c) => c.status === 'unknown') ? 'unknown' : 'pass')
const cae = computed(() => caeExample.value)
</script>

<template>
  <div class="report">
    <div class="bar noprint"><button type="button" class="dark" @click="emit('close')">← {{ t('back') }}</button><button type="button" class="solid" @click="doPrint">{{ t('print') }}</button></div>
    <article v-if="r">
      <header>
        <p class="brand">{{ t('app') }} · {{ t('report') }}</p>
        <h1>{{ nm(system.title) }}</h1>
        <p class="meta mono">{{ today }} · camkit 0.4 · {{ zh ? '计算由确定性程序完成，未经 AI' : 'Computed by deterministic code, not by AI' }}</p>
      </header>
      <section>
        <h2>1 {{ t('camshaft') }}</h2>
        <table class="kv">
          <tr><th>{{ t('runRpm') }}</th><td>{{ fmt(cs.rpm, 1) }} r/min</td></tr>
          <tr><th>{{ t('startDeg') }} / {{ t('stopDeg') }}</th><td>{{ fmt(cs.start_deg, 0) }}° / {{ fmt(cs.stop_deg, 0) }}°</td></tr>
          <tr><th>{{ t('Jcs') }}</th><td>{{ fmt(cs.J, 4) }} kg·m²</td></tr>
          <tr><th>{{ t('ratio') }} · {{ t('eta') }}</th><td>{{ fmt(dr.ratio, 1) }} · {{ fmt(dr.eta, 2) }}</td></tr>
          <tr><th>{{ zh ? '循环时间' : 'Cycle time' }}</th><td>{{ fmt(r.cycle, 3) }} s</td></tr>
        </table>
      </section>
      <section>
        <h2>2 {{ zh ? '凸轮与运动程序' : 'Cams and motion programs' }}</h2>
        <div v-for="c in system.cams" :key="c.id" class="cam">
          <h3>{{ nm(c.name) }}</h3>
          <table class="tb"><thead><tr><th>#</th><th>{{ t('kind') }}</th><th>{{ t('angle') }}</th><th>{{ t('lift') }}</th><th>{{ t('law') }}</th></tr></thead>
            <tbody><tr v-for="(s, i) in c.program.segments" :key="i"><td>{{ i + 1 }}</td><td>{{ t(s.kind === 'return' ? 'ret' : s.kind) }}</td><td>{{ s.deg }}</td>
              <td>{{ s.kind === 'dwell' ? '' : (s.h ?? s.h_deg) + (c.program.unit === 'rad' ? '°' : ' mm') }}</td><td>{{ s.kind === 'dwell' ? '' : (zh ? lawOf(s.law)?.zh : lawOf(s.law)?.en) || s.law }}</td></tr></tbody></table>
          <p v-if="c.globoidal" class="small">C {{ c.globoidal.C }} · n {{ c.globoidal.n }} · R_p {{ c.globoidal.Rp }} · r_r {{ c.globoidal.rr }} · b {{ c.globoidal.b }} · L {{ c.globoidal.L }} mm</p>
        </div>
      </section>
      <section>
        <h2>3 {{ t('timing') }}</h2>
        <TimingDiagram :res="r" :theta="0" />
      </section>
      <section>
        <h2>4 {{ t('checks') }}</h2>
        <h3>{{ zh ? '系统' : 'System' }}</h3>
        <Checks :result="{ status: status(r.checks), checks: r.checks }" />
        <template v-for="c in r.cams" :key="c.id"><h3>{{ nm(c.name) }}</h3><Checks :result="{ status: status(c.checks), checks: c.checks }" /></template>
      </section>
      <section class="figs">
        <h2>5 {{ zh ? '转矩与振动' : 'Torque and vibration' }}</h2>
        <LineChart :w="640" :title="t('camTorque')" unit="N·m" :x="r.deg" :series="[{ y: r.T_cs }]" />
        <LineChart :w="640" :title="t('motorTorque')" unit="N·m" :x="r.deg" :series="[{ y: r.T_motor, cls: 'b' }]" />
        <table class="tb"><thead><tr><th /><th>{{ t('from') }}</th><th>{{ t('amp') }}</th><th>{{ t('tipUm') }}</th></tr></thead>
          <tbody><template v-for="c in r.cams" :key="c.id"><tr v-for="(d, i) in c.vib || []" :key="c.id + i"><td>{{ i === 0 ? nm(c.name) : '' }}</td>
            <td>{{ fmt(d.from, 0) }}–{{ fmt(d.to, 0) }}°</td><td>{{ fmt(d.amp, 1) }} {{ c.unit === 'deg' ? '″' : 'µm' }}</td><td>{{ fmt(d.tip_um, 1) }} µm</td></tr></template></tbody></table>
      </section>
      <section v-if="cae">
        <h2>6 {{ t('modeCae') }}</h2>
        <p class="small">{{ zh ? cae.note.zh : cae.note.en }}</p>
        <table class="kv">
          <tr><th>{{ t('vmMax') }}</th><td>{{ fmt(cae.arm.job.stats.vm_max_mpa, 1) }} MPa</td></tr>
          <tr><th>{{ t('safety') }}</th><td>{{ fmt(cae.arm.job.stats.safety_factor, 2) }}</td></tr>
          <tr><th>{{ t('modes') }}</th><td>{{ cae.modal.freqs.slice(0, 3).map((f) => f.hz.toFixed(0) + ' Hz').join(' · ') }}</td></tr>
          <tr><th>{{ t('peakMbd') }} / {{ t('peakCamkit') }}</th><td>{{ fmt(cae.compare.compare.peak_mbd, 1) }} / {{ fmt(cae.compare.compare.peak_camkit, 1) }} N·m（{{ t('relDiff') }} {{ fmt(cae.compare.compare.rel_rms * 100, 1) }} %）</td></tr>
        </table>
      </section>
      <section class="small">
        <h2>{{ cae ? 7 : 6 }} {{ zh ? '方法与依据' : 'Method and references' }}</h2>
        <p>{{ zh ? '弧面分度凸轮齿面按啮合原理求包络（滚子法向垂直于滚子轴线和相对速度），压力角 tan α = ρφ′/(C − ρ cos φ)，根切与干涉按“接触点不被其他时刻的滚子切掉”数值检查；凸轮轴转矩按拉格朗日方程（等效转动惯量随转角变化），起动、制动按匀加减速；残余振动按单自由度基础激励模型精确离散求解。CAE 由问渠数字工厂计算服务完成。' : 'Globoidal flanks by the condition of meshing; tan α = ρφ′/(C − ρ cos φ); undercut checked numerically; camshaft torque by Lagrange with the equivalent inertia; vibration by a base-excited single degree of freedom solved exactly between samples. CAE by the WenQuest digital factory service.' }}</p>
        <p>F. L. Litvin, A. Fuentes, Gear Geometry and Applied Theory, 2004 · R. L. Norton, Cam Design and Manufacturing Handbook, 2020 · H. A. Rothbart, Cam Design Handbook, 2004 · 刘昌祺《自动机械凸轮机构实用设计手册》，2013</p>
        <p>{{ t('fictional') }}</p>
      </section>
    </article>
  </div>
</template>

<style scoped>
.report { background: var(--paper); min-height: 100vh; }
.bar { position: sticky; top: 0; z-index: 2; display: flex; justify-content: space-between; padding: 10px 20px; background: var(--night); }
article { max-width: 860px; margin: 0 auto; padding: 24px 20px 60px; background: var(--surface); color: var(--ink); }
.brand { font: 500 12px/1 var(--mono); letter-spacing: .12em; color: var(--accent-ink); margin: 0 0 6px; }
h1 { font: 700 24px/1.3 var(--serif-zh); margin: 0; }
h2 { font-size: 15px; margin: 22px 0 8px; border-bottom: 1px solid var(--line); padding-bottom: 4px; }
h3 { font-size: 13.5px; margin: 12px 0 4px; }
.meta { font-size: 12px; color: var(--muted); }
.kv, .tb { border-collapse: collapse; font-size: 13px; width: 100%; }
.kv th { text-align: left; font-weight: 400; color: var(--muted); width: 45%; padding: 3px 0; }
.tb th, .tb td { border-bottom: 1px solid var(--line); padding: 4px 6px; text-align: left; }
.small, .small p { font-size: 12.5px; color: var(--muted); }
.figs > * + * { margin-top: 8px; }
@media print { .noprint { display: none !important; } article { max-width: none; padding: 0; } section { break-inside: avoid; } .figs { break-inside: auto; } }
</style>
