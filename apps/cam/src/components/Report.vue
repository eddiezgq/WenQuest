<script setup>
// The calculation sheet: inputs, motion program, checks, curves and the cam outline, laid out for printing
// (the browser's "save as PDF"). Round 39, step 2.
import { computed } from 'vue'
import { project, result, laws, mfgResult, measResult, compResult } from '../store'
import { t, lang } from '../i18n'
import Checks from './Checks.vue'
import Charts from './Charts.vue'
import LineChart from './LineChart.vue'
import BarChart from './BarChart.vue'

const emit = defineEmits(['close'])
const doPrint = () => window.print()
const r = computed(() => result.value)
const zh = computed(() => lang.value === 'zh')
const today = new Date().toISOString().slice(0, 10)
const m = computed(() => project.mechanism)
const lawOf = (k) => laws.value.find((l) => l.key === k)
const segs = computed(() => project.program.segments || [])
const outline = computed(() => {
  const p = r.value?.shapes?.profile
  if (!p) return null
  const R = Math.max(...p[0].map((x, i) => Math.hypot(x, p[1][i])), ...(r.value.shapes.outer ? r.value.shapes.outer[0].map((x, i) => Math.hypot(x, r.value.shapes.outer[1][i])) : []))
  const d = (xy) => 'M' + xy[0].map((x, i) => `${x.toFixed(2)},${(-xy[1][i]).toFixed(2)}`).join('L') + 'Z'
  return { R: R * 1.08, prof: d(p), outer: r.value.shapes.outer ? d(r.value.shapes.outer) : null, pitch: r.value.shapes.pitch ? d(r.value.shapes.pitch) : null }
})
const mr = computed(() => mfgResult.value)
const me = computed(() => measResult.value)
const cp = computed(() => compResult.value)
const nMethod = computed(() => 6 + (mr.value ? 1 : 0) + (me.value ? 1 : 0))
const mfgRows = computed(() => {
  const f = project.mfg, r = mr.value
  if (!r) return []
  const out = [[t('process'), t(f.process)], [f.process === 'grind' ? t('wheelR') : t('millR'), `${f.tool_r} mm`], [t('chordTol'), `${f.chord_tol} mm`]]
  if (f.process === 'grind') out.push([t('xMode'), f.grind.x_mode === 'diameter' ? t('xDiameter') : t('xRadius')], [t('workRpm'), `${f.grind.work_rpm} r/min`], [t('allowances'), (f.grind.allowances || []).join(', ') + ' mm'])
  else out.push([t('feed'), `${f.mill.feed} mm/min`], [t('stepDown'), `${f.mill.step_down} mm`])
  const s = r.sim
  if (s) out.push([t('maxOver'), `${(s.over[0] * 1000).toFixed(3)} µm`], [t('maxUnder'), `${(s.under[0] * 1000).toFixed(3)} µm`])
  return out
})
const rows = computed(() => {
  const mm = m.value, L = project.loads, mat = project.material
  const osc = mm.follower === 'oscillating'
  const out = [[t('follower'), `${t(mm.follower)} · ${t(mm.contact)}${mm.groove ? ' · ' + t('groove') : ''}`], [t('sigma'), mm.sigma === 1 ? t('ccw') : t('cw')],
    [t('rb'), `${mm.rb} mm`]]
  if (mm.contact === 'roller') out.push([t('rr'), `${mm.rr} mm`])
  if (!osc && mm.contact !== 'flat') out.push([t('e'), `${mm.e || 0} mm`])
  if (osc) out.push([t('a'), `${mm.a} mm`]); if (osc && mm.contact !== 'flat') out.push([t('L'), `${mm.L} mm`])
  if (mm.width) out.push([t('width'), `${mm.width} mm`])
  const opt = (k, v, u) => out.push([t(k), v == null || v === '' ? (zh.value ? '未填' : 'not given') : `${v} ${u}`])
  opt('rpm', L.rpm, 'r/min'); osc ? opt('inertia', L.inertia, 'kg·m²') : opt('mass', L.mass, 'kg')
  opt('k', L.k, osc ? 'N·mm/rad' : 'N/mm'); opt('preload', L.preload, osc ? 'rad' : 'mm'); opt('load', L.load, osc ? 'N·mm' : 'N')
  opt('E', mat.E1 && `${mat.E1} / ${mat.E2}`, 'MPa'); opt('nu', mat.nu1 && `${mat.nu1} / ${mat.nu2}`, '')
  return out
})
</script>

<template>
  <div class="report">
    <div class="bar noprint"><button type="button" class="dark" @click="emit('close')">← {{ t('back') }}</button><button type="button" class="solid" @click="doPrint">{{ t('print') }}</button></div>
    <article v-if="r">
      <header>
        <p class="brand">{{ t('app') }} · {{ t('report') }}</p>
        <h1>{{ zh ? project.title.zh : project.title.en }}</h1>
        <p class="meta mono">{{ today }} · camkit 0.1 · {{ zh ? '计算由确定性程序完成，未经 AI' : 'Computed by deterministic code, not by AI' }}</p>
      </header>
      <section>
        <h2>1 {{ zh ? '机构与载荷' : 'Mechanism and loads' }}</h2>
        <table class="kv"><tr v-for="row in rows" :key="row[0]"><th>{{ row[0] }}</th><td>{{ row[1] }}</td></tr></table>
      </section>
      <section>
        <h2>2 {{ t('tabProgram') }}</h2>
        <table v-if="segs.length" class="tb"><thead><tr><th>#</th><th>{{ t('kind') }}</th><th>{{ t('angle') }}</th><th>{{ t('lift') }}</th><th>{{ t('law') }}</th><th>Cv</th><th>Ca</th></tr></thead>
          <tbody><tr v-for="(s, i) in segs" :key="i"><td>{{ i + 1 }}</td><td>{{ t(s.kind === 'return' ? 'ret' : s.kind) }}</td><td>{{ s.deg }}</td>
            <td>{{ s.kind === 'dwell' ? '' : (s.h ?? s.h_deg) + (r.unit === 'rad' ? '°' : ' mm') }}</td>
            <td>{{ s.kind === 'dwell' ? '' : (zh ? lawOf(s.law)?.zh : lawOf(s.law)?.en) }}</td>
            <td>{{ s.kind === 'dwell' ? '' : lawOf(s.law)?.Cv.toFixed(3) }}</td><td>{{ s.kind === 'dwell' ? '' : lawOf(s.law)?.Ca.toFixed(3) }}</td></tr></tbody></table>
        <p v-else>{{ zh ? '运动程序由点表给出（周期三次样条）。' : 'The motion is given by a point table (periodic cubic spline).' }}</p>
      </section>
      <section>
        <h2>3 {{ t('checks') }}</h2>
        <Checks :result="r" />
      </section>
      <section class="figs">
        <h2>4 {{ zh ? '曲线' : 'Curves' }}</h2>
        <Charts :result="r" :theta="0" print />
      </section>
      <section v-if="outline">
        <h2>5 {{ zh ? '凸轮廓线（凸轮坐标系，θ = 0）' : 'Cam outline (cam frame, θ = 0)' }}</h2>
        <svg class="outline" :viewBox="`${-outline.R} ${-outline.R} ${2 * outline.R} ${2 * outline.R}`">
          <path v-if="outline.outer" :d="outline.outer" class="o" /><path :d="outline.prof" class="o" /><path v-if="outline.pitch" :d="outline.pitch" class="p" />
          <circle :r="outline.R * 0.01" />
        </svg>
      </section>
      <section v-if="mr">
        <h2>6 {{ t('mfgSection') }}</h2>
        <table class="kv"><tr v-for="row in mfgRows" :key="row[0]"><th>{{ row[0] }}</th><td>{{ row[1] }}</td></tr></table>
        <Checks :result="{ status: mr.checks.some((c) => c.status === 'fail') ? 'fail' : 'pass', checks: mr.checks }" />
        <LineChart v-if="mr.sim" :w="640" :title="t('simDev')" unit="µm" :x="mr.sim.deg" :series="mr.sim.flanks.map((f, i) => ({ y: f.dev_um, cls: i ? 'b' : '' }))" :note="t('simNote')" />
        <p class="small mono">{{ zh ? '程序' : 'Program' }}: O{{ project.mfg.process === 'grind' ? project.mfg.grind.prog_no : project.mfg.mill.prog_no }}, {{ mr.program?.split('\n').length }} {{ zh ? '行（另附 .nc 文件）' : 'lines (see the .nc file)' }}</p>
      </section>
      <section v-if="me">
        <h2>{{ mr ? 7 : 6 }} {{ t('measSection') }}</h2>
        <table class="kv">
          <tr><th>{{ t('shift') }}</th><td>{{ me.shift_deg.toFixed(4) }}°</td></tr>
          <tr><th>{{ t('offset') }}</th><td>{{ me.offset.toFixed(3) }} {{ me.err_unit }}</td></tr>
          <tr><th>{{ t('gFirst') }} / {{ t('gLow') }} / {{ t('gHigh') }} ({{ t('rms') }})</th><td>{{ me.groups.first.toFixed(3) }} / {{ me.groups.low.toFixed(3) }} / {{ me.groups.high.toFixed(3) }} {{ me.err_unit }}</td></tr>
          <tr v-if="cp"><th>{{ t('comp') }} {{ cp.lo }}–{{ cp.hi }}</th><td>{{ t('rms') }} {{ cp.rms_before.toFixed(3) }} → {{ cp.rms_after.toFixed(3) }} {{ me.err_unit }}</td></tr>
        </table>
        <Checks :result="{ status: me.checks.some((c) => c.status === 'fail') ? 'fail' : me.checks.some((c) => c.status === 'unknown') ? 'unknown' : 'pass', checks: me.checks }" />
        <LineChart :w="640" :title="t('errCurve')" :unit="me.err_unit" :x="me.deg" :series="cp ? [{ y: me.e, label: t('before') }, { y: cp.remaining, label: t('after'), cls: 'b' }] : [{ y: me.e }]" />
        <BarChart :title="t('harm')" :unit="me.err_unit" :A="me.harm.A" :after="cp?.after_A" :low-hi="me.low_hi" :sel="cp ? [cp.lo, cp.hi] : null" :legend="[]" />
      </section>
      <section class="small">
        <h2>{{ nMethod }} {{ zh ? '方法与依据' : 'Method and references' }}</h2>
        <p>{{ zh ? '理论廓线由从动件位置经坐标变换得出，实际廓线为其等距线；压力角由接触点相对速度与从动件运动方向求出；曲率半径由廓线一、二阶导数求出；接触应力按赫兹线接触；跳离按弹簧力、载荷与惯性力之和是否始终大于 0 判断。未计导轨摩擦和重力。'
          : 'The pitch curve comes from the follower position by a change of frame, the profile is its offset; the pressure angle from the relative velocity at the contact and the follower’s direction of motion; the radius of curvature from the first and second derivatives; contact stress by Hertz line contact; jump by whether spring force, load and inertia force together stay above zero. Guide friction and gravity are not included.' }}</p>
        <p v-if="mr || me">{{ zh ? '制造：刀心轨迹为加工面沿法向等距刀具半径；按机床插补方式（X–C 线性或 XY 直线）以弦高公差布点；程序仿真独立读回程序文本，让刀具扫过毛坯求剩余材料边界，与设计廓线比法向偏差。测量：误差按转角均匀重采样后做傅里叶分解；加速度误差为误差二阶导数乘 ω²；补偿把所选阶次误差反向加到运动程序后重新出程序。'
          : 'Manufacturing: the tool centre path is the machined surface offset by the tool radius; points by chord tolerance under the machine\'s own interpolation (X–C linear or XY lines); the simulation reads the program text back and sweeps the tool through the blank, comparing the material left with the design along the normal. Measurement: the error resampled by cam angle and Fourier-analysed; acceleration error = second derivative × ω²; compensation subtracts the selected orders from the motion and makes the program again.' }}</p>
        <p>R. L. Norton, Cam Design and Manufacturing Handbook, 3rd ed., 2020 · F. Y. Chen, Mechanics and Design of Cam Mechanisms, 1982 · J. Angeles, C. S. López-Cajún, Optimization of Cam Mechanisms, 1991 · 孙桓《机械原理》</p>
        <p v-if="project.title.zh?.startsWith('示例')">{{ t('fictional') }}</p>
      </section>
    </article>
  </div>
</template>

<style scoped>
.report { background: var(--paper); min-height: 100vh; }
.bar { position: sticky; top: 0; display: flex; justify-content: space-between; padding: 10px 20px; background: var(--night); }
article { max-width: 820px; margin: 0 auto; padding: 24px 20px 60px; background: var(--surface); color: var(--ink); }
.brand { font: 500 12px/1 var(--mono); letter-spacing: .12em; color: var(--accent-ink); margin: 0 0 6px; }
h1 { font: 700 26px/1.25 var(--serif-zh); margin: 0; }
.meta { font-size: 12px; color: var(--muted); }
h2 { font-size: 15px; margin: 22px 0 8px; border-bottom: 1px solid var(--line); padding-bottom: 4px; }
.kv, .tb { border-collapse: collapse; font-size: 13px; width: 100%; }
.kv th { text-align: left; font-weight: 400; color: var(--muted); width: 45%; padding: 3px 0; }
.tb th, .tb td { border-bottom: 1px solid var(--line); padding: 4px 6px; text-align: left; }
.outline { width: 60%; display: block; margin: 0 auto; }
.outline .o { fill: none; stroke: var(--ink); stroke-width: .4; }
.outline .p { fill: none; stroke: var(--accent); stroke-width: .3; stroke-dasharray: 2 1.5; }
.small p { font-size: 12.5px; color: var(--muted); }
@media print {
  .noprint { display: none !important; }
  article { max-width: none; padding: 0; }
  section { break-inside: avoid; }
  .figs { break-inside: auto; }
}
</style>
