// Cloud projects (round 64, step 7; the same as the cam software's): who is signed in, and which cloud project (and
// version) the open work came from: one link for the design project, one for the process template. The work itself
// stays where it is (kept in this browser); saving sends it to the cloud.
import { reactive, ref, watch } from 'vue'

const BASE = import.meta.env.BASE_URL + 'api'
const KEY = 'wqbearing-cloud'

export const me = ref(null)                  // {login, licensed, org, name, reachable}
const blankLink = () => ({ id: null, version: 0, name: '', kind: '' })
export const links = reactive((() => {        // {design, process}: the cloud project each open work belongs to
  try { const s = JSON.parse(localStorage.getItem(KEY) || 'null'); if (s && s.design && s.process) return s } catch { /* none */ }
  return { design: blankLink(), process: blankLink() }
})())
watch(links, () => { try { localStorage.setItem(KEY, JSON.stringify(links)) } catch { /* private mode */ } }, { deep: true })

export function attach(kind, p, version) { Object.assign(links[kind], { id: p.id, version: version ?? p.version, name: p.name, kind: p.kind }) }
export function detach(kind) { Object.assign(links[kind], blankLink()) }

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
