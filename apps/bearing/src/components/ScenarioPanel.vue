<script setup>
// Where the loads on this bearing come from, and how every case comes out (round 64, step 3).
import { computed } from 'vue'
import { t, lang } from '../i18n'

const props = defineProps({ r: Object })
const sc = computed(() => props.r?.scenario)
const show = computed(() => sc.value && (sc.value.kind !== 'generic' || sc.value.cases.length > 1))
const lab = (c) => (typeof c.label === 'object' && c.label ? c.label[lang.value] : c.label)
const f0 = (x) => (x == null ? '—' : Math.round(x).toLocaleString())
const fx = (x) => (x == null ? '—' : Math.abs(x) >= 100 ? x.toFixed(0) : Math.abs(x) >= 1 ? x.toFixed(2) : x.toFixed(4))
const peak = computed(() => {
  const cs = sc.value?.cases || []
  let k = -1, v = -1
  cs.forEach((c, j) => { const m = Math.max(c.p_inner, c.p_outer); if (m > v) { v = m; k = j } })
  return k
})
// the stress round the turn (camshaft, motor unbalance)
const W = 520, H = 170, PL = 46, PR = 12, PT = 10, PB = 26
const curve = computed(() => {
  if (sc.value?.curve !== 'angle') return null
  const cs = sc.value.cases
  const ys = cs.map((c) => c.p_inner), ymax = Math.max(...ys, 1) * 1.08
  const X = (a) => PL + (a / 360) * (W - PL - PR), Y = (v) => PT + (1 - v / ymax) * (H - PT - PB)
  const pts = cs.map((c) => `${X(c.angle)},${Y(c.p_inner)}`).join(' ')
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((q) => ({ v: q * ymax, y: Y(q * ymax) }))
  return { pts, ticks, xs: [0, 90, 180, 270, 360].map((a) => ({ a, x: X(a) })), base: H - PB }
})
</script>

<template>
  <section v-if="show" class="scnres">
    <h3>{{ t('sceneResult') }} <small>{{ t('sk_' + sc.kind) }} · {{ sc.motion === 'oscillating' ? t('motionOsc') : t('motionRot') }}<template v-if="sc.outer_turns"> · {{ t('outerTurns') }}</template><template v-if="sc.fp != null"> · fp = {{ sc.fp }}</template></small></h3>
    <dl v-if="sc.steps.length" class="rows">
      <template v-for="(s, j) in sc.steps" :key="j"><dt>{{ lang === 'zh' ? s.zh : s.en }}</dt><dd class="mono">{{ fx(s.value) }} {{ s.unit }}</dd></template>
    </dl>
    <p v-for="(n, j) in sc.notes" :key="'n' + j" class="note">{{ lang === 'zh' ? n.zh : n.en }}</p>
    <figure v-if="curve" class="curve">
      <figcaption>{{ t('angleCurve') }}：{{ t('pIn') }} (MPa)</figcaption>
      <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('angleCurve')">
        <g v-for="tk in curve.ticks" :key="tk.v"><line :x1="PL" :x2="W - PR" :y1="tk.y" :y2="tk.y" class="grid" /><text :x="PL - 6" :y="tk.y + 4" class="ann end">{{ Math.round(tk.v) }}</text></g>
        <g v-for="xk in curve.xs" :key="xk.a"><text :x="xk.x" :y="curve.base + 17" class="ann mid">{{ xk.a }}°</text></g>
        <polyline :points="curve.pts" class="line" />
      </svg>
    </figure>
    <div v-else class="tblwrap">
      <table class="casetbl">
        <thead><tr><th>{{ t('caseName') }}</th><th>{{ t('share') }}</th><th>n</th><th>Fr N</th><th>Fa N</th><th>Q<sub>max</sub> N</th><th>{{ t('pIn') }}</th><th>{{ t('pOut') }}</th></tr></thead>
        <tbody><tr v-for="(c, j) in sc.cases" :key="j" :class="{ peak: j === peak }">
          <td>{{ lab(c) }}</td><td class="mono">{{ (c.share * 100).toFixed(0) }}%</td><td class="mono">{{ f0(c.n) }}</td>
          <td class="mono">{{ f0(c.Fr) }}</td><td class="mono">{{ f0(c.Fa) }}</td><td class="mono">{{ f0(c.Qmax) }}</td>
          <td class="mono">{{ f0(c.p_inner) }}</td><td class="mono">{{ f0(c.p_outer) }}</td>
        </tr></tbody>
      </table>
    </div>
  </section>
</template>
