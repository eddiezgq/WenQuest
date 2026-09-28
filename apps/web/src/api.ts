// Client for the WenQuest gateway. Uses uni.request so it runs on H5 and in mini programs.
import { ref } from "vue";
import { locale } from "./i18n";

// Empty = same origin (the web app is served next to /api). The mini program needs an absolute URL.
const BASE: string = (import.meta.env.VITE_API_BASE as string) || "";
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
  kind?: FileKind;
  hidden?: boolean;
  classic_url: string;
}

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

export function absolute(url: string | null | undefined): string {
  if (!url) return "";
  return url.startsWith("/") ? BASE + url : url;
}

function request<T>(method: "GET" | "POST" | "PUT", path: string, data?: unknown, timeout = 60000): Promise<T> {
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
  publish: (o: Outline) =>
    request<{ course_id: number; shortname: string; activities: number }>("POST", "/api/v1/courses", o, 120000),
  courses: () => request<{ courses: Course[] }>("GET", "/api/v1/courses").then((r) => r.courses),
  course: (id: number) => request<CourseInfo>("GET", `/api/v1/courses/${id}`),
  outline: (id: number) =>
    request<{ sections: Section[] }>("GET", `/api/v1/courses/${id}/outline`).then((r) => r.sections),
  activity: (id: number) => request<Activity>("GET", `/api/v1/activities/${id}`),
};
