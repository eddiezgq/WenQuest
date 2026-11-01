<script setup>
// The checks, worst first in the summary; each row says what was checked, the value and the limit.
import { computed } from 'vue'
import { t, lang } from '../i18n'

const props = defineProps({ r: Object })
const fmt = (x, u) => {
  if (x == null) return '—'
  if (typeof x !== 'number') return String(x)
  if (Number.isInteger(x)) return x + (u ? ' ' + u : '')
  const a = Math.abs(x)
  return (a >= 100 ? x.toFixed(0) : a >= 10 ? x.toFixed(1) : a >= 1 ? x.toFixed(2) : x.toFixed(3)) + (u ? ' ' + u : '')
}
const head = computed(() => {
  const s = props.r?.status
  return s ? { s, text: t(s === 'pass' ? 'overallPass' : s === 'fail' ? 'overallFail' : 'overallUnknown') } : null
})
</script>

<template>
  <section class="checks" aria-live="polite">
    <h2>{{ t('checks') }}</h2>
    <p v-if="head" class="verdict" :class="head.s">{{ head.text }}</p>
    <ul v-if="r">
      <li v-for="c in r.checks" :key="c.id" :class="c.status">
        <span class="chip">{{ t(c.status) }}</span>
        <span class="what">{{ lang === 'zh' ? c.zh : c.en }}
          <small v-if="c.note">{{ lang === 'zh' ? c.note_zh : c.note }}</small></span>
        <span class="val mono">{{ fmt(c.value, c.unit) }}<small v-if="c.limit != null && c.status !== 'info'">{{ t('limit') }} {{ fmt(c.limit, c.unit) }}</small></span>
      </li>
    </ul>
    <p class="hint">{{ t('ratingsNote') }}</p>
  </section>
</template>
