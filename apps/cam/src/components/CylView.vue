<script setup>
// The cylindrical cam (round 39, step 8): the grooved barrel turning in 3D with the roller and its follower, or the
// groove unrolled (development) with the roller's place in it. Geometry from the kernel (geometry.rings: the flanks
// at every degree of azimuth; geometry.centre: the roller axis over the turn).
// Kernel frame (cam axis z, roller axis x) → three.js: X = z, Y = x, Z = y (a cyclic swap, so turning stays right-handed).
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { t } from '../i18n'

const props = defineProps({ result: Object, theta: Number })
const emit = defineEmits(['update:theta'])
const view = ref('3d')
const box = ref(null)
const g = computed(() => props.result?.geometry)
let renderer, scene, camera, controls, ro, raf = 0
let camGroup = null, roller = null, follower = null, sig = ''

const mat = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, metalness: 0.35, roughness: 0.55, ...o })

function at1(arr, deg) {
  const n = arr.length - 1, u = (((deg % 360) + 360) % 360) * (n / 360), i = Math.floor(u), f = u - i
  return arr[i] * (1 - f) + arr[Math.min(i + 1, n)] * f
}
const centre = computed(() => (g.value ? { y: at1(g.value.centre.y, props.theta), z: at1(g.value.centre.z, props.theta) } : { y: 0, z: 0 }))

function barrel(G) {
  // one column of points per degree, each running along the cam from one end face to the other through the groove
  const R = G.outer, core = G.core, L = G.length / 2, ri = G.rings
  const cols = ri.az_deg.length
  const clamp = (z) => Math.max(-L, Math.min(L, z))
  const prof = (j) => [[R, -L], [R, clamp(ri.outer.lo[j])], [G.x1, clamp(ri.inner.lo[j])], [core, clamp(ri.inner.lo[j])],
    [core, clamp(ri.inner.hi[j])], [G.x1, clamp(ri.inner.hi[j])], [R, clamp(ri.outer.hi[j])], [R, L]]
  const per = 8, pos = new Float32Array(cols * per * 3), idx = []
  for (let j = 0; j < cols; j++) {
    const a = (ri.az_deg[j] * Math.PI) / 180, ca = Math.cos(a), sa = Math.sin(a)
    prof(j).forEach(([r, z], i) => { const o = (j * per + i) * 3; pos[o] = z; pos[o + 1] = r * ca; pos[o + 2] = r * sa })
  }
  for (let j = 0; j < cols - 1; j++) for (let i = 0; i < per - 1; i++) {
    const a = j * per + i, b = (j + 1) * per + i
    idx.push(a, b, a + 1, b, b + 1, a + 1)
  }
  const geo = new THREE.BufferGeometry()
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3))
  geo.setIndex(idx)
  geo.computeVertexNormals()
  const grp = new THREE.Group()
  grp.add(new THREE.Mesh(geo, mat(0xb9c2c7, { side: THREE.DoubleSide })))
  for (const s of [-1, 1]) {                                   // end faces with the shaft hole
    const ring = new THREE.Mesh(new THREE.RingGeometry(core * 0.45, R, 72), mat(0xa8b2b8, { side: THREE.DoubleSide }))
    ring.rotation.y = Math.PI / 2
    ring.position.x = s * L
    grp.add(ring)
  }
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(core * 0.45, core * 0.45, 2 * L + 40, 32), mat(0x6f7c84))
  shaft.rotation.z = Math.PI / 2
  grp.add(shaft)
  return grp
}

function build() {
  if (!scene || !g.value) return
  const G = g.value
  const key = JSON.stringify([G.outer, G.core, G.length, G.x1, G.rr, G.roller, G.follower, G.arm, G.rings.outer.lo.slice(0, 8), G.rings.inner.hi.slice(0, 8)])
  if (key === sig && camGroup) return
  sig = key
  for (const o of [camGroup, roller, follower]) if (o) scene.remove(o)
  camGroup = barrel(G)
  scene.add(camGroup)
  const k = G.k, top = G.roller === 'cone' ? k * G.x2 : G.rr, bot = G.roller === 'cone' ? k * G.x1 : G.rr
  roller = new THREE.Mesh(new THREE.CylinderGeometry(top, bot, G.b, 40), mat(0xf2b705, { metalness: 0.5 }))
  scene.add(roller)
  follower = new THREE.Group()
  const pin = new THREE.Mesh(new THREE.CylinderGeometry(G.rr * 0.35, G.rr * 0.35, 40, 20), mat(0x2f8fb0, { metalness: 0.2 }))
  pin.position.y = G.x2 + 20
  pin.name = 'pin'
  follower.add(pin)
  if (G.follower === 'oscillating') {
    const arm = new THREE.Mesh(new THREE.BoxGeometry(G.rr * 1.2, G.rr * 0.8, G.arm), mat(0x2f8fb0, { metalness: 0.2 }))
    arm.position.set(0, G.x2 + 40, -G.arm / 2)
    arm.name = 'arm'
    follower.add(arm)
  } else {
    const slide = new THREE.Mesh(new THREE.BoxGeometry(G.rr * 3, G.rr * 1.2, G.rr * 2.2), mat(0x2f8fb0, { metalness: 0.2 }))
    slide.position.y = G.x2 + 40
    follower.add(slide)
  }
  scene.add(follower)
  if (G.follower === 'oscillating') {
    const piv = new THREE.Mesh(new THREE.CylinderGeometry(G.rr * 0.6, G.rr * 0.6, G.rr * 2.4, 24), mat(0x6f7c84))
    piv.position.set(0, G.x2 + 40, -G.arm)
    scene.add(piv)
    follower.userData.pivot = piv
  }
  // look at the barrel from the side and a little above, so the groove runs across the view
  const span = Math.max(G.length, 2 * G.outer) + (G.follower === 'oscillating' ? G.arm : 0)
  camera.position.set(span * 0.45, span * 1.05, span * 1.9)
  controls.target.set(0, G.outer * 0.25, G.follower === 'oscillating' ? -G.arm * 0.3 : 0)
  controls.update()
  place()
}

function place() {
  const G = g.value
  if (!G || !camGroup) return
  camGroup.rotation.x = (G.sigma * props.theta * Math.PI) / 180
  const c = centre.value
  roller.position.set(c.z, G.Rp, c.y)
  if (G.follower === 'oscillating') {
    // the pin rides on the roller; the arm runs from it to the pivot (kernel (·, −L, 0)), turning about the pivot axis
    follower.getObjectByName('pin').position.set(c.z, G.x2 + 20, c.y)
    const arm = follower.getObjectByName('arm')
    arm.position.set(c.z / 2, G.x2 + 40, (c.y - G.arm) / 2)
    arm.rotation.y = Math.atan2(c.z, c.y + G.arm)
  } else {
    follower.position.set(c.z, 0, c.y)
  }
  renderer.render(scene, camera)
}

function size() {
  if (!box.value || !renderer) return
  const w = box.value.clientWidth, h = box.value.clientHeight
  renderer.setSize(w, h, false)
  camera.aspect = w / Math.max(1, h)
  camera.updateProjectionMatrix()
  renderer.render(scene, camera)
}
function loop() { raf = requestAnimationFrame(loop); controls?.update(); if (renderer) renderer.render(scene, camera) }

onMounted(() => {
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1))
  box.value.appendChild(renderer.domElement)
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(35, 1, 1, 20000)
  scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 1.1))
  const d = new THREE.DirectionalLight(0xffffff, 1.4); d.position.set(300, 500, 400); scene.add(d)
  controls = new OrbitControls(camera, renderer.domElement)
  ro = new ResizeObserver(size); ro.observe(box.value)
  size(); build(); loop()
})
onBeforeUnmount(() => { cancelAnimationFrame(raf); ro?.disconnect(); renderer?.dispose() })
watch(g, () => { if (view.value === '3d') build() })
watch(() => props.theta, place)
watch(view, (v) => { if (v === '3d') requestAnimationFrame(() => { size(); build(); place() }) })

// ---------------------------------------------------------------- development (the groove unrolled at the outer radius)
const W = 720, H = 300, PAD = { l: 44, r: 10, t: 12, b: 26 }
const dev = computed(() => {
  const G = g.value
  if (!G) return null
  const ri = G.rings, L = G.length / 2, U = 2 * Math.PI * G.outer
  const X = (deg) => PAD.l + (deg / 360) * (W - PAD.l - PAD.r)
  const Y = (z) => PAD.t + (1 - (z + L) / (2 * L)) * (H - PAD.t - PAD.b)
  const line = (zs) => 'M' + ri.az_deg.map((a, j) => `${X(a).toFixed(1)},${Y(zs[j]).toFixed(1)}`).join('L')
  const groove = line(ri.outer.lo) + 'L' + [...ri.az_deg].reverse().map((a, j) => `${X(a).toFixed(1)},${Y(ri.outer.hi[ri.az_deg.length - 1 - j]).toFixed(1)}`).join('L') + 'Z'
  const mid = ri.inner.lo.map((z, j) => (z + ri.inner.hi[j]) / 2)
  return { X, Y, groove, lo: line(ri.inner.lo), hi: line(ri.inner.hi), mid: line(mid), L, U, top: Y(L), bot: Y(-L) }
})
const rollerAt = computed(() => {
  const G = g.value
  if (!G || !dev.value) return null
  const az = (((-G.sigma * props.theta) % 360) + 360) % 360
  const r = G.roller === 'cone' ? G.k * G.x2 : G.rr
  const sx = (W - PAD.l - PAD.r) / 360 / ((2 * Math.PI * G.outer) / 360)   // px per mm along u
  const sy = (H - PAD.t - PAD.b) / G.length
  return { x: dev.value.X(az), y: dev.value.Y(centre.value.z), rx: r * sx, ry: r * sy }
})
function pick(e) {
  const b = e.currentTarget.getBoundingClientRect(), x = ((e.clientX - b.left) / b.width) * W
  const f = (x - PAD.l) / (W - PAD.l - PAD.r)
  if (f < 0 || f > 1 || !g.value) return
  const az = f * 360
  emit('update:theta', ((((-az) * g.value.sigma) % 360) + 360) % 360)
}
</script>

<template>
  <div class="cyl">
    <div class="sw" role="tablist">
      <button type="button" :class="{ on: view === '3d' }" @click="view = '3d'">{{ t('cyl3d') }}</button>
      <button type="button" :class="{ on: view === 'dev' }" @click="view = 'dev'">{{ t('cylDev') }}</button>
    </div>
    <div v-show="view === '3d'" ref="box" class="gl" />
    <svg v-if="view === 'dev' && dev" :viewBox="`0 0 ${W} ${H}`" class="dev" @pointerdown="pick" @pointermove="$event.buttons && pick($event)">
      <rect :x="PAD.l" :y="dev.top" :width="W - PAD.l - PAD.r" :height="dev.bot - dev.top" class="body" />
      <path :d="dev.groove" class="groove" />
      <path :d="dev.lo" class="inner" /><path :d="dev.hi" class="inner" />
      <path :d="dev.mid" class="mid" />
      <ellipse v-if="rollerAt" :cx="rollerAt.x" :cy="rollerAt.y" :rx="rollerAt.rx" :ry="rollerAt.ry" class="roller" />
      <text v-for="d in [0, 90, 180, 270, 360]" :key="d" :x="dev.X(d)" :y="H - 8" text-anchor="middle" class="ax">{{ d }}°</text>
      <text :x="PAD.l - 4" :y="dev.top + 4" text-anchor="end" class="ax">{{ dev.L }}</text>
      <text :x="PAD.l - 4" :y="dev.bot" text-anchor="end" class="ax">{{ -dev.L }}</text>
      <text :x="W - PAD.r" :y="dev.top - 2" text-anchor="end" class="ax">{{ t('cylDevNote') }}</text>
    </svg>
  </div>
</template>

<style scoped>
.cyl { position: absolute; inset: 0; display: flex; flex-direction: column; }
.sw { position: absolute; left: 10px; top: 8px; z-index: 2; display: flex; gap: 2px; background: var(--chip); border-radius: 7px; padding: 2px; }
.sw button { border: 0; background: none; padding: 4px 10px; border-radius: 5px; font-size: 12.5px; color: var(--muted); }
.sw button.on { background: var(--surface); color: var(--ink); font-weight: 600; }
.gl { flex: 1; min-height: 0; }
.gl :deep(canvas) { width: 100%; height: 100%; display: block; }
.dev { flex: 1; width: 100%; min-height: 0; padding-top: 34px; touch-action: none; cursor: crosshair; }
.body { fill: var(--cam); opacity: 0.55; }
.groove { fill: var(--paper); stroke: var(--ink); stroke-width: 1.1; }
.inner { fill: none; stroke: var(--muted); stroke-width: 0.8; stroke-dasharray: 4 3; }
.mid { fill: none; stroke: var(--blue); stroke-width: 0.8; stroke-dasharray: 2 3; }
.roller { fill: var(--accent); fill-opacity: 0.85; stroke: var(--ink); stroke-width: 0.8; }
.ax { font: 10px var(--mono); fill: var(--muted); }
</style>
