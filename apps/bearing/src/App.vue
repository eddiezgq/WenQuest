<script setup>
// 问渠轴承 (round 64, step 2): edit on the left, the section and the ball loads in the middle, checks on the right.
import { computed, onMounted, ref } from 'vue'
import { project, result, error, busy, analyseSoon, replace, blank } from './store'
import { api } from './api'
import { t, lang, setLang } from './i18n'
import Fields from './components/Fields.vue'
import Section from './components/Section.vue'
import SectionCyl from './components/SectionCyl.vue'
import SliceChart from './components/SliceChart.vue'
import SectionTaper from './components/SectionTaper.vue'
import LoadRing from './components/LoadRing.vue'
import Checks from './components/Checks.vue'
import Extras from './components/Extras.vue'
import ScenarioPanel from './components/ScenarioPanel.vue'
import Report from './components/Report.vue'
import AssemblyMode from './components/AssemblyMode.vue'
import Quality from './components/Quality.vue'
import Parts from './components/Parts.vue'
import Process from './components/Process.vue'
import AiDraft from './components/AiDraft.vue'
import SettingCurve from './components/SettingCurve.vue'
import AiExplain from './components/AiExplain.vue'
import CloudPanel from './components/CloudPanel.vue'
import CatalogPanel from './components/CatalogPanel.vue'
import CatalogNote from './components/CatalogNote.vue'
import FlexView from './components/FlexView.vue'
import SectionCrossed from './components/SectionCrossed.vue'
import XrLoads from './components/XrLoads.vue'
import SectionThin from './components/SectionThin.vue'
import ThinLoads from './components/ThinLoads.vue'
import { me, links, detach, loadMe, loginUrl } from './cloud'

const examples = ref([])
const pick = ref('')
const showReport = ref(false)
const showParts = ref(false)
const showCloud = ref(false)
const showCatalog = ref(false)
const MODES = ['design', 'assembly', 'quality', 'process']
const mode = ref(MODES.includes(new URLSearchParams(location.search).get('mode')) ? new URLSearchParams(location.search).get('mode') : 'design')
const fileInput = ref(null)
const q = new URLSearchParams(location.search)
const embed = q.has('embed')  // shown inside the product page: no file buttons

async function openExample(id) {
  if (!id) return
  try { replace(await api('/examples/' + id)); detach('design') } catch (e) { error.value = e }
  pick.value = ''
}
function fresh() { replace(blank()); result.value = null; detach('design') }
function save() {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([JSON.stringify(project, null, 2)], { type: 'application/json' }))
  a.download = (title.value || 'bearing').replace(/[\\/:*?"<>|]+/g, '_') + '.wqbearing.json'
  a.click()
  setTimeout(() => URL.revokeObjectURL(a.href), 1000)
}
async function openFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  try { replace(JSON.parse(await f.text())); detach('design') } catch (err) { error.value = { message: 'not a bearing project file', zh: '不是轴承项目文件' } }
  e.target.value = ''
}
const title = computed({
  get: () => (lang.value === 'zh' ? project.title.zh : project.title.en),
  set: (v) => { project.title = { ...project.title, [lang.value]: v } },
})
// cloud projects (step 7): the design project as it is edited here
const work = () => ({ body: JSON.parse(JSON.stringify(project)) })
const loadWork = (body) => { replace(body) }
const linked = computed(() => (links.design.id ? t('cloudLinked').replace('{name}', links.design.name).replace('{v}', links.design.version) : ''))
const note = computed(() => project.note && (lang.value === 'zh' ? project.note.zh : project.note.en))

onMounted(async () => {
  if (!embed) loadMe()
  try { examples.value = await api('/examples') } catch { /* the page works without the list */ }
  const ex = q.get('example')
  if (ex && /^[a-z0-9-]{1,60}$/.test(ex)) await openExample(ex)
  else if (!project.size.d && !project.inner.Dw && examples.value.length) await openExample('demo-deep-groove')
  else analyseSoon()
})
</script>

<template>
  <div class="shell" :class="{ embed }">
    <header class="top">
      <a class="brand" href="/"><b>{{ t('app') }}</b><small>{{ t('tagline') }}</small></a>
      <input v-model="title" class="title" :placeholder="t('untitled')" :aria-label="t('title')">
      <nav class="modes" :aria-label="t('modeDesign')">
        <button v-for="m in MODES" :key="m" type="button" class="dark" :class="{ on: mode === m }" :aria-pressed="mode === m" @click="mode = m">{{ t({ design: 'modeDesign', assembly: 'modeAsm', quality: 'modeQuality', process: 'modeProcess' }[m]) }}</button>
      </nav>
      <div class="tools">
        <select v-model="pick" class="dark" :aria-label="t('examples')" @change="openExample(pick)">
          <option value="">{{ t('examples') }}</option>
          <option v-for="e in examples" :key="e.id" :value="e.id">{{ lang === 'zh' ? e.title.zh : e.title.en }}</option>
        </select>
        <button v-if="!embed" type="button" class="dark" @click="fresh">{{ t('newProject') }}</button>
        <button v-if="!embed" type="button" class="dark" @click="fileInput.click()">{{ t('open') }}</button>
        <input ref="fileInput" type="file" accept=".json" hidden @change="openFile">
        <button v-if="!embed" type="button" class="dark" @click="save">{{ t('save') }}</button>
        <button v-if="!embed && mode === 'design'" type="button" class="dark" @click="showCatalog = true">{{ t('catalog') }}</button>
        <button v-if="!embed && mode === 'design'" type="button" class="dark cloud-btn" :class="{ linked: links.design.id }" :title="linked || t('cloud')" @click="showCloud = true">{{ t('cloud') }}</button>
        <button v-if="mode === 'design'" type="button" class="dark" :disabled="!result" @click="showParts = true">{{ t('partsBtn') }}</button>
        <button type="button" class="accent" :disabled="!result" @click="showReport = true">{{ t('report') }}</button>
        <button type="button" class="dark lang" @click="setLang(lang === 'zh' ? 'en' : 'zh')">{{ lang === 'zh' ? 'EN' : '中' }}</button>
        <span v-if="!embed && me?.login" class="who" :title="me.org">{{ me.name || '…' }}<small v-if="me.org">{{ me.org }}</small></span>
        <a v-else-if="!embed && me && me.reachable" class="who in" :href="loginUrl()">{{ t('signIn') }}</a>
      </div>
    </header>

    <AssemblyMode v-if="mode === 'assembly'" />
    <Quality v-if="mode === 'quality'" />
    <Process v-if="mode === 'process'" />
    <main v-show="mode === 'design'" class="work">
      <aside class="edit">
        <div class="pane"><AiDraft v-if="!embed" /><Fields /></div>
        <p class="saved">{{ linked || t('savedLocal') }}</p>
      </aside>

      <section class="stage">
        <p v-if="note" class="fict">{{ t('fictional') }}：{{ note }}</p>
        <CatalogNote />
        <div class="figs">
          <SectionCyl v-if="result?.type === 'cylindrical'" :r="result" />
          <SectionTaper v-else-if="result?.type === 'tapered'" :r="result" />
          <SectionCrossed v-else-if="result?.type === 'crossed'" :r="result" />
          <SectionThin v-else-if="result?.type === 'thin'" :r="result" />
          <Section v-else :r="result" />
          <LoadRing v-if="!['flex', 'crossed', 'thin'].includes(result?.type)" :r="result" />
        </div>
        <FlexView v-if="result?.type === 'flex'" :r="result" />
        <XrLoads v-if="result?.type === 'crossed'" :r="result" />
        <ThinLoads v-if="result?.type === 'thin'" :r="result" />
        <SliceChart :r="result" />
        <ScenarioPanel :r="result" />
        <Extras :r="result" />
        <SettingCurve :r="result" />
        <p v-if="busy" class="busy">{{ t('busy') }}</p>
        <p v-if="error" class="err" role="alert">{{ t('error') }}：{{ lang === 'zh' ? error.zh || error.message : error.message }}</p>
      </section>

      <aside class="side"><Checks :r="result" /><AiExplain v-if="result && !embed" /></aside>
    </main>

    <Report v-if="showReport && result" :r="result" @close="showReport = false" />
    <Parts v-if="showParts" @close="showParts = false" />
    <CatalogPanel v-if="showCatalog" @close="showCatalog = false" />
    <CloudPanel v-if="showCloud" kind="design" :work="work" :load="loadWork" :name="title" @close="showCloud = false" />
  </div>
</template>
