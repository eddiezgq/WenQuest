// Cloud projects (round 39, step 7): who is signed in, and which cloud project (and version) the open work came from.
// The work itself stays where it is (store.js / sysstore.js, kept in this browser); saving sends it to the cloud.
import { reactive, ref, watch } from 'vue'

const BASE = import.meta.env.BASE_URL + 'api'
const KEY = 'wqcam-cloud'

export const me = ref(null)                  // {login, licensed, org, name, reachable}
export const link = reactive((() => {        // the cloud project the open work belongs to
  try { const s = JSON.parse(localStorage.getItem(KEY) || 'null'); if (s && s.id) return s } catch { /* none */ }
  return { id: null, version: 0, name: '', kind: '' }
})())
watch(link, () => { try { localStorage.setItem(KEY, JSON.stringify(link)) } catch { /* private mode */ } }, { deep: true })

export function attach(p, version) { Object.assign(link, { id: p.id, version: version ?? p.version, name: p.name, kind: p.kind }) }
export function detach() { Object.assign(link, { id: null, version: 0, name: '', kind: '' }) }

export async function req(method, path, body) {
  const r = await fetch(BASE + path, body === undefined ? { method } : {
    method, headers: { 'content-type': 'application/json' }, body: JSON.stringify(body),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) {
    const d = data.detail || {}
    const e = new Error(typeof d === 'string' ? d : d.en || 'error')
    e.zh = typeof d === 'string' ? d : d.zh || d.en
    e.status = r.status
    e.data = data
    throw e
  }
  return data
}

export async function loadMe() {
  try { me.value = await req('GET', '/me') } catch { me.value = { login: false, licensed: false, reachable: false } }
}

// The site-wide sign-in page on the learning platform, coming back here afterwards (same as site/auth.js).
export function loginUrl() {
  const host = location.hostname.replace(/^www\./, '')
  const local = host === 'localhost' || host === '127.0.0.1'
  const learn = local ? 'http://localhost:8088' : location.protocol + '//learn.' + host
  return learn + '/pages/login/login?back=' + encodeURIComponent(location.href)
}
