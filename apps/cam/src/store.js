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
    mfg: blankMfg(),
    measure: blankMeasure(),
  }
}

// Manufacturing settings (step 3). Machine values are examples, to be set to the shop's machine.
export function blankMfg() {
  return {
    process: 'grind', tool_r: null, chord_tol: 0.001, depth: null, r_actual: null, table_step: 0.5,
    grind: { x_mode: 'radius', work_rpm: 10, allowances: [0.05, 0.02, 0], sparkout: 1, prog_no: 3901 },
    mill: { spindle_rpm: 3000, feed: 300, plunge_feed: 60, step_down: 2, safe_z: 5, climb: true, prog_no: 3902 },
    blank: { radius: null, plate: null },
  }
}
export function blankMeasure() {
  return { format: 'lift', align: true, data: '', rpm: null, a_allow: null, kmax: 60, low_hi: 6, comp: { lo: 1, hi: 6 }, records: [] }
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
  for (const k of ['mechanism', 'loads', 'material', 'limits', 'mfg', 'measure']) out[k] = { ...b[k], ...(p[k] || {}) }
  for (const k of ['grind', 'mill', 'blank']) out.mfg[k] = { ...b.mfg[k], ...((p.mfg || {})[k] || {}) }
  out.measure.comp = { ...b.measure.comp, ...((p.measure || {}).comp || {}) }
  if (!Array.isArray(out.measure.records)) out.measure.records = []
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

// The project with manufacturing and measurement, for the step-3 calls.
export function payloadFull(withMeasure = false) {
  const p = JSON.parse(JSON.stringify(project))
  const out = { ...payload(), title: p.title, mfg: p.mfg }
  if (withMeasure) { const { records, ...rest } = p.measure; out.measure = rest; void records }
  return out
}

// Step 3: what the design / manufacture / measure modes show; results kept for the calculation sheet.
export const mode = ref('design')
export const mfgResult = ref(null)
export const measResult = ref(null)
export const compResult = ref(null)

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

let lastDesign = ''
watch(project, () => {
  try { localStorage.setItem(KEY, JSON.stringify(project)) } catch { /* private mode: not saved */ }
  const d = JSON.stringify(payload())
  if (d !== lastDesign) { lastDesign = d; analyseSoon() }   // manufacturing settings do not change the design
}, { deep: true })

export async function loadLaws() {
  try { laws.value = await api('/laws') } catch { laws.value = [] }
}
