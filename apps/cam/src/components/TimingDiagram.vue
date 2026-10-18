<script setup>
// The machine cycle diagram of a cam system: every cam's motion over one camshaft turn on a shared axis, with the
// time it takes underneath; overlaps that break an interlock are marked (round 39, step 4).
import { computed } from 'vue'
import { t, lang } from '../i18n'

const props = defineProps({ res: Object, theta: Number })
const emit = defineEmits(['update:theta'])
const W = 900, rowH = 58, P = { l: 200, r: 14, t: 14, b: 40 }
const rows = computed(() => (props.res?.cams || []).map((c, k) => {
  const lo = Math.min(...c.s), hi = Math.max(...c.s), span = Math.max(hi - lo, 1e-9)
  const y0 = P.t + k * rowH
  const X = (d) => P.l + (d / 360) * (W - P.l - P.r)
  const Y = (v) => y0 + rowH - 10 - ((v - lo) / span) * (rowH - 20)
  const pts = c.s.map((v, i) => `${X(props.res.deg[i]).toFixed(1)},${Y(v).toFixed(1)}`)
  return { ...c, y0, d: 'M' + pts.join('L'), area: `M${X(0)},${y0 + rowH - 10}L` + pts.join('L') + `L${X(360)},${y0 + rowH - 10}Z`,
    bands: c.moving.map(([a, b]) => ({ x: X(a), w: Math.max(1, X(b) - X(a)) })), lo, hi }
}))
const H = computed(() => P.t + rows.value.length * rowH + P.b)
const X = (d) => P.l + (d / 360) * (W - P.l - P.r)
const bad = computed(() => (props.res?.checks || []).filter((c) => c.id.startsWith('lock_') && c.bad?.length).flatMap((c) => c.bad))
// "Arm rotation (globoidal cam)" → the name on one line, the cam kind under it, so long names fit the margin
const split = (nm) => { const s = (lang.value === 'zh' ? nm.zh : nm.en) || '', m = s.match(/^(.*?)\s*[（(](.*)[）)]\s*$/); return m ? [m[1], m[2]] : [s, ''] }
const ticks = [0, 45, 90, 135, 180, 225, 270, 315, 360]
const timeAt = (d) => {
  const r = props.res
  if (!r) return 0
  const i = Math.min(r.deg.length - 1, Math.round((d / 360) * (r.deg.length - 1)))
  return r.t[i]
}
function pick(e) {
  const b = e.currentTarget.getBoundingClientRect(), x = ((e.clientX - b.left) / b.width) * W
  const f = (x - P.l) / (W - P.l - P.r)
  if (f >= 0 && f <= 1) emit('update:theta', Math.min(359.9, f * 360))
}
</script>

<template>
  <figure class="td">
    <figcaption><b>{{ t('timing') }}</b></figcaption>
    <svg v-if="res" :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('timing')" @pointerdown="pick" @pointermove="$event.buttons && pick($event)">
      <rect v-for="(b, i) in bad" :key="'bad' + i" :x="X(b[0])" :y="P.t" :width="Math.max(2, X(b[1]) - X(b[0]))" :height="rows.length * rowH" class="bad" />
      <g v-for="r in rows" :key="r.id">
        <rect v-for="(b, i) in r.bands" :key="i" :x="b.x" :y="r.y0 + 4" :width="b.w" :height="rowH - 14" class="band" />
        <path :d="r.area" class="area" />
        <path :d="r.d" class="ln" />
        <text :x="P.l - 10" :y="r.y0 + rowH / 2 - 8" class="nm" text-anchor="end">{{ split(r.name)[0] }}</text>
        <text v-if="split(r.name)[1]" :x="P.l - 10" :y="r.y0 + rowH / 2 + 6" class="un" text-anchor="end">{{ split(r.name)[1] }}</text>
        <text :x="P.l - 10" :y="r.y0 + rowH / 2 + 20" class="un" text-anchor="end">{{ +r.lo.toFixed(1) }} … {{ +r.hi.toFixed(1) }} {{ r.unit === 'deg' ? '°' : 'mm' }}</text>
        <line :x1="P.l" :x2="W - P.r" :y1="r.y0 + rowH" :y2="r.y0 + rowH" class="sep" />
      </g>
      <g v-for="d in ticks" :key="d">
        <line :x1="X(d)" :x2="X(d)" :y1="P.t" :y2="P.t + rows.length * rowH" class="grid" />
        <text :x="X(d)" :y="P.t + rows.length * rowH + 14" class="ax" text-anchor="middle">{{ d }}°</text>
        <text :x="X(d)" :y="P.t + rows.length * rowH + 28" class="ax t" text-anchor="middle">{{ timeAt(d).toFixed(2) }} s</text>
      </g>
      <line :x1="X(theta)" :x2="X(theta)" :y1="P.t" :y2="P.t + rows.length * rowH" class="cur" />
    </svg>
  </figure>
</template>

<style scoped>
.td { margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; }
figcaption { font-size: 13px; margin-bottom: 4px; }
svg { width: 100%; height: auto; display: block; touch-action: none; cursor: crosshair; }
@media (max-width: 760px) { .td { overflow-x: auto; } svg { min-width: 640px; touch-action: pan-x; } }
.band { fill: var(--accent); opacity: .16; }
.area { fill: var(--blue); opacity: .08; }
.ln { fill: none; stroke: var(--ink); stroke-width: 1.6; }
.bad { fill: var(--bad); opacity: .18; }
.sep { stroke: var(--line); }
.grid { stroke: var(--line); stroke-dasharray: 2 3; }
.cur { stroke: var(--accent); stroke-width: 2; }
.nm { font-size: 12.5px; fill: var(--ink); font-weight: 600; }
.un { font: 10.5px var(--mono); fill: var(--muted); }
.ax { font: 10.5px var(--mono); fill: var(--muted); }
.ax.t { fill: var(--blue); }
</style>
