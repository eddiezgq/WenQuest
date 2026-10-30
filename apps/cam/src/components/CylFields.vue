<script setup>
// The cylindrical cam's sizes (round 39, step 8): follower, roller shape, pitch radius, roller, groove, cam length,
// arm; with the search for the smallest pitch radius.
import { computed, ref } from 'vue'
import { project, payload, convertProgram } from '../store'
import { api } from '../api'
import { t, lang } from '../i18n'

const c = computed(() => project.cylindrical)
const osc = computed(() => c.value.follower === 'oscillating')
const searching = ref(false)
const searchMsg = ref('')
const num = (v) => (v === '' || v === null ? null : Number(v))

function follower(f) {
  if (c.value.follower === f) return
  c.value.follower = f
  convertProgram(f === 'oscillating')
  if (f === 'oscillating' && !(c.value.arm > 0)) c.value.arm = 2 * (c.value.Rp || 60)
}
async function findRp() {
  searching.value = true; searchMsg.value = ''
  try {
    const r = await api('/min-pitch-radius', payload())
    c.value.Rp = r.Rp
    searchMsg.value = lang.value === 'zh' ? `最小节圆柱半径 ${r.Rp} mm（压力角在许用值内、不根切）` : `Smallest pitch radius ${r.Rp} mm (pressure angle within the limit, no undercut)`
  } catch (e) { searchMsg.value = lang.value === 'zh' ? e.zh : e.message } finally { searching.value = false }
}
const fields = computed(() => [
  ['Rp', 'cylRp', 'mm'], ['rr', 'cylRr', 'mm'], ['b', 'cylB', 'mm'], ['gap', 'cylGap', 'mm'], ['bottom', 'cylBottom', 'mm'],
  ['length', 'cylLength', 'mm'], ...(osc.value ? [['arm', 'cylArm', 'mm'], ['psi_mid_deg', 'cylPsiMid', '°']] : []),
])
</script>

<template>
  <div class="grid">
    <div class="row seg">
      <span class="lab">{{ t('follower') }}</span>
      <button type="button" :class="{ on: !osc }" @click="follower('translating')">{{ t('translating') }}</button>
      <button type="button" :class="{ on: osc }" @click="follower('oscillating')">{{ t('oscillating') }}</button>
    </div>
    <div class="row seg">
      <span class="lab">{{ t('cylRoller') }}</span>
      <button type="button" :class="{ on: c.roller === 'cylinder' }" @click="c.roller = 'cylinder'">{{ t('cylRollerCyl') }}</button>
      <button type="button" :class="{ on: c.roller === 'cone' }" @click="c.roller = 'cone'">{{ t('cylRollerCone') }}</button>
    </div>
    <label v-for="[k, l, u] in fields" :key="k">{{ t(l) }} <span class="u">{{ u }}</span><input :value="c[k]" type="number" step="any" :min="k === 'psi_mid_deg' ? null : 0" @input="c[k] = num($event.target.value)"></label>
    <p v-if="osc" class="note">{{ t('cylPsiMidNote') }}</p>
    <div class="row seg">
      <span class="lab">{{ t('sigma') }}</span>
      <button type="button" :class="{ on: c.sigma === 1 }" @click="c.sigma = 1">↺ {{ t('ccw') }}</button>
      <button type="button" :class="{ on: c.sigma === -1 }" @click="c.sigma = -1">↻ {{ t('cw') }}</button>
    </div>
    <p class="note">{{ t(c.roller === 'cone' ? 'cylConeNote' : 'cylCylNote') }}</p>
    <div class="row"><button type="button" class="ghost" :disabled="searching" @click="findRp">{{ t('findRp') }}</button></div>
    <p v-if="searchMsg" class="note">{{ searchMsg }}</p>
  </div>
</template>

<style scoped>
.grid { display: grid; gap: 10px; }
label { display: grid; grid-template-columns: 1fr 110px; align-items: center; gap: 4px 8px; font-size: 13.5px; }
label .u { grid-column: 1; font: 400 11.5px/1 var(--mono); color: var(--muted); margin-top: -2px; }
label input { grid-column: 2; grid-row: 1 / span 2; }
.row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.seg .lab { font-size: 13.5px; min-width: 64px; }
.seg button { border: 1px solid var(--line); background: var(--surface); padding: 5px 10px; border-radius: 6px; cursor: pointer; font: inherit; font-size: 13px; color: var(--ink); }
.seg button.on { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.note { font-size: 12.5px; color: var(--muted); margin: 0; }
</style>
