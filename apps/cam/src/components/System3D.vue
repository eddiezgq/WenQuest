<script setup>
// The tool changer in 3D (round 39, step 4): the globoidal cam made the way it is machined, the turret and its
// rollers, the arm with two tools turning and moving up and down, the groove cam on the same camshaft; with the 3D
// model, the 4-axis program and the arm's STEP to download.
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { system, sysResult, sysPayload } from '../sysstore'
import { api, saveText } from '../api'
import { t, lang } from '../i18n'

const box = ref(null)
const theta = ref(0)
const playing = ref(true)
const speed = ref(60)
const err = ref(null)
const busy = ref(false)
const msg = ref('')
const meshData = shallowRef(null)
const glob = computed(() => (system.cams || []).find((c) => c.type === 'globoidal'))
const plunge = computed(() => (sysResult.value?.cams || []).find((c) => c.type !== 'globoidal'))
const plungeSrc = computed(() => (system.cams || []).find((c) => c.type !== 'globoidal'))
let renderer, scene, camera, controls, raf = 0, last = 0, ro
const parts = {}

function b64(s, T) { const bin = atob(s); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return new T(u.buffer) }

async function loadMesh() {
  if (!glob.value) return
  busy.value = true; err.value = null
  try { meshData.value = await api('/system/mesh/' + glob.value.id, sysPayload()); build() } catch (e) { err.value = e } finally { busy.value = false }
}

const mat = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, metalness: 0.35, roughness: 0.55, ...o })
function build() {
  if (!scene || !meshData.value) return
  for (const k of Object.keys(parts)) { scene.remove(parts[k]); delete parts[k] }
  const m = meshData.value, g = m.globoidal
  // the globoidal cam: cam frame (axis z) inside a group on the cam axis x = C
  const geo = new THREE.BufferGeometry()
  geo.setAttribute('position', new THREE.BufferAttribute(b64(m.vertices, Float32Array), 3))
  geo.setIndex(new THREE.BufferAttribute(b64(m.faces, Uint32Array), 1))
  geo.computeVertexNormals()
  const cam = new THREE.Group()
  cam.add(new THREE.Mesh(geo, mat(0xb9c2c7, { side: THREE.DoubleSide })))
  const shaftLen = g.L + 260
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(18, 18, shaftLen, 32), mat(0x6f7c84))
  shaft.rotation.x = Math.PI / 2
  shaft.position.z = 90
  cam.add(shaft)
  // the groove cam for pulling the tools out, on the same camshaft
  const sh = plunge.value?.shapes
  if (sh?.profile) {
    const prof = sh.profile, outer = sh.outer
    const R = Math.max(...(outer || prof)[0].map((x, i) => Math.hypot(x, (outer || prof)[1][i]))) + 10
    const disk = new THREE.Shape()
    disk.absarc(0, 0, R, 0, Math.PI * 2, false)
    if (outer) {
      const hole = new THREE.Path(); outer[0].forEach((x, i) => (i ? hole.lineTo(x, outer[1][i]) : hole.moveTo(x, outer[1][i]))); disk.holes.push(hole)
    }
    const g2 = new THREE.ExtrudeGeometry(disk, { depth: 24, bevelEnabled: false, curveSegments: 64 })
    const inner = new THREE.Shape(); prof[0].forEach((x, i) => (i ? inner.lineTo(x, prof[1][i]) : inner.moveTo(x, prof[1][i])))
    const g3 = new THREE.ExtrudeGeometry(inner, { depth: 24, bevelEnabled: false })
    const gc = new THREE.Group()
    gc.add(new THREE.Mesh(g2, mat(0xc9b98f)), new THREE.Mesh(g3, mat(0xc9b98f)))
    gc.position.z = g.L / 2 + 120
    cam.add(gc)
  }
  cam.position.set(g.C, 0, 0)
  parts.cam = cam
  // the turret and its rollers (turret centre at the origin, axis y)
  const tur = new THREE.Group()
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(g.rho1 - 4, g.rho1 - 4, 2 * g.rr + 12, 48), mat(0x2f8fb0, { metalness: 0.2 }))
  tur.add(hub)
  for (let i = 0; i < g.n; i++) {
    const a = (g.phase_deg * Math.PI) / 180 + (2 * Math.PI * i) / g.n
    const r = new THREE.Mesh(new THREE.CylinderGeometry(g.rr, g.rr, g.b, 24), mat(0xf2b705, { metalness: 0.5 }))
    const mid = (g.rho1 + g.rho2) / 2
    r.position.set(mid * Math.cos(a), 0, mid * Math.sin(a))
    r.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3(Math.cos(a), 0, Math.sin(a)))
    tur.add(r)
  }
  parts.tur = tur
  // output shaft, the arm and two tools below the turret
  const arm = new THREE.Group()
  const A = system.arm || { R_tip: 150, R_hub: 48, w_root: 60, w_tip: 44, R_grip: 46, thickness: 28 }
  const bar = new THREE.Mesh(new THREE.BoxGeometry(2 * A.R_tip, A.thickness, (A.w_root + A.w_tip) / 2), mat(0x8f9ba3))
  arm.add(bar)
  arm.add(new THREE.Mesh(new THREE.CylinderGeometry(A.R_hub, A.R_hub, A.thickness, 40), mat(0x8f9ba3)))
  for (const s of [1, -1]) {
    const grip = new THREE.Mesh(new THREE.CylinderGeometry(A.R_grip, A.R_grip, A.thickness, 40), mat(0x8f9ba3))
    grip.position.x = s * A.R_tip
    arm.add(grip)
    const tool = new THREE.Group()
    const shank = new THREE.Mesh(new THREE.CylinderGeometry(A.r_fork || 32, 20, 90, 32), mat(0x56666e))
    shank.position.y = -45
    const cutter = new THREE.Mesh(new THREE.CylinderGeometry(10, 10, 110, 20), mat(0xd96d4a))
    cutter.position.y = -145
    tool.add(shank, cutter)
    tool.position.x = s * A.R_tip
    arm.add(tool)
  }
  const out = new THREE.Mesh(new THREE.CylinderGeometry(22, 22, 190, 32), mat(0x6f7c84))
  out.position.y = 95
  arm.add(out)
  const armHolder = new THREE.Group()
  armHolder.add(arm)
  armHolder.position.y = -170
  parts.arm = armHolder
  parts.armInner = arm
  for (const k of ['cam', 'tur', 'arm']) scene.add(parts[k])
  pose()
  if (!framed) frame()
}

// first view: from the front-left so the globoidal cam sits in front of the groove cam, whole machine in the frame
let framed = false
function frame() {
  const b = new THREE.Box3()
  for (const k of ['cam', 'tur', 'arm']) b.expandByObject(parts[k])
  const c = b.getCenter(new THREE.Vector3()), r = b.getBoundingSphere(new THREE.Sphere()).radius
  const dir = new THREE.Vector3(-0.35, 0.45, -1).normalize()
  const fov = (camera.fov * Math.PI) / 180, fit = Math.min(1, camera.aspect)
  const dist = (r * 1.05) / Math.sin(fov / 2) / Math.max(0.6, fit)
  camera.position.copy(c).addScaledVector(dir, dist)
  controls.target.copy(c)
  controls.update()
  framed = true
}

function at(arr, deg, adv = 0) {   // per-degree samples over one turn; adv: what an indexing output gains per turn
  if (!arr?.length) return 0
  const n = arr.length, u = ((deg % 360) + 360) % 360, f = (u / 360) * n, i = Math.floor(f) % n, j = (i + 1) % n
  const a = arr[i], b = arr[j] + (j === 0 ? adv : 0)
  return a + (b - a) * (f - Math.floor(f))
}
function pose() {
  if (!parts.cam || !meshData.value) return
  const th = theta.value, g = meshData.value.globoidal
  parts.cam.rotation.z = (th * Math.PI) / 180
  const phi = (at(meshData.value.turret_deg, th, Number(glob.value?.program?.advance_deg) || 0) * Math.PI) / 180
  parts.tur.rotation.y = -g.hand * phi
  parts.armInner.rotation.y = -g.hand * phi
  const pl = plunge.value, src = plungeSrc.value
  if (pl && src?.output?.radius) {
    const psi = (at(pl.s, th) * Math.PI) / 180
    parts.arm.position.y = -170 - src.output.radius * psi
  }
}
watch(theta, pose)

function loop(ts) { if (playing.value) { if (last) theta.value = (theta.value + ((ts - last) / 1000) * speed.value) % 360; last = ts } else last = 0; renderer.render(scene, camera); controls.update(); raf = requestAnimationFrame(loop) }

onMounted(() => {
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true })
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1))
  box.value.appendChild(renderer.domElement)
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(35, 1, 1, 10000)
  camera.position.set(520, 330, 620)
  controls = new OrbitControls(camera, renderer.domElement)
  controls.target.set(80, -60, 40)
  scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 1.1))
  const d = new THREE.DirectionalLight(0xffffff, 1.6); d.position.set(300, 600, 400); scene.add(d)
  const resize = () => { const w = box.value.clientWidth, h = box.value.clientHeight; renderer.setSize(w, h); camera.aspect = w / Math.max(1, h); camera.updateProjectionMatrix() }
  ro = new ResizeObserver(resize); ro.observe(box.value); resize()
  raf = requestAnimationFrame(loop)
  loadMesh()
})
onBeforeUnmount(() => { cancelAnimationFrame(raf); ro?.disconnect(); renderer?.dispose() })
watch(() => sysResult.value, () => { if (meshData.value) build() })

async function download(kind) {
  msg.value = ''
  try {
    const f = await api('/system/export/' + kind + (glob.value ? '?cam=' + glob.value.id : ''), sysPayload())
    if (f.b64) { const bin = atob(f.b64); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([u], { type: f.mime })); a.download = f.name; a.click() } else saveText(f.name, f.text, f.mime)
    if (f.sim) msg.value = (lang.value === 'zh' ? '程序仿真：最大过切 ' : 'Simulation: largest overcut ') + (f.sim.max_over * 1000).toFixed(2) + ' µm，' + (lang.value === 'zh' ? '最大欠切 ' : 'largest undercut ') + (f.sim.max_under * 1000).toFixed(2) + ' µm（' + f.sim.points + (lang.value === 'zh' ? ' 个齿面点）' : ' flank points)')
    if (f.mass) msg.value = (lang.value === 'zh' ? '换刀臂质量 ' : 'Arm mass ') + f.mass.mass.toFixed(2) + ' kg，J = ' + f.mass.J.toFixed(4) + ' kg·m²'
  } catch (e) { msg.value = lang.value === 'zh' ? e.zh : e.message }
}
</script>

<template>
  <main class="work s3d">
    <section class="stage view3d">
      <div ref="box" class="three" />
      <p v-if="busy" class="busy">{{ t('computing') }}</p>
      <p v-if="err" class="err">{{ t('error') }}：{{ lang === 'zh' ? err.zh || err.message : err.message }}</p>
      <div class="controls">
        <button type="button" class="solid" @click="playing = !playing">{{ playing ? '❚❚ ' + t('pause') : '▶ ' + t('play') }}</button>
        <label class="scrub">{{ t('camAngle') }} <input v-model.number="theta" type="range" min="0" max="359.9" step="0.1" @input="playing = false"> <span class="mono">{{ theta.toFixed(1) }}°</span></label>
        <label class="spd"><input v-model.number="speed" type="range" min="10" max="360" step="10"> <span class="mono">{{ speed }}°/s</span></label>
      </div>
    </section>
    <aside class="side">
      <h4>{{ t('downloads') }}</h4>
      <div class="dl">
        <button type="button" class="ghost" :disabled="!glob" @click="download('stl')">{{ t('stl') }}</button>
        <button type="button" class="ghost" :disabled="!glob" @click="download('nc4')">{{ t('nc4') }}</button>
        <button type="button" class="ghost" :disabled="!system.arm" @click="download('arm-step')">{{ t('armStep') }}</button>
      </div>
      <p v-if="msg" class="note">{{ msg }}</p>
      <p class="note">{{ t('model3dNote') }}</p>
      <p class="note">{{ lang === 'zh' ? '鼠标拖动旋转、滚轮缩放。三维画面里的换刀臂、刀具、轴是示意；弧面凸轮和滚子按实际尺寸。' : 'Drag to turn, scroll to zoom. The arm, tools and shafts are schematic; the globoidal cam and rollers are to size.' }}</p>
    </aside>
  </main>
</template>

<style scoped>
.s3d { grid-template-columns: minmax(0, 1fr) 300px; grid-template-rows: minmax(480px, 76vh); }
.view3d { grid-column: 1; grid-row: 1; position: relative; }
.s3d .side { grid-column: 2; grid-row: 1; }
.three { width: 100%; height: 100%; min-height: 380px; min-width: 0; overflow: hidden; }
.three :deep(canvas) { display: block; max-width: 100%; }
.dl { display: grid; gap: 6px; margin: 6px 0; }
.note { font-size: 12.5px; color: var(--muted); }
@media (max-width: 760px) { .s3d { grid-template-columns: minmax(0, 1fr); grid-template-rows: auto; } .s3d .side, .view3d { grid-column: 1; grid-row: auto; } .view3d { height: 70vh; } }
</style>
