<script setup>
// One number field: label, input, unit. Empty stays empty (sent as null: the kernel then says “unknown”).
defineProps({ label: String, unit: String, hint: String, step: { type: String, default: 'any' } })
const model = defineModel()
function onInput(e) { const v = e.target.value; model.value = v === '' ? null : Number(v) }
</script>

<template>
  <label class="num">
    <span class="lab">{{ label }}<small v-if="hint">{{ hint }}</small></span>
    <span class="box"><input type="number" :step="step" :value="model ?? ''" @input="onInput"><i>{{ unit }}</i></span>
  </label>
</template>
