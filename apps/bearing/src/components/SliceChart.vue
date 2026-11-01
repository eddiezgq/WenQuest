<script setup>
// The heaviest roller of the peak case: contact stress slice by slice along its length, inner and outer raceway.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const W = 520, H = 190, PL = 46, PR = 34, PT = 12, PB = 28
const v = computed(() => {
  const s = props.r?.slices
  if (!s) return null
  const L = props.r.geometry.Lwe
  const ymax = Math.max(...s.p_inner, ...s.p_outer, 1) * 1.1
  const X = (x) => PL + ((x + L / 2) / L) * (W - PL - PR), Y = (p) => PT + (1 - p / ymax) * (H - PT - PB)
  const line = (arr) => s.x.map((x, j) => `${X(x)},${Y(arr[j])}`).join(' ')
  return { inner: line(s.p_inner), outer: line(s.p_outer), ticks: [0, 0.25, 0.5, 0.75, 1].map((q) => ({ v: q * ymax, y: Y(q * ymax) })),
    xs: [-L / 2, 0, L / 2].map((x) => ({ x: X(x), lab: x.toFixed(1) })), base: H - PB }
})
</script>

<template>
  <figure v-if="v" class="curve slices">
    <figcaption>{{ t('sliceTitle') }} (MPa) <span class="key in">{{ t('innerRing') }}</span> <span class="key out">{{ t('outerRing') }}</span></figcaption>
    <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('sliceTitle')">
      <g v-for="tk in v.ticks" :key="tk.v"><line :x1="PL" :x2="W - PR" :y1="tk.y" :y2="tk.y" class="grid" /><text :x="PL - 6" :y="tk.y + 4" class="ann end">{{ Math.round(tk.v) }}</text></g>
      <g v-for="xk in v.xs" :key="xk.lab"><text :x="xk.x" :y="v.base + 17" class="ann mid">{{ xk.lab }} mm</text></g>
      <polyline :points="v.inner" class="line" /><polyline :points="v.outer" class="line out" />
    </svg>
  </figure>
</template>
