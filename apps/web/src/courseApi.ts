// Course menus in WenQuest's own UI (round 3, step B): announcements, discussions, online class, people.
import { request } from "./api";

export interface Discussion {
  id: number; postid: number; subject: string; message: string; author: string; avatar: string | null;
  created: number; modified: number; replies: number; unread: number; pinned: boolean; locked: boolean;
  can_reply: boolean; can_lock: boolean;
}
export interface Forum { id: number; cmid: number; name: string; intro: string; type: string; discussions: number | null; unread: number; can_post: boolean }
export interface Post {
  id: number; parent: number; subject: string; message: string; author: string; author_id: number; avatar: string | null;
  time: number; unread: boolean; deleted: boolean; can_reply: boolean; can_edit: boolean; can_delete: boolean;
  attachments: { name: string; url: string }[];
}
export interface Thread { id: number; forum: number; course: number; subject: string; posts: Post[] }
export interface Meeting {
  id: number; courseid: number; name: string; provider: "tencent" | "zoom" | "other"; url: string; meetingcode: string;
  passcode: string; notes: string; timestart: number; duration: number;
}
export type MeetingIn = Omit<Meeting, "id" | "courseid">;
export interface Member { id: number; fullname: string; email: string; avatar: string | null; role: string; groups: number[]; lastaccess: number }
export interface Group { id: number; name: string; members: number[] }
export interface PlanGroup { name: string; members: number[]; note: string; names: string[] }

export const courseApi = {
  announcements: (cid: number) =>
    request<{ forum: number | null; items: Discussion[]; can_post: boolean }>("GET", `/api/v1/courses/${cid}/announcements`),
  announce: (cid: number, subject: string, message: string) =>
    request<{ id: number }>("POST", `/api/v1/courses/${cid}/announcements`, { subject, message }),
  forums: (cid: number) => request<{ forums: Forum[] }>("GET", `/api/v1/courses/${cid}/forums`),
  discussions: (fid: number, page = 0) =>
    request<{ items: Discussion[]; can_post: boolean; can_pin: boolean }>("GET", `/api/v1/forums/${fid}/discussions?page=${page}`),
  startDiscussion: (fid: number, subject: string, message: string) =>
    request<{ id: number }>("POST", `/api/v1/forums/${fid}/discussions`, { subject, message }),
  thread: (did: number) => request<Thread>("GET", `/api/v1/discussions/${did}`),
  reply: (postid: number, message: string) => request<{ id: number }>("POST", `/api/v1/posts/${postid}/reply`, { message }),
  editPost: (postid: number, subject: string, message: string) =>
    request<{ ok: boolean }>("PUT", `/api/v1/posts/${postid}`, { subject, message }),
  deletePost: (postid: number) => request<{ ok: boolean }>("DELETE", `/api/v1/posts/${postid}`),
  pin: (did: number, on: boolean) => request<{ ok: boolean }>("PUT", `/api/v1/discussions/${did}/pin`, { on }),
  lock: (did: number, on: boolean) => request<{ ok: boolean }>("PUT", `/api/v1/discussions/${did}/lock`, { on }),

  meetings: (cid: number) => request<{ meetings: Meeting[]; can_manage: boolean }>("GET", `/api/v1/courses/${cid}/meetings`),
  addMeeting: (cid: number, m: MeetingIn) => request<Meeting>("POST", `/api/v1/courses/${cid}/meetings`, m),
  editMeeting: (cid: number, id: number, m: MeetingIn) => request<Meeting>("PUT", `/api/v1/courses/${cid}/meetings/${id}`, m),
  deleteMeeting: (cid: number, id: number) => request<{ ok: boolean }>("DELETE", `/api/v1/courses/${cid}/meetings/${id}`),

  people: (cid: number) => request<{ members: Member[]; groups: Group[]; can_manage: boolean }>("GET", `/api/v1/courses/${cid}/people`),
  enrol: (cid: number, identifiers: string[], role = "student") =>
    request<{ added: string[]; already: string[]; notfound: string[] }>("POST", `/api/v1/courses/${cid}/people`, { identifiers, role }),
  unenrol: (cid: number, uid: number) => request<{ ok: boolean }>("DELETE", `/api/v1/courses/${cid}/people/${uid}`),
  addGroup: (cid: number, name: string, members: number[] = []) =>
    request<{ groups: Group[] }>("POST", `/api/v1/courses/${cid}/groups`, { name, members }),
  editGroup: (cid: number, gid: number, body: { name?: string; members?: number[] }) =>
    request<{ groups: Group[] }>("PUT", `/api/v1/courses/${cid}/groups/${gid}`, body),
  deleteGroup: (cid: number, gid: number) => request<{ groups: Group[] }>("DELETE", `/api/v1/courses/${cid}/groups/${gid}`),
  aiGroups: (cid: number, req: string) =>
    request<{ explanation: string; groups: PlanGroup[]; has_grades: boolean; existing: number }>(
      "POST", `/api/v1/courses/${cid}/groups/ai`, { request: req }, 200000),
  applyGroups: (cid: number, groups: { name: string; members: number[] }[], replace: boolean) =>
    request<{ groups: Group[] }>("POST", `/api/v1/courses/${cid}/groups/apply`, { groups, replace }),
};

/** Initials for people without a picture. */
export const initials = (name: string) => (name || "?").trim().slice(0, 1).toUpperCase();

/** Open an outside link (meeting, file): a new tab on the web; copy it in the mini program. */
export function openOutside(url: string, copied: string) {
  // #ifdef H5
  window.open(url, "_blank", "noopener");
  // #endif
  // #ifndef H5
  uni.setClipboardData({ data: url, success: () => uni.showToast({ title: copied, icon: "none" }) });
  // #endif
}

/** Ask before something that cannot be undone. */
export function confirmAction(content: string, ok: string, cancel: string): Promise<boolean> {
  return new Promise((resolve) => {
    uni.showModal({ content, confirmText: ok, cancelText: cancel, success: (r) => resolve(!!r.confirm), fail: () => resolve(false) });
  });
}
