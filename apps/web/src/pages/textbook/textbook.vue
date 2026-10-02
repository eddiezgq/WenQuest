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
          <text class="toc-book">{{ en ? idx?.title_en || idx?.title : idx?.title }}</text>
          <view v-if="hasRes" class="res-link" :class="{ on: view === 'res' }" @click="showRes">◆ {{ t("book.res_all") }}</view>
          <view class="langs">
            <text class="langs-t">{{ t("book.lang") }}</text>
            <view class="lg" :class="{ on: !en }" @click="setLang('zh')">中文</view>
            <view class="lg" :class="{ on: en }" @click="setLang('en')">English</view>
          </view>
          <view v-for="part in parts" :key="part.title" class="toc-part">
            <text class="toc-part-t">{{ en ? idx?.parts_en?.[part.title] || part.title : part.title }}</text>
            <view v-for="c in part.chapters" :key="c.no" class="toc-ch">
              <view class="toc-ch-t" :class="{ on: cur && cur.chapter.no === c.no, empty: !hasWritten(c) }" @click="toggle(c.no)">
                <text>{{ chapterLabel(c.no) }} {{ en ? c.title_en || c.title : c.title }}</text>
                <text v-if="c.status" class="badge">{{ t("book.status." + c.status) }}</text>
              </view>
              <view v-if="expanded.has(c.no)" class="toc-secs">
                <view v-for="s in c.sections" :key="s.id" class="toc-sec" :class="{ on: cur && cur.id === s.id, off: !s.written }"
                      @click="s.written && read(s.id)">
                  <text>{{ s.kind ? "" : s.id }} {{ en && s.title_en ? s.title_en : s.title }}</text>
                  <text v-if="!s.written" class="todo">{{ t("book.unwritten") }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 全书互动资源（第 9 轮 2.5）：按章列出全部动画和虚拟实验，点一下到正文中的位置 -->
        <view v-if="view === 'res'" class="page">
          <text class="res-h">{{ t("book.res_all") }}</text>
          <text class="res-lead">{{ t("book.res_lead") }}</text>
          <view v-for="c in resChapters" :key="c.no" class="res-ch">
            <text class="res-ch-t">{{ chapterLabel(c.no) }} {{ en ? c.title_en || c.title : c.title }}</text>
            <view class="res-grid">
              <view v-for="r in c.items" :key="r.kind + r.num" class="res-card" @click="go(r)">
                <text class="res-kind">{{ t("book.kind." + r.kind) }} {{ r.num }}</text>
                <text class="res-title">{{ resTitle(r) }}</text>
              </view>
            </view>
          </view>
        </view>

        <view v-else class="page">
          <view v-if="cur" class="crumb">
            <text>{{ chapterLabel(cur.chapter.no) }} {{ cur.chapter.title }}
              <text v-if="cur.chapter.status" class="badge">{{ t("book.status." + cur.chapter.status) }}</text></text>
            <view v-if="pdfFor(cur.chapter.no)" class="pdf" @click="pdf(cur.chapter.no)">⤓ {{ t("book.pdf") }}{{ en ? " (English)" : "" }}</view>
          </view>
          <text v-if="en && cur && cur.lang !== 'en'" class="no-en">{{ t("book.no_en") }}</text>
          <!-- 本章互动资源（第 9 轮 2.5）：章的第一页上列出本章的动画和实验 -->
          <view v-if="cur && atChapterTop && chapterRes.length" class="chips">
            <text class="chips-t">{{ t("book.res") }}</text>
            <view v-for="r in chapterRes" :key="r.kind + r.num" class="chip" @click="go(r)">
              <text class="chip-k">{{ t("book.kind." + r.kind) }} {{ r.num }}</text> {{ resTitle(r) }}
            </view>
          </view>
          <text v-if="error" class="wq-error">{{ error }}</text>
          <text v-if="!cur && loaded && !error" class="wq-empty">{{ t("book.nothing") }}</text>
          <BookContent v-if="cur" :html="cur.html" />
          <view v-if="cur" class="pager">
            <view v-if="cur.prev" class="pg" @click="read(cur.prev.id)">‹ {{ cur.prev.kind ? "" : cur.prev.id }} {{ refTitle(cur.prev) }}</view>
            <view class="sp" />
            <view v-if="cur.next" class="pg" @click="read(cur.next.id)">{{ cur.next.kind ? "" : cur.next.id }} {{ refTitle(cur.next) }} ›</view>
          </view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
// 问渠教材阅读（第 7 轮）：目录按篇、章、节；正文是构建好的网页（公式已在服务器排好）；PDF 只给老师。
import { computed, nextTick, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import BookContent from "../../components/BookContent.vue";
import { absolute, api, ApiError, token, type TextbookChapter, type TextbookIndex, type TextbookResource, type TextbookSection, type TextbookSectionRef } from "../../api";
import { errorText, locale, t } from "../../i18n";

const books = ref<{ book: string; title: string; chapters: number; sections: number; written: number }[]>([]);
const book = ref("");
const idx = ref<TextbookIndex | null>(null);
const cur = ref<TextbookSection | null>(null);
const expanded = ref(new Set<number>());
const tocOpen = ref(false);
const loaded = ref(false);
const error = ref("");
// 正文语言（第 8 轮）：读者自己选，记在本机；默认跟界面语言。没有英文版的节显示中文并说明。
const LANG_KEY = "wq-book-lang";
const lang = ref<"zh" | "en">((uni.getStorageSync(LANG_KEY) as "zh" | "en") || (locale.value === "en" ? "en" : "zh"));
const en = computed(() => lang.value === "en");
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
const chapterLabel = (n: number) => (en.value ? `Chapter ${n}` : `第 ${n} 章`);
const refTitle = (s: TextbookSectionRef) => (en.value && s.title_en ? s.title_en : s.title);
const findRef = (sid: string) => idx.value?.chapters.flatMap((c) => c.sections).find((s) => s.id === sid);
// 互动资源（第 9 轮 2.5）
const view = ref<"read" | "res">("read");
const hasRes = computed(() => Object.keys(idx.value?.resources || {}).length > 0);
const resTitle = (r: TextbookResource) => (en.value && r.title_en ? r.title_en : r.title);
const chapterRes = computed(() => (cur.value && idx.value?.resources?.[String(cur.value.chapter.no)]) || []);
const atChapterTop = computed(() => {
  if (!cur.value) return false;
  const ch = idx.value?.chapters.find((c) => c.no === cur.value!.chapter.no);
  return cur.value.id === ch?.sections.find((s) => s.written)?.id;      // 章首提要，没有提要时是本章第一节
});
const resChapters = computed(() => (idx.value?.chapters || [])
  .filter((c) => idx.value?.resources?.[String(c.no)]?.length)
  .map((c) => ({ ...c, items: idx.value!.resources![String(c.no)] })));
function showRes() { view.value = "res"; tocOpen.value = false; }
async function go(r: TextbookResource) {
  view.value = "read";
  if (!cur.value || cur.value.id !== r.sec) await read(r.sec);
  await nextTick();
  // #ifdef H5
  const el = document.getElementById(`${r.kind === "anim" ? "动画" : "实验"}-${r.num}`);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  // #endif
}
const pdfFor = (ch: number) => (en.value && idx.value?.pdf_en?.includes(ch)) || (!en.value && idx.value?.pdf.includes(ch));

function setLang(l: "zh" | "en") {
  if (lang.value === l) return;
  lang.value = l;
  uni.setStorageSync(LANG_KEY, l);
  if (cur.value) read(cur.value.id);
}

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
  view.value = "read";
  try {
    const want = en.value && findRef(sid)?.en ? "en" : "zh";
    cur.value = await api.textbookSection(book.value, sid, mp, want);
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
    const r = await api.textbookPdf(book.value, ch, en.value && idx.value?.pdf_en?.includes(ch) ? "en" : "zh");
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
.badge { display: inline-block; margin-left: 6px; font-size: 11px; font-weight: 400; color: #8a5a00; background: #fff3d6;
  border: 1px solid #f0d9a8; border-radius: 9px; padding: 0 7px; vertical-align: 1px; }
.langs { display: flex; align-items: center; gap: 6px; padding: 0 6px 8px; }
.langs-t { font-size: 12px; color: var(--wq-muted); margin-right: 2px; }
.lg { font-size: 12px; border: 1px solid var(--wq-line); border-radius: 12px; padding: 2px 10px; cursor: pointer; }
.lg.on { background: var(--wq-ink, #1d2327); color: #fff; border-color: transparent; }
.no-en { display: block; font-size: 13px; color: #8a5a00; background: #fff8e6; border-radius: 6px; padding: 6px 10px; margin: 6px 0; }
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
.res-link { margin: 0 6px 8px; padding: 5px 8px; font-size: 13px; border-radius: 6px; cursor: pointer; color: #8a5a00; background: #fff8e6; }
.res-link.on { font-weight: 700; }
.chips { display: flex; flex-wrap: wrap; gap: 6px 8px; align-items: center; margin: 8px 0 14px; padding: 10px 12px; background: #fbf8f0; border-radius: 8px; }
.chips-t { font-size: 12px; color: var(--wq-muted); margin-right: 4px; }
.chip { font-size: 13px; border: 1px solid #ead9b0; background: #fff; border-radius: 14px; padding: 3px 11px; cursor: pointer; max-width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; box-sizing: border-box; }
.chip-k { color: #8a5a00; font-size: 12px; }
.res-h { display: block; font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.res-lead { display: block; font-size: 13px; color: var(--wq-muted); margin-bottom: 8px; }
.res-ch { margin-top: 18px; }
.res-ch-t { display: block; font-weight: 700; font-size: 15px; margin-bottom: 8px; }
.res-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
.res-card { border: 1px solid var(--wq-line); border-radius: 8px; padding: 10px 12px; cursor: pointer; display: flex; flex-direction: column; gap: 4px; }
.res-card:hover { border-color: #d4a24c; }
.res-kind { font-size: 12px; color: #8a5a00; }
.res-title { font-size: 13.5px; line-height: 1.55; }
@media (max-width: 860px) {
  .reader { flex-direction: column; }
  .toc-toggle { display: block; border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 12px; background: #fff; cursor: pointer; }
  .toc { display: none; width: 100%; position: static; max-height: none; box-sizing: border-box; }
  .toc.open { display: block; }
  .page { padding: 14px 14px 20px; width: 100%; box-sizing: border-box; }
}
</style>
