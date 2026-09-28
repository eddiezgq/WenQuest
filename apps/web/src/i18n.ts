// Tiny i18n that works the same on H5 and in the WeChat mini program.
import { ref } from "vue";

export type Locale = "zh" | "en";

const messages: Record<Locale, Record<string, string>> = {
  zh: {
    "app.name": "问渠",
    "app.tagline": "问渠那得清如许，为有源头活水来",
    "login.title": "登录问渠",
    "login.username": "用户名",
    "login.password": "密码",
    "login.submit": "登录",
    "login.busy": "正在登录…",
    "login.hint": "使用学校或学院发给你的账号登录",
    "nav.courses": "我的课程",
    "nav.logout": "退出登录",
    "courses.empty": "你还没有加入任何课程。",
    "courses.progress": "已完成 {n}%",
    "course.outline": "课程目录",
    "course.empty": "这门课还没有内容。",
    "course.locked": "未开放",
    "course.done": "已完成",
    "type.page": "阅读",
    "type.url": "链接",
    "type.assign": "作业",
    "type.resource": "文件",
    "type.quiz": "测验",
    "type.forum": "讨论",
    "type.other": "活动",
    "activity.open": "打开",
    "activity.openLink": "打开链接",
    "activity.linkCopied": "链接已复制，请在浏览器中打开",
    "activity.due": "截止时间",
    "activity.noDue": "未设截止时间",
    "activity.classic": "在经典界面中打开",
    "activity.classicHint": "新界面暂未支持这类活动，可在经典界面中完成。",
    "activity.download": "下载",
    "common.loading": "加载中…",
    "common.retry": "重试",
    "common.back": "返回",
    "create.button": "AI 建课",
    "create.title": "AI 建课",
    "create.step1": "描述课程",
    "create.step2": "确认大纲",
    "create.step3": "生成内容",
    "create.step4": "预览发布",
    "create.topic": "课程主题",
    "create.topicHint": "例如：用仿真学 PID 控制",
    "create.audience": "学习对象",
    "create.audienceHint": "例如：高中生、大一机械专业",
    "create.level": "难度",
    "create.level.intro": "入门",
    "create.level.mid": "中级",
    "create.level.adv": "高级",
    "create.sections": "章数",
    "create.lessons": "每章课数",
    "create.assignments": "每章布置一次作业",
    "create.languages": "课程语言",
    "create.lang.zh": "中文",
    "create.lang.en": "English",
    "create.lang.both": "中英双语",
    "create.notes": "补充材料（可选）",
    "create.notesHint": "粘贴教学大纲、讲义或要点，AI 会按你的材料和术语来设计课程",
    "create.makeOutline": "生成课程大纲",
    "create.thinking": "AI 正在设计课程大纲，通常需要 20–60 秒…",
    "create.courseTitle": "课程名称",
    "create.summary": "课程简介",
    "create.sectionTitle": "章节标题",
    "create.lessonTitle": "课时标题",
    "create.addLesson": "＋ 添加一课",
    "create.remove": "删除",
    "create.assignment": "作业",
    "create.assignmentBrief": "作业要求",
    "create.regenOutline": "重新生成大纲",
    "create.writeAll": "生成全部课程内容",
    "create.writing": "AI 正在逐课撰写内容：已完成 {done} / {total}",
    "create.status.wait": "等待",
    "create.status.busy": "撰写中",
    "create.status.done": "完成",
    "create.status.fail": "失败",
    "create.retry": "重试",
    "create.rewrite": "重写这一课",
    "create.preview": "预览",
    "create.publish": "发布课程",
    "create.publishing": "正在发布…",
    "create.published": "课程已发布",
    "create.back": "上一步",
    "create.needAll": "还有课时没有生成成功，请先重试。",
    "create.noPermission": "你的账号没有建课权限，请联系管理员。",
    "error.ai_unavailable": "平台还没有配置 AI 模型，请联系管理员",
    "error.ai_timeout": "AI 响应超时，请重试",
    "error.ai_busy": "AI 服务繁忙，请稍后再试",
    "error.ai_key_invalid": "AI 密钥无效，请联系管理员",
    "error.ai_bad_output": "AI 返回的内容不完整，请重试",
    "error.ai_unreachable": "暂时连不上 AI 服务，请稍后再试",
    "error.ai_error": "AI 服务出错，请稍后再试",
    "lang.switch": "EN",
    "error.invalid_login": "用户名或密码不正确",
    "error.session_expired": "登录已过期，请重新登录",
    "error.not_logged_in": "请先登录",
    "error.forbidden": "你没有权限查看这项内容",
    "error.account_incomplete": "你的账户资料还不完整，请先在经典界面中补全个人信息",
    "error.link_expired": "链接已过期，请刷新页面",
    "error.not_found": "内容不存在或已被删除",
    "error.maintenance": "平台正在维护，请稍后再试",
    "error.engine_unreachable": "暂时连不上教学服务，请稍后再试",
    "error.engine_misconfigured": "教学服务配置不完整，请联系管理员",
    "error.network": "网络连接失败，请检查网络",
    "error.unknown": "出错了，请稍后再试",
  },
  en: {
    "app.name": "WenQuest",
    "app.tagline": "Every answer has a source.",
    "login.title": "Sign in to WenQuest",
    "login.username": "Username",
    "login.password": "Password",
    "login.submit": "Sign in",
    "login.busy": "Signing in…",
    "login.hint": "Use the account your school or academy gave you",
    "nav.courses": "My courses",
    "nav.logout": "Sign out",
    "courses.empty": "You are not enrolled in any courses yet.",
    "courses.progress": "{n}% complete",
    "course.outline": "Course outline",
    "course.empty": "This course has no content yet.",
    "course.locked": "Locked",
    "course.done": "Done",
    "type.page": "Read",
    "type.url": "Link",
    "type.assign": "Assignment",
    "type.resource": "File",
    "type.quiz": "Quiz",
    "type.forum": "Forum",
    "type.other": "Activity",
    "activity.open": "Open",
    "activity.openLink": "Open link",
    "activity.linkCopied": "Link copied. Open it in your browser.",
    "activity.due": "Due",
    "activity.noDue": "No due date",
    "activity.classic": "Open in classic view",
    "activity.classicHint": "The new interface does not support this activity yet. You can complete it in the classic view.",
    "activity.download": "Download",
    "common.loading": "Loading…",
    "common.retry": "Retry",
    "common.back": "Back",
    "create.button": "Create with AI",
    "create.title": "Create a course with AI",
    "create.step1": "Describe",
    "create.step2": "Outline",
    "create.step3": "Write",
    "create.step4": "Publish",
    "create.topic": "Course topic",
    "create.topicHint": "e.g. Learning PID control through simulation",
    "create.audience": "Students",
    "create.audienceHint": "e.g. high-school students, first-year engineering",
    "create.level": "Level",
    "create.level.intro": "Beginner",
    "create.level.mid": "Intermediate",
    "create.level.adv": "Advanced",
    "create.sections": "Sections",
    "create.lessons": "Lessons per section",
    "create.assignments": "One assignment per section",
    "create.languages": "Course language",
    "create.lang.zh": "中文",
    "create.lang.en": "English",
    "create.lang.both": "Bilingual",
    "create.notes": "Your material (optional)",
    "create.notesHint": "Paste a syllabus, notes or key points; the AI follows your material and terms",
    "create.makeOutline": "Generate outline",
    "create.thinking": "The AI is designing your course outline. This usually takes 20–60 seconds…",
    "create.courseTitle": "Course title",
    "create.summary": "Course description",
    "create.sectionTitle": "Section title",
    "create.lessonTitle": "Lesson title",
    "create.addLesson": "+ Add a lesson",
    "create.remove": "Remove",
    "create.assignment": "Assignment",
    "create.assignmentBrief": "What students hand in",
    "create.regenOutline": "Regenerate outline",
    "create.writeAll": "Write all lessons",
    "create.writing": "The AI is writing lessons: {done} of {total} done",
    "create.status.wait": "Waiting",
    "create.status.busy": "Writing",
    "create.status.done": "Done",
    "create.status.fail": "Failed",
    "create.retry": "Retry",
    "create.rewrite": "Rewrite this lesson",
    "create.preview": "Preview",
    "create.publish": "Publish course",
    "create.publishing": "Publishing…",
    "create.published": "Course published",
    "create.back": "Back",
    "create.needAll": "Some lessons were not written yet. Please retry them first.",
    "create.noPermission": "Your account may not create courses. Please contact the administrator.",
    "error.ai_unavailable": "No AI model is configured yet. Please contact the administrator.",
    "error.ai_timeout": "The AI took too long. Please try again.",
    "error.ai_busy": "The AI service is busy. Please try again shortly.",
    "error.ai_key_invalid": "The AI key is invalid. Please contact the administrator.",
    "error.ai_bad_output": "The AI returned incomplete content. Please try again.",
    "error.ai_unreachable": "Cannot reach the AI service right now. Please try again later.",
    "error.ai_error": "The AI service had an error. Please try again later.",
    "lang.switch": "中文",
    "error.invalid_login": "Wrong username or password",
    "error.session_expired": "Your session expired. Please sign in again.",
    "error.not_logged_in": "Please sign in first",
    "error.forbidden": "You do not have permission to view this",
    "error.account_incomplete": "Your profile is incomplete. Please complete it in the classic view first.",
    "error.link_expired": "This link has expired. Please refresh the page.",
    "error.not_found": "This item does not exist or was removed",
    "error.maintenance": "The platform is under maintenance. Please try again later.",
    "error.engine_unreachable": "Cannot reach the teaching service right now. Please try again later.",
    "error.engine_misconfigured": "The teaching service is not fully configured. Please contact the administrator.",
    "error.network": "Network error. Please check your connection.",
    "error.unknown": "Something went wrong. Please try again later.",
  },
};

const KEY = "wq.locale";

function initial(): Locale {
  try {
    const saved = uni.getStorageSync(KEY);
    if (saved === "zh" || saved === "en") return saved;
    const sys = (uni.getSystemInfoSync().language || "").toLowerCase();
    return sys.startsWith("zh") ? "zh" : "en";
  } catch {
    return "zh";
  }
}

export const locale = ref<Locale>(initial());

export function setLocale(l: Locale) {
  locale.value = l;
  try {
    uni.setStorageSync(KEY, l);
  } catch {
    /* storage may be unavailable */
  }
}

export function toggleLocale() {
  setLocale(locale.value === "zh" ? "en" : "zh");
}

export function t(key: string, vars: Record<string, string | number> = {}): string {
  const s = messages[locale.value][key] ?? messages.en[key] ?? key;
  return s.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? ""));
}

export function errorText(code: string): string {
  const key = `error.${code}`;
  return messages[locale.value][key] ? t(key) : t("error.unknown");
}

export function formatDate(ts: number | null | undefined): string {
  if (!ts) return "";
  const d = new Date(ts * 1000);
  const pad = (n: number) => String(n).padStart(2, "0");
  const date = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  return `${date} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export const _messages = messages; // for tests
