<script setup>
// The design description of the calculation sheet (round 39, step 6): drafted by the AI from the results, every
// number checked by code, then edited and owned by the designer. Kept in the project (saved with it).
import AiExplain from './AiExplain.vue'
import { t } from '../i18n'

const props = defineProps({ target: Object, system: Boolean })
function setText(s) { props.target.design_note = s }
</script>

<template>
  <section :class="['dn', !target.design_note && 'noprint']">
    <h2>{{ t('designNote') }}</h2>
    <textarea v-model="target.design_note" class="noprint" rows="4" :placeholder="t('designNoteHint')" />
    <p v-if="target.design_note" class="printonly">{{ target.design_note }}</p>
    <p v-if="target.design_note" class="tag">{{ t('designNoteTag') }}</p>
    <div class="noprint"><AiExplain kind="describe" :system="system" @text="setText" /></div>
  </section>
</template>

<style scoped>
textarea { width: 100%; font-family: inherit; font-size: 13.5px; line-height: 1.6; }
.tag { font-size: 11.5px; color: var(--muted); margin: 2px 0 0; }
.printonly { display: none; }
@media print { .printonly { display: block; } }
</style>
