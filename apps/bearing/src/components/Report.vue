<script setup>
// The calculation report: inputs, every check with its value and limit, the method and sources. Print or save as PDF.
import { computed } from 'vue'
import { project } from '../store'
import { t, lang } from '../i18n'
import Section from './Section.vue'
import LoadRing from './LoadRing.vue'
import Extras from './Extras.vue'

const props = defineProps({ r: Object })
defineEmits(['close'])
const name = computed(() => (lang.value === 'zh' ? project.title.zh : project.title.en) || t('untitled'))
const inputs = computed(() => {
  const p = project, rows = [['type', t(p.type), '']]
  const add = (k, v, u) => { if (v != null && v !== '') rows.push([k, v, u]) }
  add('d', p.size.d, 'mm'); add('D', p.size.D, 'mm'); add('B', p.size.B, 'mm')
  add('Dw', p.inner.Dw, 'mm'); add('Z', p.inner.Z, ''); add('dm', p.inner.dm ?? props.r?.geometry?.dm, 'mm')
  add('fi', p.inner.fi, ''); add('fo', p.inner.fo, '')
  if (p.type === 'deep_groove') add('Pd', p.inner.Pd, 'mm'); else add('alpha0', p.inner.alpha0_deg, '°')
  add('h_i', p.inner.h_i, 'mm'); add('h_o', p.inner.h_o, 'mm')
  add('E', p.material.E, 'MPa'); add('nu', p.material.nu, '')
  add('Fr', p.loads.Fr, 'N'); add('Fa', p.loads.Fa, 'N'); add('M', p.loads.M, 'N·mm'); add('n', p.loads.n, 'r/min')
  if (p.type === 'deep_groove') {
    add('shaft_I', p.fits.shaft_I, 'mm'); add('housing_I', p.fits.housing_I, 'mm'); add('T_i', p.fits.T_i, '°C'); add('T_o', p.fits.T_o, '°C')
  }
  add('eta0', p.lube.eta0, 'Pa·s'); add('alpha_p', p.lube.alpha_p, '1/Pa'); add('sigma', p.lube.sigma, 'µm')
  add('p_max', p.limits.p_max, 'MPa'); add('gap_min', p.limits.gap_min, 'mm'); add('wall_min', p.limits.wall_min, 'mm')
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
      <h2>{{ t('inputs') }}</h2>
      <table><tbody><tr v-for="[k, x, u] in inputs" :key="k"><th>{{ t(k) }}</th><td class="mono">{{ x }} {{ u }}</td></tr></tbody></table>
      <h2>{{ t('results') }}</h2>
      <div class="figs"><Section :r="r" /><LoadRing :r="r" /></div>
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
      <Extras :r="r" />
      <h2>{{ t('method') }}</h2>
      <p>{{ t('methodText') }}</p>
      <p>{{ t('ratingsNote') }}</p>
      <p class="gen">{{ t('generated') }}：{{ now }}</p>
    </article>
  </div>
</template>
