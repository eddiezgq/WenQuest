<script setup>
// Plain-language explanation of the checks, or the design description (round 64, step 7): written by the AI from the
// deterministic results; every number in it was checked by code against the results and the inputs, and sentences
// with other numbers were dropped. For activated company accounts (the same as the cloud projects).
import { ref } from 'vue'
import { api } from '../api'
import { project } from '../store'
import { me } from '../cloud'
import { t, lang } from '../i18n'

const props = defineProps({ kind: { type: String, default: 'explain' } })
const emit = defineEmits(['text'])
const busy = ref(false), err = ref(''), out = ref(null)

async function go() {
  busy.value = true; err.value = ''
  try {
    out.value = await api('/ai/' + props.kind, { project: JSON.parse(JSON.stringify(project)), lang: lang.value })
    emit('text', out.value.sentences.join(lang.value === 'zh' ? '' : ' '))
  } catch (e) { err.value = lang.value === 'zh' ? e.zh || e.message : e.message } finally { busy.value = false }
}
</script>

<template>
  <div v-if="me?.licensed" class="aiex">
    <button type="button" class="ghost" :disabled="busy" @click="go">{{ busy ? t('computing') : t(kind === 'explain' ? 'aiExplain' : 'aiDescribe') }}</button>
    <p v-if="err" class="err">{{ err }}</p>
    <template v-if="out && kind === 'explain'">
      <p v-for="(s, i) in out.sentences" :key="i" class="s">{{ s }}</p>
      <p class="hint">{{ t('aiTextNote') }}<template v-if="out.dropped"> {{ t('aiDropped').replace('{n}', out.dropped) }}</template></p>
    </template>
  </div>
</template>

<style scoped>
.aiex { margin-top: 10px; display: grid; gap: 6px; justify-items: start; }
.s { margin: 0; font-size: 13px; line-height: 1.65; }
</style>
