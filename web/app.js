const $ = (id) => document.getElementById(id);

const apiBase = $("apiBase");
const fileInput = $("fileInput");
const previewImg = $("previewImg");
const fileName = $("fileName");

const statusPredict = $("statusPredict");
const predClass = $("predClass");
const predConf = $("predConf");

const total = $("total");
const fresh = $("fresh");
const dry = $("dry");

const statusReport = $("statusReport");
const reportBox = $("reportBox");

let lastPrediction = null;

function setStatus(el, msg) {
  el.textContent = msg;
}

function resetPredictionUI() {
  setStatus(statusPredict, "En attente…");
  predClass.textContent = "—";
  predConf.textContent = "—";
  lastPrediction = null;
}

function resetReportUI() {
  setStatus(statusReport, "En attente…");
  reportBox.value = "";
}

fileInput.addEventListener("change", () => {
  resetPredictionUI();
  const file = fileInput.files?.[0];
  if (!file) return;

  fileName.textContent = file.name;

  const url = URL.createObjectURL(file);
  previewImg.src = url;
  previewImg.style.display = "block";
});

$("btnClear").addEventListener("click", () => {
  fileInput.value = "";
  previewImg.src = "";
  previewImg.style.display = "none";
  fileName.textContent = "";
  resetPredictionUI();
  resetReportUI();
});

$("btnPredict").addEventListener("click", async () => {
  const base = apiBase.value.trim().replace(/\/$/, "");
  const file = fileInput.files?.[0];

  if (!base) return setStatus(statusPredict, "❌ Adresse API vide.");
  if (!file) return setStatus(statusPredict, "❌ Choisis une image d’abord.");

  setStatus(statusPredict, "⏳ Upload + prediction en cours…");

  try {
    const formData = new FormData();
    formData.append("file", file);

    // endpoint de ton API
    const url = `${base}/upload_and_predict/`;

    const res = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`HTTP ${res.status} — ${txt}`);
    }

    const data = await res.json();
    // attendu: { predicted_class: "...", confidence: ... }
    lastPrediction = data;

    predClass.textContent = data.predicted_class ?? "—";
    predConf.textContent = (data.confidence !== undefined)
      ? `${Number(data.confidence).toFixed(2)} %`
      : "—";

    setStatus(statusPredict, "✅ Prediction OK.");
  } catch (err) {
    console.error(err);
    setStatus(statusPredict, `❌ Erreur: ${err.message}`);
  }
});

$("btnFillFromLast").addEventListener("click", () => {
  if (!lastPrediction?.predicted_class) {
    return setStatus(statusReport, "❌ Fais une prédiction d’abord.");
  }

  // On remplit comme un lot de 1 image
  total.value = "1";

  if (lastPrediction.predicted_class === "Fresh") {
    fresh.value = "1";
    dry.value = "0";
  } else if (lastPrediction.predicted_class === "Dry") {
    fresh.value = "0";
    dry.value = "1";
  } else {
    // si autre label
    fresh.value = "0";
    dry.value = "0";
  }

  setStatus(statusReport, "✅ Stats remplies avec la dernière prédiction (lot=1).");
});

$("btnReport").addEventListener("click", async () => {
  const base = apiBase.value.trim().replace(/\/$/, "");
  if (!base) return setStatus(statusReport, "❌ Adresse API vide.");

  const payload = {
    total: Number(total.value || 0),
    fresh: Number(fresh.value || 0),
    dry: Number(dry.value || 0),
  };

  if (payload.total <= 0) return setStatus(statusReport, "❌ Total doit être > 0.");
  if (payload.fresh < 0 || payload.dry < 0) return setStatus(statusReport, "❌ Fresh/Dry doivent être >= 0.");

  setStatus(statusReport, "⏳ Génération du rapport Gemini…");
  reportBox.value = "";

  try {
    const url = `${base}/generate_report/`;

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`HTTP ${res.status} — ${txt}`);
    }

    const data = await res.json();
    reportBox.value = data.report_md ?? "(vide)";

    setStatus(statusReport, "✅ Rapport généré.");
  } catch (err) {
    console.error(err);
    setStatus(statusReport, `❌ Erreur: ${err.message}`);
  }
});
