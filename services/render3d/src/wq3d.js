// WenQuest 3D engine (round 4): the 3D animation renderer and the 3D virtual labs share it.
// Loads library models (glTF with one node per link under a root node "zup"), drives joints by name, and plays
// declarative scene scripts deterministically: seek(t) always gives the same picture for the same t, so the
// renderer can step frame by frame. No network access is needed: models come as ArrayBuffers (base64 in the page).
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

export { THREE, OrbitControls };

const THEMES = {
  dark: { bg: 0x0f1419, grid: 0x26313a, hemi: [0xffffff, 0x223040, 1.4], sun: 2.2, shadow: 0.35, ink: "#e8eef2", muted: "#9fb0bd" },
  light: { bg: 0xf4f6f8, grid: 0xd5dbe0, hemi: [0xffffff, 0xb8c2c8, 1.7], sun: 2.0, shadow: 0.18, ink: "#1f2a33", muted: "#5b6b75" },
};

export function stage(canvas, opts = {}) {
  const th = THEMES[opts.theme] || THEMES.dark;
  const w = opts.width || 1280, h = opts.height || 720;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(opts.pixelRatio || 1);
  renderer.setSize(w, h, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(th.bg);
  const camera = new THREE.PerspectiveCamera(opts.fov || 35, w / h, 0.01, 200);
  scene.add(new THREE.HemisphereLight(...th.hemi));
  const sun = new THREE.DirectionalLight(0xffffff, th.sun);
  sun.position.set(3, 6, 4);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -5, right: 5, top: 5, bottom: -5, near: 0.1, far: 40 });
  scene.add(sun, sun.target);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShadowMaterial({ opacity: th.shadow }));
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);
  const grid = new THREE.GridHelper(30, 120, th.grid, th.grid);
  grid.material.transparent = true;
  grid.material.opacity = 0.55;
  scene.add(grid);
  return {
    THREE, renderer, scene, camera, floor, grid, sun, theme: th, width: w, height: h,
    render() { renderer.render(scene, camera); },
    resize(nw, nh) { renderer.setSize(nw, nh, false); camera.aspect = nw / nh; camera.updateProjectionMatrix(); },
  };
}

function b64ToBuffer(b64) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out.buffer;
}

/** Load a library model: `src` is an ArrayBuffer, a base64 string or a URL; `entry` its entry.json. */
export async function loadModel(st, src, entry, opts = {}) {
  const loader = new GLTFLoader();
  let gltf;
  if (typeof src === "string" && !/^(https?:|\/|\.|blob:|data:)/.test(src)) src = b64ToBuffer(src);
  if (src instanceof ArrayBuffer) gltf = await new Promise((ok, bad) => loader.parse(src, "", ok, bad));
  else gltf = await loader.loadAsync(src);
  const root = gltf.scene;
  root.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true; o.receiveShadow = true;
      if (o.material) { o.material.metalness = 0.25; o.material.roughness = 0.55; o.material.transparent = true; }
    }
  });
  const holder = new THREE.Group();
  holder.add(root);
  st.scene.add(holder);
  const nodes = {};
  root.traverse((o) => { if (o.name) nodes[o.name] = o; });
  const joints = {};
  for (const j of entry.joints || []) {
    const n = nodes[j.child];
    if (!n) continue;
    joints[j.name] = { ...j, node: n, p0: n.position.clone(), q0: n.quaternion.clone(), value: 0,
                       axisV: new THREE.Vector3(...j.axis).normalize() };
  }
  const linkNodes = (entry.links || []).map((l) => nodes[l]).filter(Boolean);
  const h = {
    entry, root, holder, nodes, joints, links: linkNodes,
    set(values) {
      for (const [name, q] of Object.entries(values || {})) {
        const j = joints[name];
        if (!j || !Number.isFinite(q)) continue;
        j.value = q;
        if (j.type === "prismatic") {
          j.node.position.copy(j.p0).add(j.axisV.clone().multiplyScalar(q).applyQuaternion(j.q0));
          j.node.quaternion.copy(j.q0);
        } else {
          j.node.quaternion.copy(j.q0).multiply(new THREE.Quaternion().setFromAxisAngle(j.axisV, q));
        }
      }
      root.updateMatrixWorld(true);
    },
    get() { return Object.fromEntries(Object.entries(joints).map(([k, j]) => [k, j.value])); },
    point(link, xyz = [0, 0, 0]) {
      const n = nodes[link];
      root.updateMatrixWorld(true);
      return n ? new THREE.Vector3(...xyz).applyMatrix4(n.matrixWorld) : holder.position.clone();
    },
    tool() { return entry.tool ? h.point(entry.tool.link, entry.tool.xyz) : null; },
    /** A point of a link in the robot's own base frame (Z up, metres) — for readouts that match the textbook. */
    local(link, xyz = [0, 0, 0]) {
      const base = nodes[entry.root] || root;
      root.updateMatrixWorld(true);
      const w = h.point(link, xyz);
      const inv = new THREE.Matrix4().copy(base.matrixWorld).invert();
      const p = w.applyMatrix4(inv);
      return [p.x, p.y, p.z];
    },
    toolLocal() { return entry.tool ? h.local(entry.tool.link, entry.tool.xyz) : null; },
    box() { root.updateMatrixWorld(true); return new THREE.Box3().setFromObject(root); },
    place(x = 0, z = 0, yaw = 0) {
      holder.position.set(0, 0, 0);
      holder.rotation.set(0, yaw, 0);
      holder.updateMatrixWorld(true);
      const b = h.box();
      holder.position.set(x, -b.min.y, z);
      holder.updateMatrixWorld(true);
    },
    visible(v) { holder.visible = v; },
    opacity(a) { root.traverse((o) => { if (o.isMesh && o.material) o.material.opacity = a; }); },
  };
  h.set(entry.rest || {});
  h.place(opts.x || 0, opts.z || 0, opts.yaw || 0);
  return h;
}

/** Camera from a direction (azimuth, elevation, degrees) at a box, filling `fill` of the view. */
export function frame(st, box, az = 35, el = 22, fill = 0.8) {
  const c = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const r = Math.max(size.x, size.y, size.z, 0.05) * 0.62;   // the biggest dimension, not the bounding sphere
  const fov = THREE.MathUtils.degToRad(st.camera.fov);
  const dist = r / Math.sin(fov / 2) / fill;
  const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(el);
  st.camera.position.set(c.x + dist * Math.cos(e) * Math.sin(a), c.y + dist * Math.sin(e), c.z + dist * Math.cos(e) * Math.cos(a));
  st.camera.lookAt(c);
  st.camera.near = dist / 100;
  st.camera.far = dist * 30;
  st.camera.updateProjectionMatrix();
  st.sun.position.set(c.x + 3 * r, c.y + 6 * r, c.z + 4 * r);
  st.sun.target.position.copy(c);
  return { center: c, dist };
}

export function trace(st, color = 0xe8913a, max = 6000) {
  const pos = new Float32Array(max * 3);
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setDrawRange(0, 0);
  const line = new THREE.Line(g, new THREE.LineBasicMaterial({ color }));
  line.frustumCulled = false;
  st.scene.add(line);
  let n = 0;
  return {
    line,
    add(p) { if (n >= max) return; pos.set([p.x, p.y, p.z], n * 3); n++; g.setDrawRange(0, n); g.attributes.position.needsUpdate = true; },
    clear() { n = 0; g.setDrawRange(0, 0); },
    get count() { return n; },
  };
}

/** Coordinate axes (x red, y green, z blue; the model's Z-up convention) attached to a link. */
export function axes(h, link, size = 0.12) {
  const g = new THREE.Group();
  const mk = (dir, color) => g.add(new THREE.ArrowHelper(new THREE.Vector3(...dir), new THREE.Vector3(), size, color, size * 0.25, size * 0.12));
  mk([1, 0, 0], 0xe74c3c); mk([0, 1, 0], 0x2ecc71); mk([0, 0, 1], 0x3b82c4);
  (h.nodes[link] || h.root).add(g);
  return g;
}

export const ease = (t) => (t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t));
export const lerp = (a, b, t) => a + (b - a) * t;

/** Value of smoothly interpolated keys [[t, v], ...] at time t (eased between keys, held outside). */
export function keyed(keys, t) {
  if (!keys || !keys.length) return undefined;
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const [t0, v0] = keys[i - 1], [t1, v1] = keys[i];
      return lerp(v0, v1, ease((t - t0) / Math.max(1e-6, t1 - t0)));
    }
  }
  return keys[keys.length - 1][1];
}

function linear(keys, t) {
  if (!keys || !keys.length) return undefined;
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const [t0, v0] = keys[i - 1], [t1, v1] = keys[i];
      return lerp(v0, v1, (t - t0) / Math.max(1e-6, t1 - t0));
    }
  }
  return keys[keys.length - 1][1];
}

/** Mechanism table (rows {input_deg, joint...}) at an input angle in degrees (wraps at 360). */
function motionAt(rows, deg) {
  if (!rows || !rows.length) return {};
  const d = ((deg % 360) + 360) % 360;
  let i = rows.findIndex((r) => r.input_deg >= d);
  if (i <= 0) i = 1;
  const a = rows[i - 1], b = rows[Math.min(i, rows.length - 1)];
  const f = (d - a.input_deg) / Math.max(1e-6, b.input_deg - a.input_deg);
  const out = {};
  for (const k of Object.keys(a)) {
    if (k === "input_deg") continue;
    let va = a[k], vb = b[k];
    if (Math.abs(vb - va) > Math.PI) vb += va > vb ? 2 * Math.PI : -2 * Math.PI;   // angle wrap
    out[k] = lerp(va, vb, f);
  }
  return out;
}

/**
 * A scene player. `script`: {duration, theme, title, no, actors, tracks, spin, motion, explode, camera, traces,
 * frames, captions, labels}; `models`: {id: {entry, glb (base64), motion (rows)}}; `overlay`: an element for text.
 */
// --- 车间 workshop: the digital factory's floor, units (coloured by state) and AGVs on their recorded routes ----------
const STATE_COLOR = { run: 0x3fae6a, idle: 0xe0a83a, setup: 0x4a8fd6, down: 0xd04a3a, fault: 0xd04a3a };
export function workshop(st, w) {
  const g = new THREE.Group();
  const fw = w.floor.w, fd = w.floor.d, cx = fw / 2, cz = fd / 2;
  const P = (x, y) => new THREE.Vector3(x - cx, 0, y - cz);          // factory plan (x, y down) -> scene (x, z)
  const floor = new THREE.Mesh(new THREE.BoxGeometry(fw, 0.05, fd), new THREE.MeshStandardMaterial({ color: 0x2a3440, roughness: 0.9 }));
  floor.position.y = -0.025; floor.receiveShadow = true; g.add(floor);
  for (const a of w.aisles || []) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(a.w, a.d), new THREE.MeshBasicMaterial({ color: 0x3a4654 }));
    m.rotation.x = -Math.PI / 2; m.position.copy(P(a.x, a.y)); m.position.y = 0.01; g.add(m);
  }
  const units = {};
  for (const u of w.units || []) {
    const h = u.h || 1.6;
    const mat = new THREE.MeshStandardMaterial({ color: u.store ? 0x8aa4bf : 0xc9d2db, roughness: 0.6, metalness: 0.1 });
    const m = new THREE.Mesh(new THREE.BoxGeometry(u.w, h, u.d), mat);
    m.position.copy(P(u.x, u.y)); m.position.y = h / 2; m.castShadow = true; m.receiveShadow = true;
    const lamp = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.5, 16), new THREE.MeshStandardMaterial({ color: 0x777777, emissive: 0x000000 }));
    lamp.position.set(m.position.x + u.w / 2 - 0.3, h + 0.25, m.position.z - u.d / 2 + 0.3);
    if (u.highlight) { mat.emissive = new THREE.Color(0xc4561a); mat.emissiveIntensity = 0.35; }
    g.add(m, lamp);
    units[u.id] = { spec: u, mesh: m, lamp, el: null };
  }
  const agvs = {};
  for (const a of w.agvs || []) {
    const body = new THREE.Group();
    const base = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.35, 0.85), new THREE.MeshStandardMaterial({ color: 0xf28c28, roughness: 0.5 }));
    base.position.y = 0.25; base.castShadow = true;
    const load = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.4, 0.55), new THREE.MeshStandardMaterial({ color: 0xd8c39a }));
    load.position.y = 0.62; load.visible = false;
    body.add(base, load); g.add(body);
    agvs[a.id] = { spec: a, body, load, el: null };
  }
  st.scene.add(g);
  st.grid.visible = false;
  Object.assign(st.sun.shadow.camera, { left: -fw / 2 - 2, right: fw / 2 + 2, top: fd / 2 + 2, bottom: -fd / 2 - 2, far: 120 });
  st.sun.position.set(-fw * 0.2, fw * 0.6, fd * 0.4);
  st.sun.shadow.camera.updateProjectionMatrix();
  st.camera.far = 400; st.camera.updateProjectionMatrix();
  const at = (keys, t) => {                       // [[t, x, y, loaded], ...] -> position, heading, loaded
    if (!keys.length) return null;
    let k = keys.findIndex((x) => x[0] > t);
    if (k === -1) return { x: keys[keys.length - 1][1], y: keys[keys.length - 1][2], hd: null, load: !!keys[keys.length - 1][3] };
    if (k === 0) return { x: keys[0][1], y: keys[0][2], hd: null, load: !!keys[0][3] };
    const a = keys[k - 1], b = keys[k], f = (t - a[0]) / Math.max(1e-6, b[0] - a[0]);
    const moving = Math.hypot(b[1] - a[1], b[2] - a[2]) > 1e-3;
    return { x: lerp(a[1], b[1], f), y: lerp(a[2], b[2], f), hd: moving ? Math.atan2(b[2] - a[2], b[1] - a[1]) : null, load: !!a[3] };
  };
  const stateAt = (states, t) => { let s = null; for (const [ts, v] of states || []) { if (ts > t) break; s = v; } return s; };
  return {
    group: g,
    boxOf(target) {
      if (target === "workshop" || target === "all" || !target) return new THREE.Box3().setFromObject(g);
      if (units[target]) return new THREE.Box3().setFromObject(units[target].mesh).expandByScalar(4);
      if (agvs[target]) return new THREE.Box3().setFromObject(agvs[target].body).expandByScalar(5);
      return null;
    },
    seek(t) {
      for (const u of Object.values(units)) {
        const s = stateAt(u.spec.states, t);
        u.lamp.material.color.setHex(STATE_COLOR[s] || 0x777777);
        u.lamp.material.emissive.setHex(STATE_COLOR[s] || 0x000000);
        u.lamp.material.emissiveIntensity = s ? 0.8 : 0;
      }
      for (const a of Object.values(agvs)) {
        const p = at(a.spec.keys, t);
        if (!p) continue;
        a.body.position.copy(P(p.x, p.y));
        if (p.hd !== null) a.body.rotation.y = -p.hd;
        a.load.visible = p.load;
      }
      g.updateMatrixWorld(true);
    },
    labels(t, ov, txt) {
      const put = (o, obj, text, cls) => {
        if (!o.el) { o.el = document.createElement("div"); o.el.className = "lab " + cls; ov.appendChild(o.el); }
        const b = new THREE.Box3().setFromObject(obj);
        const p = new THREE.Vector3((b.min.x + b.max.x) / 2, b.max.y + 0.3, (b.min.z + b.max.z) / 2).project(st.camera);
        const vis = p.z < 1 && Math.abs(p.x) < 1.05 && Math.abs(p.y) < 1.05;
        o.el.style.display = vis ? "block" : "none";
        o.el.style.left = `${((p.x + 1) / 2) * st.width}px`;
        o.el.style.top = `${((1 - p.y) / 2) * st.height - 4}px`;
        o.el.innerHTML = text;
      };
      for (const u of Object.values(units)) if (w.labels !== false) put(u, u.mesh, txt(u.spec.name), "unit");
      for (const a of Object.values(agvs)) put(a, a.body, a.spec.id.toUpperCase(), "agv");
      if (w.clock) {
        let c = ov.querySelector(".clock");
        if (!c) { c = document.createElement("div"); c.className = "clock"; ov.appendChild(c); }
        const k = w.clock;       // [t0 seconds-of-day, speed]
        const s = Math.floor(k[0] + t * k[1]);
        c.textContent = `${String(Math.floor(s / 3600) % 24).padStart(2, "0")}:${String(Math.floor(s / 60) % 60).padStart(2, "0")} UTC · ×${Math.round(k[1])}`;
      }
    },
  };
}

export async function player(canvas, overlay, script, models) {
  const st = stage(canvas, { width: script.width || 1280, height: script.height || 720, theme: script.theme });
  const lang = script.lang || "both";
  const txt = (p) => (typeof p === "string" ? p : lang === "zh" ? p[0] : lang === "en" ? (p[1] || p[0]) : p[0] && p[1] && p[0] !== p[1] ? `${p[0]}<br><span class="en">${p[1]}</span>` : p[0] || p[1] || "");
  const actors = {};
  for (const a of script.actors || []) {
    const m = models[a.model];
    if (!m) throw new Error(`model ${a.model} missing`);
    const h = await loadModel(st, m.glb, m.entry, { x: a.x || 0, z: a.z || 0, yaw: (a.yaw || 0) * Math.PI / 180 });
    if (a.pose) h.set(a.pose);
    actors[a.id] = { spec: a, h, rows: m.motion || [], base: {} };
    // explode: remember each link's resting offset from the model centre
    const c = h.box().getCenter(new THREE.Vector3());
    for (const n of h.links) actors[a.id].base[n.name] = { p: n.position.clone(), dir: n.getWorldPosition(new THREE.Vector3()).sub(c) };
  }
  const shop = script.workshop ? workshop(st, script.workshop) : null;
  const traceObjs = (script.traces || []).map((t) => ({ spec: t, tr: trace(st, t.color || 0xe8913a), last: -1 }));
  for (const f of script.frames || []) {
    const a = actors[f.actor];
    if (a) axes(a.h, f.link || a.h.entry.root, f.size || 0.12);
  }
  // text overlay: title (top-left), captions (bottom), labels (above actors)
  const css = `#ov{position:absolute;inset:0;pointer-events:none;font-family:"Noto Sans CJK SC","Noto Sans SC",sans-serif;color:${st.theme.ink}}
    #ov .ttl{position:absolute;left:44px;top:30px;font-size:30px;font-weight:700}#ov .ttl .no{color:#f2c14e;margin-right:14px}
    #ov .ttl .en{display:block;font-size:17px;font-weight:400;color:${st.theme.muted}}
    #ov .cap{position:absolute;left:0;right:0;bottom:44px;text-align:center;font-size:28px;text-shadow:0 1px 3px rgba(0,0,0,.6)}
    #ov .cap .en,#ov .lab .en{font-size:18px;color:${st.theme.muted}}
    #ov .lab{position:absolute;transform:translate(-50%,-100%);font-size:20px;text-align:center;background:rgba(15,20,25,.55);padding:4px 10px;border-radius:6px;white-space:nowrap}
    #ov .lab.unit{font-size:13px;padding:2px 6px}#ov .lab.unit .en{font-size:11px}#ov .lab.agv{font-size:12px;background:rgba(242,140,40,.85);color:#1a1a1a}
    #ov .clock{position:absolute;right:44px;top:34px;font-size:18px;color:${st.theme.muted};font-variant-numeric:tabular-nums}
    #ov .src{position:absolute;right:44px;bottom:14px;font-size:13px;color:${st.theme.muted}}`;
  overlay.innerHTML = `<style>${css}</style><div id="ov"><div class="ttl"></div><div class="cap"></div></div>`;
  const ov = overlay.querySelector("#ov"), ttl = ov.querySelector(".ttl"), cap = ov.querySelector(".cap");
  if (script.source) { const sd = document.createElement("div"); sd.className = "src"; sd.textContent = script.source; ov.appendChild(sd); }
  if (script.title) ttl.innerHTML = `${script.no ? `<span class="no">${script.no}</span>` : ""}${script.title[0] || ""}<span class="en">${script.title[1] || ""}</span>`;
  const labs = (script.labels || []).map((l) => { const d = document.createElement("div"); d.className = "lab"; ov.appendChild(d); return { spec: l, el: d }; });

  const poseAt = (a, t) => {
    const vals = {};
    for (const tr of script.tracks || []) if (tr.actor === a.spec.id) vals[tr.joint] = keyed(tr.keys, t);
    for (const sp of script.spin || []) if (sp.actor === a.spec.id) {
      const t0 = sp.from ?? 0, t1 = sp.to ?? 1e9;
      vals[sp.joint] = (sp.rate || 6) * (Math.min(Math.max(t, t0), t1) - t0);
    }
    for (const mo of script.motion || []) if (mo.actor === a.spec.id) Object.assign(vals, motionAt(a.rows, linear(mo.keys, t) || 0));
    return vals;
  };
  const cameraAt = (t) => {
    const keys = (script.camera && script.camera.keys) || [[0, 35, 22, 0.8, "all"]];
    let k = keys.findIndex((x) => x[0] > t);
    if (k === -1) k = keys.length;
    const a = keys[Math.max(0, k - 1)], b = keys[Math.min(k, keys.length - 1)];
    const f = ease((t - a[0]) / Math.max(1e-6, b[0] - a[0]));
    const boxOf = (target) => {
      if (shop) {
        const b = shop.boxOf(target);
        if (b) return b;
      }
      if (target && target !== "all" && actors[target]) return actors[target].h.box();
      const bx = new THREE.Box3();
      for (const x of Object.values(actors)) if (x.h.holder.visible) bx.union(x.h.box());
      return bx.isEmpty() ? new THREE.Box3(new THREE.Vector3(-0.5, 0, -0.5), new THREE.Vector3(0.5, 1, 0.5)) : bx;
    };
    const ba = boxOf(a[4]), bb = boxOf(b[4]);
    const box = new THREE.Box3(ba.min.clone().lerp(bb.min, f), ba.max.clone().lerp(bb.max, f));
    frame(st, box, lerp(a[1], b[1], f), lerp(a[2], b[2], f), lerp(a[3] ?? 0.8, b[3] ?? 0.8, f));
  };

  function seek(t) {
    for (const a of Object.values(actors)) {
      const ap = a.spec.appear;
      a.h.visible(!ap || (t >= ap[0] && t <= ap[1]));
      a.h.set(poseAt(a, t));
      for (const ex of script.explode || []) {
        if (ex.actor !== a.spec.id) continue;
        const amt = keyed(ex.keys, t) || 0;
        for (const n of a.h.links) {
          const b = a.base[n.name];
          if (b && n.parent) n.position.copy(b.p).add(b.dir.clone().multiplyScalar(amt).applyQuaternion(n.parent.getWorldQuaternion(new THREE.Quaternion()).invert()));
        }
        a.h.root.updateMatrixWorld(true);
      }
    }
    for (const o of traceObjs) {
      const a = actors[o.spec.actor];
      if (!a) continue;
      const t0 = o.spec.from ?? 0, t1 = Math.min(t, o.spec.to ?? 1e9);
      if (t1 < o.last) { o.tr.clear(); o.last = -1; }
      const step = 1 / 30;
      for (let s = Math.max(t0, o.last < 0 ? t0 : o.last + step); s <= t1 + 1e-9; s += step) {
        a.h.set(poseAt(a, s));
        const p = a.h.tool() || a.h.point(o.spec.link || a.h.entry.root);
        o.tr.add(p);
        o.last = s;
      }
      a.h.set(poseAt(a, t));
    }
    if (shop) shop.seek(t);
    cameraAt(t);
    if (shop) shop.labels(t, ov, txt);
    const c = (script.captions || []).find((x) => t >= x[0] && t < x[1]);
    cap.innerHTML = c ? txt(c[2]) : "";
    for (const l of labs) {
      const [t0, t1, id, text] = l.spec;
      const a = actors[id];
      if (!a || t < t0 || t > t1 || !a.h.holder.visible) { l.el.style.display = "none"; continue; }
      const b = a.h.box();
      const p = new THREE.Vector3((b.min.x + b.max.x) / 2, b.max.y, (b.min.z + b.max.z) / 2).project(st.camera);
      l.el.style.display = "block";
      l.el.style.left = `${((p.x + 1) / 2) * st.width}px`;
      l.el.style.top = `${((1 - p.y) / 2) * st.height - 8}px`;
      l.el.innerHTML = txt(text);
    }
    st.render();
  }
  seek(0);
  return { st, actors, seek, duration: script.duration || 10 };
}
