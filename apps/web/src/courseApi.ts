// Course menus in WenQuest's own UI (round 3, step B): announcements, discussions, online class, people.
import { ApiError, BASE, request, token } from "./api";

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
  forums: (cid: number) => request<{ forums: Forum[]; can_manage: boolean }>("GET", `/api/v1/courses/${cid}/forums`),
  addForum: (cid: number, name: string, intro: string) => request<{ cmid: number; id: number }>("POST", `/api/v1/courses/${cid}/forums`, { name, intro }),
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

// ------------------------------------------------------------------ B2: assignments, quizzes, grades, calendar, inbox

export interface WorkFile { name: string; size: number; mimetype?: string; url: string }
export interface Submission {
  status: "new" | "draft" | "submitted" | "reopened" | string; modified: number; text: string; files: WorkFile[];
  can_edit: boolean; can_submit: boolean; grading: string; locked: boolean; extension: number; graded: boolean;
  grade: string; grade_raw: number | null; feedback: string; feedback_files: WorkFile[]; graded_at: number;
}
export interface AssignConfig { text: boolean; files: boolean; maxfiles: number; maxbytes: number; filetypes: string; wordlimit: number; drafts: boolean }
export interface Assignment {
  id: number; cmid: number; course_id: number; name: string; intro: string; attachments: { name: string; url: string }[];
  due: number; cutoff: number; opens: number; max_grade: number; config: AssignConfig; teacher: boolean;
  submission?: Submission; summary?: { participants: number; submitted: number; drafts: number; needs_grading: number };
}
export interface SubmissionRow { id: number; fullname: string; groups: string[]; status: string; modified: number; needs_grading: boolean; grade: number | null; late: boolean }
export interface QuizOption { name: string; value: string; label: string; checked: boolean; result: string; feedback: string }
export interface QuizQuestion {
  slot: number; number: string; type: string; status: string; state: string; flagged: boolean; mark: string | null; maxmark: number | null;
  kind: "choice" | "multi" | "text" | "unsupported"; input: string; options: QuizOption[]; value: string; feedback: string;
  rightanswer: string; result: string; text: string; html?: string; inline?: boolean; numeric?: boolean;
}
export interface QuizInfo {
  id: number; cmid: number; course_id: number; name: string; intro: string; opens: number; closes: number; timelimit: number;
  attempts_allowed: number; max_grade: number; questions: boolean; teacher: boolean; can_attempt: boolean; blocked: string[]; rules: string[];
  attempts: { id: number; number: number; state: string; start: number; finish: number; grade: number | null }[]; best: number | null;
}
export interface Attempt { id: number; state: string; start: number; deadline: number; now: number; quiz: { name: string; cmid: number; course_id: number }; questions: QuizQuestion[] }
export interface Review { available: boolean; grade?: number | null; max_grade?: number; finish?: number; quiz?: { name: string; cmid: number; course_id: number }; questions?: QuizQuestion[] }
export interface GradeItem { id: number; name: string; type: string; module: string | null; cmid: number | null; max: number; needs_grading?: number }
export interface GradeCell { raw: number | null; text: string; percent: string; feedback: string; hidden: boolean; graded_at: number }
export interface CalEvent { id: number; name: string; description: string; start: number; duration: number; type: string; course_id: number; course: string; module: string; cmid: number | null; can_delete: boolean }
export interface Conversation { id: number; name: string; group: boolean; members: number; unread: number; last: string; time: number; from_me: boolean }
export interface ChatMessage { id: number; from: number; author: string; text: string; time: number; mine: boolean }
export interface Notice { id: number; subject: string; text: string; time: number; read: boolean }
export interface ContactCourse { id: number; name: string; people: { id: number; fullname: string; teacher: boolean; groups: string[] }[] }

export const workApi = {
  assignment: (cmid: number) => request<Assignment>("GET", `/api/v1/assignments/${cmid}`),
  submissions: (cmid: number) =>
    request<{ assignment: { id: number; name: string; max_grade: number; due: number }; rows: SubmissionRow[] }>("GET", `/api/v1/assignments/${cmid}/submissions`),
  studentWork: (cmid: number, uid: number) => request<Submission & { userid: number; max_grade: number }>("GET", `/api/v1/assignments/${cmid}/submissions/${uid}`),
  saveGrade: (cmid: number, uid: number, grade: number | null, feedback: string) =>
    request<{ ok: boolean }>("PUT", `/api/v1/assignments/${cmid}/grades/${uid}`, { grade, feedback }),
  aiGrade: (cmid: number, uid: number) =>
    request<{ grade: number; max_grade: number; comment: string; criteria: { name: string; score: number; max: number; note: string }[] }>(
      "POST", `/api/v1/assignments/${cmid}/submissions/${uid}/ai`, {}, 200000),
  quiz: (cmid: number) => request<QuizInfo>("GET", `/api/v1/quizzes/${cmid}`),
  startAttempt: (cmid: number) => request<{ attempt: number }>("POST", `/api/v1/quizzes/${cmid}/attempt`, {}),
  attempt: (aid: number) => request<Attempt>("GET", `/api/v1/quiz-attempts/${aid}`),
  saveAttempt: (aid: number, answers: Record<string, unknown>, finish = false, timeup = false) =>
    request<{ state: string }>("POST", `/api/v1/quiz-attempts/${aid}`, { answers, finish, timeup }),
  review: (aid: number) => request<Review>("GET", `/api/v1/quiz-attempts/${aid}/review`),
  grades: (cid: number) =>
    request<{ teacher: boolean; items: GradeItem[]; cells?: Record<string, GradeCell>; rows?: { id: number; fullname: string; cells: Record<string, GradeCell> }[] }>(
      "GET", `/api/v1/courses/${cid}/grades`),
  calendar: (start: number, end: number, course = 0) =>
    request<{ events: CalEvent[]; courses: { id: number; name: string }[]; can_add: boolean }>(
      "GET", `/api/v1/calendar?start=${start}&end=${end}${course ? `&course=${course}` : ""}`),
  addEvent: (cid: number, e: { name: string; timestart: number; duration: number; description: string }) =>
    request<{ ok: boolean }>("POST", `/api/v1/courses/${cid}/events`, e),
  deleteEvent: (id: number) => request<{ ok: boolean }>("DELETE", `/api/v1/events/${id}`),
  inbox: () => request<{ conversations: Conversation[]; notifications: Notice[] }>("GET", "/api/v1/inbox"),
  unread: () => request<{ messages: number; notifications: number }>("GET", "/api/v1/inbox/unread"),
  conversation: (id: number) => request<{ id: number; name: string; messages: ChatMessage[] }>("GET", `/api/v1/inbox/${id}`),
  send: (id: number, text: string) => request<{ ok: boolean }>("POST", `/api/v1/inbox/${id}`, { text }),
  newMessage: (to: number[], text: string) =>
    request<{ sent: number; failed: string[]; conversation: number | null }>("POST", "/api/v1/inbox", { to, text }),
  contacts: () => request<{ courses: ContactCourse[] }>("GET", "/api/v1/inbox-contacts"),
};

/** A file the person picked: a browser File on the web, a temporary path in the mini program. */
export interface Picked { name: string; size: number; file?: File; path?: string }

export function pickFiles(count = 5): Promise<Picked[]> {
  return new Promise((resolve) => {
    // #ifdef H5
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = count > 1;
    input.onchange = () => resolve(Array.from(input.files || []).slice(0, count).map((f) => ({ name: f.name, size: f.size, file: f })));
    input.click();
    // #endif
    // #ifndef H5
    uni.chooseMessageFile({
      count, type: "all",
      success: (r: any) => resolve(r.tempFiles.map((f: any) => ({ name: f.name, size: f.size, path: f.path }))),
      fail: () => resolve([]),
    });
    // #endif
  });
}

/** Save an assignment submission; at most one new file per call (so it works the same in the mini program). */
export function saveSubmission(cmid: number, fields: { text?: string; keep: string[]; submit: boolean }, file?: Picked): Promise<Submission> {
  const url = `${BASE}/api/v1/assignments/${cmid}/submission`;
  const form: Record<string, string> = { keep: JSON.stringify(fields.keep), submit: fields.submit ? "true" : "false" };
  if (fields.text !== undefined) form.text = fields.text;
  const fail = (status: number, body: any) => new ApiError((body && body.error) || `http_${status}`, status);
  // #ifdef H5
  return (async () => {
    const fd = new FormData();
    for (const [k, v] of Object.entries(form)) fd.append(k, v);
    if (file?.file) fd.append("files", file.file, file.name);
    let res: Response;
    try {
      res = await fetch(url, { method: "POST", body: fd, headers: { Authorization: `Bearer ${token.value}` } });
    } catch {
      throw new ApiError("network", 0);
    }
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw fail(res.status, body);
    return body as Submission;
  })();
  // #endif
  // #ifndef H5
  return new Promise((resolve, reject) => {
    const header = { Authorization: `Bearer ${token.value}` };
    if (!file?.path) {
      uni.request({ url, method: "POST", header: { ...header, "Content-Type": "application/x-www-form-urlencoded" }, data: form,
        success: (r: any) => (r.statusCode < 300 ? resolve(r.data) : reject(fail(r.statusCode, r.data))), fail: () => reject(new ApiError("network", 0)) });
      return;
    }
    uni.uploadFile({ url, filePath: file.path, name: "files", formData: form, header,
      success: (r: any) => { const b = JSON.parse(r.data || "{}"); r.statusCode < 300 ? resolve(b) : reject(fail(r.statusCode, b)); },
      fail: () => reject(new ApiError("network", 0)) });
  });
  // #endif
}

/** "12 MB" style sizes. */
export const fileSize = (n: number) => (n > 1048576 ? `${(n / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`);

// ------------------------------------------------------------------ B3: teachers edit the course

/** Text as edited: one language (text) or both (zh, en). */
export interface Bi { text?: string; zh?: string; en?: string }
export interface EditModule { cmid: number; type: string; name: Bi; title: string; visible: boolean; file: { name: string; kind: string } | null }
export interface EditSection { id: number; number: number; name: Bi; title: string; summary: Bi; visible: boolean; modules: EditModule[] }
export interface Structure { course: { id: number; name: Bi; summary: Bi; visible: boolean }; sections: EditSection[] }
export interface QAnswer { text: string; fraction: number; feedback: string; tolerance: number }
export interface QuestionDef { type: "single" | "multiple" | "truefalse" | "shortanswer" | "numerical"; name?: string; text: string; answers: QAnswer[]; correct: boolean; feedback: string; mark: number }
export interface QuizDef {
  cmid: number; section: number; name: string; intro: string; timeopen: number; timeclose: number; timelimit: number; attempts: number;
  grade: number; showanswers: "immediately" | "afterclose" | "never"; visible: boolean | number; questions: QuestionDef[];
  hasattempts?: boolean; unsupported?: number; keep_questions?: boolean;
}
export interface ActivityContent {
  cmid: number; type: string; name: Bi; visible: boolean; content?: Bi; intro?: Bi; url?: string; duedate?: number; cutoffdate?: number;
  grade?: number; allowtext?: boolean; allowfiles?: boolean; maxfiles?: number; quiz?: QuizDef;
}

export const editApi = {
  structure: (cid: number) => request<Structure>("GET", `/api/v1/courses/${cid}/structure`),
  settings: (cid: number, body: { name?: Bi; summary?: Bi; visible?: boolean }) => request<{ ok: boolean }>("PUT", `/api/v1/courses/${cid}/settings`, body),
  addSection: (cid: number, body: { name: Bi; summary?: Bi; position?: number }) => request<{ id: number }>("POST", `/api/v1/courses/${cid}/sections`, body),
  editSection: (cid: number, sid: number, body: { name?: Bi; summary?: Bi; visible?: boolean }) =>
    request<{ ok: boolean }>("PUT", `/api/v1/courses/${cid}/sections/${sid}`, body),
  moveSection: (cid: number, sid: number, position: number) => request<{ ok: boolean }>("POST", `/api/v1/courses/${cid}/sections/${sid}/move`, { position }),
  deleteSection: (cid: number, sid: number, force = false) => request<{ ok: boolean }>("DELETE", `/api/v1/courses/${cid}/sections/${sid}?force=${force}`),
  editModule: (cid: number, cmid: number, body: { name?: Bi; visible?: boolean }) => request<{ ok: boolean }>("PUT", `/api/v1/courses/${cid}/modules/${cmid}`, body),
  moveModule: (cid: number, cmid: number, section: number, before = 0) =>
    request<{ ok: boolean }>("POST", `/api/v1/courses/${cid}/modules/${cmid}/move`, { section, before }),
  deleteModule: (cid: number, cmid: number) => request<{ ok: boolean }>("DELETE", `/api/v1/courses/${cid}/modules/${cmid}`),
  content: (cid: number, cmid: number) => request<ActivityContent>("GET", `/api/v1/courses/${cid}/modules/${cmid}/content`),
  saveContent: (cid: number, cmid: number, body: Partial<ActivityContent>) => request<{ ok: boolean }>("PUT", `/api/v1/courses/${cid}/modules/${cmid}/content`, body),
  addActivity: (cid: number, section: number, body: Partial<ActivityContent> & { type: string }) =>
    request<{ cmid: number }>("POST", `/api/v1/courses/${cid}/sections/${section}/activities`, body),
  saveQuiz: (cid: number, q: QuizDef) => request<{ cmid: number; quizid: number; questions: number }>("POST", `/api/v1/courses/${cid}/quizzes`, q, 120000),
  aiAssignment: (cid: number, section: number, note: string) =>
    request<{ name: string; intro: string; answers: string; grade: number; days: number; chapter: string }>(
      "POST", `/api/v1/courses/${cid}/assignments/ai`, { section, note }, 200000),
  aiQuiz: (cid: number, section: number, count: number, types: string[], note: string) =>
    request<{ questions: QuestionDef[]; title: string }>("POST", `/api/v1/courses/${cid}/quizzes/ai`, { section, count, types, note }, 200000),
};

/** Upload one file as a new item in a section (browser File on the web, temp path in the mini program). */
export function uploadToSection(cid: number, section: number, file: Picked, name = ""): Promise<{ cmid: number }> {
  const url = `${BASE}/api/v1/courses/${cid}/sections/${section}/files`;
  const fail = (status: number, body: any) => new ApiError((body && body.error) || `http_${status}`, status);
  // #ifdef H5
  return (async () => {
    const fd = new FormData();
    if (file.file) fd.append("file", file.file, file.name);
    fd.append("name", name);
    let res: Response;
    try {
      res = await fetch(url, { method: "POST", body: fd, headers: { Authorization: `Bearer ${token.value}` } });
    } catch {
      throw new ApiError("network", 0);
    }
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw fail(res.status, body);
    return body as { cmid: number };
  })();
  // #endif
  // #ifndef H5
  return new Promise((resolve, reject) => {
    uni.uploadFile({ url, filePath: file.path || "", name: "file", formData: { name }, header: { Authorization: `Bearer ${token.value}` },
      success: (r: any) => { const b = JSON.parse(r.data || "{}"); r.statusCode < 300 ? resolve(b) : reject(fail(r.statusCode, b)); },
      fail: () => reject(new ApiError("network", 0)) });
  });
  // #endif
}

/** Display text of a Bi in the current language. */
export const biText = (b: Bi | undefined, lang: string) => (b ? (b.text ?? (lang === "en" ? b.en || b.zh : b.zh || b.en) ?? "") : "");
