<script setup>
// The editor on the left: what the bearing is, how it is loaded, what it must meet.
import { project } from '../store'
import { t } from '../i18n'
import Num from './Num.vue'
import Scenario from './Scenario.vue'
import { computed } from 'vue'

const cyl = computed(() => project.type === 'cylindrical')
// the crown profile table: "x, drop" lines ↔ [[x, drop], …]
const pts = computed({
  get: () => (project.profile?.points || []).map((r) => r.join(', ')).join('\n'),
  set: (v) => {
    project.profile.points = v.split('\n').map((l) => l.split(/[\s,;]+/).filter(Boolean).map(Number)).filter((r) => r.length === 2 && r.every(Number.isFinite))
  },
})
</script>

<template>
  <div class="fields">
    <div class="seg" role="radiogroup" :aria-label="t('type')">
      <button v-for="k in ['deep_groove', 'angular', 'cylindrical']" :key="k" type="button" role="radio" :aria-checked="project.type === k"
              :class="{ on: project.type === k }" @click="project.type = k">{{ t(k) }}</button>
    </div>

    <Scenario />

    <fieldset><legend>{{ t('gSize') }}</legend>
      <Num v-model="project.size.d" :label="t('d')" unit="mm" />
      <Num v-model="project.size.D" :label="t('D')" unit="mm" />
      <Num v-model="project.size.B" :label="t('B')" unit="mm" />
    </fieldset>

    <fieldset v-if="!cyl"><legend>{{ t('gBalls') }}</legend>
      <Num v-model="project.inner.Dw" :label="t('Dw')" unit="mm" />
      <Num v-model="project.inner.Z" :label="t('Z')" step="1" />
      <Num v-model="project.inner.dm" :label="t('dm')" unit="mm" :hint="t('dmHint')" />
      <Num v-model="project.inner.fi" :label="t('fi')" step="0.001" :hint="t('fHint')" />
      <Num v-model="project.inner.fo" :label="t('fo')" step="0.001" />
      <Num v-if="project.type === 'deep_groove'" v-model="project.inner.Pd" :label="t('Pd')" unit="mm" step="0.001" />
      <Num v-else v-model="project.inner.alpha0_deg" :label="t('alpha0')" unit="°" />
      <Num v-model="project.inner.h_i" :label="t('h_i')" unit="mm" :hint="t('hHint')" />
      <Num v-model="project.inner.h_o" :label="t('h_o')" unit="mm" />
    </fieldset>
    <fieldset v-else><legend>{{ t('gRollers') }}</legend>
      <Num v-model="project.inner.Dw" :label="t('DwR')" unit="mm" />
      <Num v-model="project.inner.Lw" :label="t('Lw')" unit="mm" />
      <Num v-model="project.inner.Lwe" :label="t('Lwe')" unit="mm" :hint="t('LweHint')" />
      <Num v-model="project.inner.Z" :label="t('ZR')" step="1" />
      <Num v-model="project.inner.dm" :label="t('dm')" unit="mm" :hint="t('dmHint')" />
      <Num v-model="project.inner.Pd" :label="t('Pd')" unit="mm" step="0.001" />
      <label class="num"><span class="lab">{{ t('crown') }}</span>
        <select v-model="project.profile.kind"><option v-for="k in ['straight', 'arc', 'partial', 'table']" :key="k" :value="k">{{ t('crown_' + k) }}</option></select></label>
      <Num v-if="['arc', 'partial'].includes(project.profile.kind)" v-model="project.profile.R" :label="t('crownR')" unit="mm" />
      <Num v-if="project.profile.kind === 'partial'" v-model="project.profile.flat" :label="t('crownFlat')" unit="mm" />
      <label v-if="project.profile.kind === 'table'" class="area"><span class="lab">{{ t('crownTable') }}<small>{{ t('crownTableHint') }}</small></span>
        <textarea v-model.lazy="pts" rows="5" spellcheck="false"></textarea></label>
      <Num v-model="project.alignment.theta_arcmin" :label="t('misalign')" unit="′" :hint="t('misalignHint')" />
    </fieldset>

    <fieldset><legend>{{ t('gMat') }}</legend>
      <Num v-model="project.material.E" :label="t('E')" unit="MPa" />
      <Num v-model="project.material.nu" :label="t('nu')" step="0.01" />
    </fieldset>

    <fieldset v-if="project.scenario.kind === 'generic'"><legend>{{ t('gLoads') }}</legend>
      <Num v-model="project.loads.Fr" :label="t('Fr')" unit="N" />
      <Num v-model="project.loads.Fa" :label="t('Fa')" unit="N" />
      <Num v-model="project.loads.M" :label="t('M')" unit="N·mm" :hint="t('MHint')" />
      <Num v-model="project.loads.n" :label="t('n')" unit="r/min" />
    </fieldset>

    <fieldset><legend>{{ t('gFits') }}</legend>
      <template v-if="project.type !== 'angular'">
        <Num v-model="project.fits.shaft_I" :label="t('shaft_I')" unit="mm" step="0.001" />
        <Num v-model="project.fits.housing_I" :label="t('housing_I')" unit="mm" step="0.001" />
        <Num v-model="project.fits.T_i" :label="t('T_i')" unit="°C" />
        <Num v-model="project.fits.T_o" :label="t('T_o')" unit="°C" />
      </template>
      <p v-else class="hint">{{ t('fitsAngular') }}</p>
    </fieldset>

    <fieldset><legend>{{ t('gLube') }}</legend>
      <Num v-model="project.lube.eta0" :label="t('eta0')" unit="Pa·s" step="0.001" />
      <Num v-model="project.lube.alpha_p" :label="t('alpha_p')" unit="1/Pa" />
      <Num v-model="project.lube.sigma" :label="t('sigma')" unit="µm" step="0.01" />
    </fieldset>

    <fieldset><legend>{{ t('gLimits') }}</legend>
      <p class="hint">{{ t('limitsHint') }}</p>
      <Num v-model="project.limits.p_static" :label="t('p_static')" unit="MPa" />
      <Num v-model="project.limits.p_fatigue" :label="t('p_fatigue')" unit="MPa" />
      <Num v-model="project.limits.gap_min" :label="t('gap_min')" unit="mm" />
      <Num v-model="project.limits.wall_min" :label="t('wall_min')" unit="mm" />
    </fieldset>
  </div>
</template>
