// The project being edited, kept in this browser (round 39: no sign-in yet), and the latest analysis.
import { reactive, ref, watch } from 'vue'
import { api } from './api'

const KEY = 'wqcam-project'

export function blank() {
  return {
    title: { zh: '新凸轮', en: 'New cam' },
    program: { unit: 'mm', segments: [
      { kind: 'rise', deg: 120, h: 20, law: 'cycloidal' }, { kind: 'dwell', deg: 60 },
      { kind: 'return', deg: 120, h: 20, law: 'poly345' }, { kind: 'dwell', deg: 60 }] },
    mechanism: { follower: 'translating', contact: 'roller', rb: 40, rr: 10, e: 0, a: 0, L: 0, sigma: 1, groove: false, width: null },
    loads: { rpm: null, mass: null, inertia: null, k: null, preload: null, load: null },
    material: { E1: null, nu1: null, E2: null, nu2: null },
    limits: { phi_rise_deg: null, phi_return_deg: null, rho_min: null, stress: null, torque: null },
  }
}

function load() {
  try { const s = localStorage.getItem(KEY); if (s) return JSON.parse(s) } catch { /* nothing saved */ }
  return null
}

export const project = reactive(normalise(load() || blank()))
export const result = ref(null)
export const error = ref(null)
export const busy = ref(false)
export const laws = ref([])

export function normalise(p) {
  const b = blank()
  const out = { ...b, ...p }
  for (const k of ['mechanism', 'loads', 'material', 'limits']) out[k] = { ...b[k], ...(p[k] || {}) }
  out.program = p.program || b.program
  if (!out.title || typeof out.title !== 'object') out.title = { zh: String(out.title || '凸轮'), en: String(out.title || 'Cam') }
  return out
}

export function replace(p) {
  const n = normalise(JSON.parse(JSON.stringify(p)))
  for (const k of Object.keys(project)) delete project[k]
  Object.assign(project, n)
}

// What is sent to the kernel: empty fields left out (unknown, not zero).
export function payload() {
  const strip = (o) => Object.fromEntries(Object.entries(o).filter(([, v]) => v !== null && v !== '' && v !== undefined))
  const p = JSON.parse(JSON.stringify(project))
  const m = strip(p.mechanism)
  if (m.follower === 'translating') { delete m.a; delete m.L } else delete m.e
  if (m.contact !== 'roller') { delete m.rr; m.groove = false }
  return { program: p.program, mechanism: m, loads: strip(p.loads), material: strip(p.material), limits: strip(p.limits) }
}

let timer = null
let seq = 0
export function analyseSoon(delay = 250) {
  clearTimeout(timer)
  timer = setTimeout(async () => {
    const mine = ++seq
    busy.value = true
    try {
      const r = await api('/analyse', payload())
      if (mine === seq) { result.value = r; error.value = null }
    } catch (e) {
      if (mine === seq) error.value = e
    } finally {
      if (mine === seq) busy.value = false
    }
  }, delay)
}

watch(project, () => {
  try { localStorage.setItem(KEY, JSON.stringify(project)) } catch { /* private mode: not saved */ }
  analyseSoon()
}, { deep: true })

export async function loadLaws() {
  try { laws.value = await api('/laws') } catch { laws.value = [] }
}
