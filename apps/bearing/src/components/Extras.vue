<script setup>
// Below the drawings: the clearance chain (deep groove) as a stepped bar, and the fault frequencies for vibration checks.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const chain = computed(() => {
  const c = props.r?.chain
  if (!c) return null
  const um = (x) => x * 1000
  return [
    ['initial', um(c.initial)], ['fitInner', -um(c.fit_inner)], ['fitOuter', -um(c.fit_outer)],
    ['thermal', um(c.thermal)], ['operating', um(c.operating)],
  ]
})
const freq = computed(() => {
  const f = props.r?.freq
  return f ? [['shaft', f.shaft], ['ftf', f.FTF], ['bpfo', f.BPFO], ['bpfi', f.BPFI], ['bsf', f.BSF]] : null
})
const sgn = (k, x) => (k === 'initial' || k === 'operating' ? '' : x >= 0 ? '+' : '') + x.toFixed(1)
</script>

<template>
  <div class="extras">
    <section v-if="chain">
      <h3>{{ t('chain') }} <small>µm</small></h3>
      <dl class="rows">
        <template v-for="[k, x] in chain" :key="k"><dt :class="{ strong: k === 'operating' }">{{ t(k) }}</dt>
          <dd class="mono" :class="{ strong: k === 'operating', neg: k === 'operating' && x < 0 }">{{ sgn(k, x) }}</dd></template>
      </dl>
    </section>
    <section v-if="freq">
      <h3>{{ t('freq') }} <small>Hz</small></h3>
      <dl class="rows">
        <template v-for="[k, x] in freq" :key="k"><dt>{{ t(k) }}</dt><dd class="mono">{{ x.toFixed(2) }}</dd></template>
      </dl>
    </section>
    <section v-if="r?.pair_rows">
      <h3>{{ t('pairRows') }}</h3>
      <dl class="rows">
        <template v-for="(x, j) in r.pair_rows" :key="j">
          <dt>z = {{ x.z.toFixed(1) }} mm</dt><dd class="mono">Fa {{ x.Fa.toFixed(0) }}, Fr {{ x.Fr.toFixed(0) }}, Q<sub>max</sub> {{ x.Qmax.toFixed(0) }} N</dd>
        </template>
      </dl>
    </section>
    <section v-if="r?.contact?.inner">
      <h3>{{ t('heaviest') }}</h3>
      <dl class="rows">
        <dt>Q</dt><dd class="mono">{{ r.contact.inner.Q.toFixed(0) }} N</dd>
        <template v-if="r.type !== 'cylindrical'"><dt>{{ t('contactAngle') }}</dt><dd class="mono">{{ r.contact.inner.alpha_deg.toFixed(2) }}°</dd></template>
        <template v-for="ring in (r.contact.inner.a != null ? ['inner', 'outer'] : [])" :key="ring">
          <dt>{{ t('ellipse') }}，{{ t(ring + 'Ring') }}</dt>
          <dd class="mono">{{ r.contact[ring].a.toFixed(3) }} × {{ r.contact[ring].b.toFixed(3) }} mm</dd>
        </template>
      </dl>
    </section>
  </div>
</template>
