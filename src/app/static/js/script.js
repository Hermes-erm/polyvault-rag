/* ============================================================
   ingest · peripheral service
   Renders the recent-documents table + a minimal chat aside.
   Wire your RAG backend in queryBackend().
   ============================================================ */

/* ---- file-type glyphs ---- */
const ICONS = {
  pdf:  '<path d="M6 2h8l4 4v16H6z" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M14 2v4h4" fill="none" stroke="currentColor" stroke-width="1.3"/>',
  xlsx: '<rect x="4" y="4" width="16" height="16" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M4 10h16M10 4v16" stroke="currentColor" stroke-width="1.3"/>',
  png:  '<rect x="4" y="4" width="16" height="16" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.3"/><circle cx="9" cy="9" r="1.6" fill="currentColor"/><path d="M5 17l4-4 3 3 3-4 4 5" fill="none" stroke="currentColor" stroke-width="1.3"/>',
  json: '<path d="M9 4c-2 0-3 1-3 3v2c0 1-1 2-2 2 1 0 2 1 2 2v2c0 2 1 3 3 3M15 4c2 0 3 1 3 3v2c0 1 1 2 2 2-1 0-2 1-2 2v2c0 2-1 3-3 3" fill="none" stroke="currentColor" stroke-width="1.3"/>',
  txt:  '<path d="M6 2h12v20H6z" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M9 8h6M9 12h6M9 16h4" stroke="currentColor" stroke-width="1.3"/>'
};
const iconFor = (name) => ICONS[name.split(".").pop().toLowerCase()] || ICONS.txt;

/* ---- corpus / recent documents ---- */
const DOCS = [
  { name: "q3_compliance_review.pdf", chunks: 34,   size: "2.1 mb", status: "indexed"   },
  { name: "vendor_ledger.xlsx",       chunks: 61,   size: "890 kb", status: "embedding" },
  { name: "whiteboard_scan_04.png",   chunks: 5,    size: "3.4 mb", status: "indexed"   },
  { name: "api_schema_export.json",   chunks: null, size: "12 kb",  status: "failed"    }
];

const table = document.getElementById("docTable");
DOCS.forEach((d) => {
  const row = document.createElement("div");
  row.className = "row";
  row.innerHTML = `
    <span class="row__icon"><svg viewBox="0 0 24 24">${iconFor(d.name)}</svg></span>
    <span class="row__name">${d.name}</span>
    <span class="row__num">${d.chunks ?? "—"}</span>
    <span class="row__size">${d.size}</span>
    <span class="badge badge--${d.status}">${d.status}</span>`;
  table.appendChild(row);
});

/* ---- drop dock (visual only for now) ---- */
const drop = document.getElementById("drop");
["dragenter", "dragover"].forEach((e) =>
  drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.add("over"); }));
["dragleave", "drop"].forEach((e) =>
  drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.remove("over"); }));
// TODO: on 'drop', read ev.dataTransfer.files and POST them to your ingest endpoint.

/* ============================================================
   chat aside
   ============================================================ */
const stream = document.getElementById("stream");
const input  = document.getElementById("input");
const send   = document.getElementById("send");
let busy = false;

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 120) + "px";
  send.disabled = input.value.trim() === "";
});
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); }
});
send.addEventListener("click", ask);

async function ask() {
  const text = input.value.trim();
  if (!text || busy) return;

  const empty = stream.querySelector(".chat__empty");
  if (empty) empty.remove();

  busy = true;
  input.value = ""; input.style.height = "auto"; send.disabled = true;

  addMsg("user", text);
  const bot = addMsg("bot", "");
  const dots = document.createElement("div");
  dots.className = "dots";
  dots.innerHTML = "<span></span><span></span><span></span>";
  bot.querySelector(".m__body").appendChild(dots);
  scroll();

  try {
    const { answer, sources } = await queryBackend(text);
    bot.querySelector(".m__body").textContent = answer;
    if (sources?.length) {
      const src = document.createElement("div");
      src.className = "m__src";
      src.innerHTML = sources.map((s) => `<span class="chip">${s}</span>`).join("");
      bot.appendChild(src);
    }
  } catch {
    const body = bot.querySelector(".m__body");
    body.textContent = "retrieval failed — check the pipeline and try again.";
    body.style.color = "var(--red)";
  } finally {
    busy = false; input.focus(); scroll();
  }
}

function addMsg(kind, text) {
  const el = document.createElement("div");
  el.className = `m m--${kind}`;
  if (kind === "bot") {
    el.innerHTML = `<div class="m__role">assistant</div><div class="m__body"></div>`;
    el.querySelector(".m__body").textContent = text;
  } else {
    el.textContent = text;
  }
  stream.appendChild(el);
  scroll();
  return el;
}
const scroll = () => { stream.scrollTop = stream.scrollHeight; };

/* ============================================================
   BACKEND SEAM — replace with your RAG service.
   Return: { answer: string, sources: string[] }

   async function queryBackend(question) {
     const r = await fetch("/api/query", {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({ question })
     });
     if (!r.ok) throw new Error("query failed");
     return r.json();   // { answer, sources }
   }
   ============================================================ */
async function queryBackend(question) {
  await new Promise((r) => setTimeout(r, 650));
  const q = question.toLowerCase();
  const hits = DOCS
    .filter((d) => d.status === "indexed")
    .filter((d) => d.name.replace(/[_.]/g, " ").split(" ").some((w) => w.length > 3 && q.includes(w)))
    .map((d) => d.name);
  return {
    answer: `Demo response for "${question}". Replace queryBackend() with your retrieval + generation call — the grounded answer renders here, sources below.`,
    sources: hits.length ? hits : ["q3_compliance_review.pdf"]
  };
}
