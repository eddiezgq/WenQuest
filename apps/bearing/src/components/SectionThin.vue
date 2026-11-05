<script setup>
// Half section of a thin-section bearing (plan section 二十一): the rings as the drawings have them (a gothic arch
// for the four-point type), one ball, and the contact lines at the free contact angle.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const W = 460, H = 400, PAD = 54, PADL = 78, PADR = 120

const v = computed(() => {
  const g = props.r?.geometry, pf = props.r?.profile
  if (!g || !pf) return null
  const { d, D, B, dm, Dw } = g
  const s = Math.min((W - PADL - PADR) / B, (H - 2 * PAD) / ((D - d) / 2))
  const ox = PADL + (W - PADL - PADR) / 2, oy = H / 2 + ((D + d) / 4) * s
  const X = (z) => ox + z * s, Y = (r) => oy - r * s
  const poly = (pts) => 'M' + pts.map(([z, r]) => `${X(z).toFixed(1)},${Y(r).toFixed(1)}`).join(' L') + ' Z'
  const R0 = dm / 2, a = ((g.alpha0_deg || 0) * Math.PI) / 180, L = Dw * 0.9
  // contact lines through the ball centre: X both diagonals, A the one, C none (it settles under the load)
  const sides = g.thin === 'X' ? [1, -1] : g.thin === 'A' ? [1] : []
  const lines = sides.map((sg) => ({ x1: X(-sg * L * Math.sin(a)), y1: Y(R0 - L * Math.cos(a)), x2: X(sg * L * Math.sin(a)), y2: Y(R0 + L * Math.cos(a)) }))
  return { inner: poly(pf.inner), outer: poly(pf.outer), cx: X(0), cy: Y(R0), br: (Dw / 2) * s, lines, pitch: Y(R0), xL: X(-B / 2), xR: X(B / 2), yD: Y(D / 2), yd: Y(d / 2), g }
})
const f = (x, k = 1) => (x == null ? '—' : Number(x).toFixed(k))
</script>

<template>
  <figure class="sect">
    <figcaption>{{ t('section') }}</figcaption>
    <svg v-if="v" :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('section')">
      <defs>
        <pattern id="hatcht" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="7" class="hatch" />
        </pattern>
      </defs>
      <path :d="v.outer" class="ring" /><path :d="v.outer" fill="url(#hatcht)" />
      <path :d="v.inner" class="ring" /><path :d="v.inner" fill="url(#hatcht)" />
      <circle :cx="v.cx" :cy="v.cy" :r="v.br" class="ball" />
      <line v-for="(l, k) in v.lines" :key="k" v-bind="l" class="contact" />
      <line :x1="v.xL - 18" :x2="v.xR + 18" :y1="v.pitch" :y2="v.pitch" class="centre" />
      <line :x1="v.xL" :x2="v.xR" :y1="v.yD - 22" :y2="v.yD - 22" class="dim" />
      <text :x="(v.xL + v.xR) / 2" :y="v.yD - 28" class="ann mid">B {{ f(v.g.B) }}</text>
      <text :x="v.xL - 10" :y="v.yD + 4" class="ann end">⌀D {{ f(v.g.D) }}</text>
      <text :x="v.xL - 10" :y="v.yd + 4" class="ann end">⌀d {{ f(v.g.d) }}</text>
      <text :x="v.xR + 22" :y="v.pitch + 4" class="ann">⌀dm {{ f(v.g.dm) }}</text>
      <text :x="v.xR + 22" :y="v.pitch + 20" class="ann">Dw {{ f(v.g.Dw, 2) }}</text>
      <text v-if="v.g.alpha0_deg != null" :x="v.xR + 22" :y="v.pitch + 36" class="ann">α₀ {{ f(v.g.alpha0_deg, 1) }}°</text>
      <text :x="v.xR + 22" :y="v.pitch + 52" class="ann">{{ t('thin_' + v.g.thin) }}</text>
      <text v-if="v.g.arrangement && v.g.arrangement !== 'single'" :x="v.xR + 22" :y="v.pitch + 68" class="ann">{{ t('arr_' + v.g.arrangement) }}, s {{ f(v.g.spacing) }}</text>
    </svg>
  </figure>
</template>

<style scoped>
.contact { stroke: var(--muted); stroke-dasharray: 4 3; stroke-width: 1; }
</style>
