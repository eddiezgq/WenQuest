<script setup>
// The editor on the left: what the bearing is, how it is loaded, what it must meet.
import { project } from '../store'
import { t } from '../i18n'
import Num from './Num.vue'
import Scenario from './Scenario.vue'
import { computed } from 'vue'

const cyl = computed(() => ['cylindrical', 'tapered'].includes(project.type))
const tap = computed(() => project.type === 'tapered')
const flex = computed(() => project.type === 'flex')
// the cam given by points: "angle°, radial deviation mm" lines ↔ [[deg, mm], …] (plan section 十八)
const camPts = computed({
  get: () => (project.flex?.points || []).map((r) => r.join(', ')).join('\n'),
  set: (v) => {
    project.flex.points = v.split('\n').map((l) => l.split(/[\s,;]+/).filter(Boolean).map(Number)).filter((r) => r.length === 2 && r.every(Number.isFinite))
  },
})
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
      <button v-for="k in ['deep_groove', 'angular', 'cylindrical', 'tapered', 'flex']" :key="k" type="button" role="radio" :aria-checked="project.type === k"
              :class="{ on: project.type === k }" @click="project.type = k">{{ t(k) }}</button>
    </div>

    <Scenario v-if="!flex" />

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
      <Num v-if="['deep_groove', 'flex'].includes(project.type)" v-model="project.inner.Pd" :label="t('Pd')" unit="mm" step="0.001" />
      <Num v-else v-model="project.inner.alpha0_deg" :label="t('alpha0')" unit="°" />
      <template v-if="project.type === 'angular'">
        <label class="num"><span class="lab">{{ t('arrangement') }}</span>
          <select v-model="project.pair.arrangement"><option v-for="k in ['single', 'DB', 'DF', 'DT']" :key="k" :value="k">{{ t('arr_' + k) }}</option></select></label>
        <template v-if="project.pair.arrangement !== 'single'">
          <Num v-if="project.pair.arrangement !== 'DT'" v-model="project.pair.preload" :label="t('preloadF')" unit="N" />
          <Num v-model="project.pair.spacing" :label="t('rowSpacing')" unit="mm" :hint="t('rowSpacingHint')" />
        </template>
      </template>
      <Num v-model="project.inner.h_i" :label="t('h_i')" unit="mm" :hint="t('hHint')" />
      <Num v-model="project.inner.h_o" :label="t('h_o')" unit="mm" />
    </fieldset>
    <fieldset v-if="flex"><legend>{{ t('gFlex') }}</legend>
      <label class="num"><span class="lab">{{ t('camKind') }}</span>
        <select v-model="project.flex.cam"><option v-for="k in ['cosine', 'ellipse', 'points']" :key="k" :value="k">{{ t('cam_' + k) }}</option></select></label>
      <Num v-if="project.flex.cam === 'cosine'" v-model="project.flex.w0" :label="t('w0')" unit="mm" step="0.001" :hint="t('w0Hint')" />
      <template v-if="project.flex.cam === 'ellipse'">
        <Num v-model="project.flex.a" :label="t('camA')" unit="mm" step="0.001" :hint="t('camAHint')" />
        <Num v-model="project.flex.b" :label="t('camB')" unit="mm" step="0.001" />
      </template>
      <label v-if="project.flex.cam === 'points'" class="area"><span class="lab">{{ t('camPts') }}<small>{{ t('camPtsHint') }}</small></span>
        <textarea v-model.lazy="camPts" rows="6" spellcheck="false"></textarea></label>
      <Num v-model="project.flex.F" :label="t('meshF')" unit="N" :hint="t('meshFHint')" />
      <Num v-model="project.flex.beta_deg" :label="t('meshBeta')" unit="°" />
    </fieldset>
    <fieldset v-else><legend>{{ t('gRollers') }}</legend>
      <Num v-model="project.inner.Dw" :label="tap ? t('DwT') : t('DwR')" unit="mm" />
      <Num v-model="project.inner.Lw" :label="t('Lw')" unit="mm" />
      <Num v-model="project.inner.Lwe" :label="t('Lwe')" unit="mm" :hint="t('LweHint')" />
      <Num v-model="project.inner.Z" :label="t('ZR')" step="1" />
      <Num v-model="project.inner.dm" :label="t('dm')" unit="mm" :hint="t('dmHint')" />
      <Num v-if="!tap" v-model="project.inner.Pd" :label="t('Pd')" unit="mm" step="0.001" />
      <template v-else>
        <Num v-model="project.inner.alpha_o_deg" :label="t('cupAngle')" unit="°" :hint="t('cupHint')" />
        <Num v-model="project.inner.alpha_i_deg" :label="t('coneAngle')" unit="°" />
        <Num v-model="project.inner.alpha_f_deg" :label="t('ribAngle')" unit="°" :hint="t('ribHint')" />
        <Num v-model="project.inner.R_end" :label="t('rEnd')" unit="mm" />
        <label class="num"><span class="lab">{{ t('arrangement') }}</span>
          <select v-model="project.pair.arrangement"><option v-for="k in ['single', 'DB', 'DF']" :key="k" :value="k">{{ t('tarr_' + k) }}</option></select></label>
        <template v-if="project.pair.arrangement !== 'single'">
          <label class="num"><span class="lab">{{ t('mount') }}</span>
            <select v-model="project.pair.mount"><option v-for="k in ['pair', 'two_end']" :key="k" :value="k">{{ t('mount_' + k) }}</option></select></label>
          <Num v-if="project.pair.mount !== 'two_end' || project.scenario.kind === 'generic'" v-model="project.pair.spacing" :label="project.pair.mount === 'two_end' ? t('spanTwo') : t('rowSpacing')" unit="mm" :hint="project.pair.mount === 'two_end' ? t('spanTwoHint') : t('rowSpacingHint')" />
          <label class="num"><span class="lab">{{ t('setting') }}</span>
            <select v-model="project.pair.setting"><option v-for="k in ['endplay', 'preload']" :key="k" :value="k">{{ t('setting_' + k) }}</option></select></label>
          <Num v-if="project.pair.setting !== 'preload'" v-model="project.pair.endplay" :label="t('endplay')" unit="µm" :hint="t('endplayHint')" />
          <Num v-else v-model="project.pair.preload" :label="t('preloadF')" unit="N" />
          <Num v-model="project.pair.sweep_from" :label="t('sweepFrom')" unit="µm" :hint="t('sweepHint')" />
          <Num v-model="project.pair.sweep_to" :label="t('sweepTo')" unit="µm" />
        </template>
      </template>
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
      <Num v-if="project.type === 'angular'" v-model="project.material.density" :label="t('density')" unit="g/cm³" step="0.01" :hint="t('densityHint')" />
    </fieldset>

    <fieldset v-if="project.scenario.kind === 'generic' && !flex"><legend>{{ t('gLoads') }}</legend>
      <Num v-model="project.loads.Fr" :label="t('Fr')" unit="N" />
      <Num v-model="project.loads.Fa" :label="t('Fa')" unit="N" />
      <Num v-model="project.loads.M" :label="t('M')" unit="N·mm" :hint="t('MHint')" />
      <Num v-model="project.loads.n" :label="t('n')" unit="r/min" />
    </fieldset>

    <fieldset><legend>{{ t('gFits') }}</legend>
      <template v-if="['deep_groove', 'cylindrical'].includes(project.type)">
        <Num v-model="project.fits.shaft_I" :label="t('shaft_I')" unit="mm" step="0.001" />
        <Num v-model="project.fits.housing_I" :label="t('housing_I')" unit="mm" step="0.001" />
        <Num v-model="project.fits.T_i" :label="t('T_i')" unit="°C" />
        <Num v-model="project.fits.T_o" :label="t('T_o')" unit="°C" />
      </template>
      <p v-else class="hint">{{ flex ? t('fitsFlex') : tap ? t('fitsTapered') : t('fitsAngular') }}</p>
    </fieldset>

    <fieldset v-if="!flex"><legend>{{ t('gLube') }}</legend>
      <Num v-model="project.lube.eta0" :label="t('eta0')" unit="Pa·s" step="0.001" />
      <Num v-model="project.lube.alpha_p" :label="t('alpha_p')" unit="1/Pa" />
      <Num v-model="project.lube.sigma" :label="t('sigma')" unit="µm" step="0.01" />
    </fieldset>

    <fieldset><legend>{{ t('gLimits') }}</legend>
      <p class="hint">{{ t('limitsHint') }}</p>
      <Num v-model="project.limits.p_static" :label="t('p_static')" unit="MPa" />
      <Num v-if="!flex" v-model="project.limits.p_fatigue" :label="t('p_fatigue')" unit="MPa" />
      <template v-if="flex">
        <Num v-model="project.flex.sig_i_allow" :label="t('sigIAllow')" unit="MPa" />
        <Num v-model="project.flex.sig_a_allow" :label="t('sigAAllow')" unit="MPa" />
      </template>
      <Num v-model="project.limits.gap_min" :label="t('gap_min')" unit="mm" />
      <Num v-model="project.limits.wall_min" :label="t('wall_min')" unit="mm" />
    </fieldset>
  </div>
</template>
