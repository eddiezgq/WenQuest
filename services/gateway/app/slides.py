"""PowerPoint -> web presentation (round 3, R12).

A teacher's .pptx is turned into a web deck the platform can present without a download:

- LibreOffice converts it to PDF; every page is rendered to a sharp WebP image (1600 px wide)
  plus a thumbnail. The browser then only has to show pictures, which looks the same
  everywhere (including phones and the mini program).
- Embedded videos are taken out of the file with their position on the slide, so the
  animation plays in place.
- Hyperlinks become clickable areas. A link that points at a virtual lab ("...#lab-1-3")
  becomes "go to lab 1.3" inside the platform.
- Slide text mentioning a lab ("1.3 虚拟实验", "实验 1.3", "Lab 1.3") marks that slide, so the
  presenter can offer "去做实验 1.3".
- Speaker notes are kept; the gateway only hands them to the course's teachers.

Results are cached by the file's content hash, so each deck is converted once.
"""
from __future__ import annotations

import asyncio
import hashlib
import io
import json
import logging
import posixpath
import re
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Awaitable, Callable
from xml.etree import ElementTree as ET

log = logging.getLogger("wenquest.slides")

WIDTH = 1600        # slide image width in pixels
THUMB = 320         # thumbnail width
CONVERT_TIMEOUT = 240
VERSION = 1         # bump to re-convert every deck after a converter change

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
R_ID = "{%s}id" % NS["r"]
R_EMBED = "{%s}embed" % NS["r"]
R_LINK = "{%s}link" % NS["r"]

# "1.3 虚拟实验", "虚拟实验 1.3", "实验1.3", "Lab 1.3", "#lab-1-3"
LAB_TEXT = re.compile(
    r"(?:(\d{1,2})\s*[.．-]\s*(\d{1,2})\s*(?:虚拟)?实验)|(?:(?:虚拟)?实验\s*(\d{1,2})\s*[.．-]\s*(\d{1,2}))"
    r"|(?:\blab\s*(\d{1,2})\s*[.-]\s*(\d{1,2}))|(?:(\d{1,2})\s*\.\s*(\d{1,2})\s+virtual\s+lab)",
    re.I)
LAB_LINK = re.compile(r"lab-(\d{1,2})-(\d{1,2})", re.I)
VIDEO_EXT = {".mp4", ".m4v", ".webm", ".mov"}


def lab_refs(text: str) -> list[str]:
    refs: list[str] = []
    for m in LAB_TEXT.finditer(text or ""):
        nums = [g for g in m.groups() if g]
        ref = f"{int(nums[0])}.{int(nums[1])}"
        if ref not in refs:
            refs.append(ref)
    return refs


# --- reading the pptx ------------------------------------------------------------------

def _rels(z: zipfile.ZipFile, part: str) -> dict[str, dict]:
    """Relationships of a part: rId -> {target (resolved path or URL), external}."""
    folder, name = posixpath.split(part)
    path = posixpath.join(folder, "_rels", name + ".rels")
    if path not in z.namelist():
        return {}
    out = {}
    for rel in ET.fromstring(z.read(path)).findall("rel:Relationship", NS):
        target = rel.get("Target", "")
        external = rel.get("TargetMode") == "External"
        if not external:
            target = posixpath.normpath(posixpath.join(folder, target))
        out[rel.get("Id")] = {"target": target, "external": external, "type": rel.get("Type", "")}
    return out


def _box(el, sw: int, sh: int, parent=None) -> dict | None:
    """Position of a shape as fractions of the slide (x, y, w, h), following one group level."""
    xfrm = el.find("p:spPr/a:xfrm", NS)
    if xfrm is None:
        xfrm = el.find("p:grpSpPr/a:xfrm", NS)
    if xfrm is None:
        return None
    off, ext = xfrm.find("a:off", NS), xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    x, y = int(off.get("x", 0)), int(off.get("y", 0))
    w, h = int(ext.get("cx", 0)), int(ext.get("cy", 0))
    if parent is not None:  # child coordinates of a group -> slide coordinates
        (gx, gy, gw, gh), (cx, cy, cw, ch) = parent
        sx, sy = (gw / cw if cw else 1), (gh / ch if ch else 1)
        x, y, w, h = gx + (x - cx) * sx, gy + (y - cy) * sy, w * sx, h * sy
    return {"x": round(x / sw, 5), "y": round(y / sh, 5), "w": round(w / sw, 5), "h": round(h / sh, 5)}


def _group_frame(el) -> tuple | None:
    xfrm = el.find("p:grpSpPr/a:xfrm", NS)
    if xfrm is None:
        return None
    get = lambda tag, a, b: (int(xfrm.find(tag, NS).get(a, 0)), int(xfrm.find(tag, NS).get(b, 0)))  # noqa: E731
    try:
        gx, gy = get("a:off", "x", "y")
        gw, gh = get("a:ext", "cx", "cy")
        cx, cy = get("a:chOff", "x", "y")
        cw, ch = get("a:chExt", "cx", "cy")
    except AttributeError:
        return None
    return (gx, gy, gw, gh), (cx, cy, cw, ch)


def parse_pptx(data: bytes) -> dict:
    """Slide size, and per slide: text, notes, lab references, videos and links."""
    z = zipfile.ZipFile(io.BytesIO(data))
    pres = ET.fromstring(z.read("ppt/presentation.xml"))
    size = pres.find("p:sldSz", NS)
    sw, sh = (int(size.get("cx")), int(size.get("cy"))) if size is not None else (12192000, 6858000)
    prels = _rels(z, "ppt/presentation.xml")
    order = [prels[s.get(R_ID)]["target"] for s in pres.findall("p:sldIdLst/p:sldId", NS) if s.get(R_ID) in prels]
    media: dict[str, str] = {}  # zip path -> file name in the deck folder
    slides = []
    for part in order:
        root = ET.fromstring(z.read(part))
        rels = _rels(z, part)
        texts = [t.text for t in root.iter("{%s}t" % NS["a"]) if t.text]
        videos, links = [], []

        def walk(container, parent=None):
            for el in list(container):
                tag = el.tag.rsplit("}", 1)[-1]
                if tag == "grpSp":
                    walk(el, _group_frame(el) or parent)
                    continue
                if tag not in ("sp", "pic", "cxnSp", "graphicFrame"):
                    continue
                box = _box(el, sw, sh, parent)
                # embedded video
                vf = el.find(".//a:videoFile", NS)
                if vf is not None and box:
                    m = el.find(".//p14:media", NS)
                    rid = (m.get(R_EMBED) if m is not None else None) or vf.get(R_LINK)
                    rel = rels.get(rid or "")
                    if rel and not rel["external"] and Path(rel["target"]).suffix.lower() in VIDEO_EXT:
                        name = media.setdefault(rel["target"], f"v{len(media) + 1}{Path(rel['target']).suffix.lower()}")
                        videos.append({"src": name, **box})
                    continue
                # hyperlinks on the shape or on its text
                for h in el.iter("{%s}hlinkClick" % NS["a"]):
                    rel = rels.get(h.get(R_ID) or "")
                    if not rel or not rel["external"] or not box:
                        continue
                    href = rel["target"]
                    lab = LAB_LINK.search(href)
                    link = {"href": href if href.startswith(("http://", "https://")) else "", **box}
                    if lab:
                        link["lab"] = f"{int(lab.group(1))}.{int(lab.group(2))}"
                    if (link["href"] or link.get("lab")) and link not in links:
                        links.append(link)
                    break  # one area per shape

        tree = root.find("p:cSld/p:spTree", NS)
        if tree is not None:
            walk(tree)
        notes = ""
        for rel in rels.values():
            if rel["type"].endswith("/notesSlide") and rel["target"] in z.namelist():
                nroot = ET.fromstring(z.read(rel["target"]))
                body = []
                for sp in nroot.iter("{%s}sp" % NS["p"]):
                    ph = sp.find(".//p:nvPr/p:ph", NS)
                    if ph is not None and ph.get("type") == "body":
                        for para in sp.iter("{%s}p" % NS["a"]):
                            line = "".join(t.text or "" for t in para.iter("{%s}t" % NS["a"])).strip()
                            if line:
                                body.append(line)
                notes = "\n".join(body)
        text = " ".join(texts)
        refs = lab_refs(text)
        for link in links:
            if link.get("lab") and link["lab"] not in refs:
                refs.append(link["lab"])
        slides.append({"text": text[:2000], "notes": notes, "labs": refs, "videos": videos, "links": links})
    return {"width": sw, "height": sh, "slides": slides, "media": media}


# --- rendering -------------------------------------------------------------------------

def _to_pdf(pptx: Path, out: Path) -> Path:
    profile = Path(tempfile.mkdtemp(prefix="wq-lo-"))
    try:
        subprocess.run(
            ["soffice", f"-env:UserInstallation=file://{profile}", "--headless", "--norestore",
             "--convert-to", "pdf", "--outdir", str(out), str(pptx)],
            check=True, timeout=CONVERT_TIMEOUT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = out / (pptx.stem + ".pdf")
    if not pdf.exists():
        raise RuntimeError("LibreOffice produced no PDF")
    return pdf


def convert(data: bytes, folder: Path, ext: str = ".pptx") -> dict:
    """Convert one deck into `folder` (images, media, manifest.json). Blocking; run in a thread.
    .pptx gets videos, links, notes and lab marks; .ppt/.odp are converted as pages only."""
    import pypdfium2 as pdfium

    try:
        info = parse_pptx(data)
    except Exception:  # not a pptx package (old .ppt, .odp) or an odd one: pages only
        info = {"slides": [], "media": {}}
    work = Path(tempfile.mkdtemp(prefix="wq-deck-"))
    try:
        src = work / ("deck" + (ext if ext in (".pptx", ".ppt", ".odp", ".pps", ".ppsx") else ".pptx"))
        src.write_bytes(data)
        pdf = pdfium.PdfDocument(str(_to_pdf(src, work)))
        tmp = folder.with_name(folder.name + ".tmp")
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        pages = []
        for i in range(len(pdf)):
            page = pdf[i]
            w, _ = page.get_size()
            img = page.render(scale=WIDTH / w).to_pil().convert("RGB")
            name = f"p{i + 1:03d}.webp"
            img.save(tmp / name, "WEBP", quality=84, method=4)
            thumb = img.resize((THUMB, round(img.height * THUMB / img.width)))
            thumb.save(tmp / f"t{i + 1:03d}.webp", "WEBP", quality=70)
            pages.append((name, f"t{i + 1:03d}.webp", img.width, img.height))
        pdf.close()
        if info["media"]:
            z = zipfile.ZipFile(io.BytesIO(data))
            for zpath, name in info["media"].items():
                (tmp / name).write_bytes(z.read(zpath))
        slides = []
        for i, (image, thumb, w, h) in enumerate(pages):
            meta = info["slides"][i] if i < len(info["slides"]) else {"text": "", "notes": "", "labs": [], "videos": [], "links": []}
            slides.append({"image": image, "thumb": thumb, **meta})
        manifest = {"version": VERSION, "pages": len(slides), "width": pages[0][2] if pages else WIDTH,
                    "height": pages[0][3] if pages else round(WIDTH * 9 / 16), "slides": slides,
                    "created": time.time()}
        (tmp / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False))
        shutil.rmtree(folder, ignore_errors=True)
        tmp.rename(folder)
        return manifest
    finally:
        shutil.rmtree(work, ignore_errors=True)


# --- cache and background conversion --------------------------------------------------------

class SlideStore:
    """<root>/<content hash>/{manifest.json, p001.webp, t001.webp, v1.mp4} and an index that maps a
    Moodle file (url, modified time, size) to its content hash, so a known deck is not downloaded again."""

    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"
        self.index: dict[str, str] = {}
        if self.index_path.exists():
            try:
                self.index = json.loads(self.index_path.read_text())
            except ValueError:
                self.index = {}
        self.pending: dict[str, dict] = {}   # waiting decks: {priority, seq, fetch, ext, queued}
        self.current: dict | None = None     # the deck being converted now: {src, started}
        self.worker: asyncio.Task | None = None
        self.failed: dict[str, float] = {}
        self.done_count = 0
        self.seq = 0
        self.available = bool(shutil.which("soffice"))

    @staticmethod
    def source_key(url: str, modified: int | None, size: int | None) -> str:
        return hashlib.sha256(f"{url}|{modified}|{size}".encode()).hexdigest()[:40]

    def manifest(self, key: str) -> dict | None:
        p = self.root / key / "manifest.json"
        if not p.exists():
            return None
        m = json.loads(p.read_text())
        return m if m.get("version") == VERSION else None

    def file(self, key: str, name: str) -> Path | None:
        if not re.fullmatch(r"[0-9a-f]{64}", key) or not re.fullmatch(r"[pt]\d{3}\.webp|v\d{1,3}\.(mp4|m4v|webm|mov)", name):
            return None
        p = self.root / key / name
        return p if p.exists() else None

    def status(self, src: str) -> tuple[str, str | None]:
        """("ready", key) | ("converting", None) | ("failed", None) | ("missing", None)."""
        key = self.index.get(src)
        if key and self.manifest(key):
            return "ready", key
        if (self.current and self.current["src"] == src) or src in self.pending:
            return "converting", None
        if src in self.failed and time.time() - self.failed[src] < 600:
            return "failed", None
        return "missing", None

    def progress(self, src: str) -> dict:
        """Where a deck stands: converting now (with seconds so far) or waiting behind N others."""
        if self.current and self.current["src"] == src:
            return {"queue": 0, "elapsed": round(time.time() - self.current["started"])}
        if src in self.pending:
            me = self.pending[src]
            ahead = sum(1 for p in self.pending.values() if (p["priority"], p["seq"]) < (me["priority"], me["seq"]))
            return {"queue": ahead + (1 if self.current else 0), "elapsed": 0}
        return {"queue": 0, "elapsed": 0}

    def overview(self) -> dict:
        return {"available": self.available, "waiting": len(self.pending), "converted": self.done_count,
                "failed": len(self.failed),
                "current_seconds": round(time.time() - self.current["started"]) if self.current else None}

    def start(self, src: str, fetch: Callable[[], Awaitable[bytes]], ext: str = ".pptx", priority: int = 1) -> None:
        """Queue a deck for conversion. priority 0 = someone is looking at it now (goes first);
        1 = converting ahead of time. A queued deck that someone opens moves to the front."""
        if not self.available:
            return
        state, _ = self.status(src)
        if state == "ready" or (self.current and self.current["src"] == src):
            return
        if src in self.pending:
            p = self.pending[src]
            if priority < p["priority"]:
                p.update(priority=priority, fetch=fetch)
            return
        if state == "failed" and priority > 0:
            return  # do not retry failed decks in the background; a viewer's retry clears it
        self.failed.pop(src, None)
        self.seq += 1
        self.pending[src] = {"priority": priority, "seq": self.seq, "fetch": fetch, "ext": ext, "queued": time.time()}
        if not self.worker or self.worker.done():
            self.worker = asyncio.create_task(self._work())

    async def _work(self) -> None:
        # LibreOffice is heavy: one deck at a time, most urgent first.
        while self.pending:
            src = min(self.pending, key=lambda k: (self.pending[k]["priority"], self.pending[k]["seq"]))
            job = self.pending.pop(src)
            self.current = {"src": src, "started": time.time()}
            try:
                data = await job["fetch"]()
                key = hashlib.sha256(data).hexdigest()
                if not self.manifest(key):
                    await asyncio.to_thread(convert, data, self.root / key, job["ext"])
                    log.info("converted deck %s in %.1fs (%d waiting)", key[:12], time.time() - self.current["started"], len(self.pending))
                self.index[src] = key
                self.index_path.write_text(json.dumps(self.index))
                self.done_count += 1
            except Exception:
                log.exception("slide conversion failed")
                self.failed[src] = time.time()
            finally:
                self.current = None


class Settings:
    """Small per-activity settings the teacher changes in the new UI (e.g. allow downloading slides)."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _all(self) -> dict:
        try:
            return json.loads(self.path.read_text())
        except (OSError, ValueError):
            return {}

    def get(self, cmid: int) -> dict:
        return self._all().get(str(cmid), {})

    def set(self, cmid: int, **values) -> dict:
        data = self._all()
        cur = {**data.get(str(cmid), {}), **values}
        data[str(cmid)] = cur
        self.path.write_text(json.dumps(data))
        return cur
