const listElement = document.getElementById("occurrences-list");
const form = document.getElementById("occurrence-form");
const message = document.getElementById("form-message");

function safeText(value) {
  return String(value ?? "");
}

function createOccurrenceCard(item) {
  const card = document.createElement("article");
  card.className = "occurrence";

  const top = document.createElement("div");
  top.className = "occurrence-top";
  const heading = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = safeText(item.location);
  const description = document.createElement("p");
  description.textContent = safeText(item.description);
  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = `#${item.id} · ${safeText(item.status)} · ${safeText(item.created_at)}`;
  heading.append(title, description, meta);

  const severity = document.createElement("span");
  severity.className = `pill ${item.severity}`;
  severity.textContent = safeText(item.severity);
  top.append(heading, severity);
  card.append(top);

  const actions = document.createElement("div");
  actions.className = "occurrence-actions";

  const editButton = document.createElement("button");
  editButton.textContent = "Atualizar status";
  editButton.addEventListener("click", () => updateStatus(item));

  const deleteButton = document.createElement("button");
  deleteButton.textContent = "Excluir";
  deleteButton.addEventListener("click", () => removeOccurrence(item.id));

  actions.append(editButton, deleteButton);
  card.append(actions);
  return card;
}

async function loadOccurrences() {
  listElement.replaceChildren();
  try {
    const response = await fetch("/api/ocorrencias");
    if (!response.ok) throw new Error("Falha na consulta");
    const items = await response.json();
    if (items.length === 0) {
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent = "Ainda não há relatos. Seja o primeiro a contribuir.";
      listElement.append(empty);
    } else {
      items.forEach(item => listElement.append(createOccurrenceCard(item)));
    }
    document.getElementById("total-count").textContent = items.length;
    document.getElementById("open-count").textContent = items.filter(x => x.status !== "resolvida").length;
    document.getElementById("high-count").textContent = items.filter(x => x.severity === "alta" && x.status !== "resolvida").length;
  } catch (_error) {
    const error = document.createElement("p");
    error.className = "muted";
    error.textContent = "Não foi possível carregar os relatos. Verifique a conexão com a API e o banco.";
    listElement.append(error);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  const payload = {
    location: form.location.value.trim(),
    description: form.description.value.trim(),
    severity: form.severity.value
  };
  try {
    const response = await fetch("/api/ocorrencias", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.erro || "Não foi possível cadastrar.");
    form.reset();
    message.textContent = "Ocorrência registrada com sucesso.";
    await loadOccurrences();
  } catch (error) {
    message.textContent = error.message;
  }
});

async function updateStatus(item) {
  const nextStatus = item.status === "aberta" ? "em_verificacao" :
    item.status === "em_verificacao" ? "resolvida" : "aberta";
  try {
    const response = await fetch(`/api/ocorrencias/${item.id}`, {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({status: nextStatus})
    });
    if (!response.ok) throw new Error("Não foi possível atualizar.");
    await loadOccurrences();
  } catch (error) {
    window.alert(error.message);
  }
}

async function removeOccurrence(id) {
  if (!window.confirm("Deseja realmente excluir esta ocorrência?")) return;
  try {
    const response = await fetch(`/api/ocorrencias/${id}`, {method: "DELETE"});
    if (!response.ok) throw new Error("Não foi possível excluir.");
    await loadOccurrences();
  } catch (error) {
    window.alert(error.message);
  }
}

async function loadWeather() {
  const value = document.getElementById("weather-value");
  const detail = document.getElementById("weather-detail");
  try {
    const response = await fetch("/api/clima?latitude=-23.5505&longitude=-46.6333");
    if (!response.ok) throw new Error("Clima indisponível");
    const weather = await response.json();
    value.textContent = `${weather.temperatura_c} °C`;
    detail.textContent = `Chuva: ${weather.precipitacao_mm} mm · ${weather.horario}`;
  } catch (_error) {
    value.textContent = "Indisponível";
    detail.textContent = "Não foi possível consultar o serviço climático.";
  }
}

document.getElementById("refresh-button").addEventListener("click", loadOccurrences);
loadOccurrences();
loadWeather();
