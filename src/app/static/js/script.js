const API = "http://localhost:8000";

const $ = (id) => document.getElementById(id);
const table = $("table");
const tableMsg = $("tableMsg");
const stream = $("stream");
const input = $("input");
const send = $("send");
const lead = $("lead");
const LEAD = lead.textContent;

async function call(path, options) {
  const res = await fetch(API + path, options);
  const body = await res.json().catch(() => null);
  if (!res.ok) throw new Error(body?.detail || `HTTP ${res.status}`);
  return body;
}

/* ---------- documents ---------- */

function render(files) {
  table.querySelectorAll(".row:not(.row--head)").forEach((r) => r.remove());

  if (!files.length) {
    tableMsg.textContent = "No documents yet. Upload one to get started.";
    tableMsg.hidden = false;
  } else {
    tableMsg.hidden = true;
    for (const f of files) {
      const row = document.createElement("div");
      row.className = "row";
      row.append(
        cell(f.name ?? "untitled"),
        cell(f.chunks ?? "—"),
        cell(f.size ?? "—"),
        cell(f.status ?? "unknown", `badge badge--${f.status ?? "unknown"}`),
      );
      table.insertBefore(row, tableMsg);
    }
  }

  const indexed = files.filter((f) => f.status === "indexed").length;
  $("stat").textContent = `${files.length} files · ${indexed} indexed`;
}

function cell(text, className) {
  const el = document.createElement("span");
  el.textContent = text;
  if (className) el.className = className;
  return el;
}

async function loadFiles() {
  try {
    const files = await call("/rag/files/");
    render(Array.isArray(files) ? files : []);
  } catch (err) {
    tableMsg.hidden = false;
    tableMsg.textContent = `Could not load documents — ${err.message}`;
    $("stat").textContent = "offline";
  }
}

$("refresh").addEventListener("click", loadFiles);
loadFiles();

/* ---------- upload ---------- */

const drop = $("drop");
const fileInput = $("file");

drop.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
  upload(fileInput.files);
  fileInput.value = "";
});

["dragenter", "dragover", "dragleave", "drop"].forEach((type) =>
  drop.addEventListener(type, (e) => {
    e.preventDefault();
    drop.classList.toggle("over", type === "dragenter" || type === "dragover");
    if (type === "drop") upload(e.dataTransfer?.files);
  }),
);

async function upload(list) {
  const files = [...(list || [])];
  if (!files.length) return;

  for (const file of files) {
    lead.textContent = `Uploading ${file.name}…`;
    const form = new FormData();
    form.append("file", file);
    try {
      await call("/rag/files/import", { method: "POST", body: form });
      lead.textContent = `Imported ${file.name}`;
    } catch (err) {
      lead.textContent = `${file.name} failed — ${err.message}`;
    }
  }
  loadFiles();
  setTimeout(() => (lead.textContent = LEAD), 3000);
}

/* ---------- query ---------- */

let busy = false;

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 120) + "px";
  send.disabled = !input.value.trim();
});
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    $("form").requestSubmit();
  }
});
$("form").addEventListener("submit", ask);

async function ask(e) {
  e.preventDefault();
  const question = input.value.trim();
  if (!question || busy) return;

  busy = true;
  send.disabled = true;
  input.value = "";
  input.style.height = "auto";
  stream.querySelector(".empty")?.remove();

  addMsg("user", question);
  const bot = addMsg("bot", "…");

  try {
    const res = await call(
      `/query/search?query=${encodeURIComponent(question)}`,
    );
    bot.textContent = res?.data ?? "No answer returned.";
  } catch (err) {
    bot.textContent = `Retrieval failed — ${err.message}`;
    bot.classList.add("msg--error");
  } finally {
    busy = false;
    input.focus();
  }
}

function addMsg(kind, text) {
  const el = document.createElement("div");
  el.className = `msg msg--${kind}`;
  el.textContent = text;
  stream.append(el);
  stream.scrollTop = stream.scrollHeight;
  return el;
}
