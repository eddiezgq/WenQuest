<script setup>
// Harmonic amplitudes by order, grouped (1st, low, high), with the remaining amplitudes after compensation.
import { computed } from 'vue'

const props = defineProps({ title: String, unit: String, A: Array, after: Array, lowHi: Number, sel: Array, legend: Array })
const W = 640, H = 150, P = { l: 46, r: 8, t: 10, b: 20 }
const fmt = (v) => (Math.abs(v) >= 100 ? v.toFixed(0) : +v.toPrecision(3))
const g = computed(() => {
  const n = props.A.length, hi = Math.max(1e-9, ...props.A, ...(props.after || [])) * 1.08
  const bw = (W - P.l - P.r) / n
  const Y = (v) => P.t + (1 - v / hi) * (H - P.t - P.b)
  const grp = (k) => (k === 1 ? 'g1' : k <= props.lowHi ? 'g2' : 'g3')
  const bars = props.A.map((a, i) => {
    const k = i + 1, x = P.l + i * bw
    const chosen = props.sel && k >= props.sel[0] && k <= props.sel[1]
    return { k, x, w: Math.max(1, bw * 0.72), y: Y(a), h: H - P.b - Y(a), cls: grp(k) + (chosen ? ' sel' : ''),
      ay: props.after ? Y(props.after[i]) : null }
  })
  const ticks = [1, 5, 10, 20, 30, 40, 50, 60, 80, 100].filter((k) => k <= n)
  return { hi, bars, bw, ticks, Y }
})
</script>

<template>
  <figure class="bc">
    <figcaption><b>{{ title }}</b> <span class="u">{{ unit }}</span>
      <span class="legend"><span v-for="l in legend" :key="l[0]" :class="['k', l[0]]">{{ l[1] }}</span></span>
    </figcaption>
    <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="title">
      <text :x="P.l - 4" :y="P.t + 4" class="ax" text-anchor="end">{{ fmt(g.hi) }}</text>
      <text :x="P.l - 4" :y="H - P.b" class="ax" text-anchor="end">0</text>
      <line :x1="P.l" :x2="W - P.r" :y1="H - P.b" :y2="H - P.b" class="zero" />
      <g v-for="b in g.bars" :key="b.k">
        <rect :x="b.x" :y="b.y" :width="b.w" :height="Math.max(0, b.h)" :class="b.cls"><title>{{ b.k }}: {{ fmt(A[b.k - 1]) }} {{ unit }}</title></rect>
        <line v-if="b.ay != null" :x1="b.x - 0.5" :x2="b.x + b.w + 0.5" :y1="b.ay" :y2="b.ay" class="after" />
      </g>
      <text v-for="k in g.ticks" :key="k" :x="P.l + (k - 1) * g.bw + g.bw * 0.36" :y="H - 6" class="ax" text-anchor="middle">{{ k }}</text>
    </svg>
  </figure>
</template>

<style scoped>
.bc { margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 6px 8px 4px; }
figcaption { font-size: 12.5px; display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; }
.u { color: var(--muted); font: 400 11px/1 var(--mono); }
.legend { margin-left: auto; display: flex; gap: 10px; font-size: 11.5px; color: var(--muted); flex-wrap: wrap; }
.legend .k::before { content: ''; display: inline-block; width: 10px; height: 10px; vertical-align: -1px; margin-right: 4px; border-radius: 2px; }
.legend .g1::before { background: var(--bad); }
.legend .g2::before { background: var(--accent); }
.legend .g3::before { background: var(--blue); }
.legend .after::before { height: 0; border-top: 2px solid var(--ink); border-radius: 0; }
svg { width: 100%; height: auto; display: block; }
rect.g1 { fill: var(--bad); } rect.g2 { fill: var(--accent); } rect.g3 { fill: var(--blue); }
rect { opacity: .55; } rect.sel { opacity: 1; }
.after { stroke: var(--ink); stroke-width: 1.6; }
.zero { stroke: var(--line); }
.ax { font: 9px var(--mono); fill: var(--muted); }
</style>
