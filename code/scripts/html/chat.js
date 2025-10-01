const LAT = 4.7110, LON = -74.0721; // Bogotá default

function appendMessage(who, text) {
  const box = document.getElementById("messages");
  const el = document.createElement("div");
  el.className = "msg " + (who === "user" ? "user" : "bot");
  el.innerText = text;
  box.appendChild(el);
  box.scrollTop = box.scrollHeight;
}

async function getPrediction() {
  appendMessage("user", "Dame la predicción para Bogotá (24h)");
  const res = await fetch("/api/predict", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({lat: LAT, lon: LON, hours: 24})
  });
  const data = await res.json();
  const s = `Predicción PM2.5: ${data.pm25} µg/m³ — Índice: ${data.aq_index} — Confianza: ${data.confidence}\n${data.explanation}`;
  appendMessage("bot", s);
  document.getElementById("status").innerText = "Última actualización: " + new Date().toLocaleString();
  document.getElementById("pred").innerText = `PM2.5 ${data.pm25} µg/m³ — AQ index ${data.aq_index}`;
  return data;
}

async function askAdvice(pm25) {
  const res = await fetch("/api/advice", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({pm25})
  });
  const data = await res.json();
  appendMessage("bot", data.advice.join("\n"));
}

document.getElementById("send").addEventListener("click", async () => {
  const text = document.getElementById("user-input").value.trim();
  if (!text) return;
  appendMessage("user", text);
  document.getElementById("user-input").value = "";
  // very naive NLP: if user asks "predic" or "ahora" we call predict
  if (/predic|predec|cómo estará|calidad/i.test(text)) {
    const p = await getPrediction();
    await askAdvice(p.pm25);
  } else if (/consej|mascarill|salir|ejercicio/i.test(text)) {
    // consult current prediction then advice
    const p = await getPrediction();
    await askAdvice(p.pm25);
  } else {
    appendMessage("bot", "Puedo predecir la calidad del aire y dar consejos. Pregunta '¿Cómo estará hoy?' o '¿Debo salir?'");
  }
});

// auto run once on load
window.onload = () => { getPrediction().then(d => askAdvice(d.pm25)); };
