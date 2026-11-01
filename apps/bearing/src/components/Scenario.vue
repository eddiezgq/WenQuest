<script setup>
// “Where is it used”: the application scenario turns machine data into load cases on this bearing (round 64, step 3).
import { computed } from 'vue'
import { project } from '../store'
import { t, lang } from '../i18n'
import Num from './Num.vue'

const KINDS = ['generic', 'gearbox', 'motor', 'spindle', 'hub', 'joint', 'camshaft']
// a fresh scenario of each kind: only the structure, no numbers (the user fills them in)
const FRESH = {
  generic: () => ({ kind: 'generic', fp: null }),
  gearbox: () => ({ kind: 'gearbox', fp: null, mn: null, z: null, alpha_n_deg: null, beta_deg: 0, x: null, L: null, this: 'A', fixed: 'A', axial_to: 'B', cases: [{ label: '', P: null, n: null, share: 1 }] }),
  motor: () => ({ kind: 'motor', fp: null, m: null, U: null, x: null, L: null, F_belt: null, x_belt: null, belt_deg: 0, Fa: null, n: null, this: 'A' }),
  spindle: () => ({ kind: 'spindle', fp: null, a: null, L: null, this: 'A', cases: [{ label: '', Fr: null, Fa: null, n: null, share: 1 }] }),
  hub: () => ({ kind: 'hub', fp: null, W: null, ay: null, R: null, L: null, e: 0, row: 'outboard', n: null, shares: { straight: null, out: null, in: null } }),
  joint: () => ({ kind: 'joint', axis: 'horizontal', W: null, x: null, r: null, L: null, this: 'A', fixed: 'A', swing_deg: null, n: null }),
  camshaft: () => ({ kind: 'camshaft', fp: null, x: null, L: null, n: null, this: 'A', fixed: 'A', table: '' }),
}
const s = computed(() => project.scenario)
function pick(k) { if (k !== s.value.kind) project.scenario = FRESH[k]() }
function addCase() { s.value.cases.push(s.value.kind === 'gearbox' ? { label: '', P: null, n: null, share: null } : { label: '', Fr: null, Fa: null, n: null, share: null }) }
const lab = (c) => (typeof c.label === 'object' && c.label ? c.label[lang.value] : c.label)
function setLab(c, v) { c.label = v }
</script>

<template>
  <fieldset class="scn"><legend>{{ t('gScene') }}</legend>
    <label class="num"><span class="lab">{{ t('sceneKind') }}</span>
      <select :value="s.kind" @change="pick($event.target.value)"><option v-for="k in KINDS" :key="k" :value="k">{{ t('sk_' + k) }}</option></select>
    </label>
    <p class="hint">{{ t('skHint_' + s.kind) }}</p>

    <template v-if="s.kind === 'gearbox'">
      <Num v-model="s.mn" :label="t('mn')" unit="mm" /><Num v-model="s.z" :label="t('zGear')" step="1" />
      <Num v-model="s.alpha_n_deg" :label="t('alphaN')" unit="°" /><Num v-model="s.beta_deg" :label="t('beta')" unit="°" />
    </template>
    <template v-if="s.kind === 'motor'">
      <Num v-model="s.m" :label="t('rotorM')" unit="kg" /><Num v-model="s.U" :label="t('unbalance')" unit="g·mm" />
      <Num v-model="s.F_belt" :label="t('beltF')" unit="N" /><Num v-model="s.x_belt" :label="t('beltX')" unit="mm" :hint="t('xHint')" />
      <Num v-model="s.belt_deg" :label="t('beltDeg')" unit="°" /><Num v-model="s.Fa" :label="t('Fa')" unit="N" />
      <Num v-model="s.n" :label="t('n')" unit="r/min" />
    </template>
    <template v-if="s.kind === 'spindle'">
      <Num v-model="s.a" :label="t('overhang')" unit="mm" />
    </template>
    <template v-if="s.kind === 'hub'">
      <Num v-model="s.W" :label="t('wheelW')" unit="N" /><Num v-model="s.ay" :label="t('ay')" unit="g" />
      <Num v-model="s.R" :label="t('wheelR')" unit="mm" /><Num v-model="s.e" :label="t('hubE')" unit="mm" />
      <Num v-model="s.L" :label="t('rowL')" unit="mm" /><Num v-model="s.n" :label="t('n')" unit="r/min" />
      <label class="num"><span class="lab">{{ t('row') }}</span><select v-model="s.row"><option value="outboard">{{ t('outboard') }}</option><option value="inboard">{{ t('inboard') }}</option></select></label>
      <Num v-model="s.shares.straight" :label="t('shareStraight')" /><Num v-model="s.shares.out" :label="t('shareOut')" /><Num v-model="s.shares.in" :label="t('shareIn')" />
    </template>
    <template v-if="s.kind === 'joint'">
      <label class="num"><span class="lab">{{ t('axis') }}</span><select v-model="s.axis"><option value="horizontal">{{ t('horizontal') }}</option><option value="vertical">{{ t('vertical') }}</option></select></label>
      <Num v-model="s.W" :label="t('jointW')" unit="N" />
      <Num v-if="s.axis === 'vertical'" v-model="s.r" :label="t('lever')" unit="mm" />
      <Num v-model="s.swing_deg" :label="t('swing')" unit="°" /><Num v-model="s.n" :label="t('n')" unit="r/min" />
    </template>
    <template v-if="s.kind === 'camshaft'">
      <Num v-model="s.n" :label="t('n')" unit="r/min" />
      <label class="area"><span class="lab">{{ t('camTable') }}<small>{{ t('camTableHint') }}</small></span>
        <textarea v-model="s.table" rows="6" spellcheck="false"></textarea></label>
    </template>

    <!-- where the load sits between the two bearings -->
    <template v-if="['gearbox', 'motor', 'spindle', 'camshaft'].includes(s.kind) || (s.kind === 'joint')">
      <Num v-if="s.kind !== 'spindle' && !(s.kind === 'joint' && s.axis === 'vertical')" v-model="s.x" :label="t('loadX')" unit="mm" :hint="t('xHint')" />
      <Num v-model="s.L" :label="t('spanL')" unit="mm" :hint="s.kind === 'joint' ? t('jointL') : ''" />
      <label class="num"><span class="lab">{{ t('thisBearing') }}</span><select v-model="s.this"><option value="A">A</option><option value="B">B</option></select></label>
      <label v-if="['gearbox', 'camshaft', 'joint'].includes(s.kind)" class="num"><span class="lab">{{ t('fixedBearing') }}</span><select v-model="s.fixed"><option value="A">A</option><option value="B">B</option></select></label>
      <label v-if="s.kind === 'gearbox'" class="num"><span class="lab">{{ t('axialTo') }}</span><select v-model="s.axial_to"><option value="A">A</option><option value="B">B</option></select></label>
    </template>

    <!-- load spectrum -->
    <div v-if="['gearbox', 'spindle'].includes(s.kind)" class="cases">
      <span class="lab">{{ t('cases') }}</span>
      <table><thead><tr><th>{{ t('caseName') }}</th><th v-if="s.kind === 'gearbox'">P kW</th><th v-else>Fr N</th><th v-if="s.kind === 'spindle'">Fa N</th><th>n r/min</th><th>{{ t('share') }}</th><th></th></tr></thead>
        <tbody><tr v-for="(c, j) in s.cases" :key="j">
          <td><input :value="lab(c)" @input="setLab(c, $event.target.value)"></td>
          <td v-if="s.kind === 'gearbox'"><input type="number" step="any" :value="c.P ?? ''" @input="c.P = $event.target.value === '' ? null : +$event.target.value"></td>
          <td v-else><input type="number" step="any" :value="c.Fr ?? ''" @input="c.Fr = $event.target.value === '' ? null : +$event.target.value"></td>
          <td v-if="s.kind === 'spindle'"><input type="number" step="any" :value="c.Fa ?? ''" @input="c.Fa = $event.target.value === '' ? null : +$event.target.value"></td>
          <td><input type="number" step="any" :value="c.n ?? ''" @input="c.n = $event.target.value === '' ? null : +$event.target.value"></td>
          <td><input type="number" step="any" :value="c.share ?? ''" @input="c.share = $event.target.value === '' ? null : +$event.target.value"></td>
          <td><button v-if="s.cases.length > 1" type="button" class="x" :aria-label="t('removeCase')" @click="s.cases.splice(j, 1)">×</button></td>
        </tr></tbody></table>
      <button type="button" class="ghost" @click="addCase">{{ t('addCase') }}</button>
    </div>

    <Num v-if="s.kind !== 'joint'" v-model="s.fp" :label="t('fp')" step="0.05" :hint="t('fpHint')" />
  </fieldset>
</template>
