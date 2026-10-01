<template>
  <AppShell nav="textbook" :title="idx ? idx.title : t('book.nav')">
    <view class="wrap">
      <!-- the list of textbooks -->
      <view v-if="!book" class="shelf">
        <text class="wq-h1">{{ t("book.nav") }}</text>
        <text v-if="loaded && !books.length" class="wq-empty">{{ t("book.none") }}</text>
        <view v-for="b in books" :key="b.book" class="cover" @click="open(b.book)">
          <text class="c-title">{{ b.title }}</text>
          <text class="c-meta">{{ t("book.meta", { c: b.chapters, s: b.sections, w: b.written }) }}</text>
        </view>
      </view>

      <!-- reader -->
      <view v-else class="reader">
        <view class="toc-toggle narrow-only" @click="tocOpen = !tocOpen">☰ {{ t("book.toc") }}</view>
        <view class="toc" :class="{ open: tocOpen }">
          <text class="toc-book">{{ idx?.title }}</text>
          <view v-for="part in parts" :key="part.title" class="toc-part">
            <text class="toc-part-t">{{ part.title }}</text>
            <view v-for="c in part.chapters" :key="c.no" class="toc-ch">
              <view class="toc-ch-t" :class="{ on: cur && cur.chapter.no === c.no, empty: !hasWritten(c) }" @click="toggle(c.no)">
                <text>{{ t("book.chapter", { n: c.no }) }} {{ c.title }}</text>
              </view>
              <view v-if="expanded.has(c.no)" class="toc-secs">
                <view v-for="s in c.sections" :key="s.id" class="toc-sec" :class="{ on: cur && cur.id === s.id, off: !s.written }"
                      @click="s.written && read(s.id)">
                  <text>{{ s.kind ? "" : s.id }} {{ s.title }}</text>
                  <text v-if="!s.written" class="todo">{{ t("book.unwritten") }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view class="page">
          <view v-if="cur" class="crumb">
            <text>{{ t("book.chapter", { n: cur.chapter.no }) }} {{ cur.chapter.title }}</text>
            <view v-if="idx && idx.pdf.includes(cur.chapter.no)" class="pdf" @click="pdf(cur.chapter.no)">⤓ {{ t("book.pdf") }}</view>
          </view>
          <text v-if="error" class="wq-error">{{ error }}</text>
          <text v-if="!cur && loaded && !error" class="wq-empty">{{ t("book.nothing") }}</text>
          <BookContent v-if="cur" :html="cur.html" />
          <view v-if="cur" class="pager">
            <view v-if="cur.prev" class="pg" @click="read(cur.prev.id)">‹ {{ cur.prev.kind ? "" : cur.prev.id }} {{ cur.prev.title }}</view>
            <view class="sp" />
            <view v-if="cur.next" class="pg" @click="read(cur.next.id)">{{ cur.next.kind ? "" : cur.next.id }} {{ cur.next.title }} ›</view>
          </view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
// 问渠教材阅读（第 7 轮）：目录按篇、章、节；正文是构建好的网页（公式已在服务器排好）；PDF 只给老师。
import { computed, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import BookContent from "../../components/BookContent.vue";
import { absolute, api, ApiError, token, type TextbookChapter, type TextbookIndex, type TextbookSection } from "../../api";
import { errorText, t } from "../../i18n";

const books = ref<{ book: string; title: string; chapters: number; sections: number; written: number }[]>([]);
const book = ref("");
const idx = ref<TextbookIndex | null>(null);
const cur = ref<TextbookSection | null>(null);
const expanded = ref(new Set<number>());
const tocOpen = ref(false);
const loaded = ref(false);
const error = ref("");
let mp = false;
// #ifndef H5
mp = true;
// #endif

const parts = computed(() => {
  const out: { title: string; chapters: TextbookChapter[] }[] = [];
  for (const c of idx.value?.chapters || []) {
    const last = out[out.length - 1];
    if (last && last.title === c.part) last.chapters.push(c);
    else out.push({ title: c.part, chapters: [c] });
  }
  return out;
});
const hasWritten = (c: TextbookChapter) => c.sections.some((s) => s.written);

function fail(e: unknown) { error.value = errorText(e instanceof ApiError ? e.code : "unknown"); }

function toggle(no: number) {
  const s = new Set(expanded.value);
  if (s.has(no)) s.delete(no); else s.add(no);
  expanded.value = s;
}

async function open(b: string, sid = "") {
  book.value = b;
  error.value = "";
  try {
    idx.value = await api.textbook(b);
    const first = idx.value.chapters.flatMap((c) => c.sections).find((s) => s.written);
    const target = sid || first?.id || "";
    if (target) await read(target);
  } catch (e) { fail(e); }
  loaded.value = true;
}

async function read(sid: string) {
  error.value = "";
  try {
    cur.value = await api.textbookSection(book.value, sid, mp);
    expanded.value = new Set([...expanded.value, cur.value.chapter.no]);
    tocOpen.value = false;
    // #ifdef H5
    history.replaceState(null, "", `#/pages/textbook/textbook?book=${book.value}&s=${sid}`);
    window.scrollTo({ top: 0 });
    // #endif
  } catch (e) { fail(e); }
}

async function pdf(ch: number) {
  try {
    const r = await api.textbookPdf(book.value, ch);
    // #ifdef H5
    window.open(absolute(r.url), "_blank");
    // #endif
    // #ifndef H5
    uni.downloadFile({ url: absolute(r.url), success: (x) => uni.openDocument({ filePath: x.tempFilePath, fileType: "pdf" }) });
    // #endif
  } catch (e) { fail(e); }
}

onLoad(async (q: any) => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login?back=" + encodeURIComponent("/pages/textbook/textbook") });
  try {
    books.value = (await api.textbooks()).books;
    const b = q?.book || (books.value.length === 1 ? books.value[0].book : "");
    if (b) await open(b, q?.s || "");
  } catch (e) { fail(e); }
  loaded.value = true;
});
</script>

<style scoped>
.wrap { padding: 16px; }
.shelf { display: flex; flex-direction: column; gap: 12px; max-width: 640px; }
.cover { background: #fff; border: 1px solid var(--wq-line); border-left: 6px solid var(--wq-accent); border-radius: 8px; padding: 16px 18px; cursor: pointer;
  display: flex; flex-direction: column; gap: 4px; }
.c-title { font-size: 20px; font-weight: 700; }
.c-meta { font-size: 13px; color: var(--wq-muted); }
.reader { display: flex; gap: 20px; align-items: flex-start; }
.toc { width: 290px; flex-shrink: 0; background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; padding: 12px 10px;
  max-height: calc(100vh - 110px); overflow-y: auto; position: sticky; top: 16px; }
.toc-book { display: block; font-weight: 700; font-size: 16px; padding: 2px 6px 8px; }
.toc-part-t { display: block; font-size: 12px; color: var(--wq-muted); padding: 10px 6px 4px; letter-spacing: 0.04em; }
.toc-ch-t { padding: 5px 6px; font-size: 14px; border-radius: 6px; cursor: pointer; }
.toc-ch-t.on { font-weight: 700; }
.toc-ch-t.empty { color: #9aa5ab; }
.toc-secs { padding-left: 10px; }
.toc-sec { padding: 4px 6px; font-size: 13px; border-radius: 6px; cursor: pointer; display: flex; justify-content: space-between; gap: 6px; }
.toc-sec.on { background: #fff6dd; font-weight: 600; }
.toc-sec.off { color: #a7b0b5; cursor: default; }
.todo { font-size: 11px; flex-shrink: 0; }
.page { flex: 1; min-width: 0; max-width: 820px; background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; padding: 20px 28px 28px; }
.crumb { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: var(--wq-muted); margin-bottom: 4px; gap: 10px; }
.pdf { border: 1px solid var(--wq-line); border-radius: 6px; padding: 4px 10px; cursor: pointer; color: var(--wq-ink); flex-shrink: 0; }
.pager { display: flex; gap: 10px; margin-top: 28px; border-top: 1px solid var(--wq-line); padding-top: 14px; }
.pg { font-size: 14px; color: var(--wq-link); cursor: pointer; }
.sp { flex: 1; }
.toc-toggle { display: none; }
@media (max-width: 860px) {
  .reader { flex-direction: column; }
  .toc-toggle { display: block; border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 12px; background: #fff; cursor: pointer; }
  .toc { display: none; width: 100%; position: static; max-height: none; box-sizing: border-box; }
  .toc.open { display: block; }
  .page { padding: 14px 14px 20px; width: 100%; box-sizing: border-box; }
}
</style>
