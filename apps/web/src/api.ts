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
}
export interface Course {
  id: number;
  shortname: string;
  name: string;
  summary: string;
  image: string | null;
  progress: number | null;
}
export interface Module {
  id: number;
  type: string;
  name?: string;
  html?: string;
  locked?: boolean;
  completed?: boolean;
  has_completion?: boolean;
}
export interface Section {
  id: number;
  number: number;
  name: string;
  summary: string;
  modules: Module[];
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
  files?: { name: string; size: number; mimetype: string; url: string }[];
  classic_url: string;
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

function request<T>(method: "GET" | "POST", path: string, data?: unknown): Promise<T> {
  const header: Record<string, string> = { "Content-Type": "application/json" };
  if (token.value) header.Authorization = `Bearer ${token.value}`;
  const sep = path.includes("?") ? "&" : "?";
  const url = `${BASE}${path}${method === "GET" ? `${sep}lang=${locale.value}` : ""}`;
  return new Promise((resolve, reject) => {
    uni.request({
      url,
      method,
      header,
      data: data as any,
      success(res) {
        const body: any = res.data;
        if (res.statusCode >= 200 && res.statusCode < 300) return resolve(body as T);
        const code = (body && body.error) || "unknown";
        if (res.statusCode === 401 && token.value) {
          saveSession("", null);
          uni.reLaunch({ url: "/pages/login/login" });
        }
        reject(new ApiError(code, res.statusCode));
      },
      fail() {
        reject(new ApiError("network", 0));
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
  courses: () => request<{ courses: Course[] }>("GET", "/api/v1/courses").then((r) => r.courses),
  outline: (id: number) =>
    request<{ sections: Section[] }>("GET", `/api/v1/courses/${id}/outline`).then((r) => r.sections),
  activity: (id: number) => request<Activity>("GET", `/api/v1/activities/${id}`),
};
