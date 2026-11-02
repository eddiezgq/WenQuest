<script setup>
// A control chart: points joined, centre line and control limits, flagged points marked.
import { computed } from 'vue'

const props = defineProps({ c: Object, flags: { type: Array, default: () => [] }, title: String })
const W = 700, H = 190, PL = 20, PR = 120, PT = 10, PB = 24
const v = computed(() => {
  const c = props.c
  if (!c) return null
  const vals = c.points.filter((x) => x != null)
  const lo = Math.min(...vals, c.lcl), hi = Math.max(...vals, c.ucl)
  const pad = (hi - lo) * 0.08 || 1
  const y0 = lo - pad, y1 = hi + pad
  const n = c.points.length
  const X = (i) => PL + (n > 1 ? (i / (n - 1)) * (W - PL - PR) : 0)
  const Y = (y) => PT + (1 - (y - y0) / (y1 - y0)) * (H - PT - PB)
  const pts = c.points.map((y, i) => (y == null ? null : { x: X(i), y: Y(y), bad: props.flags.includes(i) }))
  const path = pts.filter(Boolean).map((p) => `${p.x},${p.y}`).join(' ')
  const fmt = (x) => (Math.abs(x) >= 100 ? x.toFixed(2) : Math.abs(x) >= 1 ? x.toFixed(4) : x.toPrecision(3))
  return { pts: pts.filter(Boolean), path, lines: [['UCL', c.ucl], ['CL', c.cl], ['LCL', c.lcl]].map(([k, y]) => ({ k, y: Y(y), lab: fmt(y) })), n, X }
})
</script>

<template>
  <figure v-if="v" class="curve cc">
    <figcaption>{{ title }}</figcaption>
    <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="title">
      <g v-for="l in v.lines" :key="l.k">
        <line :x1="PL" :x2="W - PR" :y1="l.y" :y2="l.y" :class="l.k === 'CL' ? 'cl' : 'lim'" />
        <text :x="W - PR + 4" :y="l.y + 4" class="ann">{{ l.k }} {{ l.lab }}</text>
      </g>
      <polyline :points="v.path" class="line" />
      <circle v-for="(p, i) in v.pts" :key="i" :cx="p.x" :cy="p.y" :r="p.bad ? 4.5 : 2.6" :class="p.bad ? 'pt bad' : 'pt'" />
      <text :x="PL" :y="H - 6" class="ann">1</text><text :x="W - PR" :y="H - 6" class="ann end">{{ v.n }}</text>
    </svg>
  </figure>
</template>
