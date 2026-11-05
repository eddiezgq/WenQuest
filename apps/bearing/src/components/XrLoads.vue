<script setup>
// Crossed roller bearing (plan section 十九): the load of every roller round the bearing, the two sets apart, and the
// contact stress along the heaviest roller.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const x = computed(() => props.r?.crossed)
const S = 260, C = S / 2, R0 = 78, RM = 44
const ring = computed(() => {
  const c = x.value
  if (!c) return null
  const qm = Math.max(...c.Q, 1e-9)
  return c.psi_deg.map((d, j) => {
    const a = (d * Math.PI) / 180, L = (c.Q[j] / qm) * RM
    const out = c.facing[j] > 0 ? 1 : -1
    return { x1: C + R0 * Math.cos(a), y1: C - R0 * Math.sin(a), x2: C + (R0 + out * L) * Math.cos(a), y2: C - (R0 + out * L) * Math.sin(a), plus: out > 0, on: c.Q[j] > 0 }
  })
})
const W = 360, H = 170, PL = 44, PR = 10, PT = 12, PB = 26
const along = computed(() => {
  const c = x.value
  if (!c) return null
  const s0 = Math.min(...c.s), s1 = Math.max(...c.s)
  const hi = Math.max(...c.p_i, ...c.p_o, 1)
  const X = (s) => PL + ((s - s0) / (s1 - s0 || 1)) * (W - PL - PR), Y = (p) => PT + (1 - p / hi) * (H - PT - PB)
  const line = (arr) => c.s.map((s, k) => `${X(s).toFixed(1)},${Y(arr[k]).toFixed(1)}`).join(' ')
  return { i: line(c.p_i), o: line(c.p_o), hi, y0: Y(0), yh: Y(hi), s0, s1, X }
})
const qmax = computed(() => (x.value ? Math.max(...x.value.Q) : 0))
</script>

<template>
  <div v-if="ring && along" class="xr">
    <figure>
      <figcaption>{{ t('xrLoads') }} <small>max {{ qmax.toFixed(0) }} N</small></figcaption>
      <svg :viewBox="`0 0 ${S} ${S}`" role="img" :aria-label="t('xrLoads')">
        <circle :cx="C" :cy="C" :r="R0" class="base" />
        <line v-for="(l, j) in ring" :key="j" :x1="l.x1" :y1="l.y1" :x2="l.x2" :y2="l.y2" :class="['bar', l.plus ? 'p' : 'm', { off: !l.on }]" />
        <text :x="C" :y="C - 4" class="ann" text-anchor="middle">Fa {{ x.Fa_plus.toFixed(0) }} / {{ x.Fa_minus.toFixed(0) }} N</text>
        <text :x="C" :y="C + 12" class="ann" text-anchor="middle">{{ t('xrFa') }}</text>
      </svg>
      <p class="legend"><span class="sw p"></span>{{ t('xrPlus') }}（{{ t('outerRing') }}↗） <span class="sw m"></span>{{ t('xrMinus') }}（↙）</p>
    </figure>
    <figure>
      <figcaption>{{ t('xrAlong') }} <small>MPa</small></figcaption>
      <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('xrAlong')">
        <line :x1="PL" :x2="W - PR" :y1="along.y0" :y2="along.y0" class="axis" />
        <text :x="PL - 4" :y="along.yh + 4" class="ann" text-anchor="end">{{ along.hi.toFixed(0) }}</text>
        <text :x="PL - 4" :y="along.y0" class="ann" text-anchor="end">0</text>
        <text :x="along.X(along.s0)" :y="H - 8" class="ann">{{ along.s0.toFixed(2) }}</text>
        <text :x="along.X(along.s1)" :y="H - 8" class="ann" text-anchor="end">{{ along.s1.toFixed(2) }} mm</text>
        <polyline :points="along.i" class="ln i" /><polyline :points="along.o" class="ln o" />
      </svg>
      <p class="legend"><span class="sw i"></span>{{ t('innerRing') }} <span class="sw o"></span>{{ t('outerRing') }}</p>
    </figure>
  </div>
</template>

<style scoped>
.xr { display: grid; grid-template-columns: minmax(0, 260px) minmax(0, 1fr); gap: 16px; align-items: start; margin-top: 8px; }
figure { margin: 0; min-width: 0; }
figcaption { font: 600 13px var(--serif-zh); margin-bottom: 4px; }
figcaption small { font: 400 12px var(--body); color: var(--muted); margin-left: 6px; }
svg { width: 100%; height: auto; display: block; }
.base { fill: none; stroke: var(--line); }
.bar { stroke-width: 3; stroke-linecap: round; }
.bar.p { stroke: #b0632a; } .bar.m { stroke: #2f6f8f; } .bar.off { opacity: .25; }
.axis { stroke: var(--muted); stroke-width: .6; }
.ln { fill: none; stroke-width: 1.6; } .ln.i { stroke: #2f6f8f; } .ln.o { stroke: #b0632a; }
.ann { font: 10px var(--mono); fill: var(--muted); }
.legend { font-size: 12px; color: var(--muted); margin: 4px 0 0; display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: center; }
.sw { display: inline-block; width: 14px; height: 3px; margin-right: 4px; vertical-align: middle; }
.sw.p, .sw.o { background: #b0632a; } .sw.m, .sw.i { background: #2f6f8f; }
@media (max-width: 760px) { .xr { grid-template-columns: minmax(0, 1fr); } }
</style>
