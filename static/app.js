// Загрузка файла с диска в текстовое поле
document.getElementById("file").addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => { document.getElementById("network").value = reader.result; };
  reader.readAsText(file);
});

document.getElementById("run").addEventListener("click", calculate);

function showError(text) {
  document.getElementById("error").textContent = text;
}

async function calculate() {
  showError("");
  let data;
  try {
    data = JSON.parse(document.getElementById("network").value);
  } catch {
    showError("Некорректный JSON");
    return;
  }

  // Значение поля: document.getElementById("...").value  (это строка!)
  // Превратить строку в число: Number(...)
  data.t_max = Number(document.getElementById("t_max").value);
  data.cap = Number(document.getElementById("cap").value);


  const resp = await fetch("/gm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const body = await resp.json();

  if (!resp.ok) {
    showError(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail));
    return;
  }

  drawGraph(data, body);
  fillTable(body);
}

function fillTable(body) {
  const tbody = document.getElementById("assign");
  tbody.innerHTML = "";

  for (const [site, a] of Object.entries(body.assignment)) {
    tbody.innerHTML += `<tr><td>${site}</td><td>${a.primary}</td><td>${a.backup}</td></tr>`;

  }

  const loads = Object.entries(body.load)
    .map(([gm, n]) => `GM ${gm}: ${n} БС`)
    .join(" · ");
  document.getElementById("loads").textContent = loads;
}

function drawGraph(data, body) {
  const gms = new Set(body.gms);
  const nodes = data.sites.map((s) => ({
    id: s.id,
    label: `${s.id}\n${s.bs} БС`,
    shape: "box",
    color: gms.has(s.id) ? "#FFD34D" : "#7fd6e0",
  }));
  const edges = data.links.map((l) => ({
    from: l.u,
    to: l.v,
    dashes: l.kind === "rrl",
    color: l.kind === "rrl" ? "#e07b00" : "#1f5fbf",
    width: 2,
  }));
  new vis.Network(
    document.getElementById("graph"),
    { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) },
    { physics: { stabilization: true } }
  );
}