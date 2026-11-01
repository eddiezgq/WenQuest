<script setup>
// Half section of a tapered roller bearing: cup and cone hatched, the tapered roller on its inclined axis, the cone's
// rib at the large end, and the contact line of the cup. Built from the kernel's geometry.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const W = 460, H = 400, PAD = 54, PADL = 78, PADR = 104

const v = computed(() => {
  const g = props.r?.geometry
  if (!g) return null
  const { d, D, B, dm, Dw, Lw } = g
  const ao = (g.alpha_o_deg * Math.PI) / 180, ai = (g.alpha_i_deg * Math.PI) / 180
  const am = (ao + ai) / 2, ph = (ao - ai) / 2
  const u = [Math.cos(am), Math.sin(am)], n = [-Math.sin(am), Math.cos(am)]
  const c = [0, dm / 2]
  const rad = (s) => Dw / 2 + s * Math.tan(ph)
  const pt = (s, side) => [c[0] + s * u[0] + side * rad(s) * n[0], c[1] + s * u[1] + side * rad(s) * n[1]]
  const s = Math.min((W - PADL - PADR) / B, (H - 2 * PAD) / ((D - d) / 2))
  const ox = PADL + (W - PADL - PADR) / 2, oy = H / 2 + ((D + d) / 4) * s
  const X = (x) => ox + x * s, Y = (r) => oy - r * s
  const P = (p) => `${X(p[0])},${Y(p[1])}`
  const roller = [pt(-Lw / 2, 1), pt(Lw / 2, 1), pt(Lw / 2, -1), pt(-Lw / 2, -1)]
  // raceway lines through the roller's sides
  const cup0 = pt(0, 1), cone0 = pt(0, -1)
  const cupR = (x) => cup0[1] + (x - cup0[0]) * Math.tan(ao)
  const coneR = (x) => cone0[1] + (x - cone0[0]) * Math.tan(ai)
  const cup = [[-B / 2, D / 2], [B / 2, D / 2], [B / 2, cupR(B / 2)], [-B / 2, cupR(-B / 2)]]
  // the cone with its rib at the large end (the rib face square to the roller axis, up to the roller axis)
  const end = pt(Lw / 2, -1), top = [c[0] + (Lw / 2) * u[0], c[1] + (Lw / 2) * u[1]]
  const cone = [[-B / 2, d / 2], [-B / 2, coneR(-B / 2)], end, [top[0], top[1]], [B / 2, top[1]], [B / 2, d / 2]]
  const poly = (ps) => 'M' + ps.map(P).join(' L') + ' Z'
  const L = Dw * 0.9
  const no = [Math.sin(ao), -Math.cos(ao)]
  const line = [X(cup0[0] - L * no[0]), Y(cup0[1] - L * no[1]), X(cup0[0] + 2 * L * no[0]), Y(cup0[1] + 2 * L * no[1])]
  return { cup: poly(cup), cone: poly(cone), roller: poly(roller), line, g, pitch: Y(dm / 2), xL: X(-B / 2), xR: X(B / 2),
    yD: Y(D / 2), yd: Y(d / 2), lab: { x: X(cup0[0] + 2 * L * no[0]) + 6, y: Y(cup0[1] + 2 * L * no[1]) + 4 }, rTop: Y(c[1] + Dw / 2) }
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
      <path :d="v.cup" class="ring" /><path :d="v.cup" fill="url(#hatcht)" />
      <path :d="v.cone" class="ring" /><path :d="v.cone" fill="url(#hatcht)" />
      <path :d="v.roller" class="ball" />
      <line :x1="v.xL - 18" :x2="v.xR + 18" :y1="v.pitch" :y2="v.pitch" class="centre" />
      <line :x1="v.line[0]" :y1="v.line[1]" :x2="v.line[2]" :y2="v.line[3]" class="contact" />
      <text :x="v.lab.x" :y="v.lab.y" class="ann">α = {{ f(v.g.alpha_o_deg) }}°</text>
      <line :x1="v.xL" :x2="v.xR" :y1="v.yD - 22" :y2="v.yD - 22" class="dim" />
      <text :x="(v.xL + v.xR) / 2" :y="v.yD - 28" class="ann mid">B {{ f(v.g.B) }}</text>
      <text :x="v.xL - 10" :y="v.yD + 4" class="ann end">⌀D {{ f(v.g.D) }}</text>
      <text :x="v.xL - 10" :y="v.yd + 4" class="ann end">⌀d {{ f(v.g.d) }}</text>
      <text :x="v.xR + 22" :y="v.pitch + 4" class="ann">⌀dm {{ f(v.g.dm) }}</text>
      <text :x="v.xR + 10" :y="v.rTop - 6" class="ann">Dw {{ f(v.g.Dw, 2) }}</text>
    </svg>
  </figure>
</template>
