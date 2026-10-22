<script setup>
// Manufacture (round 39, step 3): tool and machine settings, the cam on the machine, checks, the program,
// the simulated deviation and the downloads.
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { project, payloadFull, mfgResult } from '../store'
import { api, saveText } from '../api'
import { t, lang } from '../i18n'
import MfgView from './MfgView.vue'
import Checks from './Checks.vue'
import LineChart from './LineChart.vue'
const fcHref = import.meta.env.BASE_URL + 'api/freecad.zip'

const mf = computed(() => project.mfg)
const groove = computed(() => !!project.mechanism.groove)
const res = mfgResult
const err = ref(null)
const busy = ref(false)
const theta = ref(0)
const playing = ref(false)
const msg = ref('')
const num = (v) => (v === '' || v === null ? null : Number(v))
const allowText = ref((mf.value.grind.allowances || []).join(', '))
watch(allowText, (v) => { mf.value.grind.allowances = v.split(/[,\s，]+/).map(Number).filter(Number.isFinite) })

let timer = 0, seq = 0
function run(delay = 500) {
  clearTimeout(timer)
  timer = setTimeout(async () => {
    if (mf.value.process !== 'wire' && !(mf.value.tool_r > 0)) { res.value = null; err.value = null; return }
    const mine = ++seq
    busy.value = true
    try {
      const r = mf.value.process === 'wire' ? null : await api('/manufacture', payloadFull())
      if (mine === seq) { res.value = r; err.value = null }
    } catch (e) { if (mine === seq) { err.value = e; res.value = null } } finally { if (mine === seq) busy.value = false }
  }, delay)
}
const key = computed(() => JSON.stringify([payloadFull(), null]))
watch(key, () => run(), { immediate: true })

let raf = 0, last = 0
function loop(ts) { if (!playing.value) return; if (last) theta.value = (theta.value + ((ts - last) / 1000) * 30) % 360; last = ts; raf = requestAnimationFrame(loop) }
watch(playing, (p) => { if (p) { last = 0; raf = requestAnimationFrame(loop) } else cancelAnimationFrame(raf) })
onBeforeUnmount(() => { cancelAnimationFrame(raf); clearTimeout(timer) })

async function download(kind) {
  msg.value = ''
  try {
    const f = await api('/export/' + kind, payloadFull())
    saveText(f.name, f.text, f.mime)
    if (f.report?.fit_dev) {
      const d = Math.max(...Object.values(f.report.fit_dev)) * 1000
      msg.value = lang.value === 'zh' ? `STEP：B 样条拟合最大偏差 ${d.toFixed(3)} µm` : `STEP: largest B-spline fit deviation ${d.toFixed(3)} µm`
    }
  } catch (e) { msg.value = lang.value === 'zh' ? e.zh : e.message }
}
const wheel = ref(null)
async function wheelErr() {
  wheel.value = null
  try { wheel.value = await api('/wheel-error', payloadFull()) } catch (e) { wheel.value = { error: lang.value === 'zh' ? e.zh : e.message } }
}
const progHead = computed(() => {
  const p = res.value?.program
  if (!p) return ''
  const lines = p.split('\n')
  return lines.length > 60 ? lines.slice(0, 40).concat(['…', ...lines.slice(-12)]).join('\n') : p
})
const simSeries = computed(() => {
  const s = res.value?.sim
  if (!s) return []
  return s.flanks.map((f, i) => ({ y: f.dev_um, label: s.flanks.length > 1 ? (f.name === 'outer' ? (lang.value === 'zh' ? '外侧壁' : 'outer flank') : (lang.value === 'zh' ? '内侧壁' : 'inner flank')) : '', cls: i ? 'b' : '' }))
})
</script>

<template>
  <main class="work mfg">
    <aside class="edit">
      <div class="pane form">
        <div class="row seg">
          <span class="lab">{{ t('process') }}</span>
          <button v-for="p in ['grind', 'mill', 'wire']" :key="p" type="button" :class="{ on: mf.process === p }" @click="mf.process = p">{{ t(p) }}</button>
        </div>
        <template v-if="mf.process !== 'wire'">
          <label>{{ mf.process === 'grind' ? t('wheelR') : t('millR') }} <span class="u">mm</span><input :value="mf.tool_r" type="number" step="any" min="0" @input="mf.tool_r = num($event.target.value)"></label>
          <label>{{ t('chordTol') }} <span class="u">mm</span><input :value="mf.chord_tol" type="number" step="any" min="0.00001" @input="mf.chord_tol = num($event.target.value)"></label>
          <h4>{{ t('machine') }} <small>{{ t('machineNote') }}</small></h4>
          <template v-if="mf.process === 'grind'">
            <div class="row seg"><span class="lab">{{ t('xMode') }}</span>
              <button type="button" :class="{ on: mf.grind.x_mode === 'radius' }" @click="mf.grind.x_mode = 'radius'">{{ t('xRadius') }}</button>
              <button type="button" :class="{ on: mf.grind.x_mode === 'diameter' }" @click="mf.grind.x_mode = 'diameter'">{{ t('xDiameter') }}</button></div>
            <label>{{ t('workRpm') }} <span class="u">r/min</span><input :value="mf.grind.work_rpm" type="number" step="any" min="0" @input="mf.grind.work_rpm = num($event.target.value)"></label>
            <label>{{ t('allowances') }} <span class="u">mm</span><input v-model="allowText" type="text"></label>
            <label>{{ t('sparkout') }}<input :value="mf.grind.sparkout" type="number" step="1" min="0" @input="mf.grind.sparkout = num($event.target.value)"></label>
            <label>{{ t('progNo') }}<input :value="mf.grind.prog_no" type="number" step="1" min="1" @input="mf.grind.prog_no = num($event.target.value)"></label>
          </template>
          <template v-else>
            <label>{{ t('spindle') }} <span class="u">r/min</span><input :value="mf.mill.spindle_rpm" type="number" step="any" min="0" @input="mf.mill.spindle_rpm = num($event.target.value)"></label>
            <label>{{ t('feed') }} <span class="u">mm/min</span><input :value="mf.mill.feed" type="number" step="any" min="0" @input="mf.mill.feed = num($event.target.value)"></label>
            <label>{{ t('plunge') }} <span class="u">mm/min</span><input :value="mf.mill.plunge_feed" type="number" step="any" min="0" @input="mf.mill.plunge_feed = num($event.target.value)"></label>
            <label>{{ t('depth') }} <span class="u">mm · {{ t('depthNote') }}</span><input :value="mf.depth" type="number" step="any" min="0" @input="mf.depth = num($event.target.value)"></label>
            <label>{{ t('stepDown') }} <span class="u">mm</span><input :value="mf.mill.step_down" type="number" step="any" min="0" @input="mf.mill.step_down = num($event.target.value)"></label>
            <label>{{ t('safeZ') }} <span class="u">mm</span><input :value="mf.mill.safe_z" type="number" step="any" @input="mf.mill.safe_z = num($event.target.value)"></label>
            <label class="check"><input v-model="mf.mill.climb" type="checkbox"> {{ t('climb') }}</label>
            <label>{{ t('progNo') }}<input :value="mf.mill.prog_no" type="number" step="1" min="1" @input="mf.mill.prog_no = num($event.target.value)"></label>
          </template>
        </template>
        <p v-else class="note">{{ t('wireNote') }}</p>
        <h4>{{ t('blankTitle') }}</h4>
        <p class="note">{{ t('blankNote') }}</p>
        <template v-if="groove">
          <label>{{ t('blankR') }} <span class="u">mm</span><input :value="mf.blank.radius" type="number" step="any" min="0" @input="mf.blank.radius = num($event.target.value)"></label>
          <label>{{ t('plate') }} <span class="u">mm</span><input :value="mf.blank.plate" type="number" step="any" min="0" @input="mf.blank.plate = num($event.target.value)"></label>
        </template>
        <template v-if="mf.process === 'grind'">
          <h4>{{ t('wheelWear') }}</h4>
          <label>{{ t('rActual') }} <span class="u">mm</span><input :value="mf.r_actual" type="number" step="any" min="0" @input="mf.r_actual = num($event.target.value)"></label>
          <div class="row"><button type="button" class="ghost" :disabled="!(mf.tool_r > 0 && mf.r_actual > 0)" @click="wheelErr">{{ t('calc') }}</button></div>
          <p v-if="wheel?.error" class="bad">{{ wheel.error }}</p>
        </template>
      </div>
    </aside>

    <section class="stage">
      <div class="canvas">
        <MfgView v-if="res" :res="res" :theta="theta" />
        <p v-else-if="err" class="err">{{ t('error') }}：{{ lang === 'zh' ? err.zh || err.message : err.message }}</p>
        <p v-else class="hint">{{ mf.process === 'wire' ? t('wireNote') : t('needTool') }}</p>
        <p v-if="busy" class="busy">{{ t('computing') }}</p>
      </div>
      <div class="controls">
        <button type="button" class="solid" :disabled="!res" @click="playing = !playing">{{ playing ? '❚❚ ' + t('pause') : '▶ ' + t('play') }}</button>
        <label class="scrub">{{ t('camAngle') }} <input v-model.number="theta" type="range" min="0" max="359.9" step="0.1"> <span class="mono">{{ theta.toFixed(1) }}°</span></label>
      </div>
    </section>

    <aside class="side">
      <Checks v-if="res" :result="{ status: res.checks.some((c) => c.status === 'fail') ? 'fail' : 'pass', checks: res.checks }" />
      <h4>{{ t('downloads') }}</h4>
      <div class="dl">
        <button type="button" class="ghost" :disabled="!res?.program" @click="download('nc')">{{ t('dlNc') }}</button>
        <button type="button" class="ghost" @click="download('dxf')">{{ t('dlDxf') }}</button>
        <button type="button" class="ghost" @click="download('csv')">{{ t('dlCsv') }}</button>
        <button type="button" class="ghost" @click="download('step')">{{ t('dlStep') }}</button>
        <a class="ghost fc" :href="fcHref" download>{{ t('fcPack') }}</a>
      </div>
      <p class="note">{{ t('fcNote') }}</p>
      <p v-if="msg" class="note">{{ msg }}</p>
    </aside>

    <section class="curves bottom">
      <LineChart v-if="res?.sim" :title="t('simDev')" unit="µm" :x="res.sim.deg" :series="simSeries" :cursor="theta" :note="t('simNote')" />
      <LineChart v-if="wheel?.deg" :title="t('wheelWear')" unit="µm" :x="wheel.deg" :series="[{ y: wheel.dn_um, label: lang === 'zh' ? '廓线法向' : 'profile normal' }, { y: wheel.lift, label: lang === 'zh' ? '升程' : 'lift', cls: 'b' }]" />
      <figure v-if="res?.program" class="prog">
        <figcaption><b>{{ t('program') }}</b> <span class="u">{{ res.program.split('\n').length }} {{ lang === 'zh' ? '行' : 'lines' }}</span></figcaption>
        <pre>{{ progHead }}</pre>
      </figure>
    </section>
  </main>
</template>

<style scoped>
.form { display: grid; gap: 10px; align-content: start; }
.form label { display: grid; grid-template-columns: 1fr 110px; align-items: center; gap: 4px 8px; font-size: 13.5px; }
.form label .u { grid-column: 1; font: 400 11.5px/1.2 var(--mono); color: var(--muted); margin-top: -2px; }
.form label input { grid-column: 2; grid-row: 1 / span 2; }
.form label.check { display: flex; gap: 6px; }
.row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.seg .lab { font-size: 13.5px; min-width: 64px; }
.seg button { border: 1px solid var(--line); background: var(--surface); padding: 5px 9px; border-radius: 6px; font-size: 13px; color: var(--ink); }
.seg button.on { background: var(--ink); color: var(--paper); border-color: var(--ink); }
h4 { margin: 8px 0 0; font-size: 13px; font-weight: 600; }
h4 small { font-weight: 400; color: var(--hold); margin-left: 6px; }
.note { font-size: 12.5px; color: var(--muted); margin: 0; }
.bad { font-size: 12.5px; color: var(--bad); margin: 0; }
.hint { position: absolute; inset: 0; display: grid; place-items: center; color: var(--muted); margin: 0; padding: 20px; text-align: center; }
.dl { display: grid; gap: 6px; margin-top: 6px; }
.dl .fc { text-align: center; text-decoration: none; display: block; }
.side h4 { margin-top: 14px; }
.bottom { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 10px; }
.prog { margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 6px 8px; grid-column: 1 / -1; }
.prog figcaption { font-size: 12.5px; }
.prog .u { color: var(--muted); font: 400 11px/1 var(--mono); }
.prog pre { margin: 6px 0 0; max-height: 260px; overflow: auto; font: 12px/1.45 var(--mono); }
</style>
