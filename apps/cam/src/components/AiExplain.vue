<script setup>
// Plain-language explanation of the checks (round 39, step 6): written by the AI from the deterministic results;
// every number in it was checked by code against the results, and sentences with other numbers were dropped.
import { ref } from 'vue'
import { apiPost } from '../api'
import { payload } from '../store'
import { sysPayload } from '../sysstore'
import { t, lang } from '../i18n'

const props = defineProps({ system: Boolean, kind: { type: String, default: 'explain' } })
const emit = defineEmits(['text'])
const busy = ref(false)
const err = ref('')
const out = ref(null)

async function go() {
  busy.value = true; err.value = ''
  try {
    out.value = await apiPost('/ai/' + props.kind, { project: props.system ? sysPayload() : payload(), lang: lang.value })
    emit('text', out.value.sentences.join(lang.value === 'zh' ? '' : ' '))
  } catch (e) {
    err.value = lang.value === 'zh' ? e.zh || e.message : e.message
  } finally { busy.value = false }
}
</script>

<template>
  <div class="aiex">
    <button type="button" class="ghost" :disabled="busy" @click="go">{{ busy ? t('computing') : t(kind === 'explain' ? 'aiExplain' : 'aiDescribe') }}</button>
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-if="out && kind === 'explain'">
      <p v-for="(s, i) in out.sentences" :key="i" class="s">{{ s }}</p>
      <p class="note">{{ t('aiTextNote') }}<template v-if="out.dropped"> {{ t('aiDropped') }} {{ out.dropped }}</template></p>
    </template>
  </div>
</template>

<style scoped>
.aiex { margin-top: 8px; display: grid; gap: 4px; }
.s { margin: 0; font-size: 13px; line-height: 1.6; }
.note { margin: 0; color: var(--muted); font-size: 11.5px; }
.bad { margin: 0; color: var(--bad); font-size: 12.5px; }
</style>
