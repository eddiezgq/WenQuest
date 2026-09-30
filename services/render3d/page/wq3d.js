// WenQuest 3D scene engine (round 4): shared by the 3D animation renderer and the 3D virtual labs.
// Loads library models (glTF, one node per link, root node "zup"), drives joints by name, frames the camera,
// draws end-effector traces, frames and labels. No network access: models come as URLs the page is given
// (same origin in the renderer; data/blob URLs inside a sandboxed lab).
import * as THREE from "three";
import { GLTFLoader } from "./vendor/jsm/loaders/GLTFLoader.js";

export { THREE };

const PALETTE = { bg: 0x0f1419, light: 0xf4f6f8, grid: 0x2a343c, gridLight: 0xd5dbe0, accent: 0xf2c14e, trace: 0xe8913a };

export function stage(canvas, opts = {}) {
  const dark = opts.theme !== "light";
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha: false });
  renderer.setPixelRatio(opts.pixelRatio || 1);
  renderer.setSize(opts.width || canvas.clientWidth || 1280, opts.height || canvas.clientHeight || 720, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(dark ? PALETTE.bg : PALETTE.light);
  const camera = new THREE.PerspectiveCamera(opts.fov || 35, (opts.width || 1280) / (opts.height || 720), 0.01, 200);
  scene.add(new THREE.HemisphereLight(0xffffff, dark ? 0x223040 : 0xb8c2c8, dark ? 1.4 : 1.7));
  const sun = new THREE.DirectionalLight(0xffffff, dark ? 2.2 : 2.0);
  sun.position.set(3, 6, 4);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: 0.1, far: 30 });
  scene.add(sun);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.ShadowMaterial({ opacity: dark ? 0.35 : 0.18 }));
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);
  const grid = new THREE.GridHelper(20, 80, dark ? PALETTE.grid : PALETTE.gridLight, dark ? PALETTE.grid : PALETTE.gridLight);
  grid.material.transparent = true;
  grid.material.opacity = 0.6;
  scene.add(grid);
  return {
    THREE, renderer, scene, camera, floor, grid, sun,
    render() { renderer.render(scene, camera); },
    resize(w, h) { renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); },
  };
}

/** Load a library model. `entry` is its entry.json (joints, root, tool). Returns a handle with joint control. */
export async function loadModel(st, url, entry, opts = {}) {
  const gltf = await new GLTFLoader().loadAsync(url);
  const root = gltf.scene;
  root.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true;
    if (o.material) { o.material.metalness = 0.25; o.material.roughness = 0.55; } } });
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
                       axis: new THREE.Vector3(...j.axis).normalize() };
  }
  const h = {
    entry, root, holder, nodes, joints,
    set(values) {
      for (const [name, q] of Object.entries(values || {})) {
        const j = joints[name];
        if (!j) continue;
        j.value = q;
        if (j.type === "prismatic") {
          j.node.position.copy(j.p0).add(j.axis.clone().multiplyScalar(q).applyQuaternion(j.q0));
          j.node.quaternion.copy(j.q0);
        } else {
          j.node.quaternion.copy(j.q0).multiply(new THREE.Quaternion().setFromAxisAngle(j.axis, q));
        }
      }
      root.updateMatrixWorld(true);
    },
    get() { return Object.fromEntries(Object.entries(joints).map(([k, j]) => [k, j.value])); },
    /** World position of a point given in a link's own (Z-up, metres) frame. */
    point(link, xyz = [0, 0, 0]) {
      const n = nodes[link];
      root.updateMatrixWorld(true);
      return n ? new THREE.Vector3(...xyz).applyMatrix4(n.matrixWorld) : new THREE.Vector3();
    },
    tool() { return entry.tool ? h.point(entry.tool.link, entry.tool.xyz) : null; },
    box() { root.updateMatrixWorld(true); return new THREE.Box3().setFromObject(root); },
    /** Sit the model on the floor (y = 0) at x, z. */
    place(x = 0, z = 0) {
      holder.position.set(0, 0, 0);
      holder.updateMatrixWorld(true);
      const b = h.box();
      holder.position.set(x, -b.min.y, z);
      holder.updateMatrixWorld(true);
    },
  };
  h.set(entry.rest || {});
  h.place(opts.x || 0, opts.z || 0);
  return h;
}

/** Point the camera at a box from a direction (azimuth, elevation in degrees), filling `fill` of the view. */
export function frame(st, box, az = 35, el = 22, fill = 0.8) {
  const c = box.getCenter(new THREE.Vector3());
  const r = box.getSize(new THREE.Vector3()).length() / 2 || 0.5;
  const fov = THREE.MathUtils.degToRad(st.camera.fov);
  const dist = r / Math.sin(fov / 2) / fill;
  const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(el);
  st.camera.position.set(c.x + dist * Math.cos(e) * Math.sin(a), c.y + dist * Math.sin(e), c.z + dist * Math.cos(e) * Math.cos(a));
  st.camera.lookAt(c);
  st.camera.near = dist / 100;
  st.camera.far = dist * 20;
  st.camera.updateProjectionMatrix();
  return { center: c, dist };
}

/** A polyline that grows as points are added (end-effector trace). */
export function trace(st, color = PALETTE.trace, max = 4000) {
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

/** Coordinate axes (x red, y green, z blue) in the model's Z-up convention, attached to a link. */
export function axes(h, link, size = 0.12) {
  const g = new THREE.Group();
  const mk = (dir, color) => g.add(new THREE.ArrowHelper(new THREE.Vector3(...dir), new THREE.Vector3(), size, color, size * 0.25, size * 0.12));
  mk([1, 0, 0], 0xe74c3c); mk([0, 1, 0], 0x2ecc71); mk([0, 0, 1], 0x3b82c4);
  (h.nodes[link] || h.root).add(g);
  return g;
}

/** Smooth 0..1 easing. */
export const ease = (t) => (t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t));
export const lerp = (a, b, t) => a + (b - a) * t;
