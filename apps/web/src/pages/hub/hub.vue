<template>
  <AppShell :nav="view" :title="t(view === 'help' ? 'help.title' : 'shell.' + view)">
    <!-- Help: short answers to the questions people ask first -->
    <view v-if="view === 'help'" class="help">
      <text class="h1">{{ t("help.title") }}</text>
      <view v-for="qa in FAQ" :key="qa[0]" class="qa">
        <text class="q">{{ qa[0] }}</text>
        <text class="a">{{ qa[1] }}</text>
      </view>
      <text class="contact">{{ t("help.contact") }}</text>
    </view>

    <!-- Calendar of all my courses, and the inbox -->
    <Calendar v-else-if="view === 'calendar'" />
    <Inbox v-else-if="view === 'inbox'" />
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { token } from "../../api";
import Calendar from "../../components/course/Calendar.vue";
import Inbox from "../../components/Inbox.vue";
import { t } from "../../i18n";

// Page query parameters must not fall through onto the layout component.
defineOptions({ inheritAttrs: false });

const FAQ = computed(() => [
  [t("help.qStart"), t("help.aStart")], [t("help.qFind"), t("help.aFind")], [t("help.qSubmit"), t("help.aSubmit")],
  [t("help.qBuild"), t("help.aBuild")], [t("help.qDiffer"), t("help.aDiffer")],
]);
const view = ref("help");

onLoad((q: any) => {
  view.value = ["calendar", "inbox", "help"].includes(q?.view) ? q.view : "help";
});
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t(view.value === "help" ? "help.title" : "shell." + view.value) });
});
</script>

<style scoped>
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); margin-bottom: 18px; }
.help { max-width: 820px; }
.qa { background: #fff; border: 1px solid var(--wq-line); border-radius: 6px; padding: 16px 20px; margin-bottom: 10px; }
.q { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 6px; }
.a { display: block; color: var(--wq-text); line-height: 1.75; }
.contact { display: block; color: var(--wq-muted); margin-top: 16px; }
.soon { max-width: 820px; background: #fff; border: 1px solid var(--wq-line); border-left: 4px solid var(--wq-accent); border-radius: 6px; padding: 18px 22px; }
.soon-h { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 6px; }
.soon-p { display: block; color: var(--wq-text); line-height: 1.75; }
.soon-step { display: block; font-size: 13px; color: var(--wq-muted); margin-top: 10px; }
.primary { display: inline-block; margin-top: 14px; background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 9px 18px; border-radius: 8px; cursor: pointer; }
</style>
