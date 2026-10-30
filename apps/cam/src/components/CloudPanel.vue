<script setup>
// Cloud projects (round 39, step 7): the company's projects, save / save as, the versions kept, and what to do when
// someone else saved first. Only for signed-in accounts of an activated company; everyone else keeps the browser and files.
import { computed, onMounted, ref } from 'vue'
import { t, lang } from '../i18n'
import { me, link, attach, detach, req, loadMe, loginUrl } from '../cloud'

const props = defineProps({ work: { type: Function, required: true }, load: { type: Function, required: true }, name: { type: String, default: '' } })
const emit = defineEmits(['close'])

const list = ref([])
const history = ref([])
const busy = ref(false)
const msg = ref('')
const err = ref('')
const conflict = ref(null)
const asName = ref(null)          // the name being typed for "save as", or null
const sure = ref(null)            // the project whose delete waits for a second click

const zh = computed(() => lang.value === 'zh')
const when = (ts) => new Date(ts * 1000).toLocaleString(zh.value ? 'zh-CN' : 'en-GB', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
const kindName = (k) => t(k === 'system' ? 'cloudKindSys' : 'cloudKindCam')
const words = (e) => (zh.value ? e.zh || e.message : e.message)

async function refresh() {
  const r = await req('GET', '/projects')
  list.value = r.projects
  if (link.id && !r.projects.some((p) => p.id === link.id)) detach()       // deleted by someone, or another company's
}
async function run(fn) {
  busy.value = true; err.value = ''; msg.value = ''
  try { await fn() } catch (e) {
    if (e.status === 409) conflict.value = e.data
    else err.value = words(e)
  } finally { busy.value = false }
}

function done(r, what) {
  attach(r, r.opened)
  history.value = r.history
  msg.value = what.replace('{v}', r.opened)
  return refresh()
}
const save = () => run(async () => {
  if (!link.id) { asName.value = props.name || ''; return }
  const { body } = props.work()
  done(await req('PUT', `/projects/${link.id}`, { body, base: link.version }), t('cloudSaved'))
})
const saveAs = () => run(async () => {
  const n = (asName.value || '').trim()
  if (!n) { err.value = t('cloudNeedName'); return }
  const { kind, body } = props.work()
  const r = await req('POST', '/projects', { name: n, kind, body })
  asName.value = null; conflict.value = null
  await done(r, t('cloudSavedNew'))
})
const openProject = (id, why = 'cloudOpened', close = false) => run(async () => {
  const r = await req('GET', `/projects/${id}`)
  props.load(r.kind, r.body)
  conflict.value = null
  await done(r, t(why))
  if (close) emit('close')
})
const restore = (v) => run(async () => {
  const r = await req('POST', `/projects/${link.id}/restore`, { version: v, base: link.version })
  props.load(r.kind, r.body)
  await done(r, t('cloudRestored'))
})
const remove = (p) => run(async () => {
  if (sure.value !== p.id) { sure.value = p.id; return }
  await req('DELETE', `/projects/${p.id}`)
  sure.value = null
  if (link.id === p.id) { detach(); history.value = [] }
  await refresh()
})
function mineAs() { asName.value = (link.name || props.name) + t('cloudMineSuffix'); conflict.value = null }

onMounted(async () => {
  await loadMe()
  if (!me.value?.licensed) return
  await run(async () => {
    await refresh()
    if (link.id) history.value = (await req('GET', `/projects/${link.id}`)).history
  })
})
</script>

<template>
  <div class="cloud-back" @click.self="emit('close')">
    <section class="cloud" role="dialog" aria-modal="true" :aria-label="t('cloud')">
      <header>
        <h2>{{ t('cloud') }}</h2>
        <span v-if="me?.licensed" class="org">{{ me.org }}</span>
        <button type="button" class="ghost x" :aria-label="t('close')" @click="emit('close')">×</button>
      </header>

      <p v-if="!me" class="note">{{ t('computing') }}</p>
      <div v-else-if="!me.reachable" class="note">{{ t('cloudDown') }}</div>
      <div v-else-if="!me.login" class="note">
        <p>{{ t('cloudLogin') }}</p>
        <a class="accent" :href="loginUrl()">{{ t('signIn') }}</a>
      </div>
      <div v-else-if="!me.licensed" class="note"><p>{{ t('cloudLicense') }}</p></div>

      <template v-else>
        <div class="now">
          <p v-if="link.id"><b>{{ link.name }}</b> <span class="muted">{{ kindName(link.kind) }} · {{ t('cloudVersion').replace('{v}', link.version) }}</span></p>
          <p v-else class="muted">{{ t('cloudNotYet') }}</p>
          <div class="acts">
            <button type="button" class="accent" :disabled="busy" @click="save">{{ link.id ? t('cloudSave') : t('cloudSaveFirst') }}</button>
            <button v-if="link.id" type="button" class="ghost" :disabled="busy" @click="asName = props.name || link.name">{{ t('cloudSaveAs') }}</button>
          </div>
          <form v-if="asName !== null" class="as" @submit.prevent="saveAs">
            <label>{{ t('cloudName') }} <input v-model="asName" maxlength="80" autofocus></label>
            <button type="submit" class="solid" :disabled="busy">{{ t('cloudSaveAsDo') }}</button>
            <button type="button" class="ghost" @click="asName = null">{{ t('cancel') }}</button>
          </form>
          <p v-if="msg" class="ok" role="status">{{ msg }}</p>
          <p v-if="err" class="bad" role="alert">{{ err }}</p>
        </div>

        <div v-if="conflict" class="conflict" role="alert">
          <p>{{ t('cloudConflict').replace('{who}', conflict.updated_name).replace('{when}', when(conflict.updated)).replace('{v}', conflict.version) }}</p>
          <div class="acts">
            <button type="button" class="solid" @click="mineAs">{{ t('cloudKeepMine') }}</button>
            <button type="button" class="ghost" @click="openProject(link.id, 'cloudTheirs')">{{ t('cloudOpenTheirs') }}</button>
            <button type="button" class="ghost" @click="conflict = null">{{ t('cancel') }}</button>
          </div>
        </div>

        <details v-if="link.id && history.length" class="hist">
          <summary>{{ t('cloudHistory') }}（{{ history.length }}）</summary>
          <ol>
            <li v-for="h in history" :key="h.version">
              <span class="v mono">v{{ h.version }}</span>
              <span>{{ h.saved_name }}</span>
              <span class="muted mono">{{ when(h.ts) }}</span>
              <span v-if="h.note" class="muted">{{ h.note.replace('restored v', t('cloudFrom')) }}</span>
              <button v-if="h.version !== link.version" type="button" class="ghost sm" :disabled="busy" @click="restore(h.version)">{{ t('cloudRestore') }}</button>
              <span v-else class="cur">{{ t('cloudCurrent') }}</span>
            </li>
          </ol>
          <p class="muted small">{{ t('cloudKeep') }}</p>
        </details>

        <h3>{{ t('cloudList') }}</h3>
        <p v-if="!list.length" class="muted">{{ t('cloudEmpty') }}</p>
        <ul class="list">
          <li v-for="p in list" :key="p.id" :class="{ here: p.id === link.id }">
            <button type="button" class="open" :disabled="busy" @click="openProject(p.id, 'cloudOpened', true)">
              <b>{{ p.name }}</b>
              <span class="muted">{{ kindName(p.kind) }} · v{{ p.version }} · {{ p.updated_name }} {{ when(p.updated) }}</span>
            </button>
            <button type="button" class="ghost sm del" :class="{ sure: sure === p.id }" :disabled="busy" @click="remove(p)">{{ sure === p.id ? t('cloudDelSure') : t('cloudDel') }}</button>
          </li>
        </ul>
      </template>
    </section>
  </div>
</template>

<style scoped>
.cloud-back { position: fixed; inset: 0; background: rgb(10 18 22 / .45); z-index: 50; display: flex; justify-content: flex-end; }
.cloud { width: min(460px, 100%); height: 100%; overflow: auto; background: var(--surface); border-left: 1px solid var(--line); padding: 16px 18px 24px; display: flex; flex-direction: column; gap: 12px; }
header { display: flex; align-items: baseline; gap: 10px; }
h2 { font: 700 18px/1.2 var(--serif-zh); margin: 0; }
h3 { font-size: 14px; margin: 6px 0 0; }
.org { color: var(--muted); font-size: 13px; }
.x { margin-left: auto; font-size: 18px; line-height: 1; padding: 2px 9px; }
.note p { margin: 0 0 10px; }
.note .accent { text-decoration: none; display: inline-block; }
.now { border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; background: var(--paper); }
.now p { margin: 0 0 8px; }
.acts { display: flex; gap: 8px; flex-wrap: wrap; }
.as { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 10px; }
.as label { display: flex; gap: 6px; align-items: center; flex: 1 1 220px; font-size: 13px; }
.as input { flex: 1; }
.ok { color: var(--ok); margin: 8px 0 0 !important; font-size: 13px; }
.bad { color: var(--bad); margin: 8px 0 0 !important; font-size: 13px; }
.conflict { border: 1px solid var(--hold); background: var(--hold-bg); border-radius: 8px; padding: 10px 12px; }
.conflict p { margin: 0 0 8px; color: var(--ink); }
.muted { color: var(--muted); }
.small { font-size: 12px; margin: 6px 0 0; }
.hist summary { cursor: pointer; font-weight: 600; font-size: 13px; }
.hist ol { list-style: none; margin: 8px 0 0; padding: 0; }
.hist li { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; padding: 5px 0; border-bottom: 1px solid var(--line); font-size: 13px; }
.hist .v { min-width: 3ch; font-weight: 600; }
.hist li > :last-child { margin-left: auto; }
.cur { font-size: 12px; color: var(--accent-ink); }
.sm { padding: 2px 8px; font-size: 12px; }
.list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.list li { display: flex; align-items: stretch; gap: 6px; border: 1px solid var(--line); border-radius: 8px; }
.list li.here { border-color: var(--accent); }
.open { flex: 1; text-align: left; background: none; border: 0; padding: 8px 10px; color: var(--ink); display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.open b { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.open span { font-size: 12px; }
.del { align-self: center; margin-right: 8px; }
.del.sure { border-color: var(--bad); color: var(--bad); }
@media (max-width: 760px) { .cloud { border-left: 0; } }
</style>
