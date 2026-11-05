<script setup>
// The company's product catalogue (round 64, plan section 十七 K3): the company loads its own catalogue workbook into
// its cloud space (only its own accounts see it), picks a model, and the outside sizes fill in. The inner sizes
// (rollers, angles) are the company's to fill; until then the checks cannot run. The catalogue's load ratings are
// shown as the maker's figures, not used in any check.
import { computed, onMounted, ref } from 'vue'
import { t, lang } from '../i18n'
import { me, req, loadMe, loginUrl } from '../cloud'
import { project, replace, blank, analyseSoon, result } from '../store'

const emit = defineEmits(['close'])
const BASE = import.meta.env.BASE_URL + 'api'

const list = ref([])          // the company's catalogues (cloud projects of kind "catalog")
const cur = ref(null)         // {id, version, name, body: {rows, findings}}
const draft = ref(null)       // a workbook just read, not saved yet: {rows, findings, name}
const busy = ref(false)
const msg = ref('')
const err = ref('')
const q = ref('')
const sure = ref(false)
const fileIn = ref(null)
const zh = computed(() => lang.value === 'zh')
const words = (e) => (zh.value ? e.zh || e.message : e.message)
const OPENS = { metric: 'tapered', inch: 'tapered', nu: 'cylindrical', crossed: 'crossed' }
const LEVEL = { '疑似': 'catSuspect', '请确认': 'catConfirm', '未知': 'catUnknown' }
const TABLE = { metric: 'catMetric', inch: 'catInch', double: 'catDouble', nu: 'catNU', crossed: 'catCrossed' }

async function run(fn) {
  busy.value = true; err.value = ''; msg.value = ''
  try { await fn() } catch (e) { err.value = words(e) } finally { busy.value = false }
}
async function refresh() { list.value = (await req('GET', '/projects?kind=catalog')).projects }
const open = (id) => run(async () => {
  const r = await req('GET', `/projects/${id}`)
  cur.value = { id: r.id, version: r.opened, name: r.name, body: r.body }
  draft.value = null; q.value = ''
})

async function readFile(e) {
  const f = e.target.files?.[0]
  e.target.value = ''
  if (!f) return
  await run(async () => {
    const r = await fetch(BASE + '/catalog/read', { method: 'POST', headers: { 'content-type': 'application/octet-stream' }, body: await f.arrayBuffer() })
    const data = await r.json().catch(() => ({}))
    if (!r.ok) { const d = data.detail || {}; throw Object.assign(new Error(d.en || 'error'), { zh: d.zh }) }
    draft.value = { rows: data.rows, findings: data.findings, name: f.name.replace(/\.xlsx$/i, '') }
  })
}
const body = (d) => ({ rows: d.rows, findings: d.findings, source: d.name, read: new Date().toISOString() })
const saveNew = () => run(async () => {
  const n = (draft.value.name || '').trim()
  if (!n) { err.value = t('cloudNeedName'); return }
  const r = await req('POST', '/projects', { name: n, kind: 'catalog', body: body(draft.value) })
  await refresh(); await open(r.id); msg.value = t('catSaved')
})
const replaceCur = () => run(async () => {
  await req('PUT', `/projects/${cur.value.id}`, { body: body(draft.value), base: cur.value.version })
  const id = cur.value.id
  await refresh(); await open(id); msg.value = t('catReplaced')
})
const remove = () => run(async () => {
  if (!sure.value) { sure.value = true; return }
  await req('DELETE', `/projects/${cur.value.id}`)
  sure.value = false; cur.value = null
  await refresh()
})

const shown = computed(() => draft.value || cur.value?.body || null)
const ORDER = { '疑似': 0, '请确认': 1, '未知': 2 }
const finds = computed(() => [...(shown.value?.findings || [])].sort((a, b) => ORDER[a.level] - ORDER[b.level] || (Number(a.page) || 999) - (Number(b.page) || 999)))
const count = (lv) => (shown.value?.findings || []).filter((f) => f.level === lv).length
const hits = computed(() => {
  const rows = shown.value?.rows || []
  const s = q.value.trim().toUpperCase()
  const num = Number(s)
  const out = rows.filter((r) => !s || (r.model || '').toUpperCase().includes(s) || (r.cup || '').toUpperCase().includes(s) || (num && Number(r.d) === num))
  return out.slice(0, 200)
})
const more = computed(() => {
  const rows = shown.value?.rows || []
  return rows.length > hits.value.length && !q.value.trim()
})

function pick(r) {
  const type = OPENS[r.table]
  if (!type || draft.value) return
  const keep = { scenario: project.scenario, loads: project.loads, fits: project.fits, lube: project.lube, limits: project.limits, material: project.material }
  const name = r.cup ? `${r.model} / ${r.cup}` : r.model
  replace({
    ...blank(), ...JSON.parse(JSON.stringify(keep)), type,
    title: { zh: name, en: name },
    // the model's width: a tapered bearing here has one width for cone and cup, taken as the overall width T
    size: { d: Number(r.d), D: Number(r.D), B: Number(type === 'tapered' ? r.T : r.B) },
    catalog: {
      maker: cur.value.name, version: cur.value.version, table: r.table, model: r.model, cup: r.cup || null, page: r.page || null, d: r.d ?? null, D: r.D ?? null,
      T: r.T ?? null, B: r.B ?? null, C: r.C ?? null, Cr: r.Cr ?? null, Cor: r.Cor ?? null,
    },
  })
  result.value = null  // the last result belongs to the bearing before: not shown for this one
  analyseSoon()
  emit('close')
}
function download() {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([JSON.stringify({ name: cur.value.name, version: cur.value.version, ...cur.value.body }, null, 1)], { type: 'application/json' }))
  a.download = cur.value.name.replace(/[\\/:*?"<>|]+/g, '_') + '.wqcatalog.json'
  a.click()
  setTimeout(() => URL.revokeObjectURL(a.href), 1000)
}

onMounted(async () => {
  await loadMe()
  if (!me.value?.licensed) return
  await run(async () => {
    await refresh()
    if (project.catalog && list.value.some((p) => p.name === project.catalog.maker)) await open(list.value.find((p) => p.name === project.catalog.maker).id)
    else if (list.value.length === 1) await open(list.value[0].id)
  })
})
</script>

<template>
  <div class="cloud-back" @click.self="emit('close')">
    <section class="cat" role="dialog" aria-modal="true" :aria-label="t('catalog')">
      <header>
        <h2>{{ t('catalog') }}</h2>
        <span v-if="me?.licensed" class="org">{{ me.org }}</span>
        <button type="button" class="ghost x" :aria-label="t('close')" @click="emit('close')">×</button>
      </header>

      <p v-if="!me" class="note">{{ t('computing') }}</p>
      <div v-else-if="!me.reachable" class="note">{{ t('cloudDown') }}</div>
      <div v-else-if="!me.login" class="note">
        <p>{{ t('catLogin') }}</p>
        <a class="accent" :href="loginUrl()">{{ t('signIn') }}</a>
      </div>
      <div v-else-if="!me.licensed" class="note"><p>{{ t('catLicense') }}</p></div>

      <template v-else>
        <p class="muted small">{{ t('catIntro') }}</p>
        <div class="bar">
          <select :value="cur?.id || ''" :disabled="busy" :aria-label="t('catalog')" @change="$event.target.value && open(Number($event.target.value))">
            <option value="">{{ list.length ? t('catChoose') : t('catNone') }}</option>
            <option v-for="p in list" :key="p.id" :value="p.id">{{ p.name }}（v{{ p.version }}）</option>
          </select>
          <button type="button" class="ghost" :disabled="busy" @click="fileIn.click()">{{ t('catImport') }}</button>
          <input ref="fileIn" type="file" accept=".xlsx" hidden @change="readFile">
          <a class="ghost link" :href="BASE + '/catalog/template.xlsx'">{{ t('catTemplate') }}</a>
        </div>

        <div v-if="draft" class="draft">
          <p>{{ t('catRead').replace('{n}', draft.rows.length) }}</p>
          <form class="as" @submit.prevent="saveNew">
            <label>{{ t('cloudName') }} <input v-model="draft.name" maxlength="80"></label>
            <button type="submit" class="solid" :disabled="busy">{{ t('catSaveNew') }}</button>
            <button v-if="cur" type="button" class="ghost" :disabled="busy" @click="replaceCur">{{ t('catReplace').replace('{name}', cur.name) }}</button>
            <button type="button" class="ghost" @click="draft = null">{{ t('cancel') }}</button>
          </form>
        </div>
        <p v-if="msg" class="ok" role="status">{{ msg }}</p>
        <p v-if="err" class="bad" role="alert">{{ err }}</p>

        <template v-if="shown">
          <details class="finds">
            <summary>{{ t('catChecks') }}：{{ t('catSuspect') }} {{ count('疑似') }} · {{ t('catConfirm') }} {{ count('请确认') }} · {{ t('catUnknown') }} {{ count('未知') }}</summary>
            <ol>
              <li v-for="(f, i) in finds" :key="i" :class="{ s: f.level === '疑似' }">
                <span class="lv">{{ t(LEVEL[f.level]) }}</span><span class="mono">{{ f.page ? 'p' + f.page : '' }}</span><b>{{ f.model }}</b><span>{{ f.why }}</span>
              </li>
            </ol>
            <p class="muted small">{{ t('catChecksNote') }}<template v-if="lang !== 'zh'"> {{ t('catZhOnly') }}</template></p>
          </details>
          <div class="bar">
            <input v-model="q" type="search" :placeholder="t('catSearch')" :aria-label="t('catSearch')">
            <template v-if="cur && !draft">
              <button type="button" class="ghost sm" @click="download">{{ t('catFreecad') }}</button>
              <button type="button" class="ghost sm del" :class="{ sure }" :disabled="busy" @click="remove">{{ sure ? t('cloudDelSure') : t('cloudDel') }}</button>
            </template>
          </div>
          <p class="muted small">{{ draft ? t('catDraftNote') : t('catPickNote') }}</p>
          <div class="catrows">
            <table>
              <thead><tr><th>{{ t('catModel') }}</th><th>d</th><th>D</th><th>T / B</th><th>Cr</th><th>C0r</th><th>{{ t('catPage') }}</th></tr></thead>
              <tbody>
                <tr v-for="(r, i) in hits" :key="i" :class="{ off: !OPENS[r.table] || draft }" :tabindex="OPENS[r.table] && !draft ? 0 : -1" @click="pick(r)" @keydown.enter="pick(r)">
                  <td><b>{{ r.model }}</b><small v-if="r.cup"> / {{ r.cup }}</small><small class="tb">{{ t(TABLE[r.table]) }}{{ OPENS[r.table] ? '' : ' · ' + t('catNotYet') }}</small></td>
                  <td class="mono">{{ r.d }}</td><td class="mono">{{ r.D }}</td><td class="mono">{{ r.T || r.B }}</td>
                  <td class="mono">{{ r.Cr }}</td><td class="mono">{{ r.Cor }}</td><td class="mono">{{ r.page }}</td>
                </tr>
              </tbody>
            </table>
            <p v-if="more" class="muted small">{{ t('catMore').replace('{n}', shown.rows.length) }}</p>
            <p v-if="!hits.length" class="muted small">{{ t('catNoHit') }}</p>
          </div>
        </template>
      </template>
    </section>
  </div>
</template>

<style scoped>
.cloud-back { position: fixed; inset: 0; background: rgb(10 18 22 / .45); z-index: 50; display: flex; justify-content: flex-end; }
.cat { width: min(640px, 100%); height: 100%; overflow: auto; background: var(--surface); border-left: 1px solid var(--line); padding: 16px 18px 24px; display: flex; flex-direction: column; gap: 10px; }
header { display: flex; align-items: baseline; gap: 10px; }
h2 { font: 700 18px/1.2 var(--serif-zh); margin: 0; }
.org { color: var(--muted); font-size: 13px; }
.x { margin-left: auto; font-size: 18px; line-height: 1; padding: 2px 9px; }
.note p { margin: 0 0 10px; }
.note .accent { text-decoration: none; display: inline-block; }
.bar { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.bar select, .bar input { flex: 1 1 200px; min-width: 0; }
.link { text-decoration: none; font-size: 13px; padding: 4px 10px; border: 1px solid var(--line); border-radius: 6px; color: var(--ink); }
.draft { border: 1px solid var(--accent); border-radius: 8px; padding: 10px 12px; background: var(--paper); }
.draft p { margin: 0 0 8px; }
.as { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.as label { display: flex; gap: 6px; align-items: center; flex: 1 1 220px; font-size: 13px; }
.as input { flex: 1; min-width: 0; }
.ok { color: var(--ok); margin: 0; font-size: 13px; }
.bad { color: var(--bad); margin: 0; font-size: 13px; }
.muted { color: var(--muted); }
.small { font-size: 12px; margin: 0; }
.sm { padding: 2px 8px; font-size: 12px; }
.del.sure { border-color: var(--bad); color: var(--bad); }
.finds summary { cursor: pointer; font-weight: 600; font-size: 13px; }
.finds ol { list-style: none; margin: 8px 0; padding: 0; max-height: 40vh; overflow: auto; font-size: 12px; }
.finds li { display: grid; grid-template-columns: auto 3em minmax(6em, 10em) 1fr; gap: 6px; padding: 4px 0; border-bottom: 1px solid var(--line); }
.finds li.s .lv { color: var(--bad); }
.finds b { overflow-wrap: anywhere; }
.catrows { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; font-weight: 600; color: var(--muted); border-bottom: 1px solid var(--line); padding: 4px 6px; position: sticky; top: 0; background: var(--surface); }
td { padding: 5px 6px; border-bottom: 1px solid var(--line); vertical-align: top; }
td small { color: var(--muted); }
td .tb { display: block; font-size: 11px; }
tbody tr { cursor: pointer; }
tbody tr:hover:not(.off), tbody tr:focus-visible { background: var(--paper); outline: none; }
tr.off { cursor: default; color: var(--muted); }
@media (max-width: 760px) { .cat { border-left: 0; } .finds li { grid-template-columns: auto 1fr; } .finds li > :nth-child(2) { display: none; } .finds li > :nth-child(4) { grid-column: 1 / -1; } }
</style>
