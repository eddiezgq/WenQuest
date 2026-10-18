<script setup>
// Mechanism, loads and material, and limits: plain labelled number fields (round 39).
import { computed, ref } from 'vue'
import { project, payload } from '../store'
import { api } from '../api'
import { t, lang } from '../i18n'

const props = defineProps({ part: String })
const m = computed(() => project.mechanism)
const osc = computed(() => m.value.follower === 'oscillating')
const searching = ref(false)
const searchMsg = ref('')

function follower(f) {
  if (m.value.follower === f) return
  m.value.follower = f
  const toRad = f === 'oscillating'
  project.program.unit = toRad ? 'rad' : 'mm'
  for (const s of project.program.segments || []) {
    if (s.kind === 'dwell') continue
    if (toRad) { s.h_deg = s.h ?? 15; delete s.h } else { s.h = s.h_deg ?? 10; delete s.h_deg }
  }
  if (project.program.table) {
    const tb = project.program.table
    if (toRad) { tb.s_deg = tb.s; delete tb.s } else { tb.s = tb.s_deg; delete tb.s_deg }
  }
  if (toRad && !(m.value.a > 0)) { m.value.a = 2.5 * (m.value.rb || 40); m.value.L = 2 * (m.value.rb || 40) }
}
function steel() { Object.assign(project.material, { E1: 206000, nu1: 0.3, E2: 206000, nu2: 0.3 }) }
async function findRb() {
  searching.value = true; searchMsg.value = ''
  try {
    const r = await api('/min-base-radius', payload())
    m.value.rb = r.rb
    searchMsg.value = (lang.value === 'zh' ? `最小基圆 ${r.rb} mm（受限于：` : `Smallest base circle ${r.rb} mm (bound by: `) + r.binding.join(', ') + (lang.value === 'zh' ? '）' : ')')
  } catch (e) { searchMsg.value = lang.value === 'zh' ? e.zh : e.message } finally { searching.value = false }
}
const num = (v) => (v === '' || v === null ? null : Number(v))
</script>

<template>
  <div v-if="props.part === 'mech'" class="grid">
    <div class="row seg">
      <span class="lab">{{ t('follower') }}</span>
      <button type="button" :class="{ on: !osc }" @click="follower('translating')">{{ t('translating') }}</button>
      <button type="button" :class="{ on: osc }" @click="follower('oscillating')">{{ t('oscillating') }}</button>
    </div>
    <div class="row seg">
      <span class="lab">{{ t('contact') }}</span>
      <button v-for="c in ['roller', 'flat', 'knife']" :key="c" type="button" :class="{ on: m.contact === c }" @click="m.contact = c; if (c !== 'roller') m.groove = false">{{ t(c) }}</button>
    </div>
    <label>{{ t('rb') }} <span class="u">mm</span><input :value="m.rb" type="number" step="any" min="0" @input="m.rb = num($event.target.value)"></label>
    <label v-if="m.contact === 'roller'">{{ t('rr') }} <span class="u">mm</span><input :value="m.rr" type="number" step="any" min="0" @input="m.rr = num($event.target.value)"></label>
    <label v-if="!osc && m.contact !== 'flat'">{{ t('e') }} <span class="u">mm</span><input :value="m.e" type="number" step="any" @input="m.e = num($event.target.value)"></label>
    <label v-if="osc">{{ t('a') }} <span class="u">mm</span><input :value="m.a" type="number" step="any" min="0" @input="m.a = num($event.target.value)"></label>
    <label v-if="osc && m.contact !== 'flat'">{{ t('L') }} <span class="u">mm</span><input :value="m.L" type="number" step="any" min="0" @input="m.L = num($event.target.value)"></label>
    <div class="row seg">
      <span class="lab">{{ t('sigma') }}</span>
      <button type="button" :class="{ on: m.sigma === 1 }" @click="m.sigma = 1">↺ {{ t('ccw') }}</button>
      <button type="button" :class="{ on: m.sigma === -1 }" @click="m.sigma = -1">↻ {{ t('cw') }}</button>
    </div>
    <label v-if="m.contact === 'roller'" class="check"><input v-model="m.groove" type="checkbox"> {{ t('groove') }}</label>
    <label>{{ t('width') }} <span class="u">mm</span><input :value="m.width" type="number" step="any" min="0" @input="m.width = num($event.target.value)"></label>
    <div class="row"><button type="button" class="ghost" :disabled="searching" @click="findRb">{{ t('findRb') }}</button></div>
    <p v-if="searchMsg" class="note">{{ searchMsg }}</p>
  </div>

  <div v-else-if="props.part === 'loads'" class="grid">
    <label>{{ t('rpm') }} <span class="u">r/min</span><input :value="project.loads.rpm" type="number" step="any" min="0" @input="project.loads.rpm = num($event.target.value)"></label>
    <label v-if="!osc">{{ t('mass') }} <span class="u">kg</span><input :value="project.loads.mass" type="number" step="any" min="0" @input="project.loads.mass = num($event.target.value)"></label>
    <label v-else>{{ t('inertia') }} <span class="u">kg·m²</span><input :value="project.loads.inertia" type="number" step="any" min="0" @input="project.loads.inertia = num($event.target.value)"></label>
    <label>{{ t('k') }} <span class="u">{{ osc ? 'N·mm/rad' : 'N/mm' }}</span><input :value="project.loads.k" type="number" step="any" min="0" @input="project.loads.k = num($event.target.value)"></label>
    <label>{{ t('preload') }} <span class="u">{{ osc ? 'rad' : 'mm' }}</span><input :value="project.loads.preload" type="number" step="any" @input="project.loads.preload = num($event.target.value)"></label>
    <label>{{ t('load') }} <span class="u">{{ osc ? 'N·mm' : 'N' }}</span><input :value="project.loads.load" type="number" step="any" @input="project.loads.load = num($event.target.value)"></label>
    <p class="note">{{ t('speedNote') }}</p>
    <h4>{{ t('matRoller') }}</h4>
    <label>{{ t('E') }} <span class="u">MPa</span><input :value="project.material.E1" type="number" step="any" min="0" @input="project.material.E1 = num($event.target.value)"></label>
    <label>{{ t('nu') }}<input :value="project.material.nu1" type="number" step="any" min="0" max="0.5" @input="project.material.nu1 = num($event.target.value)"></label>
    <h4>{{ t('matCam') }}</h4>
    <label>{{ t('E') }} <span class="u">MPa</span><input :value="project.material.E2" type="number" step="any" min="0" @input="project.material.E2 = num($event.target.value)"></label>
    <label>{{ t('nu') }}<input :value="project.material.nu2" type="number" step="any" min="0" max="0.5" @input="project.material.nu2 = num($event.target.value)"></label>
    <div class="row"><button type="button" class="ghost" @click="steel">{{ t('steel') }}</button><span class="note">{{ t('steelNote') }}</span></div>
  </div>

  <div v-else class="grid">
    <p class="note">{{ t('limitsNote') }}</p>
    <label>{{ t('phiRise') }} <span class="u">°</span><input :value="project.limits.phi_rise_deg" type="number" step="any" min="0" max="89" @input="project.limits.phi_rise_deg = num($event.target.value)"></label>
    <label>{{ t('phiReturn') }} <span class="u">°</span><input :value="project.limits.phi_return_deg" type="number" step="any" min="0" max="89" @input="project.limits.phi_return_deg = num($event.target.value)"></label>
    <label>{{ t('rhoMin') }} <span class="u">mm</span><input :value="project.limits.rho_min" type="number" step="any" min="0" @input="project.limits.rho_min = num($event.target.value)"></label>
    <label>{{ t('stress') }} <span class="u">MPa</span><input :value="project.limits.stress" type="number" step="any" min="0" @input="project.limits.stress = num($event.target.value)"></label>
    <label>{{ t('torque') }} <span class="u">N·m</span><input :value="project.limits.torque" type="number" step="any" min="0" @input="project.limits.torque = num($event.target.value)"></label>
  </div>
</template>

<style scoped>
.grid { display: grid; gap: 10px; }
label { display: grid; grid-template-columns: 1fr 110px; align-items: center; gap: 4px 8px; font-size: 13.5px; }
label .u { grid-column: 1; font: 400 11.5px/1 var(--mono); color: var(--muted); margin-top: -2px; }
label input { grid-column: 2; grid-row: 1 / span 2; }
label.check { display: flex; gap: 6px; }
.row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.seg .lab { font-size: 13.5px; min-width: 64px; }
.seg button { border: 1px solid var(--line); background: var(--surface); padding: 5px 10px; border-radius: 6px; cursor: pointer; font: inherit; font-size: 13px; color: var(--ink); }
.seg button.on { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.note { font-size: 12.5px; color: var(--muted); margin: 0; }
h4 { margin: 8px 0 0; font-size: 13px; font-weight: 600; }
</style>
