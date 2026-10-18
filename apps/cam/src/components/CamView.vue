<script setup>
// The cam turning and the follower riding on it, with the contact normal and the pressure angle (round 39).
// Geometry comes from the kernel: the profile in the cam frame, and the follower's position at every degree.
import { computed } from 'vue'
import { t, lang } from '../i18n'

const props = defineProps({ result: Object, theta: Number })
const emit = defineEmits(['update:theta'])

const sh = computed(() => props.result?.shapes)
const m = computed(() => sh.value?.mechanism)
const toPts = (xy) => (xy ? xy[0].map((x, i) => [x, xy[1][i]]) : [])
const path = (pts) => (pts.length ? 'M' + pts.map((p) => p[0].toFixed(3) + ',' + p[1].toFixed(3)).join('L') + 'Z' : '')
const profile = computed(() => toPts(sh.value?.profile))
const pitch = computed(() => toPts(sh.value?.pitch))
const outer = computed(() => toPts(sh.value?.outer))

function at(arr2, deg) {                       // interpolate a per-degree [xs, ys] array at a cam angle
  const n = arr2[0].length, u = ((deg % 360) + 360) % 360, i = Math.floor(u) % n, j = (i + 1) % n, f = u - Math.floor(u)
  return [arr2[0][i] * (1 - f) + arr2[0][j] * f, arr2[1][i] * (1 - f) + arr2[1][j] * f]
}
function at1(arr, deg) {
  const n = arr.length, u = ((deg % 360) + 360) % 360, i = Math.floor(u) % n, j = (i + 1) % n, f = u - Math.floor(u)
  return arr[i] * (1 - f) + arr[j] * f
}

const R = computed(() => Math.max(1, ...profile.value.concat(outer.value).map((p) => Math.hypot(p[0], p[1]))))
const camR = computed(() => (m.value?.groove ? R.value + Math.max(4, 0.12 * R.value) : 0))
const F = computed(() => (sh.value ? at(sh.value.follower, props.theta) : [0, 0]))
const N = computed(() => (sh.value ? at(sh.value.normal, props.theta) : [0, 1]))
const phi = computed(() => (props.result ? at1(props.result.curves.phi_deg, props.theta) : 0))
const s = computed(() => (props.result ? at1(props.result.curves.s, props.theta) : 0))
const osc = computed(() => m.value?.follower === 'oscillating')
const contact = computed(() => {
  if (!m.value) return [0, 0]
  if (m.value.contact === 'roller') { const n = N.value, l = Math.hypot(n[0], n[1]) || 1; return [F.value[0] - m.value.rr * n[0] / l, F.value[1] - m.value.rr * n[1] / l] }
  return F.value
})
const box = computed(() => {
  const pts = [[-R.value - camR.value * 0, -R.value], [R.value, R.value], [-camR.value, -camR.value], [camR.value, camR.value]]
  if (sh.value) {
    const fx = sh.value.follower[0], fy = sh.value.follower[1]
    for (let i = 0; i < fx.length; i += 6) pts.push([fx[i], fy[i]])
  }
  if (osc.value) pts.push([m.value.a, 0], [m.value.a + 0.1 * R.value, 0])
  else pts.push([0, Math.max(...(sh.value?.follower[1] || [0])) + 0.6 * R.value])
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]), pad = 0.12 * R.value + (m.value?.rr || 0)
  const x0 = Math.min(...xs) - pad, x1 = Math.max(...xs) + pad, y0 = Math.min(...ys) - pad, y1 = Math.max(...ys) + pad
  return { x0, y0, w: x1 - x0, h: y1 - y0 }
})
const stroke = computed(() => R.value / 160)
const camAngle = computed(() => (m.value?.sigma || 1) * props.theta)
const faceHalf = computed(() => Math.max(0.5 * R.value, ...(props.result?.curves.v || [0]).map(Math.abs)) + 0.1 * R.value)
const arrow = computed(() => {
  const n = N.value, l = Math.hypot(n[0], n[1]) || 1, c = contact.value, L = 0.45 * R.value
  return { x1: c[0], y1: c[1], x2: c[0] + (n[0] / l) * L, y2: c[1] + (n[1] / l) * L }
})
const motionDir = computed(() => {                // direction the follower moves, for the pressure-angle wedge
  if (!m.value) return [0, 1]
  if (!osc.value) return [0, 1]
  const p = F.value, r = [p[0] - m.value.a, p[1]]
  return [-r[1], r[0]]
})
function onWheel(e) { emit('update:theta', (((props.theta + (e.deltaY > 0 ? 2 : -2)) % 360) + 360) % 360) }
</script>

<template>
  <div class="view">
    <svg v-if="result" :viewBox="`${box.x0} ${-box.y0 - box.h} ${box.w} ${box.h}`" role="img" :aria-label="t('app')" @wheel.prevent="onWheel">
      <g transform="scale(1,-1)" :style="`--sw:${stroke}`">
        <!-- cam -->
        <g :transform="`rotate(${camAngle})`">
          <circle v-if="m.groove" :r="camR" class="body" />
          <path v-if="m.groove" :d="path(outer)" class="groove" />
          <path :d="path(profile)" class="body" />
          <path v-if="pitch.length" :d="path(pitch)" class="pitch" />
          <circle :r="sh.rb" class="base" />
          <line :x1="0" :y1="0" :x2="0.55 * sh.rb" :y2="0" class="key" />
          <circle :r="0.12 * sh.rb" class="hub" />
        </g>
        <circle :r="stroke * 2.2" class="centre" />
        <!-- follower -->
        <template v-if="!osc">
          <template v-if="m.contact === 'flat'">
            <line :x1="-faceHalf" :x2="faceHalf" :y1="F[1]" :y2="F[1]" class="face" />
            <rect :x="-0.06 * R" :y="F[1]" :width="0.12 * R" :height="0.55 * R" class="stem" />
          </template>
          <template v-else>
            <rect :x="F[0] - 0.06 * R" :y="F[1]" :width="0.12 * R" :height="0.55 * R" class="stem" />
            <circle v-if="m.contact === 'roller'" :cx="F[0]" :cy="F[1]" :r="m.rr" class="roller" />
            <path v-else :d="`M${F[0]},${F[1]} l${-0.06 * R},${0.14 * R} h${0.12 * R}Z`" class="roller" />
          </template>
        </template>
        <template v-else>
          <line :x1="m.a" :y1="0" :x2="m.contact === 'flat' ? F[0] + (F[0] - m.a) * 0.15 : F[0]" :y2="m.contact === 'flat' ? F[1] * 1.15 : F[1]" :class="m.contact === 'flat' ? 'face' : 'arm'" />
          <circle :cx="m.a" cy="0" :r="0.05 * R" class="pivot" />
          <circle v-if="m.contact === 'roller'" :cx="F[0]" :cy="F[1]" :r="m.rr" class="roller" />
        </template>
        <!-- contact normal and the direction of motion -->
        <line :x1="arrow.x1" :y1="arrow.y1" :x2="arrow.x2" :y2="arrow.y2" class="normal" />
        <line :x1="contact[0]" :y1="contact[1]" :x2="contact[0] + motionDir[0] / Math.hypot(...motionDir) * 0.45 * R" :y2="contact[1] + motionDir[1] / Math.hypot(...motionDir) * 0.45 * R" class="motion" />
        <circle :cx="contact[0]" :cy="contact[1]" :r="stroke * 2.5" class="dot" />
      </g>
    </svg>
    <div v-if="result" class="read mono">
      <span>θ {{ theta.toFixed(1) }}°</span>
      <span>s {{ result.unit === 'rad' ? (s * 180 / Math.PI).toFixed(3) + '°' : s.toFixed(3) + ' mm' }}</span>
      <span class="phi">φ {{ Math.abs(phi).toFixed(2) }}°</span>
    </div>
    <div v-if="result" class="legend"><i class="lg-n" />{{ t('phi') }}：<i class="lg-normal" /> {{ lang === 'zh' ? '法线' : 'normal' }} · <i class="lg-motion" /> {{ lang === 'zh' ? '运动方向' : 'motion' }}</div>
  </div>
</template>

<style scoped>
.view { position: relative; height: 100%; min-height: 220px; display: grid; }
svg { width: 100%; height: 100%; min-height: 220px; }
.body { fill: var(--cam); stroke: var(--ink); stroke-width: var(--sw); }
.groove { fill: var(--paper); stroke: var(--ink); stroke-width: var(--sw); }
.pitch { fill: none; stroke: var(--accent); stroke-width: var(--sw); stroke-dasharray: calc(var(--sw) * 6) calc(var(--sw) * 4); opacity: .8; }
.base { fill: none; stroke: var(--muted); stroke-width: calc(var(--sw) * .7); stroke-dasharray: calc(var(--sw) * 2) calc(var(--sw) * 3); }
.key { stroke: var(--ink); stroke-width: calc(var(--sw) * 2); }
.hub { fill: var(--paper); stroke: var(--ink); stroke-width: var(--sw); }
.centre { fill: var(--ink); }
.stem { fill: var(--steel); stroke: var(--ink); stroke-width: var(--sw); }
.roller { fill: var(--steel-2); stroke: var(--ink); stroke-width: calc(var(--sw) * 1.3); }
.arm { stroke: var(--ink); stroke-width: calc(var(--sw) * 5); stroke-linecap: round; opacity: .85; }
.face { stroke: var(--ink); stroke-width: calc(var(--sw) * 3); stroke-linecap: round; }
.pivot { fill: var(--paper); stroke: var(--ink); stroke-width: calc(var(--sw) * 1.5); }
.normal { stroke: var(--bad); stroke-width: calc(var(--sw) * 1.6); }
.motion { stroke: var(--blue); stroke-width: calc(var(--sw) * 1.6); stroke-dasharray: calc(var(--sw) * 4) calc(var(--sw) * 3); }
.dot { fill: var(--bad); }
.read { position: absolute; left: 10px; top: 8px; display: flex; gap: 14px; font-size: 13px; color: var(--muted); }
.read .phi { color: var(--bad); }
.legend { position: absolute; left: 10px; bottom: 6px; font-size: 11.5px; color: var(--muted); }
.legend i { display: inline-block; width: 16px; height: 0; border-top: 2px solid; vertical-align: middle; margin: 0 3px; }
.lg-n { display: none !important; }
.lg-normal { border-color: var(--bad) !important; }
.lg-motion { border-color: var(--blue) !important; border-top-style: dashed !important; }
</style>
