<script setup>
// Measure and compensate (round 39, step 3): the measured table, the aligned error, its harmonics, the
// acceleration it causes at speed, and the compensated program with the error predicted to remain.
import { computed, ref } from 'vue'
import { project, payloadFull, measResult, compResult } from '../store'
import { api, saveText } from '../api'
import { t, lang } from '../i18n'
import Checks from './Checks.vue'
import LineChart from './LineChart.vue'
import BarChart from './BarChart.vue'

const ms = computed(() => project.measure)
const res = measResult
const comp = compResult
const err = ref(null)
const busy = ref(false)
const fileInput = ref(null)
const num = (v) => (v === '' || v === null ? null : Number(v))
const zh = computed(() => lang.value === 'zh')
const fmt = (v, d = 3) => (v == null || !Number.isFinite(v) ? '—' : (+v).toFixed(d))

async function analyse() {
  err.value = null; busy.value = true; comp.value = null
  try { res.value = await api('/measure', payloadFull(true)) } catch (e) { err.value = e; res.value = null } finally { busy.value = false }
}
async function compensate() {
  err.value = null; busy.value = true
  try {
    const c = await api('/compensate', payloadFull(true))
    comp.value = c; res.value = c.measure
  } catch (e) { err.value = e } finally { busy.value = false }
}
async function synthetic() {
  try {
    const r = await api('/synthetic', payloadFull())
    ms.value.format = 'lift'; ms.value.data = r.text; await analyse()
  } catch (e) { err.value = e }
}
async function readFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  ms.value.data = await f.text(); e.target.value = ''
  await analyse()
}
function record() {
  const r = res.value
  if (!r) return
  ms.value.records.unshift({
    time: new Date().toISOString().slice(0, 16).replace('T', ' '), shift: +r.shift_deg.toFixed(4), offset: +r.offset.toFixed(3),
    first: +r.groups.first.toFixed(3), low: +r.groups.low.toFixed(3), high: +r.groups.high.toFixed(3), unit: r.err_unit,
    comp: comp.value ? `${comp.value.lo}–${comp.value.hi}` : '', rms_after: comp.value ? +comp.value.rms_after.toFixed(3) : null,
  })
}
const sel = computed(() => [ms.value.comp.lo, ms.value.comp.hi])
const legend = computed(() => [['g1', t('gFirst')], ['g2', t('gLow')], ['g3', t('gHigh')]].concat(comp.value ? [['after', t('after')]] : []))
const errSeries = computed(() => {
  if (!res.value) return []
  const s = [{ y: res.value.e, label: comp.value ? t('before') : '' }]
  if (comp.value) s.push({ y: comp.value.remaining, label: t('after'), cls: 'b' })
  return s
})
const top = computed(() => {
  if (!res.value) return []
  const h = res.value.harm
  return h.k.map((k, i) => ({ k, A: h.A[i], ph: h.phase_deg[i], allow: res.value.allow_k?.[i] })).sort((a, b) => b.A - a.A).slice(0, 8)
})
</script>

<template>
  <main class="work meas">
    <aside class="edit">
      <div class="pane form">
        <div class="row seg">
          <span class="lab">{{ t('measFormat') }}</span>
          <button type="button" :class="{ on: ms.format === 'lift' }" @click="ms.format = 'lift'">{{ t('liftTable') }}</button>
          <button type="button" :class="{ on: ms.format === 'xy' }" @click="ms.format = 'xy'">{{ t('xyPoints') }}</button>
        </div>
        <p class="note">{{ ms.format === 'lift' ? t('liftHint') : t('xyHint') }}</p>
        <label class="check"><input v-model="ms.align" type="checkbox"> {{ t('align') }}</label>
        <p class="note">{{ t('paste') }} <button type="button" class="link" @click="fileInput.click()">{{ t('upload') }}</button></p>
        <input ref="fileInput" type="file" accept=".csv,.txt,.dat,text/plain" hidden @change="readFile">
        <textarea v-model="ms.data" rows="8" spellcheck="false" :placeholder="ms.format === 'lift' ? '0, 0.0000\n0.5, 0.0012\n…' : 'x, y\n…'" />
        <div class="row"><button type="button" class="ghost" @click="synthetic">{{ t('synthetic') }}</button></div>
        <p class="note">{{ t('syntheticNote') }}</p>
        <label>{{ t('rpm') }} <span class="u">r/min · {{ zh ? '不填用设计转速' : 'empty: design speed' }}</span><input :value="ms.rpm" type="number" step="any" min="0" @input="ms.rpm = num($event.target.value)"></label>
        <label>{{ t('aAllow') }} <span class="u">{{ project.mechanism.follower === 'oscillating' ? 'rad/s²' : 'm/s²' }}</span><input :value="ms.a_allow" type="number" step="any" min="0" @input="ms.a_allow = num($event.target.value)"></label>
        <label>{{ t('kmax') }}<input :value="ms.kmax" type="number" step="1" min="4" max="400" @input="ms.kmax = num($event.target.value)"></label>
        <label>{{ t('lowHi') }}<input :value="ms.low_hi" type="number" step="1" min="2" @input="ms.low_hi = num($event.target.value)"></label>
        <div class="row"><button type="button" class="solid" :disabled="busy || !ms.data" @click="analyse">{{ t('analyse') }}</button></div>
        <h4>{{ t('comp') }}</h4>
        <p class="note">{{ t('compNote') }}</p>
        <div class="row orders">{{ t('compOrders') }}
          <input :value="ms.comp.lo" type="number" step="1" min="1" @input="ms.comp.lo = num($event.target.value)"> {{ t('to') }}
          <input :value="ms.comp.hi" type="number" step="1" min="1" @input="ms.comp.hi = num($event.target.value)">
        </div>
        <div class="row"><button type="button" class="accent" :disabled="busy || !res" @click="compensate">{{ t('makeComp') }}</button></div>
      </div>
    </aside>

    <section class="stage plots">
      <p v-if="err" class="err static">{{ t('error') }}：{{ zh ? err.zh || err.message : err.message }}</p>
      <p v-if="busy" class="busy">{{ t('computing') }}</p>
      <template v-if="res">
        <LineChart :w="640" :title="t('errCurve')" :unit="res.err_unit" :x="res.deg" :series="errSeries" />
        <BarChart :title="t('harm')" :unit="res.err_unit" :A="res.harm.A" :after="comp?.after_A" :low-hi="res.low_hi" :sel="comp ? sel : null" :legend="legend" />
        <LineChart v-if="res.acc" :w="640" :title="t('accErr')" :unit="res.acc_unit + ' @ ' + Math.round(res.rpm) + ' r/min'" :x="res.deg" :series="[{ y: res.acc, cls: 'r' }]" />
      </template>
      <p v-else-if="!err" class="hint">{{ zh ? '粘贴测量数据后点“分析”，或先载入合成数据看看。' : 'Paste a measurement and press Analyse, or load the synthetic data first.' }}</p>
    </section>

    <aside class="side">
      <template v-if="res">
        <dl class="kv">
          <div><dt>{{ t('shift') }}</dt><dd class="mono">{{ fmt(res.shift_deg, 4) }}°</dd></div>
          <div><dt>{{ t('offset') }}</dt><dd class="mono">{{ fmt(res.offset) }} {{ res.err_unit }}</dd></div>
          <div><dt>{{ t('gFirst') }}</dt><dd class="mono">{{ fmt(res.groups.first) }}</dd></div>
          <div><dt>{{ t('gLow') }}</dt><dd class="mono">{{ fmt(res.groups.low) }}</dd></div>
          <div><dt>{{ t('gHigh') }}</dt><dd class="mono">{{ fmt(res.groups.high) }}</dd></div>
          <div><dt>{{ t('gAbove') }}</dt><dd class="mono">{{ fmt(res.groups.above) }}</dd></div>
        </dl>
        <p class="note">{{ t('rms') }}，{{ res.err_unit }}</p>
        <Checks :result="{ status: res.checks.some((c) => c.status === 'fail') ? 'fail' : res.checks.some((c) => c.status === 'unknown') ? 'unknown' : 'pass', checks: res.checks }" />
        <table class="harmtab">
          <thead><tr><th>{{ zh ? '阶' : 'k' }}</th><th>{{ zh ? '幅值' : 'Amp.' }}</th><th>{{ zh ? '相位' : 'Phase' }}</th><th v-if="res.allow_k">{{ zh ? '允许' : 'Allowed' }}</th></tr></thead>
          <tbody><tr v-for="h in top" :key="h.k" :class="{ bad: h.allow != null && h.A > h.allow }"><td>{{ h.k }}</td><td class="mono">{{ fmt(h.A) }}</td><td class="mono">{{ fmt(h.ph, 1) }}°</td><td v-if="res.allow_k" class="mono">{{ fmt(h.allow) }}</td></tr></tbody>
        </table>
        <template v-if="comp">
          <h4>{{ t('comp') }} {{ comp.lo }}–{{ comp.hi }}</h4>
          <p class="mono small">{{ t('rms') }} {{ fmt(comp.rms_before) }} → {{ fmt(comp.rms_after) }} {{ res.err_unit }}</p>
          <Checks :result="{ status: comp.mfg.checks.some((c) => c.status === 'fail') ? 'fail' : 'pass', checks: comp.mfg.checks }" />
          <button type="button" class="ghost" :disabled="!comp.mfg.program" @click="saveText('compensated.nc', comp.mfg.program)">{{ t('dlComp') }}</button>
        </template>
        <h4>{{ t('records') }}</h4>
        <button type="button" class="ghost" @click="record">{{ t('addRecord') }}</button>
      </template>
      <ul v-if="ms.records.length" class="recs">
        <li v-for="(r, i) in ms.records" :key="i"><span class="mono">{{ r.time }}</span> · Δ {{ r.shift }}° · c {{ r.offset }} · 1/{{ zh ? '低/高' : 'low/high' }} {{ r.first }}/{{ r.low }}/{{ r.high }} {{ r.unit }}<template v-if="r.comp"> · {{ t('comp') }} {{ r.comp }} → {{ r.rms_after }}</template></li>
      </ul>
      <p v-else-if="res" class="note">{{ t('noRecords') }}</p>
    </aside>
  </main>
</template>

<style scoped>
.form { display: grid; gap: 10px; align-content: start; }
.form label { display: grid; grid-template-columns: 1fr 110px; align-items: center; gap: 4px 8px; font-size: 13.5px; }
.form label .u { grid-column: 1; font: 400 11.5px/1.2 var(--mono); color: var(--muted); margin-top: -2px; }
.form label input { grid-column: 2; grid-row: 1 / span 2; }
.form label.check { display: flex; gap: 6px; align-items: flex-start; }
.row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; font-size: 13.5px; }
.orders input { width: 64px; }
.seg .lab { font-size: 13.5px; min-width: 64px; }
.seg button { border: 1px solid var(--line); background: var(--surface); padding: 5px 8px; border-radius: 6px; font-size: 12.5px; color: var(--ink); }
.seg button.on { background: var(--ink); color: var(--paper); border-color: var(--ink); }
textarea { width: 100%; font-size: 12px; resize: vertical; }
.link { background: none; border: 0; color: var(--blue); padding: 0; text-decoration: underline; font-size: 12.5px; }
h4 { margin: 10px 0 4px; font-size: 13px; font-weight: 600; }
.note { font-size: 12.5px; color: var(--muted); margin: 0; }
.plots { display: grid; gap: 10px; align-content: start; padding: 10px; grid-template-rows: none; overflow: auto; position: relative; }
.static { position: static; }
.hint { color: var(--muted); margin: 40px 0; text-align: center; }
.kv { display: grid; gap: 4px; margin: 0 0 4px; font-size: 13px; }
.kv div { display: flex; justify-content: space-between; gap: 8px; border-bottom: 1px solid var(--line); padding: 3px 0; }
.kv dt { color: var(--muted); } .kv dd { margin: 0; }
.harmtab { width: 100%; border-collapse: collapse; font-size: 12.5px; margin-top: 8px; }
.harmtab th, .harmtab td { text-align: right; padding: 3px 4px; border-bottom: 1px solid var(--line); }
.harmtab th:first-child, .harmtab td:first-child { text-align: left; }
.harmtab tr.bad td { color: var(--bad); }
.small { font-size: 12.5px; margin: 0 0 6px; }
.recs { list-style: none; padding: 0; margin: 8px 0 0; font-size: 12px; display: grid; gap: 4px; }
.recs li { border-bottom: 1px solid var(--line); padding: 3px 0; }
</style>
