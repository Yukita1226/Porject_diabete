const API_URL = "http://localhost:8080/predict";

const form    = document.getElementById("predict-form");
const input1  = document.getElementById("input1");
const input2  = document.getElementById("input2");
const sendBtn = document.getElementById("send-btn");
const output  = document.getElementById("output");

function setOutput(text, kind) {
  output.textContent = text;
  output.classList.remove("success", "error");
  if (kind) output.classList.add(kind);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const x = parseFloat(input1.value);
  const y = parseFloat(input2.value);

  if (Number.isNaN(x) || Number.isNaN(y)) {
    setOutput("Please enter valid numbers in both fields.", "error");
    return;
  }

  sendBtn.disabled = true;
  setOutput("Sending request...");

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input1: x, input2: y }),
    });

    if (!res.ok) {
      const text = await res.text();
      setOutput(`HTTP ${res.status}: ${text}`, "error");
      return;
    }

    const data = await res.json();
    const lines = [
      `input1 : ${data.input1}`,
      `input2 : ${data.input2}`,
      `output : ${data.output}`,
    ];
    setOutput(lines.join("\n"), "success");
  } catch (err) {
    setOutput(`Network error: ${err.message}`, "error");
  } finally {
    sendBtn.disabled = false;
  }
});