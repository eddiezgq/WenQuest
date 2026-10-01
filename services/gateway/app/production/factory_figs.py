"""工厂插图 (round 4, §7 F2): figures drawn from the digital factory's own data — never from numbers the AI made up.

  layout          workshop floor plan: units, aisles, AGV homes; `highlight` units are marked
  bom:<code>      product structure (BOM tree) as a block diagram
  routing:<item>  an item's routing (operations, workstation, minutes) as a flow
  control:<char>  control chart of one measured characteristic (values, tolerance limits, nominal)
"""
from __future__ import annotations

from pathlib import Path

from . import figures as F

AREA_COLOR = {"warehouse": "#d9e6f2", "machining": "#fde8c8", "heat": "#f8d0c8", "quality": "#d8efd8",
              "assembly": "#e6dcf4", "test": "#dff1f4"}
KIND_COLOR = {"fg": 0, "sub": 1, "make": 2, "buy": 3, "raw": 4}


def _pair(t: dict | None) -> list[str]:
    t = t or {}
    return [t.get("zh") or t.get("en") or "", t.get("en") or t.get("zh") or ""]


def _label(t: dict | None, lang: str) -> str:
    zh, en = _pair(t)
    return zh if lang == "zh" else en if lang == "en" else f"{zh}\n{en}"


def layout_png(layout: dict, dest: Path, lang: str = "both", highlight: list[str] | None = None) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    plt.rcParams.update({"font.sans-serif": [F._cjk_font(), "DejaVu Sans"], "axes.unicode_minus": False, "font.size": 9})
    fw, fd = layout["floor"]["w_m"], layout["floor"]["d_m"]
    hi = set(highlight or [])
    fig, ax = plt.subplots(figsize=(13, 13 * fd / fw + 0.9), dpi=130)
    ax.add_patch(Rectangle((0, 0), fw, fd, fill=True, fc="#f6f7f9", ec="#5b6b7b", lw=1.6))
    for a in layout.get("aisles") or []:
        if a.get("axis") == "x":
            ax.add_patch(Rectangle((0, a["y_m"] - a.get("width_m", 2.5) / 2), fw, a.get("width_m", 2.5), fc="#e9edf1", ec="none"))
        elif a.get("axis") == "y":
            y0, y1 = a.get("from_y_m", 0), a.get("to_y_m", fd)
            ax.add_patch(Rectangle((a["x_m"] - a.get("width_m", 2.5) / 2, y0), a.get("width_m", 2.5), y1 - y0, fc="#e9edf1", ec="none"))
    for u in layout.get("units") or []:
        x, y, w, d = u["x_m"], u["y_m"], u["w_m"], u["d_m"]
        on = u["unit"] in hi
        ax.add_patch(FancyBboxPatch((x - w / 2, y - d / 2), w, d, boxstyle="round,pad=0.05,rounding_size=0.25",
                                    fc=AREA_COLOR.get(u.get("area"), "#eeeeee"), ec="#c4561a" if on else "#7a8a99", lw=2.6 if on else 1.0))
        ax.text(x, y + 0.1, _label(u["name"], lang), ha="center", va="center", fontsize=8.5 if lang == "both" else 9.5,
                weight="bold" if on else "normal", color="#1f2b36")
        ax.text(x, y - d / 2 - 0.45, u["unit"], ha="center", va="top", fontsize=7, color="#5b6b7b")
    for name, p in (layout.get("agv_home") or {}).items():
        ax.plot(p["x_m"], p["y_m"], marker="s", ms=9, color="#1f5f8b")
        ax.text(p["x_m"] + 0.6, p["y_m"] + 0.4, name.upper(), fontsize=8, color="#1f5f8b")
    ax.set_xlim(-1, fw + 1)
    ax.set_ylim(fd + 1, -1)          # y grows downward, as on the factory's own plan
    ax.set_aspect("equal")
    ax.set_xlabel({"zh": "米", "en": "m"}.get(lang, "米 m"))
    ax.tick_params(labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(dest.with_suffix(".png"), facecolor="white")
    fig.savefig(dest.with_suffix(".svg"), facecolor="white")
    plt.close(fig)
    return {"png": dest.with_suffix(".png").name, "svg": dest.with_suffix(".svg").name}


def bom_graph(product: dict, depth: int = 2) -> dict:
    nodes, edges = [], []

    def walk(n, level, parent):
        nid = f"n{len(nodes)}"
        qty = f" ×{n['qty']:g}" if parent and n.get("qty") not in (None, 1) else ""
        name = n.get("name") or {}
        nodes.append({"id": nid, "label": [f"{n['item_code']}{qty}", f"{_pair(name)[0]}"],
                      "shape": "box" if n.get("kind") in ("fg", "sub") else "round", "emphasis": n.get("kind") == "fg",
                      "color": KIND_COLOR.get(n.get("kind"), 0)})
        if parent:
            edges.append({"from": parent, "to": nid})
        if level < depth:
            for c in (n.get("children") or [])[:12]:
                walk(c, level + 1, nid)
    walk(product["bom"], 0, None)
    return {"direction": "LR", "nodes": nodes[:40], "edges": [e for e in edges if int(e["to"][1:]) < 40]}


def routing_graph(product: dict, item: str) -> dict:
    ops = (product.get("routings") or {}).get(item) or []
    if not ops:
        raise F.FigureError(f"no routing for {item}")
    nodes = [{"id": f"o{k}", "label": [f"{o['seq']} {o['operation'].get('zh', '')} · {o['minutes']:g} min",
                                       f"{o['operation'].get('en', '')} · {o['workstation']}"], "shape": "box"}
             for k, o in enumerate(ops)]
    return {"direction": "LR", "nodes": nodes, "edges": [{"from": f"o{k}", "to": f"o{k + 1}"} for k in range(len(ops) - 1)]}


def control_chart(rows: list[dict], characteristic: str) -> dict:
    pts = [r for r in rows if r.get("characteristic") == characteristic and r.get("value_mm") is not None]
    if len(pts) < 3:
        raise F.FigureError(f"too few measurements of {characteristic}")
    r0 = pts[0]
    name = r0.get("name") or characteristic
    return {"type": "line", "x_label": ["零件序号", "Part no."], "y_label": [f"{name}（mm）", f"{characteristic} (mm)"],
            "series": [{"name": ["测量值", "Measured"], "x": list(range(1, len(pts) + 1)), "y": [p["value_mm"] for p in pts]}],
            "lines": [{"y": r0["upper_tol_mm"], "label": ["上限", "Upper limit"]}, {"y": r0["lower_tol_mm"], "label": ["下限", "Lower limit"]},
                      {"y": r0["nominal_mm"], "label": ["名义值", "Nominal"]}]}


async def make(fac, which: str, dest: Path, lang: str, highlight: list[str] | None = None) -> dict:
    """One factory figure; `which` = layout | bom:<code> | routing:<item> | control:<characteristic>."""
    kind, _, arg = (which or "layout").partition(":")
    kind = kind.strip().lower()
    if kind == "layout":
        import asyncio
        return await asyncio.to_thread(layout_png, await fac.layout(), dest, lang, highlight)
    if kind in ("bom", "routing"):
        products = await fac.products()
        code = arg.strip() if kind == "bom" and arg.strip() else (products[0]["code"] if products else "")
        if not code:
            raise F.FigureError("the factory lists no products")
        if kind == "routing":
            prod = await fac.product(products[0]["code"])
            spec = routing_graph(prod, arg.strip() or next(iter(prod.get("routings") or {}), ""))
        else:
            spec = bom_graph(await fac.product(code))
        import asyncio
        return await asyncio.to_thread(F.render_graph, spec, lang, dest)
    if kind == "control":
        rows = (await fac.data("measurement")).get("rows") or []
        char = arg.strip() or next((r["characteristic"] for r in rows if r.get("characteristic")), "")
        import asyncio
        return await asyncio.to_thread(F.render_chart, control_chart(rows, char), lang, dest)
    raise F.FigureError(f"unknown factory figure {which!r}")
