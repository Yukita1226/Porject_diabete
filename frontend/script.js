// these must match the Go json tags exactly
const CLINICAL = ["age", "bmi", "tc", "tg", "hdl", "ldl"];
const GENOMIC  = ["kcnj11", "tcf7l2", "slc30a8", "igf2bp2",
                  "hhex", "cdkn2a", "kcnq1", "cdkal1", "fto"];

const sentEl = document.getElementById("sent");
const gotEl  = document.getElementById("got");

function collect(keys) {
  const o = {};
  for (const k of keys) {
    // Number() matters: the backend does not validate, a string binds to 0
    o[k] = Number(document.getElementById(k).value);
  }
  return o;
}

async function post(path, body) {
  sentEl.textContent = JSON.stringify(body, null, 2);
  gotEl.textContent = "waiting...";
  gotEl.className = "";

  try {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const text = await res.text();
    gotEl.textContent = res.status + "\n" + text;
    if (!res.ok) gotEl.className = "bad";
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

fetch("/health")
  .then(r => r.json())
  .then(d => { document.getElementById("health").textContent = "python: " + d.python; })
  .catch(e => { document.getElementById("health").textContent = "python: " + e; });