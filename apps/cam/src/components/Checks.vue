<script setup>
// The checks from the kernel: pass, fail, unknown (data missing, never a pass), n/a, or a value with no limit.
import { computed } from 'vue'
import { t, lang } from '../i18n'

const props = defineProps({ result: Object })
const fmt = (v) => (v === 'inf' ? '∞' : v == null ? '' : Math.abs(v) >= 1000 ? Math.round(v).toLocaleString() : +(+v).toPrecision(4))
const UNIT_ZH = { 'per turn': '次/转' }
const unit = (u) => (lang.value === 'zh' && UNIT_ZH[u]) || u
const joints =computed(() => props.result?.joints || [])
</script>

<template>
  <div v-if="result" class="checks">
    <div class="head"><b>{{ t('checks') }}</b><span :class="['chip', result.status]">{{ t('overall') }}：{{ t(result.status) }}</span></div>
    <ul>
      <li v-for="c in result.checks" :key="c.id">
        <span :class="['chip', c.status]">{{ t(c.status) }}</span>
        <span class="name">{{ lang === 'zh' ? c.zh : c.en }}</span>
        <span class="val mono">{{ fmt(c.value) }}<template v-if="c.value != null"> {{ unit(c.unit) }}</template><template v-if="c.limit != null"> / {{ fmt(c.limit) }}</template></span>
        <span v-if="c.note" class="note">{{ lang === 'zh' ? c.note_zh : c.note }}</span>
      </li>
    </ul>
    <p v-if="joints.length" class="joints">{{ t('joints') }}：<span v-for="j in joints" :key="j.deg + j.kind">{{ j.deg.toFixed(1) }}° {{ lang === 'zh' ? j.zh : j.en }}；</span></p>
  </div>
</template>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
li { display: grid; grid-template-columns: 62px 1fr auto; gap: 2px 8px; align-items: baseline; padding: 5px 0; border-bottom: 1px solid var(--line); font-size: 13px; }
.name { min-width: 0; }
.val { font-size: 12px; white-space: nowrap; }
.note { grid-column: 2 / 4; font-size: 12px; color: var(--hold); }
.chip { display: inline-block; text-align: center; font-size: 11.5px; font-weight: 600; border-radius: 999px; padding: 2px 8px; background: var(--chip); color: var(--muted); white-space: nowrap; }
.chip.pass { background: var(--ok-bg); color: var(--ok); }
.chip.fail { background: var(--bad-bg); color: var(--bad); }
.chip.unknown { background: var(--hold-bg); color: var(--hold); }
.joints { font-size: 12px; color: var(--hold); margin: 8px 0 0; }
</style>
