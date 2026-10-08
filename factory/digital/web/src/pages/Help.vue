<!-- 帮助（第 19 轮 J-10）：每页右上角“帮助”打开这里；左边是目录，右边是帮助正文（仓库 docs/帮助、docs/演示 的副本）。手机宽度可用 -->
<template>
  <div class="page help">
    <nav class="toc card" aria-label="帮助目录">
      <div v-for="g in groups" :key="g.group" class="tg">
        <span class="small muted">{{ g.group }}</span>
        <router-link v-for="i in g.items" :key="i.name" :to="'/help/' + i.name" :class="{ on: i.name === name }">{{ i.title }}</router-link>
      </div>
    </nav>
    <article class="card doc">
      <div v-if="err" class="err">{{ err }}</div>
      <!-- 帮助正文来自仓库里的 Markdown（服务器转 HTML），不是用户输入 -->
      <div v-if="doc" class="md" v-html="doc.html"></div>
    </article>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { get } from '../lib/api';

const route = useRoute();
const groups = ref([]);
const doc = ref(null);
const err = ref('');
const name = computed(() => route.params.name || '使用说明');

async function load() {
  err.value = '';
  try { doc.value = await get('/help/' + encodeURIComponent(name.value)); window.scrollTo({ top: 0 }); } catch (e) { doc.value = null; err.value = e.message; }
}
watch(name, load);
onMounted(async () => { load(); try { groups.value = (await get('/help')).groups; } catch (e) { /* 目录读不到不影响正文 */ } });
</script>

<style scoped>
.page.help { display: flex; flex-direction: row; gap: 14px; align-items: flex-start; }
.toc { width: 220px; flex-shrink: 0; display: flex; flex-direction: column; gap: 10px; position: sticky; top: 8px; }
.tg { display: flex; flex-direction: column; gap: 2px; }
.tg a { padding: 3px 6px; border-radius: 5px; color: inherit; text-decoration: none; font-size: 13px; }
.tg a.on { background: var(--accent); color: #fff; }
.doc { flex: 1; min-width: 0; }
.md :deep(table) { border-collapse: collapse; margin: 8px 0; display: block; overflow-x: auto; }
.md :deep(th), .md :deep(td) { border: 1px solid var(--line); padding: 4px 8px; font-size: 13px; vertical-align: top; }
.md :deep(h1) { font-size: 22px; }
.md :deep(h2) { font-size: 18px; margin-top: 20px; }
.md :deep(code) { background: var(--surface-2); padding: 0 4px; border-radius: 4px; }
.md :deep(pre) { background: var(--surface-2); padding: 8px; overflow-x: auto; }
@media (max-width: 800px) { .page.help { flex-direction: column; align-items: stretch; } .toc { width: auto; position: static; } }
</style>
