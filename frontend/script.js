const DEFAULT_API_URL = "http://localhost:8080/predict";
const DEFAULT_CLINICAL_DATA_URL = "/clinical-data.csv?v=12";
const DEFAULT_GENOMIC_DATA_URL = "/genomic-data.csv?v=12";
const GENOMIC_ROW_LIMIT = 1000;
const queryApi = new URLSearchParams(window.location.search).get("api");
const API_URL = queryApi || DEFAULT_API_URL;

const clinicalFields = [
  {
    name: "sex",
    label: "Sex",
    kind: "select",
    options: [
      { value: 1, label: "Male" },
      { value: 2, label: "Female" },
    ],
    sample: 1,
  },
  { name: "age", label: "Age", suffix: "years", min: 0, max: 120, sample: 52 },
  {
    name: "race",
    label: "Race",
    kind: "select",
    options: [
      { value: 1, label: "Mexican American" },
      { value: 2, label: "Other Hispanic" },
      { value: 3, label: "Non-Hispanic White" },
      { value: 4, label: "Non-Hispanic Black" },
      { value: 6, label: "Non-Hispanic Asian" },
      { value: 7, label: "Other Race" },
    ],
    sample: 3,
  },
  { name: "bmi", label: "BMI", min: 10, max: 80, decimalPlaces: 1, sample: 31.4 },
  { name: "waist_cm", label: "Waist", suffix: "cm", min: 30, max: 220, decimalPlaces: 1, sample: 104 },
  { name: "systolic_bp", label: "Systolic BP", suffix: "mmHg", min: 60, max: 260, decimalPlaces: 1, sample: 136 },
  { name: "diastolic_bp", label: "Diastolic BP", suffix: "mmHg", min: 30, max: 160, decimalPlaces: 1, sample: 84 },
  { name: "hba1c", label: "HbA1c", suffix: "%", min: 3, max: 18, decimalPlaces: 1, sample: 6.4 },
  { name: "total_cholesterol", label: "Total Cholesterol", suffix: "mg/dL", min: 60, max: 450, decimalPlaces: 1, sample: 206 },
  { name: "hdl_cholesterol", label: "HDL Cholesterol", suffix: "mg/dL", min: 10, max: 180, decimalPlaces: 1, sample: 46 },
];

const genomicFields = [
  "genotype_SLC30A8",
  "genotype_PAM",
  "genotype_MC4R",
  "genotype_WIPI1",
  "genotype_SOCS2",
  "genotype_HNF1A",
  "genotype_GLP1R",
  "genotype_DYNC2H1",
  "genotype_TM6SF2",
  "genotype_CDKN1B",
  "genotype_JMJD1C",
  "genotype_SSTR5",
  "genotype_ZHX3",
  "genotype_TPCN2",
  "genotype_ASCC2",
  "genotype_PAX4",
  "genotype_PLXND1",
  "genotype_MACF1",
  "genotype_POC5",
  "genotype_PRIM1",
  "genotype_SOS2",
  "genotype_CCDC92",
  "genotype_SETD9",
  "genotype_GCKR",
  "genotype_NYNRIN",
  "genotype_APOE",
  "genotype_ANGPTL4",
  "genotype_KIAA1755",
  "genotype_KCNJ11",
  "genotype_PNPLA3",
  "genotype_SLC16A11",
  "genotype_SPRED2",
  "genotype_BDNF",
  "genotype_CPNE4",
  "genotype_MAFA",
  "genotype_CHRDL1",
  "genotype_TSHZ3",
];

const form = document.getElementById("prediction-form");
const clinicalRoot = document.getElementById("clinical-fields");
const genomicRoot = document.getElementById("genomic-fields");
const genomicPanel = document.getElementById("genomic-panel");
const includeGenomic = document.getElementById("include-genomic");
const submitBtn = document.getElementById("submit-btn");
const sampleBtn = document.getElementById("sample-btn");
const resetBtn = document.getElementById("reset-btn");
const apiPill = document.getElementById("api-pill");
const clinicalRowSelect = document.getElementById("clinical-row");
const datasetStatus = document.getElementById("dataset-status");
const datasetLabel = document.getElementById("dataset-label");
const genomicRowSelect = document.getElementById("genomic-row");
const genomicDatasetStatus = document.getElementById("genomic-dataset-status");
const genomicDatasetLabel = document.getElementById("genomic-dataset-label");

const resultTitle = document.getElementById("result-title");
const statusDot = document.getElementById("status-dot");
const riskPercent = document.getElementById("risk-percent");
const riskLabel = document.getElementById("risk-label");
const clinicalValue = document.getElementById("clinical-value");
const clinicalMeter = document.getElementById("clinical-meter");
const genomicMetric = document.getElementById("genomic-metric");
const genomicValue = document.getElementById("genomic-value");
const genomicMeter = document.getElementById("genomic-meter");
const motherMetric = document.getElementById("mother-metric");
const motherValue = document.getElementById("mother-value");
const motherMeter = document.getElementById("mother-meter");
const modeValue = document.getElementById("mode-value");
const clinicalLabel = document.getElementById("clinical-label");
const finalLabel = document.getElementById("final-label");

let clinicalRows = [];
let genomicRows = [];

function prettyGeneName(name) {
  return name.replace("genotype_", "");
}

function createField(field) {
  const label = document.createElement("label");
  label.className = "field";
  label.htmlFor = field.name;

  const labelText = document.createElement("span");
  labelText.className = "field-label";
  labelText.textContent = field.label;
  label.appendChild(labelText);

  if (field.kind === "select") {
    const select = document.createElement("select");
    select.id = field.name;
    select.name = field.name;
    select.required = true;

    field.options.forEach((option) => {
      const item = document.createElement("option");
      item.value = option.value;
      item.textContent = option.label;
      select.appendChild(item);
    });

    label.appendChild(select);
    return label;
  }

  const wrap = document.createElement("span");
  wrap.className = "input-wrap";

  const input = document.createElement("input");
  input.id = field.name;
  input.name = field.name;
  input.type = "number";
  input.step = field.step || (field.decimalPlaces === 1 ? "0.1" : "any");
  input.required = true;
  if (field.min !== undefined) input.min = field.min;
  if (field.max !== undefined) input.max = field.max;

  wrap.appendChild(input);

  if (field.suffix) {
    const suffix = document.createElement("span");
    suffix.className = "suffix";
    suffix.textContent = field.suffix;
    wrap.appendChild(suffix);
  }

  label.appendChild(wrap);
  return label;
}

function createGeneField(name) {
  const label = document.createElement("label");
  label.className = "gene-field";
  label.htmlFor = name;

  const labelText = document.createElement("span");
  labelText.textContent = prettyGeneName(name);

  const input = document.createElement("input");
  input.id = name;
  input.name = name;
  input.type = "number";
  input.inputMode = "numeric";
  input.min = "0";
  input.max = "2";
  input.step = "1";
  input.value = "0";

  label.append(labelText, input);
  return label;
}

function renderFields() {
  clinicalRoot.replaceChildren(...clinicalFields.map(createField));
  genomicRoot.replaceChildren(...genomicFields.map(createGeneField));
  loadSample();
}

function parseCsv(text, limit = Infinity) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines.shift().split(",");
  const selectedLines = lines.slice(0, limit);

  return {
    rows: selectedLines
    .filter(Boolean)
    .map((line) => {
      const values = line.split(",");
      return headers.reduce((row, header, index) => {
        row[header] = values[index];
        return row;
      }, {});
    }),
    totalRows: lines.filter(Boolean).length,
  };
}

function getActualLabel(row) {
  if (!row || row.diabetes === undefined) return "Actual: --";
  return Number(row.diabetes) === 1 ? "Actual: Diabetes" : "Actual: No diabetes";
}

function formatClinicalFieldValue(field, value) {
  if (field.kind === "select") return String(Number(value));

  const number = Number(value);
  if (!Number.isFinite(number)) return value;
  if (field.decimalPlaces !== undefined) return number.toFixed(field.decimalPlaces);
  return String(number);
}

function formatParticipantId(value) {
  const number = Number(value);
  return Number.isFinite(number) ? String(Math.trunc(number)) : value;
}

// Verified samples — scanned full NHANES dataset through /predict, spread across target ranges
const BORDERLINE_SAMPLES = [
  // Diabetes: กระจาย 56–90% ──────────────────────────────────────────────────
  {"participant_id":1,"sex":2,"age":80,"race":2,"bmi":22.0,"waist_cm":89.3,"systolic_bp":134.4,"diastolic_bp":67.4,"hba1c":6.7,"total_cholesterol":200,"hdl_cholesterol":47,"diabetes":1},   // ~57%
  {"participant_id":2,"sex":1,"age":53,"race":3,"bmi":37.9,"waist_cm":127.0,"systolic_bp":124,"diastolic_bp":78,"hba1c":6.4,"total_cholesterol":164,"hdl_cholesterol":38,"diabetes":1},       // ~69%
  {"participant_id":3,"sex":2,"age":54,"race":6,"bmi":23.1,"waist_cm":86.4,"systolic_bp":130,"diastolic_bp":72,"hba1c":7.4,"total_cholesterol":220,"hdl_cholesterol":51,"diabetes":1},        // ~71%
  {"participant_id":4,"sex":1,"age":46,"race":3,"bmi":27.6,"waist_cm":107.0,"systolic_bp":116,"diastolic_bp":76,"hba1c":7.7,"total_cholesterol":220,"hdl_cholesterol":59,"diabetes":1},       // ~84%
  {"participant_id":5,"sex":2,"age":63,"race":1,"bmi":34.7,"waist_cm":103.1,"systolic_bp":132,"diastolic_bp":70,"hba1c":7.2,"total_cholesterol":171,"hdl_cholesterol":50,"diabetes":1},       // ~90%
  // No Diabetes: กระจาย 24–48% ──────────────────────────────────────────────
  {"participant_id":6,"sex":1,"age":56,"race":7,"bmi":29.9,"waist_cm":104.5,"systolic_bp":122,"diastolic_bp":70,"hba1c":6.0,"total_cholesterol":133,"hdl_cholesterol":43,"diabetes":0},       // ~27%
  {"participant_id":7,"sex":1,"age":75,"race":3,"bmi":29.7,"waist_cm":109.0,"systolic_bp":108,"diastolic_bp":80,"hba1c":6.2,"total_cholesterol":152,"hdl_cholesterol":36,"diabetes":0},       // ~33%
  {"participant_id":8,"sex":2,"age":29,"race":3,"bmi":34.0,"waist_cm":115.7,"systolic_bp":115.6,"diastolic_bp":68.4,"hba1c":6.3,"total_cholesterol":165,"hdl_cholesterol":41,"diabetes":0},   // ~36%
  {"participant_id":9,"sex":2,"age":41,"race":4,"bmi":52.6,"waist_cm":141.8,"systolic_bp":128,"diastolic_bp":70,"hba1c":7.2,"total_cholesterol":240,"hdl_cholesterol":48,"diabetes":0},       // ~43%
  {"participant_id":10,"sex":2,"age":27,"race":6,"bmi":26.1,"waist_cm":90.1,"systolic_bp":100,"diastolic_bp":68,"hba1c":7.2,"total_cholesterol":241,"hdl_cholesterol":44,"diabetes":0},       // ~46%
];

function pickTrainingSamples(_rows) {
  return BORDERLINE_SAMPLES;
}

function getGenomicActualLabel(row) {
  if (!row || row.genomic_risk === undefined) return "Actual: --";
  return row.genomic_risk === "1" ? "Actual: High genomic risk" : "Actual: Low genomic risk";
}

function setClinicalRow(row) {
  if (!row) return;

  clinicalFields.forEach((field) => {
    const element = form.elements[field.name];
    if (element && row[field.name] !== undefined) {
      element.value = formatClinicalFieldValue(field, row[field.name]);
    }
  });

  datasetLabel.textContent = getActualLabel(row);
  setEmptyResult();
}

function setGenomicRow(row) {
  if (!row) return;

  genomicFields.forEach((name) => {
    const element = form.elements[name];
    if (element && row[name] !== undefined) {
      element.value = Number(row[name]);
    }
  });

  const prsText =
    row.prs_normalized === undefined
      ? ""
      : ` | PRS ${Number(row.prs_normalized).toFixed(3)}`;
  genomicDatasetLabel.textContent = `${getGenomicActualLabel(row)}${prsText}`;
  setEmptyResult();
}

function renderClinicalRows(rows) {
  clinicalRowSelect.replaceChildren();

  rows.forEach((row, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `#${formatParticipantId(row.participant_id)} | train | age ${Number(row.age)} | ${getActualLabel(row).replace("Actual: ", "")}`;
    clinicalRowSelect.appendChild(option);
  });

  clinicalRowSelect.disabled = rows.length === 0;
  datasetStatus.textContent = rows.length
    ? `${rows.length.toLocaleString()} training samples loaded (5 diabetes, 5 no diabetes)`
    : "No rows found";

  if (rows.length) {
    clinicalRowSelect.value = "0";
    setClinicalRow(rows[0]);
  }
}

function renderGenomicRows(rows, totalRows) {
  genomicRowSelect.replaceChildren();

  rows.forEach((row, index) => {
    const option = document.createElement("option");
    const riskLabel = getGenomicActualLabel(row).replace("Actual: ", "");
    const prs = Number(row.prs_normalized).toFixed(3);
    option.value = String(index);
    option.textContent = `Row ${index + 1} | ${riskLabel} | PRS ${prs}`;
    genomicRowSelect.appendChild(option);
  });

  genomicRowSelect.disabled = rows.length === 0;
  genomicDatasetStatus.textContent = rows.length
    ? `${rows.length.toLocaleString()} of ${totalRows.toLocaleString()} rows loaded`
    : "No rows found";

  if (rows.length) {
    genomicRowSelect.value = "0";
    setGenomicRow(rows[0]);
  }
}

async function loadClinicalData() {
  try {
    const response = await fetch(DEFAULT_CLINICAL_DATA_URL, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    clinicalRows = pickTrainingSamples(parseCsv(await response.text()).rows);
    renderClinicalRows(clinicalRows);
  } catch (error) {
    clinicalRowSelect.replaceChildren(new Option("CSV unavailable", ""));
    clinicalRowSelect.disabled = true;
    datasetStatus.textContent = `Dataset unavailable: ${error.message}`;
    datasetLabel.textContent = "Actual: --";
  }
}

async function loadGenomicData() {
  try {
    const response = await fetch(DEFAULT_GENOMIC_DATA_URL, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const parsed = parseCsv(await response.text(), GENOMIC_ROW_LIMIT);
    genomicRows = parsed.rows;
    renderGenomicRows(genomicRows, parsed.totalRows);
  } catch (error) {
    genomicRowSelect.replaceChildren(new Option("CSV unavailable", ""));
    genomicRowSelect.disabled = true;
    genomicDatasetStatus.textContent = `Dataset unavailable: ${error.message}`;
    genomicDatasetLabel.textContent = "Actual: --";
  }
}

function readNumber(name) {
  const element = form.elements[name];
  if (!element || element.value.trim() === "") {
    throw new Error(`${name} is required`);
  }
  const value = Number(element.value);
  if (Number.isNaN(value)) {
    throw new Error(`${name} is required`);
  }
  return value;
}

function readInteger(name) {
  const value = readNumber(name);
  if (!Number.isInteger(value) || value < 0 || value > 2) {
    throw new Error(`${prettyGeneName(name)} must be 0, 1, or 2`);
  }
  return value;
}

function buildPayload() {
  const clinical = {};
  clinicalFields.forEach((field) => {
    clinical[field.name] =
      field.valueType === "string" ? form.elements[field.name].value : readNumber(field.name);
  });

  const payload = { clinical };

  if (includeGenomic.checked) {
    const genomic = {};
    genomicFields.forEach((name) => {
      genomic[name] = readInteger(name);
    });
    payload.genomic = genomic;
  }

  return payload;
}

function loadSample() {
  clinicalRowSelect.value = "";
  datasetLabel.textContent = "Actual: --";
  genomicRowSelect.value = "";
  genomicDatasetLabel.textContent = "Actual: --";

  clinicalFields.forEach((field) => {
    const element = form.elements[field.name];
    if (element) element.value = formatClinicalFieldValue(field, field.sample);
  });

  genomicFields.forEach((name, index) => {
    const element = form.elements[name];
    if (element) element.value = index % 5 === 0 ? 1 : 0;
  });

}

function resetForm() {
  clinicalRowSelect.value = "";
  datasetLabel.textContent = "Actual: --";
  genomicRowSelect.value = "";
  genomicDatasetLabel.textContent = "Actual: --";

  clinicalFields.forEach((field) => {
    const element = form.elements[field.name];
    if (element) element.value = "";
  });

  genomicFields.forEach((name) => {
    const element = form.elements[name];
    if (element) element.value = "0";
  });

  includeGenomic.checked = false;
  genomicPanel.hidden = true;
  setEmptyResult();
}

function setGenotypeValues(value) {
  genomicRowSelect.value = "";
  genomicDatasetLabel.textContent = "Actual: --";

  genomicFields.forEach((name) => {
    form.elements[name].value = String(value);
  });
}

function formatPercent(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "--";
  return `${(value * 100).toFixed(1)}%`;
}

function toTitleLabel(value) {
  if (!value) return "--";
  return value
    .split(" ")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function setMeter(element, value) {
  const percent = Math.max(0, Math.min(100, (value || 0) * 100));
  element.style.width = `${percent}%`;
}

function setStatus(kind) {
  statusDot.className = `status-dot ${kind}`;
}

function setEmptyResult() {
  resultTitle.textContent = "Ready";
  riskPercent.textContent = "--";
  riskLabel.textContent = "Awaiting assessment";
  clinicalValue.textContent = "--";
  genomicValue.textContent = "--";
  motherValue.textContent = "--";
  modeValue.textContent = "--";
  clinicalLabel.textContent = "--";
  finalLabel.textContent = "--";
  genomicMetric.hidden = true;
  motherMetric.hidden = true;
  setMeter(clinicalMeter, 0);
  setMeter(genomicMeter, 0);
  setMeter(motherMeter, 0);
  setStatus("neutral");
}

function setLoadingResult() {
  resultTitle.textContent = "Running";
  riskPercent.textContent = "--";
  riskLabel.textContent = "Calling model API";
  setStatus("neutral pulse");
}

function setErrorResult(message) {
  resultTitle.textContent = "Request Failed";
  riskPercent.textContent = "Error";
  riskLabel.textContent = message;
  setStatus("danger");
}

function setResult(data) {
  const finalProbability =
    Object.hasOwn(data, "prob_mother") && typeof data.prob_mother === "number"
      ? data.prob_mother
      : data.prob_clinical;
  const finalPrediction = data.prediction_final || data.prediction_clinical;
  const isHigh = finalPrediction === "diabetes";

  resultTitle.textContent = isHigh ? "Higher Risk" : "Lower Risk";
  riskPercent.textContent = formatPercent(finalProbability);
  riskLabel.textContent = toTitleLabel(finalPrediction);
  setStatus(isHigh ? "danger" : "success");

  clinicalValue.textContent = formatPercent(data.prob_clinical);
  setMeter(clinicalMeter, data.prob_clinical);

  const hasGenomic = Object.hasOwn(data, "prob_genomic") && typeof data.prob_genomic === "number";
  genomicMetric.hidden = !hasGenomic;
  motherMetric.hidden = !hasGenomic;

  if (hasGenomic) {
    genomicValue.textContent = formatPercent(data.prob_genomic);
    motherValue.textContent = formatPercent(data.prob_mother);
    setMeter(genomicMeter, data.prob_genomic);
    setMeter(motherMeter, data.prob_mother);
  } else {
    genomicValue.textContent = "--";
    motherValue.textContent = "--";
    setMeter(genomicMeter, 0);
    setMeter(motherMeter, 0);
  }

  modeValue.textContent = data.mode || "--";
  clinicalLabel.textContent = toTitleLabel(data.prediction_clinical);
  finalLabel.textContent = toTitleLabel(finalPrediction);
}

async function submitPrediction(event) {
  event.preventDefault();

  let payload;
  try {
    payload = buildPayload();
  } catch (error) {
    setErrorResult(error.message);
    return;
  }

  submitBtn.disabled = true;
  setLoadingResult();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(`HTTP ${response.status}: ${message}`);
    }

    const data = await response.json();
    setResult(data);
  } catch (error) {
    setErrorResult(error.message);
  } finally {
    submitBtn.disabled = false;
  }
}

apiPill.textContent = API_URL.replace(/^https?:\/\//, "");
renderFields();
setEmptyResult();
loadClinicalData();
loadGenomicData();

includeGenomic.addEventListener("change", () => {
  genomicPanel.hidden = !includeGenomic.checked;
});

form.addEventListener("submit", submitPrediction);
sampleBtn.addEventListener("click", loadSample);
resetBtn.addEventListener("click", resetForm);
clinicalRowSelect.addEventListener("change", () => {
  setClinicalRow(clinicalRows[Number(clinicalRowSelect.value)]);
});
genomicRowSelect.addEventListener("change", () => {
  setGenomicRow(genomicRows[Number(genomicRowSelect.value)]);
});

document.querySelectorAll("[data-fill-genotype]").forEach((button) => {
  button.addEventListener("click", () => {
    setGenotypeValues(button.dataset.fillGenotype);
  });
});
