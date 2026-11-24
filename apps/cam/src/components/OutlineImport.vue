<script setup>
// An outline in, the follower motion out (round 179): a drawn disk cam (DXF or x, y points) and the follower set on
// the Mechanism tab give the lift over a turn; it becomes the point-table program the rest of the software uses.
import { computed, ref } from 'vue'
import { project, payload, outlineStale, followerKey } from '../store'
import { api } from '../api'
import { t, lang } from '../i18n'
import LineChart from './LineChart.vue'

const o = computed(() => project.outline)
const busy = ref(false)
const err = ref('')
const fileIn = ref(null)
const rep = computed(() => o.value?.report || null)
const SMOOTH = [[1, 'smAuto'], [0.3, 'smLight'], [3, 'smStrong'], [10, 'smStronger'], [0, 'smNone']]

async function pick(e) {
  const f = e.target.files?.[0]
  e.target.value = ''
  if (!f) return
  if (f.size > 8 * 1024 * 1024) { err.value = t('olTooBig'); return }
  const text = await f.text()
  o.value.name = f.name
  o.value.format = /\.dxf$/i.test(f.name) || /^\s*0\s*\n\s*SECTION/m.test(text.slice(0, 2000)) ? 'dxf' : 'xy'
  o.value.data = text
  solve()
}
function pasted() { o.value.format = 'xy'; o.value.name = '' }

async function solve() {
  if (!o.value.data) { err.value = t('olNoData'); return }
  busy.value = true; err.value = ''
  try {
    const p = payload()
    const body = { mechanism: p.mechanism, outline: { format: o.value.format, data: o.value.data, center: [Number(o.value.cx) || 0, Number(o.value.cy) || 0], zero: o.value.zero, smooth: o.value.smooth } }
    const r = await api('/inverse', body)
    project.program = r.program
    project.mechanism.rb = r.mechanism.rb
    o.value.report = r.report
    o.value.used = followerKey(project.mechanism)
  } catch (e) { err.value = lang.value === 'zh' ? e.zh : e.message } finally { busy.value = false }
}

const fmt = (v, d = 4) => (Number.isFinite(v) ? +v.toFixed(d) : '—')
const srcText = computed(() => {
  const s = rep.value?.source
  if (!s) return ''
  if (s.format === 'dxf') {
    const names = { 'open lines': ['未封闭的直线（中心线等）', 'open lines (centre lines)'], TEXT: ['文字', 'text'], MTEXT: ['文字', 'text'], DIMENSION: ['尺寸', 'dimensions'], HATCH: ['剖面线', 'hatching'], POINT: ['点', 'points'] }
    const nm = (k) => (names[k] ? names[k][lang.value === 'zh' ? 0 : 1] : k)
    const ign = Object.entries(s.ignored || {}).map(([k, n]) => `${nm(k)} ×${n}`).join(lang.value === 'zh' ? '，' : ', ')
    return t('olSrcDxf').replace('{loops}', s.loops).replace('{how}', t(s.spline ? 'olSpline' : 'olExact')) + (ign ? t('olIgnored').replace('{list}', ign) : '')
  }
  return t('olSrcXy').replace('{n}', s.points).replace('{how}', t(s.spline ? 'olSpline' : 'olExact'))
})
const resText = computed(() => {
  const r = rep.value?.smooth?.largest
  if (!Number.isFinite(r)) return '—'
  return rep.value.unit === 'deg' ? `${+r.toPrecision(2)}°` : `${+(r * 1000).toPrecision(2)} µm`
})
const unitLift = computed(() => (rep.value?.unit === 'deg' ? '°' : 'mm'))
const accUnit = computed(() => (rep.value?.unit === 'deg' ? '°/rad²' : 'mm/rad²'))
</script>

<template>
  <div class="ol">
    <p class="hint">{{ t('olHint') }} <a href="help/#outline" target="_blank" rel="noopener">{{ t('help') }}</a></p>
    <div class="row">
      <button type="button" class="ghost" @click="fileIn.click()">{{ t('olChoose') }}</button>
      <input ref="fileIn" type="file" accept=".dxf,.csv,.txt,.tsv" hidden @change="pick">
      <span v-if="o.name" class="name mono">{{ o.name }}</span>
    </div>
    <details :open="!o.name && !o.data">
      <summary>{{ t('olPaste') }}</summary>
      <textarea v-model="o.data" rows="6" class="mono" :placeholder="'x, y\n40.000, 0.000\n39.994, 0.698\n…'" @input="pasted" />
    </details>
    <div class="grid">
      <label>{{ t('olCenter') }} x <span class="u">mm</span><input v-model.number="o.cx" type="number" step="any"></label>
      <label>{{ t('olCenter') }} y <span class="u">mm</span><input v-model.number="o.cy" type="number" step="any"></label>
    </div>
    <div class="seg">
      <span class="lab">{{ t('olZero') }}</span>
      <button type="button" :class="{ on: o.zero === 'rise' }" @click="o.zero = 'rise'">{{ t('olZeroRise') }}</button>
      <button type="button" :class="{ on: o.zero === 'drawing' }" @click="o.zero = 'drawing'">{{ t('olZeroDrawing') }}</button>
    </div>
    <label class="sm">{{ t('olSmooth') }}
      <select v-model.number="o.smooth"><option v-for="[v, k] in SMOOTH" :key="k" :value="v">{{ t(k) }}</option></select></label>
    <p class="note">{{ t('olSmoothNote') }}</p>
    <p class="note">{{ t('olFollowerNote') }}</p>
    <div class="row"><button type="button" class="go" :disabled="busy" @click="solve">{{ busy ? t('olBusy') : rep ? t('olAgain') : t('olSolve') }}</button></div>
    <p v-if="err" class="err">{{ err }}</p>
    <p v-if="rep && outlineStale" class="warn">{{ t('olStale') }}</p>

    <template v-if="rep">
      <p class="note">{{ srcText }}</p>
      <dl class="res">
        <dt>{{ t('rb') }}</dt><dd class="mono">{{ fmt(rep.rb) }} mm</dd>
        <dt>{{ t('olLift') }}</dt><dd class="mono">{{ fmt(rep.lift) }} {{ unitLift }}</dd>
        <dt v-if="rep.zero === 'rise'">{{ t('olShift') }}</dt><dd v-if="rep.zero === 'rise'" class="mono">{{ fmt(rep.shift_deg > 180 ? rep.shift_deg - 360 : rep.shift_deg, 2) }}°</dd>
        <dt>{{ t('olCheck') }}</dt>
        <dd :class="['mono', rep.check.ok ? 'ok' : 'bad']">{{ fmt(rep.check.max_dev * 1000, 2) }} µm {{ rep.check.ok ? '✓' : '✗' }}</dd>
      </dl>
      <p v-if="!rep.check.ok" class="warn">{{ t('olCheckBad').replace('{dev}', fmt(rep.check.max_dev, 4)).replace('{deg}', fmt(rep.check.at_deg, 1)) }}</p>
      <LineChart :title="t('olAcc')" :unit="accUnit" :x="rep.acc.deg" :w="340"
        :series="[{ y: rep.acc.raw, label: t('olRaw'), cls: 'r' }, { y: rep.acc.smooth, label: t('olSmoothed'), cls: 'b' }]"
        :note="t('olAccNote').replace('{raw}', fmt(rep.acc.raw_peak, 3)).replace('{sm}', fmt(rep.acc.smooth_peak, 3)).replace('{res}', resText)" />
    </template>
  </div>
</template>

<style scoped>
.ol { display: grid; gap: 10px; }
.hint, .note { font-size: 12.5px; color: var(--muted); margin: 0; }
.row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.name { font-size: 12px; color: var(--muted); overflow-wrap: anywhere; }
details summary { font-size: 13px; cursor: pointer; color: var(--muted); }
textarea { width: 100%; margin-top: 6px; }
.grid { display: grid; gap: 8px; }
label { display: grid; grid-template-columns: 1fr 110px; align-items: center; gap: 4px 8px; font-size: 13.5px; }
label .u { grid-column: 1; font: 400 11.5px/1 var(--mono); color: var(--muted); margin-top: -2px; }
label input, label select { grid-column: 2; grid-row: 1 / span 2; }
label.sm { grid-template-columns: 1fr 150px; }
label.sm select { grid-row: 1; }
.seg { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.seg .lab { font-size: 13.5px; min-width: 64px; }
.seg button { border: 1px solid var(--line); background: var(--surface); padding: 5px 10px; border-radius: 6px; cursor: pointer; font: inherit; font-size: 13px; color: var(--ink); }
.seg button.on { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.go { border: 0; background: var(--accent); color: #fff; padding: 7px 14px; border-radius: 6px; cursor: pointer; font: inherit; font-size: 13.5px; }
.go:disabled { opacity: 0.6; cursor: wait; }
.err, .bad { color: var(--bad); }
.err, .warn { font-size: 12.5px; margin: 0; }
.warn { color: var(--bad); background: color-mix(in srgb, var(--bad) 8%, transparent); padding: 6px 8px; border-radius: 6px; }
.ok { color: var(--ok); }
.res { display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; margin: 0; font-size: 13px; }
.res dt { color: var(--muted); }
.res dd { margin: 0; }
.mono { font-family: var(--mono); }
</style>
