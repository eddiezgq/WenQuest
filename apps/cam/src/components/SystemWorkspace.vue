<script setup>
// Cam system design (round 39, step 4): edit the camshaft and drive, every cam and its output, the interlocks and
// limits; see the timing diagram, the checks, the camshaft and motor torque, the vibration in the dwells, and search
// for a better motion law and speed.
import { computed, ref } from 'vue'
import { system, sysResult, sysError, sysBusy, sysPayload } from '../sysstore'
import { api } from '../api'
import { t, lang } from '../i18n'
import NumField from './NumField.vue'
import ProgramEditor from './ProgramEditor.vue'
import AiExplain from './AiExplain.vue'
import TimingDiagram from './TimingDiagram.vue'
import Checks from './Checks.vue'
import LineChart from './LineChart.vue'

const tab = ref('camshaft')
const theta = ref(0)
const res = sysResult
const cs = computed(() => system.camshaft || (system.camshaft = {}))
const dr = computed(() => system.drive || (system.drive = {}))
const lim = computed(() => system.limits || (system.limits = {}))
const cam = computed(() => (system.cams || []).find((c) => c.id === tab.value))
const nm = (n) => (lang.value === 'zh' ? n?.zh : n?.en) || ''
const ensure = (o, k) => o[k] || (o[k] = {})
const groups = computed(() => {
  const r = res.value
  if (!r) return []
  const sysChecks = { title: lang.value === 'zh' ? '系统' : 'System', result: { status: r.checks.some((c) => c.status === 'fail') ? 'fail' : r.checks.some((c) => c.status === 'unknown') ? 'unknown' : 'pass', checks: r.checks } }
  return [sysChecks, ...r.cams.map((c) => ({ title: nm(c.name), result: { status: c.checks.some((x) => x.status === 'fail') ? 'fail' : c.checks.some((x) => x.status === 'unknown') ? 'unknown' : 'pass', checks: c.checks } }))]
})
const search = ref(null)
const searching = ref(false)
async function runSearch() {
  searching.value = true
  try { search.value = await api('/system/optimize', sysPayload()) } catch (e) { search.value = { error: lang.value === 'zh' ? e.zh : e.message } } finally { searching.value = false }
}
function adopt(row) {
  for (const c of system.cams || []) for (const s of c.program?.segments || []) if (s.kind !== 'dwell') s.law = row.law
  if (row.rpm_max) cs.value.rpm = Math.floor(row.rpm_max * 10) / 10
  search.value = null
}
const fmt = (v, d = 2) => (v == null || !Number.isFinite(v) ? '—' : (+v).toFixed(d))
</script>

<template>
  <main class="work sysw">
    <aside class="edit">
      <nav class="tabs wrap">
        <button type="button" :class="{ on: tab === 'camshaft' }" @click="tab = 'camshaft'">{{ t('camshaft') }}</button>
        <button v-for="c in system.cams" :key="c.id" type="button" :class="{ on: tab === c.id }" @click="tab = c.id">{{ nm(c.name).split('（')[0].split(' (')[0] }}</button>
        <button type="button" :class="{ on: tab === 'locks' }" @click="tab = 'locks'">{{ t('locks') }}</button>
      </nav>
      <div class="pane form">
        <template v-if="tab === 'camshaft'">
          <NumField :obj="cs" k="rpm" :label="t('runRpm')" unit="r/min" />
          <NumField :obj="cs" k="start_deg" :label="t('startDeg')" unit="°" />
          <NumField :obj="cs" k="stop_deg" :label="t('stopDeg')" unit="°" />
          <NumField :obj="cs" k="J" :label="t('Jcs')" unit="kg·m²" />
          <NumField :obj="cs" k="friction" :label="t('friction')" unit="N·m" />
          <h4>{{ lang === 'zh' ? '驱动' : 'Drive' }}</h4>
          <NumField :obj="dr" k="ratio" :label="t('ratio')" unit="" />
          <NumField :obj="dr" k="eta" :label="t('eta')" unit="0–1" />
          <NumField :obj="dr" k="J_motor" :label="t('Jm')" unit="kg·m²" />
          <NumField :obj="dr" k="rated_Nm" :label="t('ratedNm')" unit="N·m" />
          <NumField :obj="dr" k="peak_Nm" :label="t('peakNm')" unit="N·m" />
          <NumField :obj="dr" k="max_rpm" :label="t('maxRpm')" unit="r/min" />
          <p class="note">{{ t('motorNote') }}</p>
        </template>
        <template v-else-if="cam">
          <p class="kind">{{ cam.type === 'globoidal' ? t('globoidal') : t('disk') }}</p>
          <ProgramEditor :program="cam.program" :indexing="cam.type === 'globoidal'" :cam-id="cam.id" />
          <template v-if="cam.type === 'globoidal'">
            <h4>{{ t('globoidal') }}</h4>
            <NumField :obj="cam.globoidal" k="C" :label="t('gC')" unit="mm" />
            <NumField :obj="cam.globoidal" k="n" :label="t('gn')" unit="" step="1" />
            <NumField :obj="cam.globoidal" k="Rp" :label="t('gRp')" unit="mm" />
            <NumField :obj="cam.globoidal" k="rr" :label="t('grr')" unit="mm" />
            <NumField :obj="cam.globoidal" k="b" :label="t('gb')" unit="mm" />
            <NumField :obj="cam.globoidal" k="L" :label="t('gL')" unit="mm" />
            <NumField :obj="cam.globoidal" k="clearance" :label="t('gclr')" unit="mm" />
            <NumField :obj="cam.globoidal" k="phase_deg" :label="t('gphase')" unit="°" />
          </template>
          <template v-else>
            <h4>{{ t('tabMech') }}</h4>
            <NumField :obj="cam.mechanism" k="rb" :label="t('rb')" unit="mm" />
            <NumField :obj="cam.mechanism" k="rr" :label="t('rr')" unit="mm" />
            <NumField v-if="cam.mechanism.follower === 'oscillating'" :obj="cam.mechanism" k="a" :label="t('a')" unit="mm" />
            <NumField v-if="cam.mechanism.follower === 'oscillating'" :obj="cam.mechanism" k="L" :label="t('L')" unit="mm" />
            <NumField :obj="cam.mechanism" k="width" :label="t('width')" unit="mm" />
          </template>
          <h4>{{ t('output') }}</h4>
          <NumField v-if="cam.program.unit === 'rad'" :obj="ensure(cam, 'output')" k="J" :label="t('outJ')" unit="kg·m²" />
          <NumField :obj="ensure(cam, 'output')" k="m" :label="t('outM')" unit="kg" />
          <NumField :obj="ensure(cam, 'output')" k="load" :label="t('outLoad')" :unit="cam.program.unit === 'rad' ? 'N·m' : 'N'" />
          <NumField :obj="ensure(cam, 'output')" k="radius" :label="t('outRadius')" unit="mm" />
          <NumField :obj="ensure(cam, 'output')" k="tip" :label="t('outTip')" unit="mm" />
          <h4>{{ t('elastic') }}</h4>
          <NumField :obj="ensure(cam, 'elastic')" k="fn" :label="t('fn')" unit="Hz" />
          <NumField :obj="ensure(cam, 'elastic')" k="zeta" :label="t('zeta')" unit="" />
          <p class="note">{{ t('elasticNote') }}</p>
          <h4>{{ t('tabLimits') }}</h4>
          <NumField :obj="ensure(cam, 'limits')" k="phi_rise_deg" :label="t('phiRise')" unit="°" />
          <NumField v-if="cam.type !== 'globoidal'" :obj="ensure(cam, 'limits')" k="phi_return_deg" :label="t('phiReturn')" unit="°" />
          <NumField v-if="cam.type === 'globoidal'" :obj="ensure(cam, 'limits')" k="rib_min" :label="t('ribMin')" unit="mm" />
          <NumField :obj="ensure(cam, 'limits')" k="stress" :label="t('stress')" unit="MPa" />
        </template>
        <template v-else>
          <p class="note">{{ lang === 'zh' ? '联锁：前一个凸轮运动时，后一个必须停着。' : 'Interlocks: while the first cam moves, the second stands still.' }}</p>
          <ul class="locks"><li v-for="(l, i) in system.interlocks" :key="i">{{ l.moving }} → {{ l.still }}</li></ul>
          <NumField :obj="lim" k="vib_um" :label="t('vibUm')" unit="µm" />
          <NumField :obj="lim" k="cycle_s" :label="t('cycleS')" unit="s" />
        </template>
      </div>
    </aside>

    <section class="stage plots">
      <p v-if="sysError" class="err static">{{ t('error') }}：{{ lang === 'zh' ? sysError.zh || sysError.message : sysError.message }}</p>
      <p v-if="sysBusy && !res" class="busy">{{ t('computing') }}</p>
      <TimingDiagram v-if="res" v-model:theta="theta" :res="res" />
      <div v-if="res" class="row2">
        <LineChart :w="440" :title="t('camTorque')" unit="N·m" :x="res.deg" :series="[{ y: res.T_cs }]" :cursor="theta" />
        <LineChart :w="440" :title="t('motorTorque')" unit="N·m" :x="res.deg" :series="[{ y: res.T_motor, cls: 'b' }]" :cursor="theta" />
      </div>
    </section>

    <aside class="side">
      <p v-if="res" class="cycle">{{ lang === 'zh' ? '循环时间' : 'Cycle time' }} <b class="mono">{{ fmt(res.cycle, 3) }} s</b></p>
      <section v-for="g in groups" :key="g.title" class="grp"><h4>{{ g.title }}</h4><Checks :result="g.result" /></section>
      <AiExplain v-if="res" system />
    </aside>

    <section class="curves bottom">
      <div v-if="res" class="vib">
        <h4>{{ t('vibTable') }}</h4>
        <table class="tb"><thead><tr><th /><th>{{ t('from') }}</th><th>{{ t('amp') }}</th><th>{{ t('tipUm') }}</th></tr></thead>
          <tbody><template v-for="c in res.cams" :key="c.id"><tr v-for="(d, i) in c.vib || []" :key="c.id + i"><td>{{ i === 0 ? nm(c.name) : '' }}</td>
            <td class="mono">{{ fmt(d.from, 0) }}–{{ fmt(d.to, 0) }}°</td><td class="mono">{{ fmt(d.amp, 1) }} {{ c.unit === 'deg' ? '″' : 'µm' }}</td>
            <td class="mono">{{ fmt(d.tip_um, 1) }} µm</td></tr></template></tbody></table>
      </div>
      <div class="srch">
        <h4>{{ t('search') }}</h4>
        <p class="note">{{ t('searchNote') }}</p>
        <button type="button" class="solid" :disabled="searching || !res" @click="runSearch">{{ searching ? t('computing') : t('runSearch') }}</button>
        <p v-if="search?.error" class="bad">{{ search.error }}</p>
        <table v-else-if="search" class="tb">
          <thead><tr><th>{{ t('law') }}</th><th>{{ t('atRpm') }}<br>{{ t('vibUm').slice(0, 4) }} µm</th><th>{{ t('peakNm') }}</th><th>{{ t('rpmMax') }}</th><th /></tr></thead>
          <tbody><tr v-for="r in search.rows" :key="r.law" :class="{ best: search.best && r.law === search.best.law, off: r.fails?.length }">
            <td>{{ r.law }}</td><td class="mono">{{ fmt(r.vib_um, 1) }}</td><td class="mono">{{ fmt(r.motor_peak, 1) }}</td>
            <td class="mono">{{ r.rpm_max ? fmt(r.rpm_max, 1) + ' r/min' : (r.fails?.length ? r.fails.join(', ') : '—') }}</td>
            <td><button v-if="!r.fails?.length && !r.error" type="button" class="ghost" @click="adopt(r)">{{ t('adopt') }}</button></td></tr></tbody>
        </table>
        <p v-if="search && search.limits_missing?.length" class="note">{{ lang === 'zh' ? '没填的限值不参与：' : 'Limits not given are not used: ' }}{{ search.limits_missing.join(', ') }}</p>
      </div>
    </section>
  </main>
</template>

<style scoped>
.tabs.wrap { flex-wrap: wrap; }
.tabs.wrap button { flex: 1 1 auto; padding: 8px 6px; font-size: 12.5px; }
.form { display: grid; gap: 8px; align-content: start; }
h4 { margin: 8px 0 0; font-size: 13px; font-weight: 600; }
.note { font-size: 12px; color: var(--muted); margin: 0; }
.kind { margin: 0; font-weight: 600; font-size: 13px; color: var(--accent-ink); }
.plots { display: grid; gap: 10px; align-content: start; padding: 10px; overflow: auto; position: relative; grid-template-rows: none; }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.static { position: static; }
.cycle { margin: 0 0 6px; font-size: 13px; }
.grp h4 { margin: 10px 0 4px; }
.bottom { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); gap: 12px; }
.vib, .srch { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; }
.tb { width: 100%; border-collapse: collapse; font-size: 12.5px; margin-top: 6px; }
.tb th, .tb td { text-align: left; padding: 4px 6px; border-bottom: 1px solid var(--line); }
.tb th { color: var(--muted); font-weight: 500; }
.tb tr.best td { background: var(--ok-bg); }
.tb tr.off td { color: var(--muted); }
.bad { color: var(--bad); font-size: 12.5px; }
.locks { margin: 0; padding-left: 18px; font-size: 13px; }
.srch .solid { margin-top: 6px; }
@media (max-width: 760px) { .row2, .bottom { grid-template-columns: 1fr; } }
</style>
