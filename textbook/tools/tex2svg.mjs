// Typesets formulas to SVG with MathJax on the server, so the web reader, the mini program and the PDF all show
// the same formulas without client-side scripts.
// stdin: JSON [{tex, display}]; stdout: JSON [{svg} | {error}] in the same order.
import { mathjax } from "mathjax-full/js/mathjax.js";
import { TeX } from "mathjax-full/js/input/tex.js";
import { SVG } from "mathjax-full/js/output/svg.js";
import { liteAdaptor } from "mathjax-full/js/adaptors/liteAdaptor.js";
import { RegisterHTMLHandler } from "mathjax-full/js/handlers/html.js";
import { AllPackages } from "mathjax-full/js/input/tex/AllPackages.js";

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const tex = new TeX({ packages: AllPackages.filter((p) => p !== "bussproofs"), formatError: (_jax, err) => { throw err; } });
const svg = new SVG({ fontCache: "none" });
const doc = mathjax.document("", { InputJax: tex, OutputJax: svg });

let input = "";
process.stdin.on("data", (d) => (input += d));
process.stdin.on("end", () => {
  const items = JSON.parse(input || "[]");
  const out = items.map(({ tex: src, display }) => {
    try {
      const node = doc.convert(src, { display: !!display });
      return { svg: adaptor.innerHTML(node) };
    } catch (e) {
      return { error: String(e && e.message ? e.message : e) };
    }
  });
  process.stdout.write(JSON.stringify(out));
});
