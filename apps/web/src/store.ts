// Course data shared by the course, unit and activity pages, so moving between them is instant.
import { ref, watch } from "vue";
import { api, type CourseInfo, type Module, type Section } from "./api";
import { locale } from "./i18n";

export interface CourseData { info: CourseInfo; sections: Section[] }

const cache = new Map<number, CourseData>();
const pending = new Map<number, Promise<CourseData>>();

/** A teacher can look at the course exactly as a student sees it. */
export const studentPreview = ref(false);

watch(locale, () => cache.clear());

export async function loadCourse(id: number, force = false): Promise<CourseData> {
  if (!force && cache.has(id)) return cache.get(id)!;
  if (!force && pending.has(id)) return pending.get(id)!;
  const p = Promise.all([api.course(id), api.outline(id)])
    .then(([info, sections]) => {
      const d = { info, sections };
      cache.set(id, d);
      return d;
    })
    .finally(() => pending.delete(id));
  pending.set(id, p);
  return p;
}

export function cachedCourse(id: number): CourseData | undefined {
  return cache.get(id);
}

export const isTeacher = (d?: CourseData | null) => !!d && d.info.role === "teacher" && !studentPreview.value;

/** Modules the current viewer should see (teachers previewing as a student lose hidden ones). */
export function visibleModules(d: CourseData, s: Section): Module[] {
  return s.modules.filter((m) => m.type !== "label" && (isTeacher(d) || !m.hidden));
}

/** What a module is, for icons, grouping and choosing a viewer. */
export function moduleKind(m: Module): string {
  if (m.type === "resource") return m.file?.kind || "file";
  if (m.type === "page") return "reading";
  if (m.type === "url") return "link";
  return m.type; // assign, quiz, forum, ...
}

export const KIND_ICON: Record<string, string> = {
  reading: "文", video: "▶", slides: "◧", pdf: "▤", lab: "⚗", doc: "▤", sheet: "▦", image: "◩",
  audio: "♪", file: "▢", link: "↗", assign: "✎", quiz: "?", forum: "✉",
};

/** A chapter-like section: has lessons, videos, slides or labs (not the course-info section). */
export function isUnit(d: CourseData, s: Section): boolean {
  return visibleModules(d, s).some((m) => ["reading", "video", "slides", "lab", "assign"].includes(moduleKind(m)));
}

export function findModule(d: CourseData, cmid: number): { section: Section; module: Module; index: number } | null {
  for (const section of d.sections) {
    const index = section.modules.findIndex((m) => m.id === cmid);
    if (index >= 0) return { section, module: section.modules[index], index };
  }
  return null;
}

export function lastVisited(courseId: number): number | null {
  try { return Number(uni.getStorageSync(`wq.last.${courseId}`)) || null; } catch { return null; }
}
export function rememberVisit(courseId: number, cmid: number) {
  try { uni.setStorageSync(`wq.last.${courseId}`, String(cmid)); } catch { /* ignore */ }
}

/** The course-information section (syllabus, calendar, rubrics) if the course has one. */
export function syllabusSection(d: CourseData): Section | null {
  const named = d.sections.find((s) => /课程说明|教学大纲|课程信息|syllabus|course info/i.test(s.name));
  if (named) return named;
  return d.sections.find((s) => !isUnit(d, s) && visibleModules(d, s).some((m) => m.type === "resource")) || null;
}

export function units(d: CourseData): Section[] {
  return d.sections.filter((s) => isUnit(d, s));
}

/** The 13 items of the course menu (R11). Teachers always see all of them; students only see
 * content menus that have something behind them, plus the class-wide ones. */
export function courseMenu(d: CourseData): { key: string }[] {
  const mods = d.sections.flatMap((s) => visibleModules(d, s));
  const has = (...kinds: string[]) => mods.some((m) => kinds.includes(moduleKind(m)));
  const teacher = isTeacher(d);
  const show: Record<string, boolean> = {
    home: true,
    announcements: true,
    syllabus: teacher || !!syllabusSection(d) || !!d.info.summary,
    modules: true,
    slides: teacher || has("slides", "pdf"),
    labs: teacher || has("lab"),
    assignments: teacher || has("assign"),
    quizzes: teacher || has("quiz"),
    discussions: true,
    online: true,
    grades: true,
    people: true,
    calendar: true,
  };
  return MENU_ORDER.filter((k) => show[k]).map((key) => ({ key }));
}

export const MENU_ORDER = [
  "home", "announcements", "syllabus", "modules", "slides", "labs", "assignments",
  "quizzes", "discussions", "online", "grades", "people", "calendar",
];

/** Forum activities: the course's announcements forum vs. discussion forums. */
export const isNewsForum = (m: Module) => m.type === "forum" && /公告|announce|news/i.test(m.name || "");
