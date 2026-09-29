<template>
  <AuthCard wide>
    <!-- done: what happens next -->
    <template v-if="done">
      <text class="title">{{ done === "student" ? t("reg.doneStudent") : done === "approved" ? t("reg.doneTeacher") : t("reg.doneApplied") }}</text>
      <text class="lead">{{ done === "student" ? t("reg.doneStudentText") : done === "approved" ? t("reg.doneTeacherText") : t("reg.doneAppliedText") }}</text>
      <view v-if="appStatus === 'need_more'" class="note warn">
        <text class="block strong">{{ t("apply.needMore") }}</text>
        <text class="block">{{ appMore }}</text>
      </view>
      <view class="submit" @click="finish">{{ t("reg.enter") }}</view>
      <text v-if="done === 'pending'" class="wq-link center" @click="uni2('/pages/apply/apply')">{{ t("reg.seeApplication") }}</text>
    </template>

    <template v-else>
      <text class="title">{{ t("reg.title") }}</text>
      <text class="tagline">{{ t("reg.tagline") }}</text>

      <!-- role -->
      <view class="roles">
        <view class="role" :class="{ on: role === 'student' }" @click="role = 'student'">
          <text class="r-name">🎓 {{ t("reg.student") }}</text>
          <text class="r-desc">{{ t("reg.studentDesc") }}</text>
        </view>
        <view class="role" :class="{ on: role === 'teacher' }" @click="role = 'teacher'">
          <text class="r-name">🧑‍🏫 {{ t("reg.teacher") }}</text>
          <text class="r-desc">{{ t("reg.teacherDesc") }}</text>
        </view>
      </view>

      <view class="two">
        <view class="field">
          <text class="label">{{ t("reg.lastname") }}</text>
          <input class="input" v-model="lastname" autocomplete="family-name" />
        </view>
        <view class="field">
          <text class="label">{{ t("reg.firstname") }}</text>
          <input class="input" v-model="firstname" autocomplete="given-name" />
        </view>
      </view>

      <view class="field">
        <text class="label">{{ t("reg.email") }}</text>
        <view class="code-row">
          <input class="input grow" v-model="email" type="text" autocomplete="email" :placeholder="role === 'teacher' ? t('reg.emailTeacherHint') : 'name@example.com'" />
          <view class="code-btn" :class="{ disabled: wait > 0 || sending || !emailOk }" @click="sendCode">
            {{ sending ? t("reg.sending") : wait > 0 ? t("reg.resendIn", { n: wait }) : sent ? t("reg.resend") : t("reg.sendCode") }}
          </view>
        </view>
        <text v-if="sent" class="hint">{{ t("reg.codeSent", { email: sentTo }) }}</text>
        <text v-if="role === 'teacher' && schoolMail" class="hint ok">✓ {{ t("reg.schoolMail") }}</text>
      </view>
      <view class="field">
        <text class="label">{{ t("reg.code") }}</text>
        <input class="input" v-model="code" type="number" maxlength="6" :placeholder="t('reg.codeHint')" autocomplete="one-time-code" />
      </view>
      <view class="field">
        <text class="label">{{ t("login.password") }}</text>
        <input class="input" v-model="password" password autocomplete="new-password" :placeholder="t('reg.passwordHint')" />
        <text v-if="password && !pwOk" class="hint bad">{{ t("reg.passwordHint") }}</text>
      </view>

      <!-- teachers -->
      <view v-if="role === 'teacher'" class="teacher">
        <text class="sec">{{ t("reg.teacherInfo") }}</text>
        <view class="field">
          <text class="label">{{ t("apply.institution") }} *</text>
          <input class="input" v-model="institution" :placeholder="t('apply.institutionHint')" />
        </view>
        <view class="two">
          <view class="field">
            <text class="label">{{ t("apply.department") }}</text>
            <input class="input" v-model="department" />
          </view>
          <view class="field">
            <text class="label">{{ t("apply.jobTitle") }}</text>
            <input class="input" v-model="title" :placeholder="t('apply.jobTitleHint')" />
          </view>
        </view>
        <template v-if="!schoolMail">
          <text class="label">{{ t("apply.evidence") }}</text>
          <text class="hint">{{ t("apply.evidenceHint") }}</text>
          <view class="files">
            <view v-for="(f, i) in files" :key="i" class="file">
              <text class="f-name">{{ f.name }}</text>
              <text class="wq-link" @click="files.splice(i, 1)">✕</text>
            </view>
            <view v-if="files.length < 5" class="wq-btn small" @click="pick">＋ {{ t("apply.addFile") }}</view>
          </view>
          <view class="field">
            <text class="label">{{ t("apply.note") }}</text>
            <textarea v-model="note" class="wq-textarea short" :placeholder="t('apply.noteHint')" />
          </view>
        </template>
      </view>

      <view class="agree" @click="agree = !agree">
        <text class="box">{{ agree ? "☑" : "☐" }}</text>
        <text>{{ t("reg.agree1") }}<text class="wq-link" @click.stop="openSite('/terms.html')">{{ t("auth.terms") }}</text>{{ t("reg.agree2") }}<text class="wq-link" @click.stop="openSite('/privacy.html')">{{ t("auth.privacy") }}</text></text>
      </view>

      <text v-if="error" class="error" role="alert">{{ error }}</text>
      <view class="submit" :class="{ disabled: busy || !ready }" @click="submit">{{ busy ? busyText : t("reg.submit") }}</view>
      <view class="alt">
        <text class="wq-muted">{{ t("reg.haveAccount") }}</text>
        <text class="wq-link strong" @click="toLogin">{{ t("login.submit") }}</text>
      </view>
    </template>
  </AuthCard>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import AuthCard from "../../components/auth/AuthCard.vue";
import { PASSWORD_OK, accountApi, afterLogin, siteUrl } from "../../accountApi";
import { ApiError } from "../../api";
import { errorText, t } from "../../i18n";

const role = ref<"student" | "teacher">("student");
const lastname = ref("");
const firstname = ref("");
const email = ref("");
const code = ref("");
const password = ref("");
const institution = ref("");
const department = ref("");
const title = ref("");
const note = ref("");
const files = ref<File[]>([]);
const agree = ref(false);
const busy = ref(false);
const busyText = ref("");
const error = ref("");
const sending = ref(false);
const sent = ref(false);
const sentTo = ref("");
const wait = ref(0);
const done = ref<"" | "student" | "approved" | "pending">("");
const appStatus = ref("");
const appMore = ref("");
const back = ref("");
let timer: ReturnType<typeof setInterval> | null = null;

const emailOk = computed(() => /^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$/.test(email.value.trim()));
const schoolMail = computed(() => /(^|\.)(edu|ac)(\.[a-z]{2})?$/i.test(email.value.trim().split("@")[1] || ""));
const pwOk = computed(() => PASSWORD_OK(password.value));
const ready = computed(() => lastname.value.trim() && firstname.value.trim() && emailOk.value && code.value.trim().length >= 4 &&
  pwOk.value && agree.value && (role.value === "student" || institution.value.trim()));

onLoad((q: any) => {
  back.value = q?.back ? decodeURIComponent(String(q.back)) : "";
  if (q?.role === "teacher") role.value = "teacher";
});
onUnmounted(() => timer && clearInterval(timer));

async function sendCode() {
  if (wait.value > 0 || sending.value || !emailOk.value) return;
  sending.value = true;
  error.value = "";
  try {
    await accountApi.sendCode(email.value.trim(), "register");
    sent.value = true;
    sentTo.value = email.value.trim();
    countdown(60);
  } catch (e) {
    const c = e instanceof ApiError ? e.code : "unknown";
    error.value = errorText(c);
    if (c === "code_too_soon") countdown(60);
  } finally {
    sending.value = false;
  }
}
function countdown(n: number) {
  wait.value = n;
  timer && clearInterval(timer);
  timer = setInterval(() => {
    wait.value -= 1;
    if (wait.value <= 0 && timer) clearInterval(timer);
  }, 1000);
}

function pick() {
  // #ifdef H5
  const input = document.createElement("input");
  input.type = "file";
  input.multiple = true;
  input.accept = "image/*,.pdf";
  input.onchange = () => {
    for (const f of Array.from(input.files || [])) if (files.value.length < 5) files.value.push(f);
  };
  input.click();
  // #endif
}

async function submit() {
  if (busy.value || !ready.value) return;
  busy.value = true;
  busyText.value = t("reg.busy");
  error.value = "";
  try {
    const r = await accountApi.register({
      role: role.value, email: email.value.trim(), code: code.value.trim(), password: password.value,
      lastname: lastname.value.trim(), firstname: firstname.value.trim(), agree: agree.value,
      institution: institution.value.trim(), department: department.value.trim(), title: title.value.trim(), note: note.value.trim(),
    });
    if (role.value === "student") done.value = "student";
    else if (r.teacher_status === "approved") done.value = "approved";
    else {
      // The account exists now: upload the evidence, then the AI reviews the application.
      for (const [i, f] of files.value.entries()) {
        busyText.value = t("reg.uploading", { i: i + 1, n: files.value.length });
        try { await accountApi.uploadEvidence(f); } catch { /* a bad file must not block sign-up; it can be added later */ }
      }
      busyText.value = t("reg.reviewing");
      try {
        const a = (await accountApi.submitApplication()).application;
        appStatus.value = a.status;
        appMore.value = a.more;
      } catch { /* reviewed later by the gateway */ }
      done.value = "pending";
    }
  } catch (e) {
    error.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    busy.value = false;
  }
}
function finish() {
  afterLogin(back.value, done.value === "approved" ? "/pages/studio/studio" : "/pages/courses/courses");
}
const uni2 = (url: string) => uni.reLaunch({ url });
const toLogin = () => uni.redirectTo({ url: `/pages/login/login${back.value ? `?back=${encodeURIComponent(back.value)}` : ""}` });
function openSite(path: string) {
  // #ifdef H5
  window.open(siteUrl(path), "_blank");
  // #endif
}
</script>

<style scoped>
.title { font-size: 24px; font-weight: 700; color: var(--wq-ink); }
.tagline, .lead { font-size: 14px; color: var(--wq-muted); margin: 6px 0 20px; line-height: 1.7; }
.roles { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 18px; }
.role { border: 1.5px solid var(--wq-line); border-radius: 10px; padding: 12px; cursor: pointer; }
.role.on { border-color: var(--wq-ink); background: #fbfaf3; box-shadow: inset 0 0 0 1px var(--wq-ink); }
.r-name { display: block; font-weight: 700; color: var(--wq-ink); font-size: 15px; }
.r-desc { display: block; font-size: 12px; color: var(--wq-muted); margin-top: 4px; line-height: 1.5; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.field { display: flex; flex-direction: column; margin-bottom: 14px; }
.label { font-size: 14px; color: var(--wq-text); margin-bottom: 6px; display: block; }
.input { height: 42px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 0 12px; font-size: 15px; background: #fafbfa; }
.code-row { display: flex; gap: 8px; }
.grow { flex: 1; min-width: 0; }
.code-btn { flex-shrink: 0; height: 42px; line-height: 42px; padding: 0 14px; border-radius: 8px; background: var(--wq-ink); color: #fff; font-size: 14px; cursor: pointer; white-space: nowrap; }
.code-btn.disabled { opacity: .45; pointer-events: none; }
.hint { display: block; font-size: 12px; color: var(--wq-muted); margin-top: 5px; line-height: 1.5; }
.hint.ok { color: var(--wq-ok); }
.hint.bad { color: var(--wq-danger); }
.teacher { border-top: 1px dashed var(--wq-line); padding-top: 14px; margin-top: 4px; }
.sec { display: block; font-weight: 700; color: var(--wq-ink); margin-bottom: 10px; }
.files { display: flex; flex-direction: column; gap: 6px; margin: 8px 0 14px; align-items: flex-start; }
.file { display: flex; gap: 10px; align-items: center; background: var(--wq-bg); border-radius: 6px; padding: 5px 10px; font-size: 13px; }
.f-name { max-width: 380px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.short { min-height: 70px; }
.agree { display: flex; gap: 8px; align-items: flex-start; font-size: 13px; color: var(--wq-text); margin: 6px 0 12px; cursor: pointer; line-height: 1.6; }
.box { font-size: 16px; line-height: 1.3; }
.error { color: var(--wq-danger); font-size: 14px; margin-bottom: 12px; }
.submit { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; border-radius: 8px; height: 46px; line-height: 46px;
  font-size: 16px; text-align: center; cursor: pointer; width: 100%; margin-top: 4px; }
.submit.disabled { opacity: 0.5; cursor: default; }
.alt { display: flex; justify-content: center; gap: 8px; margin-top: 18px; align-items: baseline; }
.strong { font-weight: 600; }
.center { text-align: center; margin-top: 14px; font-size: 14px; }
.block { display: block; }
.note { border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; font-size: 14px; line-height: 1.6; }
.note.warn { background: #fff6dc; color: #6b4e00; }
@media (max-width: 480px) { .two, .roles { grid-template-columns: 1fr; } }
</style>
