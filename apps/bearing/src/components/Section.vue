<script setup>
// Half section through the axis (upper half): rings hatched as in a drawing, the ball, the contact line at the
// heaviest ball's operating angle and its contact ellipse arcs. Built from the kernel's geometry, never guessed.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const W = 460, H = 400, PAD = 54, PADL = 78, PADR = 104

const v = computed(() => {
  const g = props.r?.geometry
  if (!g) return null
  const { d, D, B, dm, Dw, fi, fo } = g
  const ri = fi * Dw, ro = fo * Dw
  const a0 = (g.type === 'angular' ? g.alpha0_deg : 0) * Math.PI / 180
  const n0 = [Math.sin(a0), Math.cos(a0)]
  const bc = [0, dm / 2]
  const ci = [bc[0] + (ri - Dw / 2) * n0[0], bc[1] + (ri - Dw / 2) * n0[1]]
  const co = g.type === 'angular'
    ? [bc[0] - (ro - Dw / 2) * n0[0], bc[1] - (ro - Dw / 2) * n0[1]]
    : [0, g.do / 2 - ro]
  const botI = ci[1] - ri, botO = co[1] + ro
  const hI = g.h_i ?? Math.min(0.2 * Dw, ri * 0.9), hO = g.h_o ?? Math.min(0.2 * Dw, ro * 0.9)  // drawing only when not given
  const rsI = Math.min(botI + hI, ci[1] - 1e-6), rsO = Math.max(botO - hO, co[1] + 1e-6)
  // scale: the ring section from the bore to the outside, the width across
  const s = Math.min((W - PADL - PADR) / B, (H - 2 * PAD) / ((D - d) / 2))
  const ox = PADL + (W - PADL - PADR) / 2, oy = H / 2 + ((D + d) / 4) * s
  const X = (x) => ox + x * s, Y = (r) => oy - r * s
  const half = (c, rad, rs) => Math.sqrt(Math.max(rad * rad - (rs - c[1]) ** 2, 0))
  const wI = half(ci, ri, rsI), wO = half(co, ro, rsO)
  const xl = (x) => Math.max(x, -B / 2), xr = (x) => Math.min(x, B / 2)
  const inner = `M${X(-B / 2)},${Y(d / 2)} L${X(-B / 2)},${Y(rsI)} L${X(xl(ci[0] - wI))},${Y(rsI)} ` +
    `A${ri * s},${ri * s} 0 0 0 ${X(xr(ci[0] + wI))},${Y(rsI)} L${X(B / 2)},${Y(rsI)} L${X(B / 2)},${Y(d / 2)} Z`
  const outer = `M${X(-B / 2)},${Y(D / 2)} L${X(-B / 2)},${Y(rsO)} L${X(xl(co[0] - wO))},${Y(rsO)} ` +
    `A${ro * s},${ro * s} 0 0 1 ${X(xr(co[0] + wO))},${Y(rsO)} L${X(B / 2)},${Y(rsO)} L${X(B / 2)},${Y(D / 2)} Z`
  // the contact line at the heaviest ball (loaded angle), else the free angle
  const c = props.r.contact || {}
  const al = ((c.inner?.alpha_deg ?? g.alpha_op_deg ?? g.alpha0_deg) || 0) * Math.PI / 180
  const n = [Math.sin(al), Math.cos(al)], L = Dw / 2 + 0.35 * Dw
  const line = [X(bc[0] - L * n[0]), Y(bc[1] - L * n[1]), X(bc[0] + L * n[0]), Y(bc[1] + L * n[1])]
  const arc = (sign, a) => {  // the contact ellipse's long axis as an arc on the ball
    if (!a) return null
    const th = a / (Dw / 2), R = Dw / 2
    const p = (k) => { const ang = Math.atan2(sign * n[0], sign * n[1]) + k * th; return [X(bc[0] + R * Math.sin(ang)), Y(bc[1] + R * Math.cos(ang))] }
    const [x1, y1] = p(-1), [x2, y2] = p(1)
    return `M${x1},${y1} A${R * s},${R * s} 0 0 ${sign > 0 ? 1 : 0} ${x2},${y2}`
  }
  return {
    inner, outer, ball: { cx: X(bc[0]), cy: Y(bc[1]), r: (Dw / 2) * s }, line,
    arcO: arc(1, c.outer?.a), arcI: arc(-1, c.inner?.a),
    pitch: Y(dm / 2), xL: X(-B / 2), xR: X(B / 2), yD: Y(D / 2), yd: Y(d / 2),
    alDeg: al * 180 / Math.PI, g, guessedShoulder: g.h_i == null || g.h_o == null,
    lab: { x: X(bc[0] + L * n[0]) + 6, y: Y(bc[1] + L * n[1]) },
  }
})
const f = (x, k = 1) => (x == null ? '—' : Number(x).toFixed(k))
</script>

<template>
  <figure class="sect">
    <figcaption>{{ t('section') }}</figcaption>
    <svg v-if="v" :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('section')">
      <defs>
        <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="7" class="hatch" />
        </pattern>
      </defs>
      <path :d="v.outer" class="ring" /><path :d="v.outer" fill="url(#hatch)" />
      <path :d="v.inner" class="ring" /><path :d="v.inner" fill="url(#hatch)" />
      <line :x1="v.xL - 18" :x2="v.xR + 18" :y1="v.pitch" :y2="v.pitch" class="centre" />
      <circle :cx="v.ball.cx" :cy="v.ball.cy" :r="v.ball.r" class="ball" />
      <line :x1="v.line[0]" :y1="v.line[1]" :x2="v.line[2]" :y2="v.line[3]" class="contact" />
      <path v-if="v.arcO" :d="v.arcO" class="ellipse" /><path v-if="v.arcI" :d="v.arcI" class="ellipse" />
      <text :x="v.lab.x" :y="v.lab.y" class="ann">α = {{ f(v.alDeg) }}°</text>
      <!-- dimensions -->
      <line :x1="v.xL" :x2="v.xR" :y1="v.yD - 22" :y2="v.yD - 22" class="dim" />
      <text :x="(v.xL + v.xR) / 2" :y="v.yD - 28" class="ann mid">B {{ f(v.g.B) }}</text>
      <text :x="v.xL - 10" :y="v.yD + 4" class="ann end">⌀D {{ f(v.g.D) }}</text>
      <text :x="v.xL - 10" :y="v.yd + 4" class="ann end">⌀d {{ f(v.g.d) }}</text>
      <text :x="v.xR + 22" :y="v.pitch + 4" class="ann">⌀dm {{ f(v.g.dm) }}</text>
      <text :x="v.xR + 10" :y="v.ball.cy - v.ball.r - 6" class="ann">⌀Dw {{ f(v.g.Dw, 2) }}</text>
    </svg>
    <p v-if="v?.guessedShoulder" class="cap-note">{{ t('h_i') }} / {{ t('h_o') }}: {{ t('unknown') }}</p>
  </figure>
</template>
