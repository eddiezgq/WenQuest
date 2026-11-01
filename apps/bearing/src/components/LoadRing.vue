<script setup>
// Front view: every ball on the pitch circle, its load as a spoke outside the outer ring; the radial force points down.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const S = 384, C = S / 2

const v = computed(() => {
  const g = props.r?.geometry, b = props.r?.balls
  if (!g) return null
  const R = 92, k = R / (g.dm / 2)
  const Q = b?.Q || [], qmax = Math.max(...Q, 0)
  const psi = b?.psi_deg || Array.from({ length: g.Z }, (_, j) => (360 * j) / g.Z)
  const at = (deg, rad) => { const a = (deg * Math.PI) / 180; return [C + rad * Math.sin(a), C + rad * Math.cos(a)] }
  const ro = (g.do / 2) * k, rD = (g.D / 2) * k
  const balls = psi.map((p, j) => {
    const [x, y] = at(p, R), q = Q[j] || 0, w = qmax ? q / qmax : 0
    const [x1, y1] = at(p, rD + 6), [x2, y2] = at(p, rD + 6 + 34 * w)
    return { x, y, w, q, spoke: [x1, y1, x2, y2], top: qmax && q === qmax, lab: at(p, rD + 6 + 34 * w + 16) }
  })
  return { R, ballR: (g.Dw / 2) * k, balls, rd: (g.d / 2) * k, rdi: (g.di / 2) * k, ro, rD, qmax, any: Q.length > 0 }
})
</script>

<template>
  <figure class="ldring">
    <figcaption>{{ t('loadRing') }}</figcaption>
    <svg v-if="v" :viewBox="`0 0 ${S} ${S}`" role="img" :aria-label="t('loadRing')">
      <circle :cx="C" :cy="C" :r="v.rD" class="ringline" /><circle :cx="C" :cy="C" :r="v.ro" class="ringline thin" />
      <circle :cx="C" :cy="C" :r="v.rdi" class="ringline thin" /><circle :cx="C" :cy="C" :r="v.rd" class="ringline" />
      <circle :cx="C" :cy="C" :r="v.R" class="centre" fill="none" />
      <g v-for="(b, j) in v.balls" :key="j">
        <line v-if="b.w > 0" :x1="b.spoke[0]" :y1="b.spoke[1]" :x2="b.spoke[2]" :y2="b.spoke[3]" class="spoke" />
        <circle :cx="b.x" :cy="b.y" :r="v.ballR" class="ball" :style="{ '--w': b.w }" :class="{ idle: b.w === 0 }" />
        <text v-if="b.top" :x="b.lab[0]" :y="b.lab[1] + 4" class="ann mid">{{ Math.round(b.q) }} N</text>
      </g>
      <g v-if="v.any" class="arrow">
        <line :x1="C" :y1="C - 22" :x2="C" :y2="C + 26" /><path :d="`M${C - 6},${C + 18} L${C},${C + 30} L${C + 6},${C + 18} Z`" />
        <text :x="C + 9" :y="C - 10" class="ann">Fr</text>
      </g>
    </svg>
  </figure>
</template>
