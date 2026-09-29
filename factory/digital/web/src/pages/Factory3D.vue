<template>
  <div class="wrap3d">
    <div ref="host" class="host" @pointerdown="down" @pointerup="up"></div>
    <div class="legend small">
      <span v-for="s in ['run', 'idle', 'setup', 'down']" :key="s"><i :style="{ background: HEX[s] }"></i>{{ STATE[s].label }}</span>
      <span class="muted">拖动旋转 · 滚轮缩放 · 点设备看详情</span>
    </div>
    <aside v-if="sel" class="panel">
      <button class="x" aria-label="关闭" @click="sel = null">×</button>
      <h2>{{ sel.toUpperCase() }} {{ layout?.units[sel]?.name }}</h2>
      <template v-if="bus.machines[sel]">
        <p><span class="pill" :style="{ color: STATE[m.state].color, background: STATE[m.state].bg }">{{ STATE[m.state].label }}</span>
          <span v-if="m.reason" class="small"> {{ m.reason }}</span></p>
        <p class="small">工单 <b class="mono">{{ m.work_order || '—' }}</b> · {{ (m.operation || '').split(' ')[0] }} · {{ m.qty_done }}/{{ m.qty }} 件</p>
        <p class="small">待加工 {{ m.queue }} 件 · 刀具寿命 {{ Math.round((m.tool_life_left ?? 1) * 100) }}%</p>
        <router-link :to="{ path: '/work/operator', query: { unit: sel } }" class="small">打开车间终端 →</router-link>
      </template>
      <p v-else class="small muted">这个单元没有状态消息。</p>
      <template v-if="sel === 'key-01'">
        <hr>
        <h3>键槽刀路回放</h3>
        <div ref="gcHost" class="gchost"></div>
        <p v-if="!gcode" class="small muted">还没有 G 代码：工艺员在 FreeCAD 发布后生成。</p>
        <button v-else class="btn" @click="playGcode">{{ gcPlaying ? '重新播放' : '播放刀路' }}</button>
      </template>
    </aside>
    <div v-if="err" class="errbox err">{{ err }}</div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { get } from '../lib/api';
import { bus } from '../lib/bus';
import { STATE } from '../lib/fmt';
import { parseGcode } from '../lib/gcode';

const HEX = { run: '#1F7A4D', idle: '#9AA3AD', setup: '#C98A12', down: '#B42318', fault: '#B42318' };
const HEIGHT = { 'ht-01': 2.6, 'store-01': 3, 'store-02': 3, 'hmc-01': 2.4, 'vmc-01': 2.3, 'cnc-l01-a': 1.8, 'cnc-l01-b': 1.8,
  'grd-01': 1.7, 'hob-01': 2, 'key-01': 1.6, 'saw-01': 1.2, 'qc-01': 1.5, 'asm-01': 1.0, 'test-01': 1.3 };
const route = useRoute();
const host = ref(null);
const gcHost = ref(null);
const layout = ref(null);
const sel = ref(null);
const err = ref('');
const gcode = ref('');
const gcPlaying = ref(false);
const m = computed(() => bus.machines[sel.value] || {});
let renderer, scene, camera, controls, raf, raycaster, pointer, downAt;
const meshes = {};         // 单元 → { body, lamp, label, queue: Group }
const agvMeshes = {};
let gc = null;             // 刀路小窗

function labelSprite(text, color = '#17212B') {
  const c = document.createElement('canvas');
  c.width = 256; c.height = 64;
  const g = c.getContext('2d');
  g.fillStyle = 'rgba(255,255,255,0.92)'; g.fillRect(0, 0, 256, 64);
  g.fillStyle = color; g.font = 'bold 28px "IBM Plex Mono", monospace'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(text, 128, 34);
  const tex = new THREE.CanvasTexture(c);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false }));
  sp.scale.set(3.2, 0.8, 1);
  return sp;
}

function build() {
  const L = layout.value;
  const [FW, FD] = L.floor;
  scene = new THREE.Scene();
  scene.background = new THREE.Color('#EEF0EC');
  camera = new THREE.PerspectiveCamera(45, host.value.clientWidth / host.value.clientHeight, 0.1, 500);
  camera.position.set(FW / 2, 40, FD + 34);
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
  renderer.setSize(host.value.clientWidth, host.value.clientHeight);
  host.value.appendChild(renderer.domElement);
  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(FW / 2, 0, FD / 2);
  controls.maxPolarAngle = Math.PI / 2.1;
  controls.update();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f86, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 1.4);
  sun.position.set(20, 40, 10);
  scene.add(sun);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(FW, FD), new THREE.MeshLambertMaterial({ color: '#D9DDD6' }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(FW / 2, 0, FD / 2);
  scene.add(floor);
  for (const a of L.aisles) {
    const s = new THREE.Mesh(new THREE.PlaneGeometry(FW - 4, 2.2), new THREE.MeshLambertMaterial({ color: '#F2EDD7' }));
    s.rotation.x = -Math.PI / 2; s.position.set(FW / 2 + 1, 0.01, a); scene.add(s);
  }
  const cross = new THREE.Mesh(new THREE.PlaneGeometry(2.2, L.aisles[1] - L.aisles[0]), new THREE.MeshLambertMaterial({ color: '#F2EDD7' }));
  cross.rotation.x = -Math.PI / 2; cross.position.set(L.cross_x, 0.01, (L.aisles[0] + L.aisles[1]) / 2); scene.add(cross);

  for (const [u, v] of Object.entries(L.units)) {
    const hgt = HEIGHT[u] || 1.5;
    const store = u.startsWith('store');
    const body = new THREE.Mesh(new THREE.BoxGeometry(v.w, hgt, v.d),
      new THREE.MeshLambertMaterial({ color: store ? '#B8BEB5' : u === 'ht-01' ? '#6E7B85' : '#DCE2E6' }));
    body.position.set(v.x, hgt / 2, v.y);
    body.userData.unit = u;
    scene.add(body);
    const lamp = new THREE.Mesh(new THREE.BoxGeometry(v.w * 0.9, 0.12, v.d * 0.9), new THREE.MeshLambertMaterial({ color: '#9AA3AD', emissive: '#000' }));
    lamp.position.set(v.x, hgt + 0.06, v.y);
    lamp.userData.unit = u;
    scene.add(lamp);
    const label = labelSprite(u.toUpperCase());
    label.position.set(v.x, hgt + 1.1, v.y);
    scene.add(label);
    const queue = new THREE.Group();
    scene.add(queue);
    meshes[u] = { body, lamp, label, queue, v, hgt };
  }
  for (const a of ['agv-01', 'agv-02']) {
    const g = new THREE.Group();
    const base = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.35, 0.8), new THREE.MeshLambertMaterial({ color: '#F2B705' }));
    base.position.y = 0.25;
    const load = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.5, 16), new THREE.MeshLambertMaterial({ color: '#5D6873' }));
    load.rotation.z = Math.PI / 2; load.position.y = 0.6; load.visible = false;
    g.add(base, load);
    const [x, y] = L.agv_home[a];
    g.position.set(x, 0, y);
    g.userData = { target: new THREE.Vector3(x, 0, y), load };
    const lb = labelSprite(a.toUpperCase(), '#6B4E00');
    lb.scale.set(2.2, 0.55, 1); lb.position.set(0, 1.4, 0);
    g.add(lb);
    scene.add(g);
    agvMeshes[a] = g;
  }
  raycaster = new THREE.Raycaster();
  pointer = new THREE.Vector2();
}

function applyStatus() {
  for (const [u, o] of Object.entries(meshes)) {
    const st = bus.machines[u];
    const state = st?.state || 'idle';
    o.lamp.material.color.set(HEX[state] || '#9AA3AD');
    o.lamp.material.emissive.set(state === 'run' ? '#0B3320' : state === 'down' || state === 'fault' ? '#4A0D08' : '#000');
    // 待加工的零件：在设备旁摆成一排小圆柱
    const n = Math.min(st?.queue || 0, 12);
    while (o.queue.children.length > n) o.queue.remove(o.queue.children[0]);
    while (o.queue.children.length < n) {
      const p = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.9, 12), new THREE.MeshLambertMaterial({ color: '#4A5560' }));
      p.rotation.z = Math.PI / 2;
      o.queue.add(p);
    }
    o.queue.children.forEach((p, i) => p.position.set(o.v.x - o.v.w / 2 + 0.3 + (i % 6) * 0.4, 0.2 + Math.floor(i / 6) * 0.35, o.v.y + o.v.d / 2 + 0.5));
  }
  for (const [a, g] of Object.entries(agvMeshes)) {
    const s = bus.agvs[a];
    if (!s) continue;
    g.userData.target.set(s.x_m, 0, s.y_m);
    g.rotation.y = -((s.heading_deg || 0) * Math.PI) / 180;
    g.userData.load.visible = !!s.load;
  }
}

function loop() {
  raf = requestAnimationFrame(loop);
  for (const g of Object.values(agvMeshes)) g.position.lerp(g.userData.target, 0.08);
  const t = performance.now() / 300;
  for (const [u, o] of Object.entries(meshes)) {
    const st = bus.machines[u]?.state;
    o.lamp.scale.y = st === 'down' || st === 'fault' ? 1 + 0.6 * Math.abs(Math.sin(t)) : 1;
  }
  controls.update();
  renderer.render(scene, camera);
  if (gc) gc.render();
}

function down(e) { downAt = [e.clientX, e.clientY]; }
function up(e) {
  if (!downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 5) return;
  const r = renderer.domElement.getBoundingClientRect();
  pointer.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(Object.values(meshes).flatMap((o) => [o.body, o.lamp]))[0];
  if (hit) sel.value = hit.object.userData.unit;
}

function resize() {
  if (!renderer) return;
  camera.aspect = host.value.clientWidth / host.value.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(host.value.clientWidth, host.value.clientHeight);
}

// ---------------------------------------------------------------- 刀路小窗
async function loadGcode() {
  const q = route.query.gcode;
  let ref_ = q;
  if (!ref_) {
    const d = await get('/design/SH-301');
    ref_ = d.gcode[0]?.gcode_ref;
  }
  if (ref_) gcode.value = await (await fetch(ref_)).text();
}
function initGc() {
  if (!gcHost.value || gc) return;
  const w = gcHost.value.clientWidth, h = 200;
  const s = new THREE.Scene();
  s.background = new THREE.Color('#F6F7F4');
  const cam = new THREE.PerspectiveCamera(40, w / h, 0.1, 2000);
  const r = new THREE.WebGLRenderer({ antialias: true });
  r.setSize(w, h);
  gcHost.value.appendChild(r.domElement);
  s.add(new THREE.HemisphereLight(0xffffff, 0x888888, 2));
  const pts = parseGcode(gcode.value);
  const xs = pts.map((p) => p[0]);
  const xmid = (Math.min(...xs) + Math.max(...xs)) / 2;
  // 轴段（Ø40），轴线沿 X；Z0 为最高母线
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(20, 20, 120, 48), new THREE.MeshLambertMaterial({ color: '#C7CDD1' }));
  shaft.rotation.z = Math.PI / 2; shaft.position.set(xmid, -20, 0);
  s.add(shaft);
  const tool = new THREE.Mesh(new THREE.CylinderGeometry(6, 6, 30, 24), new THREE.MeshLambertMaterial({ color: '#F2B705' }));
  s.add(tool);
  const trail = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: '#0E5E6F' }));
  s.add(trail);
  cam.position.set(xmid - 40, 70, 110);
  cam.lookAt(xmid, -5, 0);
  gc = { s, cam, r, pts, tool, trail, i: 0, f: 0, done: [], render() {
    if (gcPlaying.value) {
      const a = this.pts[this.i], b = this.pts[this.i + 1];
      if (!b) { gcPlaying.value = false; } else {
        this.f += b[3] ? 0.2 : 0.035;
        const p = [a[0] + (b[0] - a[0]) * Math.min(1, this.f), a[2] + (b[2] - a[2]) * Math.min(1, this.f)];
        this.tool.position.set(p[0], p[1] + 15, 0);
        if (!b[3]) { this.done.push(new THREE.Vector3(p[0], p[1], 0)); this.trail.geometry.setFromPoints(this.done); }
        if (this.f >= 1) { this.f = 0; this.i += 1; }
      }
    }
    this.r.render(this.s, this.cam);
  } };
  gc.tool.position.set(pts[0][0], pts[0][2] + 15, 0);
}
function playGcode() {
  initGc();
  if (!gc) return;
  gc.i = 0; gc.f = 0; gc.done = [];
  gcPlaying.value = true;
}
watch(sel, async (u) => {
  if (gc) { gc.r.dispose(); gc = null; }
  if (u === 'key-01') { await nextTick(); if (gcode.value) initGc(); }
});

let off;
onMounted(async () => {
  try {
    layout.value = await get('/layout');
    build();
    applyStatus();
    loop();
    window.addEventListener('resize', resize);
    off = watch(() => [bus.machines, bus.agvs], applyStatus, { deep: true });
    await loadGcode();
    if (route.query.gcode) sel.value = 'key-01';
  } catch (e) { err.value = '3D 车间载入失败：' + e.message; }
});
onUnmounted(() => {
  cancelAnimationFrame(raf);
  window.removeEventListener('resize', resize);
  if (off) off();
  if (renderer) renderer.dispose();
  if (gc) gc.r.dispose();
});
</script>

<style scoped>
.wrap3d { position: relative; height: calc(100vh - 64px); }
.host { position: absolute; inset: 0; }
.legend { position: absolute; left: 16px; bottom: 16px; background: rgba(255, 255, 255, .92); border-radius: 8px; padding: 8px 12px;
  display: flex; gap: 12px; flex-wrap: wrap; }
.legend i { width: 9px; height: 9px; border-radius: 2px; display: inline-block; margin-right: 5px; }
.panel { position: absolute; right: 16px; top: 16px; width: 340px; background: #fff; border-radius: 10px; border: 1px solid var(--line);
  padding: 14px 16px; max-height: calc(100% - 32px); overflow-y: auto; }
.panel h3 { font-size: 14px; margin: 6px 0; }
.x { position: absolute; right: 10px; top: 6px; border: 0; background: none; font-size: 20px; cursor: pointer; color: var(--muted); }
.gchost { width: 100%; height: 200px; margin-bottom: 8px; border-radius: 8px; overflow: hidden; }
.errbox { position: absolute; left: 16px; top: 16px; background: #fff; padding: 10px; border-radius: 8px; }
hr { border: 0; border-top: 1px solid var(--line); margin: 12px 0; }
</style>
