// Client for the WenQuest gateway. Uses uni.request so it runs on H5 and in mini programs.
import { ref } from "vue";
import { locale } from "./i18n";

// Empty = same origin (the web app is served next to /api). The mini program needs an absolute URL.
export const BASE: string = (import.meta.env.VITE_API_BASE as string) || "";
const TOKEN_KEY = "wq.token";
const USER_KEY = "wq.user";

export interface User {
  id: number;
  fullname: string;
  username: string;
  avatar: string | null;
  lang: "zh" | "en";
  can_create_courses?: boolean;
  classic_url?: string;
}
export interface Course {
  id: number;
  shortname: string;
  name: string;
  summary: string;
  image: string | null;
  progress: number | null;
  /** 已下架: only its teachers still get it in the list */
  hidden?: boolean;
}
export type FileKind = "video" | "pdf" | "slides" | "lab" | "doc" | "sheet" | "image" | "audio" | "file";
export interface ModuleFile { name: string; size: number; mimetype: string; kind: FileKind }
export interface Module {
  id: number;
  type: string;
  name?: string;
  html?: string;
  locked?: boolean;
  hidden?: boolean;
  completed?: boolean;
  has_completion?: boolean;
  file?: ModuleFile;
}
export interface Section {
  id: number;
  number: number;
  name: string;
  summary: string;
  visible?: boolean;
  modules: Module[];
}
export interface CourseInfo {
  id: number;
  shortname: string;
  name: string;
  summary: string;
  image: string | null;
  teachers: string[];
  start: number | null;
  end: number | null;
  role: "teacher" | "student";
  /** false = 已下架 (students do not see the course) */
  visible?: boolean;
  classic_url: string;
}
export interface Activity {
  id: number;
  type: string;
  course_id: number;
  name: string;
  html?: string;
  intro?: string;
  url?: string;
  due?: number | null;
  files?: { name: string; size: number; mimetype: string; kind: FileKind; url: string; lab_url?: string }[];
  kind?: FileKind | "lecture";
  /** 讲解视频: the two voices and the subtitles */
  lecture?: LectureMedia;
  hidden?: boolean;
  classic_url: string;
}
export interface LectureMedia { video: { zh?: string; en?: string }; subs: { zh?: string; en?: string }; poster?: string }

// --- AI course workshop ---
export type Languages = "zh" | "en" | "both";
export interface Text { zh?: string; en?: string }
export interface OutlineLesson { title: Text; goal?: Text; content: Text; sources?: string[] }
export interface OutlineSection {
  title: Text;
  summary: Text;
  lessons: OutlineLesson[];
  assignment: { title: Text; brief: Text } | null;
  files?: string[];
}
export interface Outline {
  title: Text;
  summary: Text;
  languages: Languages;
  sections: OutlineSection[];
  import_id?: string;
  files?: Record<string, { name: string; category: string; teacher_only: boolean }>;
}
export interface Material {
  id: string;
  name: string;
  path: string;
  size: number;
  ext: string;
  chars: number;
  pages: number;
  category: string;
  category_label: string;
  chapter: number | null;
  confidence: string;
  teacher_only: boolean;
  error: string;
}
/** AI professor team (D30): one course project. */
export type Stage = "intake" | "materials" | "outline" | "lessons";
export type LessonStatus = "planned" | "writing" | "reviewing" | "awaiting" | "published" | "failed";
export interface StudioFile {
  id: string; name: string; path: string; size: number; pages: number; error: string; url?: string; ocr?: number;
  role: string; role_label: string; chapters: number[]; title: string; confidence: string; note: string; by: string;
}
export interface StudioQuestion { id: string; text: string; options: string[]; status: "open" | "answered" | "dropped"; answer: string }
export interface StudioMessage { id: string; role: "teacher" | "lead" | "system"; text: string; ts: number; kind: string; proposal?: string }
export interface StudioLesson {
  id: string; title: Text; goal: Text; week: number; sections: string[]; status: LessonStatus;
  content: Text; exercises: Text; answers: Text; notes: string; error: string;
  files?: {
    name: string; kind: "animation" | "lecture" | "lab" | "slides" | "guide" | "report" | "plan" | "figure"; teacher_only: boolean; url: string;
    seconds?: number; langs?: ("zh" | "en")[]; source?: "ai" | "teacher"; lecture?: LectureMedia;
  }[];
  review: { verdict: "pass" | "revise"; issues: { severity: string; text: string }[]; summary: string; round: number } | null;
  /** 需要你处理: what the team could not finish (kind "animation" | "lab"), shown prominently with a redo button. */
  attention?: { kind: string; text: string }[];
  review_flow?: ReviewFlow;
  /** 每课一张清单: ok true = ticked, false = crossed, null = not checked; by "ai" | "auto+ai". */
  checklist?: { key: string; label: string; ok: boolean | null; by: string; note: string; image?: string; image_url?: string }[];
}
/** ready: the teacher confirmed this chapter's lessons (本章确认); only then are they written. */
export interface ReviewOpinion {
  verdict: "approve" | "revise" | "reject"; summary: string;
  items: { area: string; label: string; ok: boolean | null; note: string }[];
  issues: { severity: "high" | "medium" | "low"; where: string; text: string; fix: string }[]; highlights?: string[];
}
/** 审核流程 of a lesson (round 6) */
export interface ReviewFlow {
  state: "" | "prereviewed" | "submitted" | "returned" | "approved"; prereview?: ReviewOpinion; note?: string;
  history: { ts: number; who: string; action: string; comment: string }[];
}
export interface TextbookSectionRef { id: string; title: string; written?: boolean; chapter?: number; kind?: "intro" | "summary";
  en?: boolean; title_en?: string }
export interface TextbookChapter { no: number; title: string; level: string; part: string; sections: TextbookSectionRef[];
  title_en?: string; status?: string }
/** 互动资源（第 9 轮 2.5）: an animation or a virtual lab of a chapter, and the section it is in. */
export interface TextbookResource { kind: "anim" | "lab"; num: string; title: string; title_en?: string; sec: string }
export interface TextbookIndex { book: string; title: string; title_en?: string; parts: { title: string }[]; parts_en?: Record<string, string>;
  chapters: TextbookChapter[]; teacher: boolean; pdf: number[]; pdf_en?: number[]; resources?: Record<string, TextbookResource[]> }
export interface TextbookSection { id: string; title: string; lang?: "zh" | "en"; chapter: { no: number; title: string; status?: string }; html: string;
  prev: TextbookSectionRef | null; next: TextbookSectionRef | null }
export interface CommitteeItem { pid: string; lid: string; course: Text; chapter: Text; no: string; title: Text; teacher: string; state: string; submitted?: number; verdict: string }
export interface StudioChapter { id: string; no: number; title: Text; summary: Text; lessons: StudioLesson[]; confirmed?: boolean; ready?: boolean }
/** 课程负责人的提议: what the lead will do once the teacher confirms. */
export interface StudioProposal { id: string; summary: string; lines: string[]; status: "open" | "done" | "cancelled" | "superseded"; result: string[] }
export interface StudioOutline { title: Text; summary: Text; languages: Languages; chapters: StudioChapter[]; calendar_note: string }
export interface StudioProject {
  id: string; stage: Stage; created: number; updated: number;
  requirements: Record<string, string>;
  materials: { textbook: string; book_title: string; summary: string };
  toc: { no: number; title: string; start: number | null; sections: { no: string; title: string; start: number | null }[] }[];
  files: StudioFile[]; roles: Record<string, string>;
  questions: StudioQuestion[]; messages: StudioMessage[]; outline: StudioOutline | null;
  course: { id: number; shortname: string };
  pace: { mode: "manual" | "daily"; hour: number; tz: string; last_auto: string };
  busy: { label: string; since: number } | null;
  progress: Record<LessonStatus | "total", number>;
  labs_on?: boolean;
  anims_on?: boolean;
  proposals?: StudioProposal[];
  /** 专家版课程负责人（试用）: Claude itself as the course lead */
  lead_v2?: boolean;
  lead_v2_available?: boolean;
  /** what the course lead is doing right now ("正在查阅资料（第 3–8 页）") */
  lead_status?: string;
  /** 教材研读笔记, by chapter number */
  textbook_notes?: Record<string, { title: string; notes: string; seen_book: boolean }>;
  /** the course lead is answering the teacher's last message */
  lead_thinking?: boolean;
  /** 讲解视频 can be made (the voice service is set up); the course's voices */
  voices_on?: boolean;
  voices?: { zh: string; en: string };
  zip_url?: string;
  design_book?: DesignBook | null;
  assets?: CourseAsset[];
}
export interface Voice { id: string; lang: "zh" | "en"; gender: string; zh: string; en: string; sample: string }
/** The lines of a lecture video: AI narration per slide, or the recording's subtitles. */
export interface LectureRows {
  source: "" | "ai" | "teacher"; seconds?: number; langs?: string[]; locked?: boolean;
  rows: { n: number; start: number; end?: number; zh: string; en: string; raw?: string; edited?: boolean }[];
  urls?: LectureMedia;
}
/** 课程设计书: the course's own subject, robot platform, notation and per-chapter means (every lesson follows it). */
export interface DesignBook {
  subject: string; audience: string; textbook: string; platform: string; notation: string; visual_style: string;
  chapters: { no: number; animation: string; lab: string; problems: string }[];
  avoid: string[]; by?: string;
  library?: { id: string; role: string }[];
}
/** 问渠零件与机器人库: an entry this course uses (a copy lives in the course). */
export interface CourseAsset {
  id: string; version: string; spec: string; name: Text; kind: string; category: string; license: string; attribution: string;
  by: string; added: number; thumb: string; used_in: string[];
}
export interface LibraryItem { id: string; name: Text; category: string; kind: string; tags: string[]; principle: string; license: string; thumb: string }
export interface StudioSummary {
  id: string; title: string; stage: Stage; updated: number; course_id: number;
  lessons: number; published: number; awaiting: number; busy: boolean; open_questions: number;
}

/** A slide deck converted for presenting in the browser (R12). Positions are fractions of the slide. */
export interface SlideBox { x: number; y: number; w: number; h: number }
export interface Slide {
  image: string;
  thumb: string;
  labs: string[];
  videos: (SlideBox & { src: string })[];
  links: (SlideBox & { href: string; lab?: string })[];
  notes?: string;
}
export interface SlideDeck {
  id: number;
  course_id: number;
  name: string;
  status: "ready" | "converting" | "failed" | "missing" | "unavailable";
  teacher: boolean;
  allow_download: boolean;
  file_name: string;
  download_url: string | null;
  queue?: number;    // while converting: decks ahead of this one (0 = being converted now)
  elapsed?: number;  // seconds this deck has been converting
  pages?: number;
  width?: number;
  height?: number;
  slides?: Slide[];
}

/** A one-click generation job (D28), as the gateway reports it. */
export type LessonState = "wait" | "busy" | "done" | "fail";
export interface Job {
  state: "running" | "done" | "error" | "interrupted";
  phase: "classify" | "plan" | "write" | "done";
  error: string;
  languages: Languages;
  brief: Brief | null;
  files: { total: number; readable: number; unreadable: number };
  outline: Outline | null;
  lessons: Record<string, LessonState>;
  errors: Record<string, string>;
  progress: { lessons_total: number; lessons_done: number; lessons_failed: number };
}

export interface Brief {
  topic: string;
  audience: string;
  level: string;
  sections: number;
  lessons_per_section: number;
  assignments: boolean;
  languages: Languages;
  notes: string;
}

export class ApiError extends Error {
  constructor(public code: string, public status: number) {
    super(code);
  }
}

function load<T>(key: string): T | null {
  try {
    const v = uni.getStorageSync(key);
    return v ? (JSON.parse(v) as T) : null;
  } catch {
    return null;
  }
}

export const token = ref<string>((() => { try { return uni.getStorageSync(TOKEN_KEY) || ""; } catch { return ""; } })());
export const user = ref<User | null>(load<User>(USER_KEY));

function saveSession(tok: string, u: User | null) {
  token.value = tok;
  user.value = u;
  try {
    if (tok) {
      uni.setStorageSync(TOKEN_KEY, tok);
      uni.setStorageSync(USER_KEY, JSON.stringify(u));
    } else {
      uni.removeStorageSync(TOKEN_KEY);
      uni.removeStorageSync(USER_KEY);
    }
  } catch {
    /* ignore */
  }
}

/** Keep a session that another call (sign-up, reset, site-wide sign-in) returned. */
export function adoptSession(tok: string, u: User) {
  saveSession(tok, u);
}

export function absolute(url: string | null | undefined): string {
  if (!url) return "";
  return url.startsWith("/") ? BASE + url : url;
}

export function request<T>(method: "GET" | "POST" | "PUT" | "DELETE", path: string, data?: unknown, timeout = 60000): Promise<T> {
  const header: Record<string, string> = { "Content-Type": "application/json" };
  if (token.value) header.Authorization = `Bearer ${token.value}`;
  const sep = path.includes("?") ? "&" : "?";
  const url = `${BASE}${path}${method === "GET" ? `${sep}lang=${locale.value}` : ""}`;
  return new Promise((resolve, reject) => {
    uni.request({
      url,
      method,
      header,
      timeout,
      data: data as any,
      success(res) {
        const body: any = res.data;
        if (res.statusCode >= 200 && res.statusCode < 300) return resolve(body as T);
        const code = (body && typeof body === "object" && body.error) || `http_${res.statusCode}`;
        if (res.statusCode === 401 && token.value) {
          saveSession("", null);
          uni.reLaunch({ url: "/pages/login/login" });
        }
        reject(new ApiError(code, res.statusCode));
      },
      fail(err: any) {
        const msg = String((err && err.errMsg) || "");
        reject(new ApiError(msg.includes("timeout") ? "ai_timeout" : "network", 0));
      },
    });
  });
}

export const api = {
  async login(username: string, password: string): Promise<User> {
    const r = await request<{ token: string; user: User }>("POST", "/api/v1/auth/login", {
      username,
      password,
      lang: locale.value,
    });
    saveSession(r.token, r.user);
    return r.user;
  },
  logout() {
    saveSession("", null);
  },
  async me(): Promise<User> {
    const u = await request<User>("GET", "/api/v1/me");
    saveSession(token.value, u);
    return u;
  },
  aiOutline: (b: Brief) => request<Outline>("POST", "/api/v1/ai/outline", b, 200000),
  aiLesson: (body: Record<string, unknown>) =>
    request<{ content: Text }>("POST", "/api/v1/ai/lesson", body, 200000),
  importStart: () => request<{ import_id: string }>("POST", "/api/v1/imports"),
  importClassify: (id: string) =>
    request<{ files: Material[]; categories: Record<string, string> }>("POST", `/api/v1/imports/${id}/classify`, {}, 120000),
  importEdit: (id: string, edits: { id: string; category: string; chapter: number | null }[]) =>
    request<{ files: Material[] }>("PUT", `/api/v1/imports/${id}/files`, edits),
  importOutline: (id: string, languages: Languages) =>
    request<Outline>("POST", `/api/v1/imports/${id}/outline`, { languages }, 200000),
  // Browser-only: multipart upload of one file with its path inside the chosen folder.
  async importUpload(id: string, file: File, path: string): Promise<Material> {
    const form = new FormData();
    form.append("file", file, file.name);
    form.append("path", path);
    let res: Response;
    try {
      res = await fetch(`${BASE}/api/v1/imports/${id}/files`, {
        method: "POST", body: form, headers: { Authorization: `Bearer ${token.value}` },
      });
    } catch {
      throw new ApiError("network", 0);
    }
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new ApiError(body.error || `http_${res.status}`, res.status);
    return body as Material;
  },
  studioProjects: () => request<{ projects: StudioSummary[] }>("GET", "/api/v1/studio/projects").then((r) => r.projects),
  studioCreate: (description: string) => request<StudioProject>("POST", "/api/v1/studio/projects", { description }),
  studio: (id: string) => request<StudioProject>("GET", `/api/v1/studio/projects/${id}`),
  studioStart: (id: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/start`, {}),
  studioSay: (id: string, text: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/messages`, { text }),
  studioAnswer: (id: string, qid: string, answer: string) =>
    request<StudioProject>("POST", `/api/v1/studio/projects/${id}/questions/${qid}`, { answer }),
  studioMaterials: (id: string, files: { id: string; role: string; chapters: number[] }[], textbook?: string) =>
    request<StudioProject>("PUT", `/api/v1/studio/projects/${id}/materials`, { files, textbook }),
  studioApproveMaterials: (id: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/approve-materials`, {}),
  studioRedoAnimation: (id: string, lid: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/lessons/${lid}/animation`),
  studioLibrary: (q: string) => request<{ version: string; sample: boolean; items: LibraryItem[] }>("GET", `/api/v1/studio/library?q=${encodeURIComponent(q)}`),
  studioAddAsset: (id: string, aid: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/assets/${aid}`),
  studioRemoveAsset: (id: string, aid: string) => request<StudioProject>("DELETE", `/api/v1/studio/projects/${id}/assets/${aid}`),
  studioMakeDesignBook: (id: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/design-book`),
  studioRereadTextbook: (id: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/textbook/reread`),
  studioDesignBook: (id: string, book: Partial<DesignBook>) => request<StudioProject>("PUT", `/api/v1/studio/projects/${id}/design-book`, book),
  studioOutline: (id: string, outline: StudioOutline) => request<StudioProject>("PUT", `/api/v1/studio/projects/${id}/outline`, outline),
  studioApproveOutline: (id: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/approve-outline`, {}, 300000),
  studioNext: (id: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/lessons/next`, {}),
  studioDeck: (id: string, lid: string) =>
    request<{ status: string; slides?: { image: string; thumb: string }[]; done?: number; total?: number }>(
      "GET", `/api/v1/studio/projects/${id}/lessons/${lid}/deck`),
  studioFilesDone: (id: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/files/done`, {}),
  studioDeleteFile: (id: string, fid: string) => request<StudioProject>("DELETE", `/api/v1/studio/projects/${id}/files/${fid}`),
  studioRedoLab: (id: string, lid: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/lessons/${lid}/lab`, {}),
  studioVoices: () => request<{ available: boolean; voices: Voice[]; default: { zh?: string; en?: string } }>("GET", "/api/v1/studio/voices"),
  studioSetVoices: (id: string, v: { zh?: string; en?: string }) => request<StudioProject>("PUT", `/api/v1/studio/projects/${id}/voices`, v),
  studioLecture: (id: string, lid: string) => request<LectureRows>("GET", `/api/v1/studio/projects/${id}/lessons/${lid}/lecture`),
  studioEditLecture: (id: string, lid: string, rows: { n: number; zh?: string; en?: string }[]) =>
    request<StudioProject>("PUT", `/api/v1/studio/projects/${id}/lessons/${lid}/lecture`, { rows }),
  studioRedoLecture: (id: string, lid: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/lessons/${lid}/lecture/redo`, {}),
  // Browser-only: the teacher's lecture recording, sent in 32 MB pieces (resumes nothing; one try per piece).
  async studioUploadRecording(id: string, lid: string, file: File, progress: (done: number) => void): Promise<StudioProject> {
    const piece = 32 * 1024 * 1024;
    const total = Math.max(1, Math.ceil(file.size / piece));
    const upload = Math.random().toString(36).slice(2, 12).replace(/[^a-z0-9]/g, "x").padEnd(10, "0");
    let body: any = {};
    for (let i = 0; i < total; i++) {
      const q = `upload=${upload}&index=${i}&total=${total}&name=${encodeURIComponent(file.name)}`;
      let res: Response;
      try {
        res = await fetch(`${BASE}/api/v1/studio/projects/${id}/lessons/${lid}/recording?${q}`, {
          method: "POST", body: file.slice(i * piece, (i + 1) * piece),
          headers: { Authorization: `Bearer ${token.value}`, "Content-Type": "application/octet-stream" },
        });
      } catch {
        throw new ApiError("network", 0);
      }
      body = await res.json().catch(() => ({}));
      if (!res.ok) throw new ApiError(body.error || `http_${res.status}`, res.status);
      progress((i + 1) / total);
    }
    return body as StudioProject;
  },
  studioWrite: (id: string, lid: string, note = "") =>
    request<StudioProject>("POST", `/api/v1/studio/projects/${id}/lessons/${lid}/write`, { note }),
  studioPublish: (id: string, lid: string) =>
    request<StudioProject>("POST", `/api/v1/studio/projects/${id}/lessons/${lid}/approve`, {}, 300000),
  studioStop: (id: string) => request<{ stopped: boolean }>("POST", `/api/v1/studio/projects/${id}/stop`, {}),
  studioConfirmProposal: (id: string, prop: string, stopFirst = false) =>
    request<StudioProject>("POST", `/api/v1/studio/projects/${id}/proposals/${prop}/confirm${stopFirst ? "?stop_first=true" : ""}`, {}),
  studioCancelProposal: (id: string, prop: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/proposals/${prop}/cancel`, {}),
  studioLeadV2: (id: string, on: boolean) => request<StudioProject>("PUT", `/api/v1/studio/projects/${id}/lead-v2`, { on }),
  studioSubmitReview: (id: string, lid: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/lessons/${lid}/submit`, {}),
  studioToCommittee: (id: string, lid: string, comment: string) =>
    request<StudioProject>("POST", `/api/v1/studio/projects/${id}/lessons/${lid}/to-committee`, { comment }),
  studioReviseFromReview: (id: string, lid: string) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/lessons/${lid}/revise-from-review`, {}),
  committeeMe: () => request<{ member: boolean; chair: boolean; self_review: boolean; waiting?: number }>("GET", "/api/v1/committee/me"),
  committeeQueue: (done = false) => request<{ items: CommitteeItem[] }>("GET", `/api/v1/committee/queue${done ? "?done=true" : ""}`),
  committeeItem: (pid: string, lid: string) => request<{ pid: string; lid: string; course: Text; chapter: Text; no: string; teacher: string; owner: number;
    lesson: StudioLesson; flow: ReviewFlow; role: { member: boolean; chair: boolean; self_review: boolean } }>("GET", `/api/v1/committee/items/${pid}/${lid}`),
  committeeApprove: (pid: string, lid: string, comment: string) => request<{ ok: boolean }>("POST", `/api/v1/committee/items/${pid}/${lid}/approve`, { comment }),
  committeeReturn: (pid: string, lid: string, comment: string) => request<{ ok: boolean }>("POST", `/api/v1/committee/items/${pid}/${lid}/return`, { comment }),
  adminCommittee: () => request<{ members: { id: number; name: string; email: string; key?: string }[]; chair: number; self_review: boolean }>("GET", "/api/v1/admin/committee"),
  adminSetCommittee: (members: string[], chair: string, self_review: boolean) =>
    request<{ members: { id: number; name: string; email: string; key?: string }[]; chair: number; self_review: boolean }>("PUT", "/api/v1/admin/committee", { members, chair, self_review }),
  // 问渠教材（第 7 轮）
  textbooks: () => request<{ books: { book: string; title: string; title_en?: string; web?: boolean; labs?: number; chapters: number; sections?: number; written?: number }[] }>("GET", "/api/v1/textbooks"),
  textbookWeb: (book: string, lang: "zh" | "en" = "zh") =>
    request<{ url: string; title: string; title_en: string }>("GET", `/api/v1/textbooks/${book}/webed?lang=${lang}`),
  textbook: (book: string) => request<TextbookIndex>("GET", `/api/v1/textbooks/${book}`),
  textbookSection: (book: string, sid: string, mp = false, lang: "zh" | "en" = "zh") =>
    request<TextbookSection>("GET", `/api/v1/textbooks/${book}/sections/${sid}?mp=${mp}&lang=${lang}`),
  textbookPdf: (book: string, chapter: number, lang: "zh" | "en" = "zh") =>
    request<{ url: string }>("GET", `/api/v1/textbooks/${book}/pdf/${chapter}?lang=${lang}`),
  studioConfirmChapter: (id: string, no: number) => request<StudioProject>("POST", `/api/v1/studio/projects/${id}/chapters/${no}/confirm`, {}),
  studioPace: (id: string, mode: "manual" | "daily", hour: number, tz: string) =>
    request<StudioProject>("PUT", `/api/v1/studio/projects/${id}/pace`, { mode, hour, tz }),
  // Browser-only: one file into a course project.
  async studioUpload(id: string, file: File, path: string): Promise<unknown> {
    const form = new FormData();
    form.append("file", file, file.name);
    form.append("path", path);
    let res: Response;
    try {
      res = await fetch(`${BASE}/api/v1/studio/projects/${id}/files`, {
        method: "POST", body: form, headers: { Authorization: `Bearer ${token.value}` },
      });
    } catch {
      throw new ApiError("network", 0);
    }
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new ApiError(body.error || `http_${res.status}`, res.status);
    return body;
  },
  slides: (cmid: number) => request<SlideDeck>("GET", `/api/v1/slides/${cmid}`),
  slidesRetry: (cmid: number) => request<SlideDeck>("POST", `/api/v1/slides/${cmid}/retry`, {}),
  slideSettings: (cmid: number, allow_download: boolean) =>
    request<{ allow_download: boolean }>("PUT", `/api/v1/slides/${cmid}/settings`, { allow_download }),
  generate: (id: string, body: { languages?: Languages; brief?: Brief; outline?: Outline }) =>
    request<Job>("POST", `/api/v1/imports/${id}/generate`, body),
  job: (id: string) => request<Job>("GET", `/api/v1/imports/${id}/job`),
  retryLesson: (id: string, si: number, li: number) => request<Job>("POST", `/api/v1/imports/${id}/job/lessons/${si}/${li}`, {}),
  publish: (o: Outline) =>
    request<{ course_id: number; shortname: string; activities: number }>("POST", "/api/v1/courses", o, 120000),
  courses: () => request<{ courses: Course[] }>("GET", "/api/v1/courses").then((r) => r.courses),
  course: (id: number) => request<CourseInfo>("GET", `/api/v1/courses/${id}`),
  outline: (id: number) =>
    request<{ sections: Section[] }>("GET", `/api/v1/courses/${id}/outline`).then((r) => r.sections),
  activity: (id: number) => request<Activity>("GET", `/api/v1/activities/${id}`),
};
