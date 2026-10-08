// ---- chain: click a link to see the record and how the link was made ----
const LL = () => (lang === "en" ? 1 : 0);
let cur = 0;
function drawChain() {
  const box = document.getElementById("chain");
  box.innerHTML = "";
  STORY.chain.forEach((n, i) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "node " + (n.tone || ""); b.setAttribute("aria-pressed", i === cur ? "true" : "false");
    b.innerHTML = `<span class="k">${String(i + 1).padStart(2, "0")} · ${n.k[LL()]}</span><span class="v mono">${n.v}</span><span class="s">${n.sub[LL()]}</span>`;
    b.addEventListener("click", () => { cur = i; drawChain(); });
    box.appendChild(b);
  });
  const n = STORY.chain[cur];
  document.getElementById("nodeDetail").innerHTML =
    `<p>${n.d[LL()]}</p><p class="how"><span>${LL() ? "Link from" : "链接依据"}</span> <code>${n.how}</code></p>`;
}
drawChain();
onLang.push(drawChain);
