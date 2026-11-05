// The project being edited, kept in this browser; every change is sent to the kernel after a short pause.
import { reactive, ref, watch } from 'vue'
import { api } from './api'

const KEY = 'wqbearing-project'
export function blank() {
  return {
    title: { zh: '', en: '' }, type: 'deep_groove',
    size: { d: null, D: null, B: null },
    inner: { Dw: null, Z: null, dm: null, fi: null, fo: null, Pd: null, alpha0_deg: null, h_i: null, h_o: null, Lw: null, Lwe: null, alpha_o_deg: null, alpha_i_deg: null, alpha_f_deg: null, R_end: null },
    profile: { kind: 'straight', R: null, flat: null, points: [] },
    flex: { cam: 'cosine', w0: null, a: null, b: null, points: [], F: null, beta_deg: null, sig_i_allow: null, sig_a_allow: null },
    alignment: { theta_arcmin: null },
    pair: { arrangement: 'single', preload: null, spacing: null, mount: 'pair', setting: 'endplay', endplay: null, sweep_from: null, sweep_to: null },
    material: { E: 206000, nu: 0.3, density: null },
    scenario: { kind: 'generic', fp: null },
    loads: { Fr: null, Fa: null, M: null, n: null },
    fits: { shaft_I: null, housing_I: null, T_i: 20, T_o: 20 },
    lube: { eta0: null, alpha_p: null, sigma: null },
    limits: { p_static: null, p_fatigue: null, gap_min: null, wall_min: null },
    design_note: '',
    catalog: null,  // the catalogue row the project was set from (plan section 十七 K3), or null
  }
}
function loadSaved() {
  try { const s = localStorage.getItem(KEY); return s ? JSON.parse(s) : null } catch { return null }
}
export const project = reactive(blank())
export const result = ref(null)
{ const saved = loadSaved(); if (saved) replace(saved) }
export const error = ref(null)
export const busy = ref(false)

export function replace(p) {
  const b = blank()
  for (const k of Object.keys(b)) project[k] = typeof b[k] === 'object' && b[k] ? { ...b[k], ...(p[k] || {}) } : p[k] ?? b[k]
  project.scenario = p.scenario ? JSON.parse(JSON.stringify(p.scenario)) : b.scenario
  if (p.limits && p.limits.p_max != null && p.limits.p_static == null) project.limits.p_static = p.limits.p_max  // saved before step 3
  delete project.limits.p_max
  project.note = p.note || null
}

let timer = 0, seq = 0
export function analyseSoon() {
  clearTimeout(timer)
  timer = setTimeout(async () => {
    const my = ++seq
    busy.value = true
    try {
      const r = await api('/analyse', JSON.parse(JSON.stringify(project)))
      if (my === seq) { result.value = r; error.value = null }
    } catch (e) { if (my === seq) { error.value = e } }
    finally { if (my === seq) busy.value = false }
  }, 250)
}
watch(project, () => {
  try { localStorage.setItem(KEY, JSON.stringify(project)) } catch { /* private mode */ }
  analyseSoon()
}, { deep: true })
