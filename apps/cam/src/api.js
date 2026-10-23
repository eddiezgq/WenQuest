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

// Save text from the service as a file in the browser.
export function saveText(name, text, mime = 'text/plain') {
  const blob = new Blob([text], { type: mime + ';charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = name
  a.click()
  setTimeout(() => URL.revokeObjectURL(a.href), 1000)
}

// POST an object as it is (the AI calls send the project with a sentence or the language beside it).
export async function apiPost(path, obj) {
  const r = await fetch(BASE + path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(obj) })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) {
    const d = data.detail || {}
    const e = new Error(typeof d === 'string' ? d : d.en || 'error')
    e.zh = typeof d === 'string' ? d : d.zh || d.en
    e.status = r.status
    throw e
  }
  return data
}
