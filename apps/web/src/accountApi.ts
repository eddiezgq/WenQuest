// Sign-up, password reset, teacher applications, administration and the course catalogue (round 3, step C).
import { ref } from "vue";
import { ApiError, BASE, request, token, type User, adoptSession } from "./api";
import { locale } from "./i18n";

export interface AiReview {
  recommendation: "approve" | "more" | "reject" | "manual";
  reason: string;
  checks: { item: string; result: "ok" | "doubt" | "bad" | "unknown"; note: string }[];
  message_to_applicant: string;
}
export interface MyApplication {
  status: "pending" | "need_more" | "approved" | "rejected";
  institution: string; department: string; title: string;
  evidence: string[]; more: string; reason: string; created: number;
}
export interface Application {
  id: number; userid: number; email: string; name: string; lang: string;
  institution: string; department: string; title: string; note: string; school: number;
  status: "pending" | "need_more" | "approved" | "rejected";
  ai: AiReview | null; evidence: { name: string; mime: string; url: string }[];
  created: number; reviewed: number; more_requested: number; decided: number; decided_by: string; reason: string;
}
export interface AdminUser {
  id: number; username: string; fullname: string; email: string; lang: string;
  suspended: boolean; teacher: boolean; admin: boolean; timecreated: number; lastaccess: number;
}
export interface EnrolRequest {
  id: number; courseid: number; course: string; userid: number; name: string; email: string; note: string;
  status: string; created: number; price: number; currency: string;
}
export interface CatalogCourse {
  id: number; name: string; summary: string; teachers: string[]; chapters: number; students: number;
  mode: "free" | "paid"; price: number; currency: "CNY" | "USD"; blurb: string; enrolled: boolean; requested: boolean;
}
export interface Listing { mode: "private" | "free" | "paid"; price: number; currency: "CNY" | "USD"; blurb: string }

type SignedIn = { token: string; user: User; teacher_status?: string };

export const accountApi = {
  sendCode: (email: string, purpose: "register" | "reset") =>
    request<{ sent: boolean }>("POST", "/api/v1/auth/code", { email, purpose, lang: locale.value }),
  async register(body: Record<string, unknown>): Promise<SignedIn> {
    const r = await request<SignedIn>("POST", "/api/v1/auth/register", { ...body, lang: locale.value });
    adoptSession(r.token, r.user);
    return r;
  },
  async reset(email: string, code: string, password: string): Promise<SignedIn> {
    const r = await request<SignedIn>("POST", "/api/v1/auth/reset", { email, code, password });
    adoptSession(r.token, r.user);
    return r;
  },
  /** Sign in with the site-wide cookie (signed in on the academy website or another platform). */
  async sso(): Promise<boolean> {
    try {
      const r = await request<SignedIn>("GET", "/api/v1/auth/sso");
      adoptSession(r.token, r.user);
      return true;
    } catch {
      return false;
    }
  },
  logoutEverywhere: () => request<{ ok: boolean }>("POST", "/api/v1/auth/logout", {}).catch(() => null),

  myApplication: () => request<{ application: MyApplication | null; teacher: boolean }>("GET", "/api/v1/me/application"),
  apply: (b: { institution: string; department: string; title: string; note: string }) =>
    request<{ application: MyApplication }>("POST", "/api/v1/me/application", b),
  submitApplication: () => request<{ application: MyApplication }>("POST", "/api/v1/me/application/submit", {}, 120000),
  // Browser-only: one evidence file.
  async uploadEvidence(file: File): Promise<MyApplication> {
    const form = new FormData();
    form.append("file", file, file.name);
    let res: Response;
    try {
      res = await fetch(`${BASE}/api/v1/me/application/files`, { method: "POST", body: form, headers: { Authorization: `Bearer ${token.value}` } });
    } catch {
      throw new ApiError("network", 0);
    }
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new ApiError(body.error || `http_${res.status}`, res.status);
    return body.application as MyApplication;
  },

  summary: () => request<{ admin: boolean; applications?: number; requests?: number; mail?: boolean; ai?: string }>("GET", "/api/v1/admin/summary"),
  applications: (status: "open" | "done") =>
    request<{ applications: Application[] }>("GET", `/api/v1/admin/applications?status=${status}`).then((r) => r.applications),
  decide: (id: number, approve: boolean, reason = "") =>
    request<{ ok: boolean; mailed: boolean }>("POST", `/api/v1/admin/applications/${id}/decide`, { approve, reason }),
  rereview: (id: number) => request<{ ai: AiReview; status: string }>("POST", `/api/v1/admin/applications/${id}/review`, {}, 120000),
  users: (q: string, page = 0) =>
    request<{ total: number; users: AdminUser[] }>("GET", `/api/v1/admin/users?q=${encodeURIComponent(q)}&page=${page}`),
  changeUser: (id: number, body: { suspended?: boolean; teacher?: boolean }) => request<AdminUser>("PUT", `/api/v1/admin/users/${id}`, body),
  resetUser: (id: number) => request<{ mailed: boolean }>("POST", `/api/v1/admin/users/${id}/reset`, {}),
  requests: (status = "pending") => request<{ requests: EnrolRequest[] }>("GET", `/api/v1/admin/requests?status=${status}`).then((r) => r.requests),
  decideRequest: (id: number, approve: boolean) => request<{ ok: boolean; mailed: boolean }>("POST", `/api/v1/admin/requests/${id}/decide`, { approve }),

  catalog: () => request<{ courses: CatalogCourse[]; signed_in: boolean }>("GET", "/api/v1/catalog"),
  join: (cid: number, note = "") => request<{ status: "enrolled" | "requested" }>("POST", `/api/v1/catalog/${cid}/join`, { note }),
  listing: (cid: number) => request<Listing>("GET", `/api/v1/courses/${cid}/listing`),
  saveListing: (cid: number, l: Listing) => request<Listing>("PUT", `/api/v1/courses/${cid}/listing`, l),
};

/** Administrator status for the navigation (asked once per sign-in). */
export const admin = ref<{ admin: boolean; applications?: number; requests?: number } | null>(null);
let asked = "";
export async function loadAdmin(force = false) {
  if (!token.value) return (admin.value = null);
  if (!force && asked === token.value) return admin.value;
  asked = token.value;
  try {
    admin.value = await accountApi.summary();
  } catch {
    admin.value = { admin: false };
  }
  return admin.value;
}

export const PASSWORD_OK = (pw: string) => pw.length >= 8 && /[A-Za-z]/.test(pw) && /\d/.test(pw);

/** Where to go after signing in: back to the academy website if it sent us here, else the platform. */
export function afterLogin(back: string, fallback = "/pages/courses/courses") {
  if (back.startsWith("/pages/")) return uni.reLaunch({ url: back });
  // #ifdef H5
  if (back) {
    try {
      const u = new URL(back);
      const here = window.location.hostname.split(".").slice(-2).join(".");
      if ((u.protocol === "https:" || u.protocol === "http:") && (u.hostname === here || u.hostname.endsWith("." + here))) {
        window.location.href = u.href;
        return;
      }
    } catch {
      /* not a URL: ignore */
    }
  }
  // #endif
  uni.reLaunch({ url: fallback });
}

/** The academy website's legal pages (terms, privacy). */
export function siteUrl(path: string): string {
  // #ifdef H5
  const host = window.location.hostname;
  if (host.startsWith("learn.")) return `${window.location.protocol}//${host.slice(6)}${path}`;
  // #endif
  return `https://wenquestrobotics.com${path}`;
}
