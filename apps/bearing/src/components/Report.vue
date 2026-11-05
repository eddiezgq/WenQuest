<script setup>
// The calculation report: inputs, every check with its value and limit, the method and sources. Print or save as PDF.
import { computed } from 'vue'
import { project } from '../store'
import { t, lang } from '../i18n'
import Section from './Section.vue'
import SectionCyl from './SectionCyl.vue'
import SliceChart from './SliceChart.vue'
import SectionTaper from './SectionTaper.vue'
import LoadRing from './LoadRing.vue'
import Extras from './Extras.vue'
import SettingCurve from './SettingCurve.vue'
import ScenarioPanel from './ScenarioPanel.vue'
import DesignNote from './DesignNote.vue'
import CatalogNote from './CatalogNote.vue'

const props = defineProps({ r: Object })
defineEmits(['close'])
const name = computed(() => (lang.value === 'zh' ? project.title.zh : project.title.en) || t('untitled'))
const inputs = computed(() => {
  const p = project, rows = [['type', t(p.type), '']]
  const add = (k, v, u) => { if (v != null && v !== '') rows.push([k, v, u]) }
  add('d', p.size.d, 'mm'); add('D', p.size.D, 'mm'); add('B', p.size.B, 'mm')
  add('Dw', p.inner.Dw, 'mm'); add('Z', p.inner.Z, ''); add('dm', p.inner.dm ?? props.r?.geometry?.dm, 'mm')
  if (['cylindrical', 'tapered'].includes(p.type)) {
    add('Lw', p.inner.Lw, 'mm'); add('Lwe', p.inner.Lwe, 'mm')
    if (p.type === 'cylindrical') add('Pd', p.inner.Pd, 'mm')
    else {
      add('cupAngle', p.inner.alpha_o_deg, '°'); add('coneAngle', p.inner.alpha_i_deg, '°'); add('ribAngle', p.inner.alpha_f_deg, '°'); add('rEnd', p.inner.R_end, 'mm')
      if (p.pair?.arrangement && p.pair.arrangement !== 'single') {
        rows.push(['arrangement', t('tarr_' + p.pair.arrangement), '']); rows.push(['mount', t('mount_' + (p.pair.mount || 'pair')), ''])
        add(p.pair.mount === 'two_end' ? 'spanTwo' : 'rowSpacing', props.r?.pair?.spacing, 'mm')
        add('endplay', props.r?.pair?.endplay_um != null ? props.r.pair.endplay_um.toFixed(1) : null, 'µm'); add('preloadF', props.r?.pair?.preload != null ? props.r.pair.preload.toFixed(0) : null, 'N')
      }
    }
    rows.push(['crown', t('crown_' + (p.profile?.kind || 'straight')), ''])
    add('crownR', p.profile?.R, 'mm'); add('crownFlat', p.profile?.flat, 'mm'); add('misalign', p.alignment?.theta_arcmin, '′')
  } else {
    add('fi', p.inner.fi, ''); add('fo', p.inner.fo, '')
    if (p.type === 'deep_groove') add('Pd', p.inner.Pd, 'mm'); else add('alpha0', p.inner.alpha0_deg, '°')
    if (p.type === 'angular' && p.pair?.arrangement && p.pair.arrangement !== 'single') {
      rows.push(['arrangement', t('arr_' + p.pair.arrangement), '']); add('preloadF', p.pair.preload, 'N'); add('rowSpacing', p.pair.spacing, 'mm')
    }
    if (p.type === 'angular') add('density', p.material?.density, 'g/cm³')
    add('h_i', p.inner.h_i, 'mm'); add('h_o', p.inner.h_o, 'mm')
  }
  add('E', p.material.E, 'MPa'); add('nu', p.material.nu, '')
  rows.push(['sceneKind', t('sk_' + (p.scenario?.kind || 'generic')), ''])
  if ((p.scenario?.kind || 'generic') === 'generic') { add('Fr', p.loads.Fr, 'N'); add('Fa', p.loads.Fa, 'N'); add('M', p.loads.M, 'N·mm'); add('n', p.loads.n, 'r/min') }
  if (p.scenario?.fp != null) add('fp', p.scenario.fp, '')
  // the machine data of the scenario (the cases are in the results)
  const S = p.scenario || {}
  const KEYS = [['mn', 'mn', 'mm'], ['z', 'zGear', ''], ['alpha_n_deg', 'alphaN', '°'], ['beta_deg', 'beta', '°'], ['m', 'rotorM', 'kg'],
    ['U', 'unbalance', 'g·mm'], ['F_belt', 'beltF', 'N'], ['x_belt', 'beltX', 'mm'], ['belt_deg', 'beltDeg', '°'], ['a', 'overhang', 'mm'],
    ['W', S.kind === 'hub' ? 'wheelW' : 'jointW', 'N'], ['ay', 'ay', 'g'], ['R', 'wheelR', 'mm'], ['e', 'hubE', 'mm'], ['r', 'lever', 'mm'],
    ['swing_deg', 'swing', '°'], ['x', 'loadX', 'mm'], ['L', S.kind === 'hub' ? 'rowL' : 'spanL', 'mm']]
  if (S.kind && S.kind !== 'generic') {
    for (const [k, w, u] of KEYS) add(w, S[k], u)
    if (S.this || S.kind === 'hub') rows.push(['thisBearing', S.kind === 'hub' ? t(S.row) : S.this, ''])
  }
  if (!['angular', 'tapered'].includes(p.type)) {
    add('shaft_I', p.fits.shaft_I, 'mm'); add('housing_I', p.fits.housing_I, 'mm'); add('T_i', p.fits.T_i, '°C'); add('T_o', p.fits.T_o, '°C')
  }
  add('eta0', p.lube.eta0, 'Pa·s'); add('alpha_p', p.lube.alpha_p, '1/Pa'); add('sigma', p.lube.sigma, 'µm')
  add('p_static', p.limits.p_static, 'MPa'); add('p_fatigue', p.limits.p_fatigue, 'MPa'); add('gap_min', p.limits.gap_min, 'mm'); add('wall_min', p.limits.wall_min, 'mm')
  return rows
})
const fmt = (x) => (x == null ? '—' : typeof x === 'number' ? (Math.abs(x) >= 100 ? x.toFixed(0) : Math.abs(x) >= 1 ? x.toFixed(2) : x.toFixed(4)) : x)
const now = new Date().toLocaleString()
const print = () => window.print()
</script>

<template>
  <div class="report-wrap" role="dialog" aria-modal="true" :aria-label="t('reportTitle')">
    <div class="report-bar no-print">
      <button type="button" class="accent" @click="print">{{ t('print') }}</button>
      <button type="button" class="ghost" @click="$emit('close')">{{ t('close') }}</button>
    </div>
    <article class="report">
      <header>
        <h1>{{ t('reportTitle') }}</h1>
        <p class="sub">{{ name }}</p>
        <p v-if="project.note" class="fict">{{ t('fictional') }}：{{ lang === 'zh' ? project.note.zh : project.note.en }}</p>
        <p class="verdict" :class="r?.status">{{ t('overall') }}：{{ t(r?.status === 'pass' ? 'overallPass' : r?.status === 'fail' ? 'overallFail' : 'overallUnknown') }}</p>
      </header>
      <CatalogNote />
      <DesignNote />
      <h2>{{ t('inputs') }}</h2>
      <table><tbody><tr v-for="[k, x, u] in inputs" :key="k"><th>{{ t(k) }}</th><td class="mono">{{ x }} {{ u }}</td></tr></tbody></table>
      <h2>{{ t('results') }}</h2>
      <div class="figs"><SectionCyl v-if="r.type === 'cylindrical'" :r="r" /><SectionTaper v-else-if="r.type === 'tapered'" :r="r" /><Section v-else :r="r" /><LoadRing :r="r" /></div>
      <table class="ck">
        <thead><tr><th></th><th>{{ t('value') }}</th><th>{{ t('limit') }}</th><th></th></tr></thead>
        <tbody>
          <tr v-for="c in r.checks" :key="c.id" :class="c.status">
            <th>{{ lang === 'zh' ? c.zh : c.en }}<small v-if="c.note">{{ lang === 'zh' ? c.note_zh : c.note }}</small></th>
            <td class="mono">{{ fmt(c.value) }} {{ c.value != null ? c.unit : '' }}</td>
            <td class="mono">{{ c.status === 'info' ? '' : fmt(c.limit) }}</td><td>{{ t(c.status) }}</td>
          </tr>
        </tbody>
      </table>
      <SliceChart :r="r" />
      <ScenarioPanel :r="r" />
      <Extras :r="r" />
      <SettingCurve :r="r" />
      <h2>{{ t('method') }}</h2>
      <p>{{ t('methodText') }}</p>
      <p>{{ t('ratingsNote') }}</p>
      <p class="gen">{{ t('generated') }}：{{ now }}</p>
    </article>
  </div>
</template>
