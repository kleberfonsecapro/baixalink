let token = null;
const API_BASE = "/api";

const loginCard = document.getElementById("loginCard");
const downloadCard = document.getElementById("downloadCard");
const loginBtn = document.getElementById("loginBtn");
const loginError = document.getElementById("loginError");
const downloadBtn = document.getElementById("downloadBtn");
const resultDiv = document.getElementById("result");

const installBtn = document.getElementById("installBtn");

loginBtn.addEventListener("click", login);

function showError(el, msg) {
  el.textContent = msg;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 4000);
}

async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  if (!username || !password) {
    showError(loginError, "Preencha usuário e senha");
    return;
  }

  loginBtn.disabled = true;
  loginBtn.textContent = "Entrando...";

  try {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);

    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Erro no login");
    }

    const data = await res.json();
    token = data.access_token;
    loginCard.classList.add("hidden");
    downloadCard.classList.remove("hidden");
  } catch (e) {
    showError(loginError, e.message);
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = "Entrar";
  }
}

downloadBtn.addEventListener("click", () => {
  const url = document.getElementById("url").value.trim();
  const tipo = document.getElementById("tipo").value;

  if (!url) {
    resultDiv.innerHTML = '<p class="error">Insira uma URL</p>';
    resultDiv.classList.remove("hidden");
    return;
  }

  resultDiv.classList.add("hidden");

  const params = new URLSearchParams({ url, tipo, token });
  const dlUrl = `${API_BASE}/dl?${params}`;

  const a = document.createElement("a");
  a.href = dlUrl;
  a.download = "";
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
});

async function checkInstalled() {
  try {
    const apps = await navigator.getInstalledRelatedApps?.();
    return apps?.some(a => a.id === "baixelink" || a.platform === "webapp");
  } catch { return false; }
}

async function initInstall() {
  if (window.matchMedia("(display-mode: standalone)").matches) {
    installBtn.remove();
    return;
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("service-worker.js").catch(() => {});
  }

  const alreadyInstalled = await checkInstalled();
  if (alreadyInstalled) {
    installBtn.textContent = "✅ App instalado • Abrir";
    installBtn.addEventListener("click", () => {
      window.open(window.location.origin, "_blank");
    });
    return;
  }

  installBtn.addEventListener("click", async () => {
    const prompt = window.__deferredPrompt;
    if (prompt) {
      try {
        prompt.prompt();
        const { outcome } = await prompt.userChoice;
        if (outcome === "accepted") {
          installBtn.remove();
          return;
        }
      } catch {}
      window.__deferredPrompt = null;
    }

    const installed = await checkInstalled();
    if (installed) {
      installBtn.textContent = "✅ App instalado • Abrir";
      window.open(window.location.origin, "_blank");
      return;
    }

    if (navigator.install) {
      try {
        await navigator.install();
        installBtn.remove();
        return;
      } catch {}
    }

    installBtn.textContent = "Use o menu ⋮ > Instalar";
    setTimeout(() => {
      installBtn.textContent = "📲 Adicionar à tela inicial";
    }, 4000);
  });
}

initInstall();
