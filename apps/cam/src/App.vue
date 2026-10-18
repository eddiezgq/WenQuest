<script setup>
// 问渠凸轮 (round 39, step 2): edit on the left, the cam turning in the middle, checks on the right, curves below.
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { project, result, error, busy, analyseSoon, loadLaws, replace, blank } from './store'
import { api } from './api'
import { t, lang, setLang } from './i18n'
import ProgramEditor from './components/ProgramEditor.vue'
import Fields from './components/Fields.vue'
import CamView from './components/CamView.vue'
import Charts from './components/Charts.vue'
import Checks from './components/Checks.vue'
import Report from './components/Report.vue'

const tab = ref('program')
const theta = ref(0)
const playing = ref(false)
const speed = ref(45)
const examples = ref([])
const showReport = ref(false)
const embed = new URLSearchParams(location.search).has('embed')
const fileInput = ref(null)

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
  try { replace(await api('/examples/' + id)); theta.value = 0 } catch (e) { error.value = e }
}
function fresh() { replace(blank()) }
function saveFile() {
  const blob = new Blob([JSON.stringify(project, null, 1)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = ((lang.value === 'zh' ? project.title.zh : project.title.en) || 'cam').replace(/[\\/:*?"<>|]+/g, '_') + '.wqcam.json'
  a.click()
  URL.revokeObjectURL(a.href)
}
async function openFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  try { replace(JSON.parse(await f.text())) } catch { error.value = { message: 'not a project file', zh: '不是问渠凸轮的项目文件' } }
  e.target.value = ''
}
const titleText = computed({
  get: () => (lang.value === 'zh' ? project.title.zh : project.title.en),
  set: (v) => { project.title = { ...project.title, [lang.value]: v } },
})

onMounted(async () => {
  await loadLaws()
  try { examples.value = await api('/examples') } catch { examples.value = [] }
  const ex = new URLSearchParams(location.search).get('example')
  if (ex) await openExample(ex)
  analyseSoon(0)
  if (embed) playing.value = true
})
</script>

<template>
  <Report v-if="showReport" @close="showReport = false" />
  <div v-else class="shell" :class="{ embed }">
    <header class="top">
      <a class="brand" :href="embed ? '/cam/' : '/cases/cam.html'" :target="embed ? '_blank' : null" rel="noopener"><b>{{ t('app') }}</b><small>{{ t('tagline') }}</small></a>
      <input v-if="!embed" v-model="titleText" class="title" :aria-label="t('title')">
      <div class="tools">
        <select class="dark" :aria-label="t('examples')" @change="openExample($event.target.value); $event.target.value = ''">
          <option value="">{{ t('examples') }}…</option>
          <option v-for="e in examples" :key="e.id" :value="e.id">{{ lang === 'zh' ? e.title.zh : e.title.en }}</option>
        </select>
        <template v-if="!embed">
          <button type="button" class="dark" @click="fresh">{{ t('newProject') }}</button>
          <button type="button" class="dark" @click="fileInput.click()">{{ t('open') }}</button>
          <input ref="fileInput" type="file" accept=".json,application/json" hidden @change="openFile">
          <button type="button" class="dark" @click="saveFile">{{ t('save') }}</button>
          <button type="button" class="accent" :disabled="!result" @click="showReport = true">{{ t('report') }}</button>
        </template>
        <button type="button" class="dark lang" @click="setLang(lang === 'zh' ? 'en' : 'zh')">{{ lang === 'zh' ? 'EN' : '中' }}</button>
      </div>
    </header>

    <main class="work">
      <aside class="edit">
        <nav class="tabs">
          <button v-for="[k, l] in [['program', 'tabProgram'], ['mech', 'tabMech'], ['loads', 'tabLoads'], ['limits', 'tabLimits']]" :key="k" type="button" :class="{ on: tab === k }" @click="tab = k">{{ t(l) }}</button>
        </nav>
        <div class="pane">
          <ProgramEditor v-if="tab === 'program'" />
          <Fields v-else :part="tab" />
        </div>
        <p class="saved">{{ t('savedLocal') }}</p>
      </aside>

      <section class="stage">
        <div class="canvas">
          <CamView v-model:theta="theta" :result="result" />
          <p v-if="error" class="err">{{ t('error') }}：{{ lang === 'zh' ? error.zh || error.message : error.message }}</p>
          <p v-else-if="busy && !result" class="busy">{{ t('computing') }}</p>
        </div>
        <div class="controls">
          <button type="button" class="solid" @click="playing = !playing">{{ playing ? '❚❚ ' + t('pause') : '▶ ' + t('play') }}</button>
          <label class="scrub">{{ t('camAngle') }} <input v-model.number="theta" type="range" min="0" max="359.9" step="0.1"> <span class="mono">{{ theta.toFixed(1) }}°</span></label>
          <label class="spd"><input v-model.number="speed" type="range" min="5" max="360" step="5"> <span class="mono">{{ speed }}°/s</span></label>
        </div>
      </section>

      <aside class="side"><Checks :result="result" /></aside>

      <section class="curves"><Charts v-model:theta="theta" :result="result" /></section>
    </main>
  </div>
</template>
