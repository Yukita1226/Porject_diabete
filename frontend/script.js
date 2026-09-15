// these must match the Go json tags exactly
const CLINICAL = ["age", "bmi", "tc", "tg", "hdl", "ldl"];
const GENOMIC  = ["kcnj11", "tcf7l2", "slc30a8", "igf2bp2",
                  "hhex", "cdkn2a", "kcnq1", "cdkal1", "fto"];

const sentEl   = document.getElementById("sent");
const gotEl    = document.getElementById("got");
const healthEl = document.getElementById("health");
const cardsEl  = document.getElementById("result-cards");

const PROB_LABELS = {
  clinical_prob: "Clinical risk",
  genomic_prob: "Genomic risk",
  fused_prob: "Fused risk",
};

function collect(keys) {
  const o = {};
  for (const k of keys) {
    // Number() matters: the backend does not validate, a string binds to 0
    o[k] = Number(document.getElementById(k).value);
  }
  return o;
}

function riskClass(p) {
  if (p >= 0.66) return "risk-high";
  if (p >= 0.33) return "risk-mid";
  return "risk-low";
}

function renderResultCards(json) {
  cardsEl.innerHTML = "";
  const probs = Object.entries(PROB_LABELS).filter(([key]) => typeof json[key] === "number");
  if (probs.length === 0) {
    cardsEl.hidden = true;
    return;
  }
  for (const [key, label] of probs) {
    const p = json[key];
    const pct = Math.round(p * 1000) / 10;
    const card = document.createElement("div");
    card.className = "result-card " + riskClass(p);
    card.innerHTML = `
      <div class="label">${label}</div>
      <div class="value">${pct}%</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
    `;
    cardsEl.appendChild(card);
  }
  cardsEl.hidden = false;
}

async function post(path, body) {
  sentEl.textContent = JSON.stringify(body, null, 2);
  gotEl.textContent = "waiting...";
  gotEl.className = "";
  cardsEl.hidden = true;

  try {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const text = await res.text();
    gotEl.textContent = res.status + "\n" + text;
    gotEl.className = res.ok ? "" : "bad";
    if (res.ok) {
      try { renderResultCards(JSON.parse(text)); } catch { /* not JSON, ignore */ }
    }
  } catch (e) {
    gotEl.textContent = String(e);
    gotEl.className = "bad";
  }
}

document.getElementById("btn-both").onclick = () =>
  post("/predict", { clinical: collect(CLINICAL), genomic: collect(GENOMIC) });

document.getElementById("btn-clinical").onclick = () =>
  post("/predict/clinical", collect(CLINICAL));

document.getElementById("btn-genomic").onclick = () =>
  post("/predict/genomic", collect(GENOMIC));

function setHealth(cls, text) {
  healthEl.className = "health-pill " + cls;
  healthEl.querySelector(".health-label").textContent = text;
}

fetch("/health")
  .then(r => r.json())
  .then(d => setHealth(d.python === "ok" ? "health-ok" : "health-bad", "python: " + d.python))
  .catch(e => setHealth("health-bad", "python: " + e));
