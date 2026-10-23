<script setup>
// AI drafting of the motion program (round 39, step 6): one sentence in, a draft out. The draft is checked by code
// in the service (numbers the sentence does not give are cleared, gaps are asked for, the cam's checks run on it);
// nothing changes in the project until the user adopts it, and an adopted draft can be undone.
import { computed, ref } from 'vue'
import { apiPost } from '../api'
import { payload, laws } from '../store'
import { sysPayload } from '../sysstore'
import { t, lang } from '../i18n'

const props = defineProps({ program: Object, camId: { type: String, default: '' } })
const open = ref(false)
const sentence = ref('')
const busy = ref(false)
const err = ref('')
const res = ref(null)
const undo = ref(null)

const counts = computed(() => {
  const out = { pass: 0, fail: 0, unknown: 0 }
  for (const c of res.value?.checks || []) if (c.status in out) out[c.status]++
  return out
})
const bad = computed(() => (res.value?.checks || []).filter((c) => c.status === 'fail' || c.status === 'unknown'))
const colon = computed(() => (lang.value === 'zh' ? '：' : ': '))
const kindName = (k) => t(k === 'return' ? 'ret' : k)
const lawName = (k) => { const l = laws.value.find((x) => x.key === k); return l ? (lang.value === 'zh' ? l.zh : l.en) : k }
const missingOf = (i, f) => (res.value?.check?.missing || []).some((m) => m.seg === i + 1 && m.field === f)
const filledOf = (i, f) => (res.value?.check?.filled || []).some((m) => m.seg === i + 1 && m.field === f)
const unit = computed(() => (res.value?.follower === 'translating' ? 'mm' : '°'))

async function draft() {
  if (!sentence.value.trim()) return
  busy.value = true; err.value = ''; res.value = null
  try {
    const project = props.camId ? sysPayload() : payload()
    res.value = await apiPost('/ai/draft', { project, sentence: sentence.value, cam: props.camId, lang: lang.value })
  } catch (e) {
    err.value = lang.value === 'zh' ? e.zh || e.message : e.message
  } finally { busy.value = false }
}
function adopt() {
  const p = res.value?.check?.program
  if (!p) return
  undo.value = JSON.parse(JSON.stringify(props.program))
  for (const k of Object.keys(props.program)) delete props.program[k]
  Object.assign(props.program, JSON.parse(JSON.stringify(p)))
}
function back() {
  if (!undo.value) return
  for (const k of Object.keys(props.program)) delete props.program[k]
  Object.assign(props.program, undo.value)
  undo.value = null
}
</script>

<template>
  <section class="ai">
    <button type="button" class="ghost tog" :aria-expanded="open" @click="open = !open">{{ open ? '▾' : '▸' }} {{ t('aiDraft') }}</button>
    <div v-if="open" class="body">
      <textarea v-model="sentence" rows="2" :placeholder="t('aiPlaceholder')" maxlength="600" />
      <div class="row">
        <button type="button" class="solid" :disabled="busy || !sentence.trim()" @click="draft">{{ busy ? t('computing') : t('aiDo') }}</button>
        <button v-if="undo" type="button" class="ghost" @click="back">{{ t('aiUndo') }}</button>
        <span v-if="res?.left_today != null" class="note">{{ t('aiLeft') }} {{ res.left_today }}</span>
      </div>
      <p v-if="err" class="bad">{{ err }}</p>
      <template v-if="res">
        <table class="segs">
          <thead><tr><th>{{ t('kind') }}</th><th>{{ t('angle') }}</th><th>{{ t('lift') }} ({{ unit }})</th><th>{{ t('law') }}</th></tr></thead>
          <tbody>
            <tr v-for="(s, i) in res.check.segments" :key="i" :title="s.why">
              <td>{{ kindName(s.kind) }}</td>
              <td :class="{ miss: missingOf(i, 'deg'), fill: filledOf(i, 'deg') }">{{ s.deg ?? '？' }}</td>
              <td :class="{ miss: missingOf(i, 'h'), fill: filledOf(i, 'h') }">{{ s.kind === 'dwell' ? '' : s.h ?? '？' }}</td>
              <td :class="{ miss: missingOf(i, 'law') }">{{ s.kind === 'dwell' ? '' : (s.law ? lawName(s.law) : '？') }}</td>
            </tr>
          </tbody>
        </table>
        <p v-if="res.check.advance_deg != null" class="note">{{ t('advance') }} {{ res.check.advance_deg }}°</p>
        <p v-if="res.check.cleared.length" class="warn">{{ t('aiCleared') }}</p>
        <p v-if="res.check.filled.length" class="note">{{ t('aiFilled') }}</p>
        <p v-if="res.check.missing.length" class="warn">{{ t('aiMissing') }}</p>
        <p v-if="res.check.error" class="bad">{{ res.check.error }}</p>
        <ul v-if="res.questions.length || res.assumptions.length" class="qs">
          <li v-for="(q, i) in res.questions" :key="'q' + i">？{{ q }}</li>
          <li v-for="(a, i) in res.assumptions" :key="'a' + i">· {{ a }}</li>
        </ul>
        <template v-if="res.check.usable">
          <p class="note">{{ t('aiChecks') }}{{ colon }}{{ t('pass') }} {{ counts.pass }} · {{ t('fail') }} {{ counts.fail }} · {{ t('unknown') }} {{ counts.unknown }}</p>
          <ul v-if="bad.length" class="qs"><li v-for="c in bad" :key="c.group + c.id">{{ t(c.status) }}{{ colon }}{{ c.name }}</li></ul>
          <button type="button" class="accent" @click="adopt">{{ t('aiAdopt') }}</button>
        </template>
        <p class="note small">{{ t('aiNote') }}</p>
      </template>
    </div>
  </section>
</template>

<style scoped>
.ai { border: 1px dashed var(--line); border-radius: 8px; padding: 6px 8px; margin-bottom: 10px; }
.tog { border: 0; padding: 2px 0; font-weight: 600; }
.body { display: grid; gap: 6px; margin-top: 6px; }
textarea { width: 100%; resize: vertical; font-family: inherit; }
.row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.segs { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.segs th { text-align: left; font-weight: 500; color: var(--muted); font-size: 12px; padding: 2px 3px; }
.segs td { padding: 2px 3px; border-top: 1px solid var(--line); }
.miss { background: #fff1b8; }
.fill { color: var(--blue); }
.warn { color: #9a6700; font-size: 12.5px; margin: 0; }
.bad { color: var(--bad); font-size: 12.5px; margin: 0; }
.note { color: var(--muted); font-size: 12.5px; margin: 0; }
.small { font-size: 11.5px; }
.qs { margin: 0; padding-left: 4px; list-style: none; font-size: 12.5px; }
</style>
