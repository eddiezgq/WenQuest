<script setup>
// The flexible bearing of a harmonic reducer (plan section 十八): the rings as bent by the cam and the balls
// (radial deformation exaggerated), the ball loads and the meshing zones; the bending stress round the raceways.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const f = computed(() => props.r?.flex)

const S = 300, C = S / 2
const shape = computed(() => {
  const x = f.value, g = props.r?.geometry
  if (!x || !g) return null
  const ri = (g.dm - g.Dw) / 2, ro = (g.dm + g.Dw) / 2
  const dev = Math.max(...x.w_cam.map(Math.abs), ...x.u_outer.map(Math.abs), 1e-9) / 1000  // mm
  const k = Math.max(1, Math.round((0.12 * ro) / dev))  // radial exaggeration
  const reach = ro + k * dev + (x.F ? 3.6 * g.Dw : g.Dw)  // the farthest thing drawn: the zone arrows
  const s = (C - 14) / reach
  const P = (rad, deg) => { const a = (deg * Math.PI) / 180; return [C + rad * s * Math.cos(a), C - rad * s * Math.sin(a)] }
  const ring = (r0, dev_um) => x.theta_deg.map((d, i) => P(r0 + (k * dev_um[i]) / 1000, d).map((v) => v.toFixed(1)).join(',')).join(' ')
  const at = (deg, arr) => { const i = Math.round(((deg % 360) + 360) % 360 / (360 / arr.length)) % arr.length; return arr[i] / 1000 }
  const Qm = Math.max(...x.balls.Q, 1e-9)
  const balls = x.balls.phi_deg.map((d, j) => {
    const rc = (ri + ro) / 2 + (k * (at(d, x.w_cam) + at(d, x.u_outer))) / 2
    const [cx, cy] = P(rc, d)
    return { cx, cy, q: x.balls.Q[j], on: x.balls.Q[j] > 0, o: 0.25 + 0.75 * (x.balls.Q[j] / Qm), max: x.balls.Q[j] === Qm }
  })
  const zones = x.F && x.beta_deg ? [0, 180].map((c) => {
    const a0 = c - x.beta_deg, a1 = c + x.beta_deg, rr = ro + (k * at(c, x.u_outer)) + g.Dw * 1.6
    const [x0, y0] = P(rr, a0), [x1, y1] = P(rr, a1)
    const [ax, ay] = P(rr + g.Dw * 1.8, c), [bx, by] = P(rr + g.Dw * 0.3, c)
    return { d: `M${x0},${y0} A${rr * s},${rr * s} 0 0 0 ${x1},${y1}`, ax, ay, bx, by }
  }) : []
  const qmax = balls.find((b) => b.max)
  return { k, inner: ring(ri, x.w_cam), outer: ring(ro, x.u_outer), ri: ri * s, ro: ro * s, balls, br: Math.max(2.5, (g.Dw / 2) * s * 0.9), zones, qmax, Qm }
})

const W = 420, H = 230, PL = 46, PR = 12, PT = 14, PB = 30
const chart = computed(() => {
  const x = f.value
  if (!x) return null
  const all = [...x.sig_i, ...x.sig_o]
  let lo = Math.min(...all, 0), hi = Math.max(...all, 0)
  const pad = (hi - lo) * 0.08 || 1
  lo -= pad; hi += pad
  const X = (d) => PL + (d / 360) * (W - PL - PR)
  const Y = (v) => PT + (1 - (v - lo) / (hi - lo)) * (H - PT - PB)
  const line = (arr) => x.theta_deg.map((d, i) => `${X(d).toFixed(1)},${Y(arr[i]).toFixed(1)}`).join(' ')
  const step = Math.pow(10, Math.floor(Math.log10((hi - lo) / 4)))
  const ticks = []
  for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) if ((hi - lo) / step < 12 || Math.round(v / step) % 2 === 0) ticks.push({ v, y: Y(v) })
  return { i: line(x.sig_i), o: line(x.sig_o), zero: Y(0), ticks, X, xt: [0, 90, 180, 270, 360] }
})
const amp = computed(() => f.value && t('flexAmp').replace('{a}', f.value.sig_o_amp.toFixed(0)).replace('{m}', f.value.sig_o_mean.toFixed(0)))
</script>

<template>
  <div v-if="shape && chart" class="flexview">
    <figure>
      <figcaption>{{ t('flexShape') }} <small>{{ t('flexScale').replace('{k}', shape.k) }}</small></figcaption>
      <svg :viewBox="`0 0 ${S} ${S}`" role="img" :aria-label="t('flexShape')">
        <circle :cx="C" :cy="C" :r="shape.ri" class="ghost" /><circle :cx="C" :cy="C" :r="shape.ro" class="ghost" />
        <line :x1="8" :x2="S - 8" :y1="C" :y2="C" class="axis" />
        <polygon :points="shape.outer" class="race o" /><polygon :points="shape.inner" class="race i" />
        <g v-for="(z, j) in shape.zones" :key="j" class="zone">
          <path :d="z.d" /><line :x1="z.ax" :y1="z.ay" :x2="z.bx" :y2="z.by" marker-end="url(#fv-arrow)" />
        </g>
        <circle v-for="(b, j) in shape.balls" :key="j" :cx="b.cx" :cy="b.cy" :r="shape.br" :class="b.on ? 'ball on' : 'ball'" :style="b.on ? { opacity: b.o } : {}" />
        <defs><marker id="fv-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L8,4 L0,8 z" /></marker></defs>
      </svg>
      <p class="legend"><span class="sw i"></span>{{ t('innerRing') }} <span class="sw o"></span>{{ t('outerRing') }} <span class="sw b"></span>{{ t('flexBalls') }}（max {{ shape.Qm.toFixed(0) }} N）<template v-if="shape.zones.length"> <span class="sw z"></span>{{ t('flexZone') }}</template></p>
    </figure>
    <figure>
      <figcaption>{{ t('flexStress') }} <small>MPa</small></figcaption>
      <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('flexStress')">
        <g v-for="tk in chart.ticks" :key="tk.v"><line :x1="PL" :x2="W - PR" :y1="tk.y" :y2="tk.y" class="grid" /><text :x="PL - 4" :y="tk.y + 3" class="ann" text-anchor="end">{{ tk.v.toFixed(0) }}</text></g>
        <line :x1="PL" :x2="W - PR" :y1="chart.zero" :y2="chart.zero" class="axis" />
        <g v-for="d in chart.xt" :key="d"><text :x="chart.X(d)" :y="H - PB + 14" class="ann" text-anchor="middle">{{ d }}°</text></g>
        <text :x="(W + PL) / 2" :y="H - 3" class="ann" text-anchor="middle">{{ t('flexAngle') }}</text>
        <polyline :points="chart.i" class="ln i" /><polyline :points="chart.o" class="ln o" />
      </svg>
      <p class="legend"><span class="sw i"></span>{{ t('flexInner') }} <span class="sw o"></span>{{ t('flexOuter') }}</p>
      <p class="legend mono">{{ amp }}</p>
    </figure>
  </div>
</template>

<style scoped>
.flexview { display: grid; grid-template-columns: minmax(0, 300px) minmax(0, 1fr); gap: 16px; align-items: start; }
figure { margin: 0; min-width: 0; }
figcaption { font: 600 13px var(--serif-zh); margin-bottom: 4px; }
figcaption small { font: 400 12px var(--body); color: var(--muted); margin-left: 6px; }
svg { width: 100%; height: auto; display: block; }
.ghost { fill: none; stroke: var(--line); stroke-dasharray: 3 3; }
.axis { stroke: var(--muted); stroke-width: .6; stroke-dasharray: 6 3 1 3; }
.grid { stroke: var(--line); stroke-width: .5; }
.race { fill: none; stroke-width: 2; }
.race.i, .ln.i { stroke: #2f6f8f; }
.race.o, .ln.o { stroke: #b0632a; }
.ln { fill: none; stroke-width: 1.6; }
.ball { fill: var(--surface); stroke: var(--muted); stroke-width: .8; }
.ball.on { fill: #d8a400; stroke: #8a6a00; }
.zone path { fill: none; stroke: #7a3d8f; stroke-width: 3; }
.zone line { stroke: #7a3d8f; stroke-width: 1.4; }
marker path { fill: #7a3d8f; }
.ann { font: 10px var(--mono); fill: var(--muted); }
.legend { font-size: 12px; color: var(--muted); margin: 4px 0 0; display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: center; }
.sw { display: inline-block; width: 14px; height: 3px; margin-right: 4px; vertical-align: middle; }
.sw.i { background: #2f6f8f; } .sw.o { background: #b0632a; } .sw.b { background: #d8a400; height: 8px; width: 8px; border-radius: 50%; } .sw.z { background: #7a3d8f; }
@media (max-width: 760px) { .flexview { grid-template-columns: minmax(0, 1fr); } }
</style>
