// Calls to the cam service (same origin, under /cam/api).
const BASE = import.meta.env.BASE_URL + 'api'

export async function api(path, body) {
  const r = await fetch(BASE + path, body === undefined ? {} : {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ project: body }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) {
    const d = data.detail || {}
    const e = new Error(typeof d === 'string' ? d : d.en || 'error')
    e.zh = typeof d === 'string' ? d : d.zh || d.en
    throw e
  }
  return data
}
