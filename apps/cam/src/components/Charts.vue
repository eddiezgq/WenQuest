<script setup>
// Curves over one turn, each with the current cam angle; click or drag on a chart to move the cam (round 39).
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ result: Object, theta: Number, print: Boolean })
const emit = defineEmits(['update:theta'])
const W = 300, H = 120, P = { l: 44, r: 8, t: 10, b: 18 }

const charts = computed(() => {
  const r = props.result
  if (!r) return []
  const c = r.curves, rad = r.unit === 'rad', d = (a) => (rad ? a.map((x) => (x * 180) / Math.PI) : a)
  const u = rad ? '°' : 'mm'
  const out = [
    { key: 's', y: d(c.s), unit: u },
    { key: 'v', y: d(c.v), unit: `${u}/rad` },
    { key: 'acc', y: d(c.a), unit: `${u}/rad²` },
    { key: 'j', y: d(c.j), unit: `${u}/rad³` },
    { key: 'phi', y: c.phi_deg.map(Math.abs), unit: '°' },
    { key: 'rho', y: c.rho_profile, unit: 'mm', clip: true },
  ]
  if (c.vel) out.splice(4, 0, { key: 'vel', y: c.vel, unit: rad ? 'rad/s' : 'm/s' }, { key: 'accel', y: c.acc, unit: rad ? 'rad/s²' : 'm/s²' })
  if (c.force) out.push({ key: 'force', y: c.force, unit: rad ? 'N·mm' : 'N', zero: true }, { key: 'torqueC', y: c.torque_Nm, unit: 'N·m' })
  return out.map((ch) => {
    let ys = ch.y.map((v) => (v == null ? NaN : v))
    if (ch.clip) {                       // radius of curvature: very flat parts would squash the plot
      const sorted = ys.filter(Number.isFinite).map(Math.abs).sort((a, b) => a - b)
      const cap = sorted[Math.floor(sorted.length * 0.9)] * 1.5 || 1
      ys = ys.map((v) => Math.max(-cap, Math.min(cap, v)))
    }
    const fin = ys.filter(Number.isFinite)
    let lo = Math.min(0, ...fin), hi = Math.max(0, ...fin)
    if (hi - lo < 1e-12) { hi += 1; lo -= 1 }
    const X = (i) => P.l + (i / (ys.length - 1)) * (W - P.l - P.r), Y = (v) => P.t + (1 - (v - lo) / (hi - lo)) * (H - P.t - P.b)
    const pts = ys.map((v, i) => (Number.isFinite(v) ? `${X(i).toFixed(1)},${Y(v).toFixed(1)}` : null)).filter(Boolean)
    return { ...ch, line: 'M' + pts.join('L'), zeroY: Y(0), lo, hi, Y, X, ys, n: ys.length }
  })
})
const fmt = (v) => (Math.abs(v) >= 1000 || (Math.abs(v) < 0.01 && v !== 0) ? v.toExponential(2) : +v.toPrecision(4))
function pick(e, ch) {
  if (props.print) return
  const svg = e.currentTarget, b = svg.getBoundingClientRect(), x = ((e.clientX - b.left) / b.width) * W
  const f = (x - P.l) / (W - P.l - P.r)
  if (f >= 0 && f <= 1) emit('update:theta', f * 360 * (ch.n / 360) >= 360 ? 359.9 : f * 360)
}
const valAt = (ch) => ch.ys[Math.round(props.theta) % ch.n]
</script>

<template>
  <div class="charts" :class="{ print }">
    <figure v-for="ch in charts" :key="ch.key">
      <figcaption><b>{{ t(ch.key) }}</b> <span class="u">{{ ch.unit }}</span><span v-if="!print" class="v mono">{{ Number.isFinite(valAt(ch)) ? fmt(valAt(ch)) : '—' }}</span></figcaption>
      <svg :viewBox="`0 0 ${W} ${H}`" @pointerdown="pick($event, ch)" @pointermove="$event.buttons && pick($event, ch)">
        <line :x1="P.l" :x2="W - P.r" :y1="ch.zeroY" :y2="ch.zeroY" class="zero" />
        <text :x="P.l - 4" :y="P.t + 4" class="ax" text-anchor="end">{{ fmt(ch.hi) }}</text>
        <text :x="P.l - 4" :y="H - P.b" class="ax" text-anchor="end">{{ fmt(ch.lo) }}</text>
        <text v-for="d in [0, 90, 180, 270, 360]" :key="d" :x="P.l + (d / 360) * (W - P.l - P.r)" :y="H - 4" class="ax" text-anchor="middle">{{ d }}</text>
        <path :d="ch.line" class="ln" />
        <line v-if="!print" :x1="P.l + (theta / 360) * (W - P.l - P.r)" :x2="P.l + (theta / 360) * (W - P.l - P.r)" :y1="P.t" :y2="H - P.b" class="cur" />
      </svg>
    </figure>
  </div>
</template>

<style scoped>
.charts { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; }
.charts.print { grid-template-columns: repeat(2, 1fr); }
figure { margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 6px 8px 2px; }
figcaption { font-size: 12.5px; display: flex; gap: 6px; align-items: baseline; }
figcaption .u { color: var(--muted); font: 400 11px/1 var(--mono); }
figcaption .v { margin-left: auto; color: var(--ink); font-size: 12px; }
svg { width: 100%; height: auto; display: block; touch-action: none; cursor: crosshair; }
.zero { stroke: var(--line); }
.ln { fill: none; stroke: var(--ink); stroke-width: 1.4; }
.cur { stroke: var(--accent); stroke-width: 1.2; }
.ax { font: 9px var(--mono); fill: var(--muted); }
</style>
