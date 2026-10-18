<script setup>
// A plain line chart over the cam angle (0–360°) with one or more series (round 39, step 3).
import { computed } from 'vue'

const props = defineProps({
  title: String, unit: String, x: Array, series: Array, // [{ y: [], label, cls }]
  cursor: { type: Number, default: null }, note: String, zero: { type: Boolean, default: true }, w: { type: Number, default: 320 },
})
const H = 130, P = { l: 46, r: 8, t: 10, b: 18 }
const fmt = (v) => (!Number.isFinite(v) ? '—' : Math.abs(v) >= 1000 || (Math.abs(v) < 0.01 && v !== 0) ? v.toExponential(2) : +v.toPrecision(4))
const geo = computed(() => {
  const all = props.series.flatMap((s) => s.y.filter(Number.isFinite))
  let lo = Math.min(props.zero ? 0 : Infinity, ...all), hi = Math.max(props.zero ? 0 : -Infinity, ...all)
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) { lo = -1; hi = 1 }
  if (hi - lo < 1e-12) { hi += 1; lo -= 1 }
  const W = props.w
  const X = (d) => P.l + (d / 360) * (W - P.l - P.r)
  const Y = (v) => P.t + (1 - (v - lo) / (hi - lo)) * (H - P.t - P.b)
  const lines = props.series.map((s) => ({
    ...s,
    d: 'M' + s.y.map((v, i) => (Number.isFinite(v) ? `${X(props.x[i]).toFixed(1)},${Y(v).toFixed(1)}` : null)).filter(Boolean).join('L'),
  }))
  return { lo, hi, X, Y, lines, zy: Y(0), W }
})
</script>

<template>
  <figure class="lc">
    <figcaption><b>{{ title }}</b> <span class="u">{{ unit }}</span>
      <span class="legend"><span v-for="s in series.filter((s) => s.label)" :key="s.label" :class="['k', s.cls]">{{ s.label }}</span></span>
    </figcaption>
    <svg :viewBox="`0 0 ${geo.W} ${H}`" role="img" :aria-label="title">
      <line :x1="P.l" :x2="geo.W - P.r" :y1="geo.zy" :y2="geo.zy" class="zero" />
      <text :x="P.l - 4" :y="P.t + 4" class="ax" text-anchor="end">{{ fmt(geo.hi) }}</text>
      <text :x="P.l - 4" :y="H - P.b" class="ax" text-anchor="end">{{ fmt(geo.lo) }}</text>
      <text v-for="d in [0, 90, 180, 270, 360]" :key="d" :x="geo.X(d)" :y="H - 4" class="ax" text-anchor="middle">{{ d }}</text>
      <path v-for="s in geo.lines" :key="s.label || s.cls" :d="s.d" :class="['ln', s.cls]" />
      <line v-if="cursor != null" :x1="geo.X(cursor)" :x2="geo.X(cursor)" :y1="P.t" :y2="H - P.b" class="cur" />
    </svg>
    <p v-if="note" class="nt">{{ note }}</p>
  </figure>
</template>

<style scoped>
.lc { margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 6px 8px 4px; }
figcaption { font-size: 12.5px; display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; }
.u { color: var(--muted); font: 400 11px/1 var(--mono); }
.legend { margin-left: auto; display: flex; gap: 10px; font-size: 11.5px; color: var(--muted); }
.legend .k::before { content: ''; display: inline-block; width: 14px; border-top: 2px solid var(--ink); vertical-align: middle; margin-right: 4px; }
.legend .k.b::before { border-color: var(--blue); }
.legend .k.a::before { border-color: var(--accent); }
.legend .k.r::before { border-color: var(--bad); }
svg { width: 100%; height: auto; display: block; }
.zero { stroke: var(--line); }
.ln { fill: none; stroke: var(--ink); stroke-width: 1.3; }
.ln.b { stroke: var(--blue); }
.ln.a { stroke: var(--accent); }
.ln.r { stroke: var(--bad); }
.cur { stroke: var(--accent); stroke-width: 1.2; }
.ax { font: 9px var(--mono); fill: var(--muted); }
.nt { margin: 2px 0 0; font-size: 11.5px; color: var(--muted); }
</style>
