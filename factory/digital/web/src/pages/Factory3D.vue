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
import { createWorkshop, HEX } from '../lib/workshop3d';
import { get } from '../lib/api';
import { bus } from '../lib/bus';
import { STATE } from '../lib/fmt';
import { parseGcode } from '../lib/gcode';

const route = useRoute();
const host = ref(null);
const gcHost = ref(null);
const layout = ref(null);
const sel = ref(null);
const err = ref('');
const gcode = ref('');
const gcPlaying = ref(false);
const m = computed(() => bus.machines[sel.value] || {});
let ws, downAt;
let gc = null;             // 刀路小窗

function applyStatus() { if (ws) ws.update(bus.machines, bus.agvs); }
function down(e) { downAt = [e.clientX, e.clientY]; }
function up(e) {
  if (!ws || !downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 5) return;
  const u = ws.pick(e);
  if (u) sel.value = u;
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
    ws = createWorkshop(host.value, layout.value, { onFrame: () => { if (gc) gc.render(); } });
    applyStatus();
    off = watch(() => [bus.machines, bus.agvs], applyStatus, { deep: true });
    await loadGcode();
    if (route.query.gcode) sel.value = 'key-01';
  } catch (e) { err.value = '3D 车间载入失败：' + e.message; }
});
onUnmounted(() => {
  if (off) off();
  if (ws) ws.dispose();
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
