<script setup>
// One sentence → the application and its loads (round 64, step 7): the AI drafts, plain code clears every number that
// is not in the sentence and every field that is not the application's, and lists what is still empty (yellow). The
// draft goes into the form only when "Use it" is pressed, and can be undone. For activated company accounts.
import { computed, ref } from 'vue'
import { api } from '../api'
import { project } from '../store'
import { me } from '../cloud'
import { t, lang } from '../i18n'

const sentence = ref(''), busy = ref(false), err = ref(''), out = ref(null), undo = ref(null), open = ref(false)
const say = (e) => (lang.value === 'zh' ? e.zh || e.message : e.message)
const show = (v) => (v == null || v === '' ? '' : typeof v === 'object' ? JSON.stringify(v) : String(v))
const missing = computed(() => new Set((out.value?.missing || []).map((m) => m.path)))

async function go() {
  busy.value = true; err.value = ''; out.value = null
  try { out.value = await api('/ai/draft', { project: JSON.parse(JSON.stringify(project)), sentence: sentence.value, lang: lang.value }) }
  catch (e) { err.value = say(e) } finally { busy.value = false }
}
function adopt() {
  undo.value = { scenario: JSON.parse(JSON.stringify(project.scenario)), loads: { ...project.loads } }
  project.scenario = JSON.parse(JSON.stringify(out.value.scenario))
  if (out.value.kind === 'generic') project.loads = { ...out.value.loads }
  out.value = null
}
function back() { project.scenario = undo.value.scenario; project.loads = undo.value.loads; undo.value = null }
</script>

<template>
  <section class="aidraft">
    <button type="button" class="ghost" :aria-expanded="open" @click="open = !open">{{ t('aiDraftTitle') }}</button>
    <div v-if="open" class="box">
      <p v-if="!me?.licensed" class="hint">{{ t('aiLicense') }}</p>
      <template v-else>
        <textarea v-model="sentence" rows="3" maxlength="600" :placeholder="t('aiDraftHint')" />
        <div class="btns"><button type="button" class="accent" :disabled="busy || sentence.trim().length < 2" @click="go">{{ busy ? t('computing') : t('aiDraft') }}</button>
          <button v-if="undo" type="button" class="ghost" @click="back">{{ t('aiUndo') }}</button></div>
        <p v-if="err" class="err" role="alert">{{ err }}</p>
        <template v-if="out">
          <p v-if="out.error" class="err">{{ say(out.error) }}</p>
          <p class="hint"><b>{{ t('sk_' + out.kind) || out.kind }}</b>　{{ t('aiDraftNote') }}</p>
          <table class="casetbl"><tbody>
            <tr v-for="r in out.values" :key="r.path" :class="{ miss: missing.has(r.path) }">
              <td>{{ r.label }}</td><td class="mono">{{ show(r.value) }} {{ r.value != null ? r.unit : '' }}</td></tr>
            <tr v-for="(c, i) in out.scenario?.cases || []" :key="'c' + i" :class="{ miss: [...missing].some((p) => p.startsWith('scenario.cases.' + i + '.')) }">
              <td>{{ t('cases') }} {{ i + 1 }}</td><td class="mono">{{ ['P', 'Fr', 'Fa', 'n', 'share'].filter((k) => k in c).map((k) => k + ' ' + (c[k] ?? '—')).join('，') }}</td></tr>
          </tbody></table>
          <p v-if="out.missing.length" class="warn">{{ t('aiMissing') }}</p>
          <p v-if="out.cleared.length" class="warn">{{ t('aiCleared') }}：{{ out.cleared.map((c) => c.path.replace('scenario.', '').replace('loads.', '') + ' = ' + show(c.value)).join('；') }}</p>
          <p v-if="out.dropped.length" class="hint">{{ t('aiDroppedFields') }}：{{ out.dropped.map((c) => c.path).join('，') }}</p>
          <ul v-if="out.questions.length" class="qs"><li v-for="(q, i) in out.questions" :key="i">{{ q }}</li></ul>
          <p v-if="out.status" class="hint">{{ t('aiChecked') }}：{{ t(out.status) }}</p>
          <div class="btns"><button type="button" class="accent" :disabled="!out.usable" @click="adopt">{{ t('aiAdopt') }}</button>
            <button type="button" class="ghost" @click="out = null">{{ t('cancel') }}</button></div>
          <p class="hint small">{{ t('aiModel') }} {{ out.model }}，{{ t('aiLeft').replace('{n}', out.left_today) }}</p>
        </template>
      </template>
    </div>
  </section>
</template>

<style scoped>
.aidraft { margin-bottom: 10px; display: grid; gap: 6px; }
.aidraft > button { justify-self: start; }
.box { display: grid; gap: 8px; padding: 10px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }
textarea { width: 100%; font-family: inherit; font-size: 13px; }
.btns { display: flex; gap: 8px; flex-wrap: wrap; }
tr.miss td { background: var(--hold-bg); }
.warn { color: var(--hold); font-size: 12.5px; margin: 0; }
.qs { margin: 0; padding-left: 18px; font-size: 12.5px; }
.small { font-size: 11.5px; }
</style>
