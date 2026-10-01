<template>
  <view v-if="flow && (flow.prereview || history.length)" class="ro">
    <view v-if="flow.prereview" class="ro-pre">
      <view class="ro-head">
        <text class="ro-h">{{ t("rev.pre") }}</text>
        <text class="ro-v" :class="flow.prereview.verdict">{{ t("rev.verdict." + flow.prereview.verdict) }}</text>
      </view>
      <text class="ro-sum">{{ flow.prereview.summary }}</text>
      <view class="ro-items">
        <text v-for="(it, i) in flow.prereview.items" :key="i" class="ro-item" :class="it.ok === true ? 'ok' : it.ok === false ? 'no' : 'unk'">
          {{ it.ok === true ? "✓" : it.ok === false ? "✗" : "?" }} {{ it.label }}<text v-if="it.note" class="ro-note">：{{ it.note }}</text>
        </text>
      </view>
      <view v-if="flow.prereview.issues.length" class="ro-issues">
        <text class="ro-sub">{{ t("rev.issues", { n: flow.prereview.issues.length }) }}</text>
        <view v-for="(x, i) in flow.prereview.issues" :key="i" class="ro-issue" :class="x.severity">
          <text class="ro-sev">{{ t("rev.sev." + x.severity) }}</text>
          <text class="ro-t"><text v-if="x.where" class="ro-where">{{ x.where }} · </text>{{ x.text }}<text v-if="x.fix" class="ro-fix">　→ {{ x.fix }}</text></text>
        </view>
      </view>
      <text v-if="flow.prereview.highlights && flow.prereview.highlights.length" class="ro-hl">✦ {{ flow.prereview.highlights.join("；") }}</text>
    </view>
    <view v-if="history.length" class="ro-hist">
      <text class="ro-sub">{{ t("rev.history") }}</text>
      <text v-for="(h, i) in history" :key="i" class="ro-hrow">{{ day(h.ts) }} · {{ h.who }} · {{ t("rev.act." + h.action) }}<text v-if="h.comment && h.action !== 'prereview'">：{{ h.comment }}</text></text>
    </view>
  </view>
</template>

<script setup lang="ts">
// 预审意见 and the review history of one lesson (round 6) — shown to the teacher and to the committee.
import { computed } from "vue";
import { formatDate, t } from "../../i18n";
import type { ReviewFlow } from "../../api";

const props = defineProps<{ flow?: ReviewFlow | null }>();
const history = computed(() => (props.flow?.history || []).filter((h) => h.action !== "submit").slice().reverse());
const day = (ts: number) => formatDate(ts);
</script>

<style scoped>
.ro { display: flex; flex-direction: column; gap: 10px; margin: 10px 0; }
.ro-pre { border: 1px solid var(--wq-line); border-radius: 8px; padding: 10px 12px; background: #fbfcfd; display: flex; flex-direction: column; gap: 6px; }
.ro-head { display: flex; gap: 10px; align-items: center; }
.ro-h { font-weight: 600; font-size: 14px; }
.ro-v { font-size: 12px; padding: 2px 8px; border-radius: 10px; background: #eef1f4; }
.ro-v.approve { background: #dff3e4; color: #1f6b35; }
.ro-v.revise { background: #fff1d6; color: #8a5a00; }
.ro-v.reject { background: #fde2df; color: #9b2c1f; }
.ro-sum { font-size: 14px; line-height: 1.6; }
.ro-items { display: flex; flex-direction: column; gap: 2px; }
.ro-item { font-size: 13px; }
.ro-item.ok { color: #1f6b35; } .ro-item.no { color: #9b2c1f; } .ro-item.unk { color: #8a5a00; }
.ro-note { color: var(--wq-text); }
.ro-sub { font-size: 12px; color: var(--wq-muted); }
.ro-issues { display: flex; flex-direction: column; gap: 4px; }
.ro-issue { display: flex; gap: 8px; font-size: 13px; line-height: 1.55; }
.ro-sev { flex-shrink: 0; font-size: 11px; padding: 1px 6px; border-radius: 8px; background: #eef1f4; height: fit-content; }
.ro-issue.high .ro-sev { background: #fde2df; color: #9b2c1f; }
.ro-issue.medium .ro-sev { background: #fff1d6; color: #8a5a00; }
.ro-where { color: var(--wq-muted); }
.ro-fix { color: #1f5f8b; }
.ro-hl { font-size: 13px; color: #1f6b35; }
.ro-hist { display: flex; flex-direction: column; gap: 2px; }
.ro-hrow { font-size: 12px; color: var(--wq-text); }
</style>
