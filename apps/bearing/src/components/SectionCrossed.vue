<script setup>
// Half section of a crossed roller bearing (plan section 十九): rings with V grooves (hatched), and one roller of
// each set drawn in the same plane so the crossing shows (in the bearing they sit one pitch apart).
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const W = 460, H = 400, PAD = 54, PADL = 78, PADR = 104

const v = computed(() => {
  const g = props.r?.geometry, pf = props.r?.profile
  if (!g || !pf) return null
  const { d, D, B, dm, Dw, Lw } = g
  const s = Math.min((W - PADL - PADR) / B, (H - 2 * PAD) / ((D - d) / 2))
  const ox = PADL + (W - PADL - PADR) / 2, oy = H / 2 + ((D + d) / 4) * s
  const X = (z) => ox + z * s, Y = (r) => oy - r * s
  const poly = (pts) => 'M' + pts.map(([r, z]) => `${X(z).toFixed(1)},${Y(r).toFixed(1)}`).join(' L') + ' Z'
  const a = (g.alpha_deg * Math.PI) / 180, ca = Math.cos(a), sa = Math.sin(a), R0 = dm / 2
  // a roller of set σ: centre (R0, 0), axis (−σ sin α, cos α) in (r, z), half length Lw/2, half width Dw/2 across
  const roller = (sg) => {
    const ar = -sg * sa, az = ca, nr = ca, nz = sg * sa
    const c = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => [R0 + i * (Lw / 2) * ar + j * (Dw / 2) * nr, i * (Lw / 2) * az + j * (Dw / 2) * nz])
    return poly(c)
  }
  return {
    inner: poly(pf.inner), outer: poly(pf.outer), r1: roller(1), r2: roller(-1),
    pitch: Y(R0), xL: X(-B / 2), xR: X(B / 2), yD: Y(D / 2), yd: Y(d / 2), g,
  }
})
const f = (x, k = 1) => (x == null ? '—' : Number(x).toFixed(k))
</script>

<template>
  <figure class="sect">
    <figcaption>{{ t('section') }}</figcaption>
    <svg v-if="v" :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('section')">
      <defs>
        <pattern id="hatchx" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="7" class="hatch" />
        </pattern>
      </defs>
      <path :d="v.outer" class="ring" /><path :d="v.outer" fill="url(#hatchx)" />
      <path :d="v.inner" class="ring" /><path :d="v.inner" fill="url(#hatchx)" />
      <path :d="v.r2" class="ball ghost" /><path :d="v.r1" class="ball" />
      <line :x1="v.xL - 18" :x2="v.xR + 18" :y1="v.pitch" :y2="v.pitch" class="centre" />
      <line :x1="v.xL" :x2="v.xR" :y1="v.yD - 22" :y2="v.yD - 22" class="dim" />
      <text :x="(v.xL + v.xR) / 2" :y="v.yD - 28" class="ann mid">B {{ f(v.g.B) }}</text>
      <text :x="v.xL - 10" :y="v.yD + 4" class="ann end">⌀D {{ f(v.g.D) }}</text>
      <text :x="v.xL - 10" :y="v.yd + 4" class="ann end">⌀d {{ f(v.g.d) }}</text>
      <text :x="v.xR + 22" :y="v.pitch + 4" class="ann">⌀dm {{ f(v.g.dm) }}</text>
      <text :x="v.xR + 22" :y="v.pitch + 20" class="ann">α {{ f(v.g.alpha_deg, 1) }}°</text>
      <text :x="v.xR + 22" :y="v.pitch + 36" class="ann">Dw {{ f(v.g.Dw, 2) }}</text>
      <text :x="v.xR + 22" :y="v.pitch + 52" class="ann">Lw {{ f(v.g.Lw, 2) }}</text>
    </svg>
  </figure>
</template>

<style scoped>
.ghost { opacity: .45; stroke-dasharray: 3 2; }
</style>
