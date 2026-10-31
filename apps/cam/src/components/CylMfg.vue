<script setup>
// Manufacturing a cylindrical cam (round 39, step 8c): 4-axis program (A + X, and Y for an oscillating follower), its
// simulation against the exact flanks, and the model made by the cutter (STL).
import { computed, ref } from 'vue'
import { project, payload } from '../store'
import { apiPost, saveText } from '../api'
import { t, lang } from '../i18n'
import Checks from './Checks.vue'
import LineChart from './LineChart.vue'
import { cylMfgResult } from '../cylmfg'

const four = computed(() => {
  if (!project.mfg.four) project.mfg.four = { tool_r: null, chord_tol: 0.002, work_rpm: 2, prog_no: 3904 }
  return project.mfg.four
})
const cone = computed(() => project.cylindrical?.roller === 'cone')
const busy = ref(false)
const err = ref('')
const r = computed(() => cylMfgResult.value)
const num = (v) => (v === '' || v === null ? null : Number(v))
const body = () => ({ project: { ...payload(), title: project.title, mfg: { four: JSON.parse(JSON.stringify(four.value)) } } })
const name = () => ((lang.value === 'zh' ? project.title.zh : project.title.en) || 'cam').replace(/[\\/:*?"<>|]+/g, '_')

async function make() {
  busy.value = true; err.value = ''
  try { cylMfgResult.value = await apiPost('/cyl/manufacture', body()) } catch (e) { err.value = lang.value === 'zh' ? e.zh : e.message } finally { busy.value = false }
}
async function stlFile() {
  busy.value = true; err.value = ''
  try {
    const res = await fetch(import.meta.env.BASE_URL + 'api/cyl/stl', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body()) })
    if (!res.ok) { const d = (await res.json().catch(() => ({}))).detail || {}; throw Object.assign(new Error(d.en || 'error'), { zh: d.zh }) }
    const a = document.createElement('a'); a.href = URL.createObjectURL(await res.blob()); a.download = name() + '.stl'; a.click()
    setTimeout(() => URL.revokeObjectURL(a.href), 1000)
  } catch (e) { err.value = lang.value === 'zh' ? e.zh || e.message : e.message } finally { busy.value = false }
}
const status = computed(() => (r.value ? (r.value.checks.some((c) => c.status === 'fail') ? 'fail' : 'pass') : null))
</script>

<template>
  <main class="work mfg cylmfg">
    <aside class="edit">
      <div class="pane grid">
        <h4>{{ t('cylMfg') }}</h4>
        <p class="note">{{ t('cylMfgNote') }}</p>
        <label v-if="!cone">{{ t('cylToolR') }} <span class="u">mm</span><input :value="four.tool_r" type="number" step="any" min="0" :placeholder="String(project.cylindrical.rr)" @input="four.tool_r = num($event.target.value)"></label>
        <p v-else class="note">{{ t('cylConeTool') }}</p>
        <label>{{ t('chordTol') }} <span class="u">mm</span><input :value="four.chord_tol" type="number" step="any" min="0" @input="four.chord_tol = num($event.target.value)"></label>
        <label>{{ t('cylWorkRpm') }} <span class="u">r/min</span><input :value="four.work_rpm" type="number" step="any" min="0" @input="four.work_rpm = num($event.target.value)"></label>
        <label>{{ t('progNo') }} <span class="u">O</span><input :value="four.prog_no" type="number" step="1" min="1" @input="four.prog_no = num($event.target.value)"></label>
        <p class="note">{{ t('machineNote') }}</p>
        <button type="button" class="accent" :disabled="busy" @click="make">{{ busy ? t('computing') : t('cylMake') }}</button>
        <div v-if="r" class="row">
          <button type="button" class="ghost" @click="saveText(name() + '.nc', r.program)">{{ t('nc4') }}</button>
          <button type="button" class="ghost" :disabled="busy" @click="stlFile">{{ t('cylStl') }}</button>
        </div>
        <p v-if="err" class="bad">{{ err }}</p>
      </div>
    </aside>
    <section class="stage plots">
      <template v-if="r">
        <Checks :result="{ status, checks: r.checks }" />
        <LineChart :w="640" :title="t('simDev')" unit="µm" :x="r.sim.deg" :series="r.sim.flanks.flatMap((f, i) => [{ y: f.dev_um, cls: i ? 'b' : '', label: (f.side > 0 ? '+' : '−') + ' max' }, { y: f.dev_min_um, cls: i ? 'b' : '', label: (f.side > 0 ? '+' : '−') + ' min' }])" :note="t('simNote')" />
        <p class="small mono">O{{ r.settings.prog_no }} · {{ r.lines }} {{ lang === 'zh' ? '行' : 'lines' }} · {{ t('cylAxes') }}</p>
        <pre class="nc">{{ r.program.split('\n').slice(0, 16).join('\n') }}
…</pre>
      </template>
      <p v-else class="note">{{ t('cylMfgEmpty') }}</p>
    </section>
  </main>
</template>

<style scoped>
.cylmfg { grid-template-columns: 340px minmax(0, 1fr); grid-template-rows: auto; }
.grid { display: grid; gap: 10px; align-content: start; }
label { display: grid; grid-template-columns: 1fr 110px; align-items: center; gap: 4px 8px; font-size: 13.5px; }
label .u { grid-column: 1; font: 400 11.5px/1 var(--mono); color: var(--muted); margin-top: -2px; }
label input { grid-column: 2; grid-row: 1 / span 2; }
.row { display: flex; gap: 6px; flex-wrap: wrap; }
.note { font-size: 12.5px; color: var(--muted); margin: 0; }
.bad { color: var(--bad); font-size: 13px; margin: 0; }
h4 { margin: 0; font-size: 14px; }
.plots { padding: 12px; display: grid; gap: 12px; align-content: start; overflow: auto; }
.small { font-size: 12px; color: var(--muted); margin: 0; }
.nc { font: 11.5px/1.45 var(--mono); background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 8px; margin: 0; overflow: auto; }
@media (max-width: 760px) { .cylmfg { grid-template-columns: minmax(0, 1fr); } }
</style>
