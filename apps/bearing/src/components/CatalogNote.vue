<script setup>
// Where the project's outside sizes came from: the company's catalogue row (plan section 十七 K3), with the maker's
// load ratings as printed (shown, not checked or used).
import { computed } from 'vue'
import { project } from '../store'
import { t } from '../i18n'

const c = computed(() => project.catalog)
const changed = computed(() => {
  const k = c.value
  if (!k) return false
  const w = project.type === 'tapered' ? k.T : k.B
  return Number(project.size.d) !== Number(k.d ?? project.size.d) || Number(project.size.D) !== Number(k.D ?? project.size.D) || Number(project.size.B) !== Number(w ?? project.size.B)
})
</script>

<template>
  <p v-if="c" class="catnote">
    {{ t('catFrom') }}：{{ c.maker }} · <b>{{ c.model }}{{ c.cup ? ' / ' + c.cup : '' }}</b><span v-if="c.page">（p{{ c.page }}）</span>
    <span v-if="c.Cr || c.Cor"> · Cr {{ c.Cr ?? '—' }} kN、C0r {{ c.Cor ?? '—' }} kN，{{ t('catMakerRatings') }}</span>
    <span v-if="changed" class="chg"> · {{ t('catChanged') }}</span>
  </p>
</template>

<style scoped>
.catnote { margin: 0 0 8px; font-size: 13px; color: var(--muted); }
.catnote b { color: var(--ink); }
.chg { color: var(--hold); }
</style>
