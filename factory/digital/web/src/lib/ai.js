// AI 工厂助手的对话状态（全站共用一个抽屉）
import { reactive } from 'vue';
import { post } from './api';

export const ai = reactive({ open: false, busy: false, messages: [], error: null });

export async function ask(text) {
  if (!text.trim() || ai.busy) return;
  ai.open = true;
  ai.error = null;
  ai.messages.push({ role: 'user', content: text.trim() });
  ai.busy = true;
  try {
    const r = await post('/ai/chat', { messages: ai.messages.map(({ role, content }) => ({ role, content })) });
    ai.messages.push({ role: 'assistant', content: r.answer, proposals: r.proposals || [], engine: r.engine, note: r.note });
  } catch (e) {
    ai.error = e.message;
  } finally {
    ai.busy = false;
  }
}
