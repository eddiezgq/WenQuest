"""Snapshot the readouts and drawings of the sewing labs under a fixed sequence of actions (round 20).
Used to prove that moving the models into the shared mechanism library changes nothing:

    python3 tools/labsnap.py out_before.json [lab ...]     # before the change
    python3 tools/labsnap.py out_after.json  [lab ...]     # after
    python3 tools/labsnap.py --diff out_before.json out_after.json

Labs are opened from a built copy (build.py out) so the library is inlined exactly as it will be published.
"""
import json, sys, hashlib, pathlib, subprocess, tempfile
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parents[1]
LABS = ["slidercrank", "takeup", "hook", "feed", "tension", "timing", "lockstitch"]
IDS = ["meter", "state", "tasks", "phase", "checks", "sewOut", "stitches", "verdict", "d-val", "angOut", "rdOut", "wOut",
       "hookNote", "camHint", "ph-title", "ph-text", "r-th", "r-x", "r-rise", "r-hook", "r-loop", "r-n",
       "k-lam", "k-s", "k-v", "k-va", "k-at", "k-atg", "k-ab", "k-abg", "k-f", "k-h", "k-dw", "secNote", "modeNote", "viewNote"]
BUTTONS = ["mess", "reset", "lowb", "sew", "camFromLink", "camSmooth", "lkReset"]

SNAP = """(ids)=>{const o={};for(const i of ids){const e=document.getElementById(i);if(e)o[i]=e.innerHTML;}
  const h=s=>{let x=0;for(let i=0;i<s.length;i++)x=(x*31+s.charCodeAt(i))|0;return x;};
  document.querySelectorAll('canvas').forEach((c,k)=>{try{o['canvas'+k]=h(c.toDataURL());}catch(e){}});
  document.querySelectorAll('svg[id]').forEach(s=>{o['svg:'+s.id]=h(s.innerHTML);});
  return o;}"""


def actions(page):
    """the action list of this page: ranges to min/max/default, selects through their options, buttons, mode buttons"""
    return page.evaluate("""()=>{const a=[];
      document.querySelectorAll('input[type=range]').forEach(e=>{if(['ang','theta','spd'].includes(e.id))return;
        a.push(['range',e.id,e.min]);a.push(['range',e.id,e.max]);a.push(['range',e.id,e.value]);});
      document.querySelectorAll('select').forEach(e=>{const v=e.value;[...e.options].forEach(o=>a.push(['select',e.id,o.value]));a.push(['select',e.id,v]);});
      document.querySelectorAll('#modes button').forEach((b,k)=>a.push(['mode',k]));
      return a;}""")


def act(page, a):
    kind = a[0]
    if kind == "range":
        page.evaluate("([i,v])=>{const e=document.getElementById(i);e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));}", [a[1], a[2]])
    elif kind == "select":
        page.evaluate("([i,v])=>{const e=document.getElementById(i);e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}));e.dispatchEvent(new Event('input',{bubbles:true}));}", [a[1], a[2]])
    elif kind == "mode":
        page.evaluate("k=>document.querySelectorAll('#modes button')[k].click()", a[1])
    elif kind == "button":
        page.evaluate("i=>{const e=document.getElementById(i);if(e)e.click();}", a[1])
    elif kind == "angle":
        page.evaluate("([i,v])=>{const e=document.getElementById(i);if(!e)return;e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));}", [a[1], a[2]])


def freeze(page):
    """stop the animations and park the angle at a fixed value"""
    page.evaluate("""()=>{for(const id of ['play']){const b=document.getElementById(id);
        if(b&&(b.getAttribute('aria-pressed')==='true'||/暂停|Pause/.test(b.textContent)))b.click();}}""")
    for i, v in (("ang", "200"), ("theta", "200")):
        act(page, ("angle", i, v))


def snap_lab(page, url):
    page.goto(url)
    page.wait_for_timeout(400)
    freeze(page)
    page.wait_for_timeout(200)
    out = []
    seq = actions(page) + [("button", b) for b in BUTTONS] + [("angle", "ang", v) for v in ("0", "100", "230", "300")]
    for a in seq:
        act(page, a)
        freeze(page)
        page.wait_for_timeout(60)
        out.append([list(a), page.evaluate(SNAP, IDS)])
    return out


def main():
    if sys.argv[1] == "--diff":
        A, B = (json.load(open(p)) for p in sys.argv[2:4])
        bad = 0
        for k in A:
            if k not in B:
                print("missing", k); bad += 1; continue
            for (aa, sa), (ab, sb) in zip(A[k], B[k]):
                for key in sorted(set(sa) | set(sb)):
                    if sa.get(key) != sb.get(key):
                        bad += 1
                        if bad <= 40:
                            print(k, aa, key, "\n  before:", str(sa.get(key))[:200], "\n  after: ", str(sb.get(key))[:200])
        print("differences:", bad)
        sys.exit(1 if bad else 0)
    dest = sys.argv[1]
    labs = sys.argv[2:] or LABS
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, str(HERE / "build.py"), tmp], check=True, capture_output=True)
        res = {}
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 1280, "height": 900})
            for lang, base in (("zh", f"{tmp}/labs"), ("en", f"{tmp}/en/labs")):
                for lab in labs:
                    res[f"{lang}/{lab}"] = snap_lab(page, f"file://{base}/{lab}.html")
            b.close()
    json.dump(res, open(dest, "w"), ensure_ascii=False)
    print("saved", dest, {k: len(v) for k, v in res.items()})


if __name__ == "__main__":
    main()
