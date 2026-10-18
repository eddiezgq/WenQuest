<script setup>
// The cam on the machine (round 39, step 3). Grinding X–C: the cam turns by C and the wheel moves along X.
// Milling XY: the cam is fixed and the end mill runs along the tool centre path. Marks the largest over- and undercut
// found by the program simulation.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ res: Object, theta: Number })
const pts = (xy) => xy[0].map((x, i) => [x, xy[1][i]])
const path = (p, close = true) => (p.length ? 'M' + p.map((q) => q[0].toFixed(3) + ',' + q[1].toFixed(3)).join('L') + (close ? 'Z' : '') : '')
const surfaces = computed(() => (props.res?.surfaces || []).map((s) => ({ ...s, p: pts(s.xy) })))
const tools = computed(() => (props.res?.paths || []).map((p) => ({ ...p, p: pts(p.tool) })))
const R = computed(() => Math.max(1, ...surfaces.value.flatMap((s) => s.p.map((q) => Math.hypot(q[0], q[1])))))
const grind = computed(() => props.res?.process === 'grind')
const r = computed(() => props.res?.tool_r || 0)
const C = computed(() => props.theta % 360)

function xAt(xc, c) {   // X at cam angle C from the program points (linear in C, as the machine does)
  const [X, Cs] = xc
  let i = Cs.findIndex((v) => v >= c)
  if (i <= 0) return X[0]
  const f = (c - Cs[i - 1]) / (Cs[i] - Cs[i - 1])
  return X[i - 1] + f * (X[i] - X[i - 1])
}
const wheels = computed(() => (grind.value ? tools.value.filter((p) => p.xc).map((p) => ({ x: xAt(p.xc, C.value), y: 0 })) : []))
const mills = computed(() => {
  if (grind.value) return []
  return tools.value.map((p) => { const i = Math.floor((C.value / 360) * p.p.length) % p.p.length; return { x: p.p[i][0], y: p.p[i][1] } })
})
function onSurface(deg, name) {    // the design point at a polar angle (degrees), for the deviation marks
  const s = surfaces.value.find((x) => x.name === name) || surfaces.value[0]
  if (!s || deg == null) return null
  let best = null, bd = 1e9
  for (const q of s.p) {
    const a = ((Math.atan2(q[1], q[0]) * 180) / Math.PI + 360) % 360, d = Math.min(Math.abs(a - deg), 360 - Math.abs(a - deg))
    if (d < bd) { bd = d; best = q }
  }
  return best
}
const marks = computed(() => {
  const sim = props.res?.sim
  if (!sim) return []
  const out = []
  const o = sim.over, u = sim.under
  if (o && o[1] != null) out.push({ p: onSurface(o[1], o[2]), cls: 'over', v: o[0] })
  if (u && u[1] != null) out.push({ p: onSurface(u[1], u[2]), cls: 'under', v: u[0] })
  return out.filter((m) => m.p)
})
const rot = computed(() => (grind.value ? C.value : 0))   // the cam turns by C on the grinder
const view = computed(() => {
  const k = R.value * 1.25
  if (grind.value) { const x1 = Math.max(k, ...wheels.value.map((w) => w.x + Math.min(r.value, 0.5 * R.value))); return { x0: -k, y0: -k, w: x1 + k, h: 2 * k } }
  return { x0: -k, y0: -k, w: 2 * k, h: 2 * k }
})
const sw = computed(() => R.value / 170)
</script>

<template>
  <div class="mv">
    <svg v-if="res" :viewBox="`${view.x0} ${-view.y0 - view.h} ${view.w} ${view.h}`" role="img" :aria-label="t('modeMfg')">
      <g transform="scale(1,-1)" :style="`--sw:${sw}`">
        <g :transform="`rotate(${rot})`">
          <path v-for="s in surfaces" :key="s.name" :d="path(s.p)" class="design" />
          <path v-for="p in tools" :key="'t' + p.name" :d="path(p.p)" class="tool" />
          <circle v-for="(m, i) in marks" :key="'m' + i" :cx="m.p[0]" :cy="m.p[1]" :r="R * 0.025" :class="['mark', m.cls]" />
          <circle :r="R * 0.02" class="hub" />
        </g>
        <circle v-for="(w, i) in wheels" :key="'w' + i" :cx="w.x" :cy="w.y" :r="r" class="cutter" />
        <line v-for="(w, i) in wheels" :key="'x' + i" :x1="0" :y1="0" :x2="w.x" :y2="0" class="xaxis" />
        <circle v-for="(m, i) in mills" :key="'c' + i" :cx="m.x" :cy="m.y" :r="r" class="cutter" />
      </g>
    </svg>
    <p class="leg"><i class="l-design" /> {{ t('design') }} · <i class="l-tool" /> {{ t('toolPath') }}
      <template v-if="marks.length"> · <i class="l-over" /> {{ t('maxOver') }} · <i class="l-under" /> {{ t('maxUnder') }}</template>
      <span v-if="grind" class="mono"> · C {{ C.toFixed(1) }}°<template v-if="wheels.length"> · X {{ wheels[0].x.toFixed(3) }}</template></span>
    </p>
  </div>
</template>

<style scoped>
.mv { position: relative; height: 100%; min-height: 220px; display: grid; grid-template-rows: 1fr auto; }
svg { width: 100%; height: 100%; min-height: 220px; }
.design { fill: var(--cam); fill-opacity: .55; stroke: var(--ink); stroke-width: var(--sw); }
.tool { fill: none; stroke: var(--blue); stroke-width: var(--sw); stroke-dasharray: calc(var(--sw) * 5) calc(var(--sw) * 3); }
.cutter { fill: var(--steel); fill-opacity: .5; stroke: var(--steel-2); stroke-width: var(--sw); }
.xaxis { stroke: var(--muted); stroke-width: calc(var(--sw) * .6); stroke-dasharray: calc(var(--sw) * 2) calc(var(--sw) * 3); }
.hub { fill: var(--ink); }
.mark.over { fill: var(--bad); } .mark.under { fill: var(--ok); }
.leg { margin: 0; padding: 4px 10px; font-size: 11.5px; color: var(--muted); }
.leg i { display: inline-block; width: 14px; height: 0; border-top: 2px solid; vertical-align: middle; margin-right: 3px; }
.l-design { border-color: var(--ink); } .l-tool { border-color: var(--blue); border-top-style: dashed !important; }
.l-over { border-color: var(--bad); } .l-under { border-color: var(--ok); }
</style>
