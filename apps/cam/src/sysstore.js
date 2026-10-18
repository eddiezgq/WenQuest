// Cam systems (round 39, step 4): the system being edited (kept in this browser), its analysis, and the example's
// precomputed CAE results. A project is either one cam (store.js) or a system (here); `kind` says which is open.
import { reactive, ref, watch } from 'vue'
import { api } from './api'

const KEY = 'wqcam-system'
const KIND = 'wqcam-kind'

function load(k) { try { const s = localStorage.getItem(k); return s ? JSON.parse(s) : null } catch { return null } }

export const kind = ref((() => { try { return localStorage.getItem(KIND) || 'cam' } catch { return 'cam' } })())
export const system = reactive(load(KEY) || {})
export const sysResult = ref(null)
export const sysError = ref(null)
export const sysBusy = ref(false)
export const caeExample = ref(null)
export const sysMode = ref('sys')

watch(kind, (k) => { try { localStorage.setItem(KIND, k) } catch { /* private mode */ } })

export function openSystem(p, exampleId = '') {
  for (const k of Object.keys(system)) delete system[k]
  Object.assign(system, JSON.parse(JSON.stringify(p)), { example_id: exampleId })
  kind.value = 'system'
  sysMode.value = 'sys'
  sysResult.value = null
  loadExampleCae()
}

export async function loadExampleCae() {
  caeExample.value = null
  if (!system.example_id) return
  try { caeExample.value = await api(`/examples/${system.example_id}/cae`) } catch { caeExample.value = null }
}

// What goes to the service: the system without the browser's own fields.
export function sysPayload() {
  const p = JSON.parse(JSON.stringify(system))
  delete p.example_id
  return p
}

let timer = null
let seq = 0
export function analyseSystemSoon(delay = 400) {
  clearTimeout(timer)
  timer = setTimeout(async () => {
    if (kind.value !== 'system' || !system.cams) return
    const mine = ++seq
    sysBusy.value = true
    try {
      const r = await api('/system', sysPayload())
      if (mine === seq) { sysResult.value = r; sysError.value = null }
    } catch (e) {
      if (mine === seq) sysError.value = e
    } finally {
      if (mine === seq) sysBusy.value = false
    }
  }, delay)
}

watch(system, () => {
  try { localStorage.setItem(KEY, JSON.stringify(system)) } catch { /* private mode */ }
  analyseSystemSoon()
}, { deep: true })
