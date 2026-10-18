<script setup>
// One labelled number field bound to obj[k]; empty means "not given" (null), never 0.
defineProps({ obj: Object, k: String, label: String, unit: String, step: { type: String, default: 'any' } })
const num = (v) => (v === '' || v === null ? null : Number(v))
</script>

<template>
  <label class="nf">{{ label }} <span v-if="unit" class="u">{{ unit }}</span>
    <input :value="obj[k]" type="number" :step="step" @input="obj[k] = num($event.target.value)">
  </label>
</template>

<style scoped>
.nf { display: grid; grid-template-columns: 1fr 104px; align-items: center; gap: 2px 8px; font-size: 13px; }
.nf .u { grid-column: 1; font: 400 11px/1.2 var(--mono); color: var(--muted); }
.nf input { grid-column: 2; grid-row: 1 / span 2; }
</style>
