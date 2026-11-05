<script setup>
// The assembly mode (round 64): selective assembly of measured parts, and the clearance dimension chain (plan 二十).
import { ref } from 'vue'
import { t } from '../i18n'
import Assembly from './Assembly.vue'
import ChainTol from './ChainTol.vue'

const tab = ref('match')
</script>

<template>
  <div class="asmmode">
    <nav class="subtabs" :aria-label="t('modeAsm')">
      <button type="button" :class="{ on: tab === 'match' }" :aria-pressed="tab === 'match'" @click="tab = 'match'">{{ t('asmTitle') }}</button>
      <button type="button" :class="{ on: tab === 'chain' }" :aria-pressed="tab === 'chain'" @click="tab = 'chain'">{{ t('tolTitle') }}</button>
    </nav>
    <Assembly v-if="tab === 'match'" />
    <ChainTol v-else />
  </div>
</template>

<style scoped>
.subtabs { display: flex; gap: 6px; padding: 10px 12px 0; flex-wrap: wrap; }
.subtabs button { border: 1px solid var(--line); background: var(--surface); padding: 5px 12px; border-radius: 6px; font-size: 13px; }
.subtabs button.on { border-color: var(--accent); color: var(--accent-ink); font-weight: 600; }
@media (max-width: 760px) { .subtabs { padding: 8px 16px 0; } }
</style>
