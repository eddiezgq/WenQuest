<script setup>
// 问渠凸轮 (round 39, step 2): edit on the left, the cam turning in the middle, checks on the right, curves below.
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { project, result, error, busy, analyseSoon, loadLaws, replace, blank, blankCyl, mode, mfgResult, measResult, compResult } from './store'
import { api } from './api'
import { t, lang, setLang } from './i18n'
import ProgramEditor from './components/ProgramEditor.vue'
import Fields from './components/Fields.vue'
import CylFields from './components/CylFields.vue'
import CylView from './components/CylView.vue'
import CylMfg from './components/CylMfg.vue'
import { cylMfgResult } from './cylmfg'
import CamView from './components/CamView.vue'
import Charts from './components/Charts.vue'
import Checks from './components/Checks.vue'
import AiExplain from './components/AiExplain.vue'
import Report from './components/Report.vue'
import MfgWorkspace from './components/MfgWorkspace.vue'
import MeasureWorkspace from './components/MeasureWorkspace.vue'
import SystemWorkspace from './components/SystemWorkspace.vue'
import System3D from './components/System3D.vue'
import CaePanel from './components/CaePanel.vue'
import SystemReport from './components/SystemReport.vue'
import CloudPanel from './components/CloudPanel.vue'
import { me, link, detach, loadMe, loginUrl } from './cloud'
import { kind, system, openSystem, sysMode, analyseSystemSoon, loadExampleCae, sysResult } from './sysstore'

const tab = ref('program')
const theta = ref(0)
const playing = ref(false)
const speed = ref(45)
const examples = ref([])
const showReport = ref(false)
const embed = new URLSearchParams(location.search).has('embed')
const fileInput = ref(null)
const showCloud = ref(false)

let raf = 0, last = 0
function loop(ts) {
  if (!playing.value) return
  if (last) theta.value = (theta.value + ((ts - last) / 1000) * speed.value) % 360
  last = ts
  raf = requestAnimationFrame(loop)
}
watch(playing, (p) => { if (p) { last = 0; raf = requestAnimationFrame(loop) } else cancelAnimationFrame(raf) })
onBeforeUnmount(() => cancelAnimationFrame(raf))

async function openExample(id) {
  if (!id) return
  try {
    const p = await api('/examples/' + id)
    detach(); cylMfgResult.value = null
    if (p.kind === 'system') { openSystem(p, id); return }
    kind.value = 'cam'
    replace(p); theta.value = 0; mfgResult.value = null; measResult.value = null; compResult.value = null
  } catch (e) { error.value = e }
}
function fresh(what = 'disk') { detach(); cylMfgResult.value = null; kind.value = 'cam'; replace(what === 'cylindrical' ? blankCyl() : blank()); mfgResult.value = null; measResult.value = null; compResult.value = null; theta.value = 0 }
const isSys = computed(() => kind.value === 'system' && system.cams)
const isCylP = computed(() => !isSys.value && project.type === 'cylindrical')   // round 39 step 8
const modeList = computed(() => (isSys.value ? [['sys', 'modeSys'], ['sys3d', 'modeSys3d'], ['cae', 'modeCae']] : isCylP.value ? [['design', 'modeDesign'], ['mfg', 'modeMfg']] : [['design', 'modeDesign'], ['mfg', 'modeMfg'], ['measure', 'modeMeasure']]))
watch(isCylP, (c) => { if (c && mode.value === 'measure') mode.value = 'design' }, { immediate: true })
const curMode = computed({ get: () => (isSys.value ? sysMode.value : mode.value), set: (v) => { if (isSys.value) sysMode.value = v; else mode.value = v } })
function saveFile() {
  const blob = new Blob([JSON.stringify(isSys.value ? system : project, null, 1)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = ((lang.value === 'zh' ? project.title.zh : project.title.en) || 'cam').replace(/[\\/:*?"<>|]+/g, '_') + '.wqcam.json'
  a.click()
  URL.revokeObjectURL(a.href)
}
async function openFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  try {
    const p = JSON.parse(await f.text())
    detach(); cylMfgResult.value = null
    if (p.kind === 'system') openSystem(p, p.example_id || '')
    else { kind.value = 'cam'; replace(p) }
  } catch { error.value = { message: 'not a project file', zh: '不是问渠凸轮的项目文件' } }
  e.target.value = ''
}
const titleText = computed({
  get: () => { const tt = isSys.value ? system.title || {} : project.title; return lang.value === 'zh' ? tt.zh : tt.en },
  set: (v) => { if (isSys.value) system.title = { ...(system.title || {}), [lang.value]: v }; else project.title = { ...project.title, [lang.value]: v } },
})

// Cloud projects: what is open now, and how a project from the cloud is put into the editor.
function work() {
  return isSys.value ? { kind: 'system', body: JSON.parse(JSON.stringify(system)) } : { kind: 'cam', body: JSON.parse(JSON.stringify(project)) }
}
function loadWork(k, body) {
  cylMfgResult.value = null
  if (k === 'system' || body.kind === 'system') { openSystem(body, body.example_id || ''); return }
  kind.value = 'cam'; replace(body); theta.value = 0; mfgResult.value = null; measResult.value = null; compResult.value = null
}
const linked = computed(() => (link.id ? t('cloudLinked').replace('{name}', link.name).replace('{v}', link.version) : ''))

onMounted(async () => {
  if (!embed) loadMe()
  await loadLaws()
  try { examples.value = await api('/examples') } catch { examples.value = [] }
  const ex = new URLSearchParams(location.search).get('example')
  if (ex) await openExample(ex)
  analyseSoon(0)
  if (isSys.value) { analyseSystemSoon(0); loadExampleCae() }
  if (embed) playing.value = true
})
</script>

<template>
  <SystemReport v-if="showReport && isSys" @close="showReport = false" />
  <Report v-else-if="showReport" @close="showReport = false" />
  <div v-else class="shell" :class="{ embed }">
    <CloudPanel v-if="showCloud" :work="work" :load="loadWork" :name="titleText" @close="showCloud = false" />
    <header class="top">
      <a class="brand" :href="embed ? '/cam/' : '/cases/cam.html'" :target="embed ? '_blank' : null" rel="noopener"><b>{{ t('app') }}</b><small>{{ t('tagline') }}</small></a>
      <input v-if="!embed" v-model="titleText" class="title" :aria-label="t('title')">
      <nav v-if="!embed" class="modes" :aria-label="t('app')">
        <button v-for="[k, l] in modeList" :key="k" type="button" :class="{ on: curMode === k }" @click="curMode = k">{{ t(l) }}</button>
      </nav>
      <div class="tools">
        <select class="dark" :aria-label="t('examples')" @change="openExample($event.target.value); $event.target.value = ''">
          <option value="">{{ t('examples') }}…</option>
          <option v-for="e in examples" :key="e.id" :value="e.id">{{ lang === 'zh' ? e.title.zh : e.title.en }}</option>
        </select>
        <template v-if="!embed">
          <select class="dark new" :aria-label="t('newProject')" @change="fresh($event.target.value); $event.target.value = ''">
            <option value="">{{ t('newProject') }}…</option>
            <option value="disk">{{ t('newDisk') }}</option>
            <option value="cylindrical">{{ t('newCyl') }}</option>
          </select>
          <button type="button" class="dark" @click="fileInput.click()">{{ t('open') }}</button>
          <input ref="fileInput" type="file" accept=".json,application/json" hidden @change="openFile">
          <button type="button" class="dark" @click="saveFile">{{ t('save') }}</button>
          <button type="button" class="dark cloud-btn" :class="{ linked: link.id }" :title="linked || t('cloud')" @click="showCloud = true">{{ t('cloud') }}</button>
          <button type="button" class="accent" :disabled="isSys ? !sysResult : !result" @click="showReport = true">{{ t('report') }}</button>
        </template>
        <span v-if="!embed && me?.login" class="who" :title="me.org">{{ me.name || '…' }}<small v-if="me.org">{{ me.org }}</small></span>
        <a v-else-if="!embed && me && me.reachable" class="who in" :href="loginUrl()">{{ t('signIn') }}</a>
        <button type="button" class="dark lang" @click="setLang(lang === 'zh' ? 'en' : 'zh')">{{ lang === 'zh' ? 'EN' : '中' }}</button>
      </div>
    </header>

    <template v-if="isSys">
      <System3D v-if="embed" />
      <SystemWorkspace v-else-if="sysMode === 'sys'" />
      <System3D v-else-if="sysMode === 'sys3d'" />
      <CaePanel v-else />
    </template>
    <CylMfg v-else-if="mode === 'mfg' && !embed && isCylP" />
    <MfgWorkspace v-else-if="mode === 'mfg' && !embed && !isCylP" />
    <MeasureWorkspace v-else-if="mode === 'measure' && !embed && !isCylP" />
    <main v-else class="work">
      <aside class="edit">
        <nav class="tabs">
          <button v-for="[k, l] in [['program', 'tabProgram'], ['mech', 'tabMech'], ['loads', 'tabLoads'], ['limits', 'tabLimits']]" :key="k" type="button" :class="{ on: tab === k }" @click="tab = k">{{ t(l) }}</button>
        </nav>
        <div class="pane">
          <ProgramEditor v-if="tab === 'program'" />
          <CylFields v-else-if="tab === 'mech' && isCylP" />
          <Fields v-else :part="tab" />
        </div>
        <p class="saved">{{ linked || t('savedLocal') }}</p>
      </aside>

      <section class="stage">
        <div class="canvas">
          <CylView v-if="isCylP" v-model:theta="theta" :result="result?.type === 'cylindrical' ? result : null" />
          <CamView v-else v-model:theta="theta" :result="result?.type === 'cylindrical' ? null : result" />
          <p v-if="error" class="err">{{ t('error') }}：{{ lang === 'zh' ? error.zh || error.message : error.message }}</p>
          <p v-else-if="busy && !result" class="busy">{{ t('computing') }}</p>
        </div>
        <div class="controls">
          <button type="button" class="solid" @click="playing = !playing">{{ playing ? '❚❚ ' + t('pause') : '▶ ' + t('play') }}</button>
          <label class="scrub">{{ t('camAngle') }} <input v-model.number="theta" type="range" min="0" max="359.9" step="0.1"> <span class="mono">{{ theta.toFixed(1) }}°</span></label>
          <label class="spd"><input v-model.number="speed" type="range" min="5" max="360" step="5"> <span class="mono">{{ speed }}°/s</span></label>
        </div>
      </section>

      <aside class="side"><Checks :result="result" /><AiExplain v-if="result && !embed" /></aside>

      <section class="curves"><Charts v-model:theta="theta" :result="result" /></section>
    </main>
  </div>
</template>
