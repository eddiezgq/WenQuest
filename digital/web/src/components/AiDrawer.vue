<template>
  <aside v-if="ai.open" class="drawer" aria-label="AI 工厂助手">
    <header>
      <b>AI 工厂助手</b>
      <span class="muted small">{{ session.user?.mode === 'teach' ? '教学模式：只提示方向' : '生产模式：可代办，写操作需你确认' }}</span>
      <button class="x" aria-label="关闭" @click="ai.open = false">×</button>
    </header>
    <div ref="box" class="msgs">
      <p v-if="!ai.messages.length" class="muted small">
        问我全厂的任何情况，我从统一数据总线和历史库里查，并注明来源。例如：
      </p>
      <div v-if="!ai.messages.length" class="chips">
        <button v-for="q in samples" :key="q" class="chip" @click="ask(q)">{{ q }}</button>
      </div>
      <div v-for="(m, i) in ai.messages" :key="i" class="msg" :class="m.role">
        <div class="bubble">{{ m.content }}</div>
        <div v-if="m.note" class="muted small">{{ m.note }}</div>
        <div v-for="pid in m.proposals || []" :key="pid" class="prop">
          <span>已起草提议 <b class="mono">{{ pid }}</b></span>
          <button class="btn primary" @click="openProposal(pid)">预览并确认</button>
        </div>
      </div>
      <div v-if="ai.busy" class="muted small">正在查询总线与历史库…</div>
      <div v-if="ai.error" class="err">{{ ai.error }}</div>
    </div>
    <form class="ask" @submit.prevent="send">
      <input v-model="text" placeholder="例如：SO 为什么会延期？本周瓶颈在哪？" aria-label="问 AI 工厂助手">
      <button class="btn primary" :disabled="ai.busy">发送</button>
    </form>
    <ProposalModal v-if="pid" :pid="pid" @close="pid = null" />
  </aside>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue';
import { session } from '../lib/api';
import { ai, ask } from '../lib/ai';
import ProposalModal from './ProposalModal.vue';

const text = ref('');
const box = ref(null);
const pid = ref(null);
const samples = computed(() => (session.user?.mode === 'teach'
  ? ['我下一步做什么？', 'MRP 是什么？', '本周瓶颈在哪？']
  : ['哪张订单可能延期？为什么？', '本周瓶颈在哪？', '10 台 WQR-105，10 月 15 日交货']));
function send() { const t = text.value; text.value = ''; ask(t); }
function openProposal(id) { pid.value = id; }
watch(() => ai.messages.length, async () => { await nextTick(); if (box.value) box.value.scrollTop = box.value.scrollHeight; });
</script>

<style scoped>
.drawer { position: fixed; right: 0; top: 0; bottom: 0; width: min(420px, 100%); background: #fff; border-left: 1px solid var(--line);
  box-shadow: -8px 0 24px rgba(23, 33, 43, .08); display: flex; flex-direction: column; z-index: 40; }
header { display: flex; align-items: baseline; gap: 10px; padding: 16px 18px; border-bottom: 1px solid var(--line); }
.x { margin-left: auto; border: 0; background: none; font-size: 22px; cursor: pointer; color: var(--muted); }
.msgs { flex-grow: 1; overflow-y: auto; padding: 16px 18px; display: flex; flex-direction: column; gap: 12px; }
.msg.user { align-self: flex-end; max-width: 85%; }
.msg.user .bubble { background: var(--accent); color: #fff; }
.msg.assistant { align-self: flex-start; max-width: 95%; }
.bubble { background: var(--surface-2); border-radius: 10px; padding: 10px 12px; white-space: pre-wrap; line-height: 1.55; font-size: 13px; }
.prop { display: flex; align-items: center; gap: 10px; margin-top: 6px; font-size: 13px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { height: 28px; padding: 0 10px; border-radius: 14px; border: 1px solid var(--line); background: var(--surface-2); cursor: pointer; font-size: 12px; }
.ask { display: flex; gap: 8px; padding: 12px 18px; border-top: 1px solid var(--line); }
.ask input { flex-grow: 1; height: 38px; border: 1px solid #C8CEC7; border-radius: 8px; padding: 0 12px; }
</style>
