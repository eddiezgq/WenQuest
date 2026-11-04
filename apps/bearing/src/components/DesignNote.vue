<script setup>
// The design description of the calculation report (round 64, step 7): written by the designer, or drafted by the AI
// from the results with every number checked by code, then edited and owned by the designer. Saved with the project.
import AiExplain from './AiExplain.vue'
import { project } from '../store'
import { t } from '../i18n'

function setText(s) { project.design_note = s }
</script>

<template>
  <section :class="['dn', !project.design_note && 'no-print']">
    <h2>{{ t('designNote') }}</h2>
    <textarea v-model="project.design_note" class="no-print" rows="4" :placeholder="t('designNoteHint')" />
    <p v-if="project.design_note" class="printonly">{{ project.design_note }}</p>
    <p v-if="project.design_note" class="tag">{{ t('designNoteTag') }}</p>
    <div class="no-print"><AiExplain kind="describe" @text="setText" /></div>
  </section>
</template>

<style scoped>
textarea { width: 100%; font-family: inherit; font-size: 13.5px; line-height: 1.6; }
.tag { font-size: 11.5px; color: var(--muted); margin: 2px 0 0; }
.printonly { display: none; }
@media print { .printonly { display: block; } }
</style>
