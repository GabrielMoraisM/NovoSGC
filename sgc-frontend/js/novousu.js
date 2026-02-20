// ===== helpers =====
function initialsFromName(name){
  const parts = (name || "").trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "NU";
  const first = parts[0][0] || "";
  const last = (parts.length > 1 ? parts[parts.length - 1][0] : "") || "";
  return (first + last).toUpperCase();
}

function setBadge(el, text, kind){
  if (!el) return;
  el.textContent = text;
  el.classList.remove("badge-primary","badge-secondary","badge-success","badge-warning","badge-danger");
  el.classList.add(kind);
}

const permsByRole = {
  admin: [
    "Acesso total ao sistema",
    "Gerenciar usuários e permissões",
    "Criar/editar empresas, contratos e medições",
    "Ver e editar financeiro e relatórios",
  ],
  engenheiro: [
    "Criar/editar medições",
    "Acessar contratos vinculados",
    "Acessar empresas",
    "Sem acesso a parâmetros financeiros globais",
  ],
  financeiro: [
    "Acessar e editar financeiro",
    "Visualizar contratos e medições",
    "Exportar dados",
    "Sem gerenciar usuários",
  ],
  gestor: [
    "Visualizar tudo da unidade",
    "Aprovar medições (se habilitado)",
    "Criar contratos (se permitido)",
  ],
  leitura: [
    "Somente leitura (sem edição)",
    "Acesso a relatórios básicos",
  ],
};

function renderPerms(role){
  const list = document.getElementById("permList");
  if (!list) return;

  const items = permsByRole[role];
  if (!items) {
    list.innerHTML = `<li>Selecione um perfil para ver as permissões.</li>`;
    return;
  }
  list.innerHTML = items.map(t => `<li>${t}</li>`).join("");
}

// ===== elementos =====
const form = document.getElementById("newUserForm");
const nameEl = document.getElementById("name");
const emailEl = document.getElementById("email");
const statusEl = document.getElementById("status");
const roleEl = document.getElementById("role");
const orgEl = document.getElementById("org");

const avatarPreview = document.getElementById("avatarPreview");
const namePreview = document.getElementById("namePreview");
const emailPreview = document.getElementById("emailPreview");
const roleBadge = document.getElementById("roleBadge");
const statusBadge = document.getElementById("statusBadge");
const orgPreview = document.getElementById("orgPreview");

const passEl = document.getElementById("password");
const confirmEl = document.getElementById("confirmPassword");
const passHint = document.getElementById("passHint");
const togglePassBtn = document.getElementById("togglePass");

const toast = document.getElementById("toast");

// ===== preview live =====
function syncPreview(){
  const name = nameEl?.value || "";
  const email = emailEl?.value || "";

  if (avatarPreview) avatarPreview.textContent = initialsFromName(name);
  if (namePreview) namePreview.textContent = name.trim() || "Novo Usuário";
  if (emailPreview) emailPreview.textContent = email.trim() || "email@exemplo.com";

  // status
  const status = statusEl?.value || "ativo";
  if (status === "ativo") setBadge(statusBadge, "Ativo", "badge-success");
  else setBadge(statusBadge, "Bloqueado", "badge-danger");

  // org
  const orgText = orgEl?.selectedOptions?.[0]?.textContent || "—";
  if (orgPreview) orgPreview.textContent = orgText;

  // role
  const role = roleEl?.value || "";
  const roleText = roleEl?.selectedOptions?.[0]?.textContent || "—";
  if (!role) setBadge(roleBadge, "—", "badge-secondary");
  else {
    const kind =
      role === "admin" ? "badge-primary" :
      role === "financeiro" ? "badge-warning" :
      "badge-secondary";
    setBadge(roleBadge, roleText, kind);
  }

  renderPerms(role);
}

["input","change"].forEach(evt => {
  nameEl?.addEventListener(evt, syncPreview);
  emailEl?.addEventListener(evt, syncPreview);
  statusEl?.addEventListener(evt, syncPreview);
  roleEl?.addEventListener(evt, syncPreview);
  orgEl?.addEventListener(evt, syncPreview);
});

// senha: feedback simples
function checkPasswords(){
  if (!passEl || !confirmEl || !passHint) return;

  const p1 = passEl.value || "";
  const p2 = confirmEl.value || "";
  if (!p1 && !p2) { passHint.textContent = ""; return; }

  if (p1.length < 8) {
    passHint.textContent = "Senha muito curta (mínimo 8).";
    passHint.style.color = "#991b1b";
    return;
  }

  if (p2 && p1 !== p2) {
    passHint.textContent = "As senhas não coincidem.";
    passHint.style.color = "#991b1b";
    return;
  }

  if (p2 && p1 === p2) {
    passHint.textContent = "Senhas conferem.";
    passHint.style.color = "#166534";
  } else {
    passHint.textContent = "";
  }
}

passEl?.addEventListener("input", checkPasswords);
confirmEl?.addEventListener("input", checkPasswords);

// mostrar/ocultar senha
togglePassBtn?.addEventListener("click", () => {
  if (!passEl) return;
  const isPass = passEl.type === "password";
  passEl.type = isPass ? "text" : "password";
  togglePassBtn.textContent = isPass ? "Ocultar" : "Mostrar";
});

// submit demo
form?.addEventListener("submit", (e) => {
  e.preventDefault();

  const name = (nameEl?.value || "").trim();
  const email = (emailEl?.value || "").trim();
  const role = roleEl?.value || "";
  const p1 = passEl?.value || "";
  const p2 = confirmEl?.value || "";

  toast.className = "nu-toast";
  toast.textContent = "";

  if (!name || !email || !role || p1.length < 8 || p1 !== p2) {
    toast.classList.add("err");
    toast.textContent = "Revise os campos obrigatórios (nome, e-mail, perfil e senha).";
    return;
  }

  // aqui você trocaria por fetch() pra sua API
  toast.classList.add("ok");
  toast.textContent = "Usuário criado (demo). Agora é só integrar com o backend.";
});

// ===== Theme toggle (igual ao seu) =====
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');

function setTheme(isDark){
  document.body.classList.toggle('dark', isDark);
  localStorage.setItem('sgc_theme', isDark ? 'dark' : 'light');
  if (themeIcon) themeIcon.textContent = isDark ? "☀️" : "🌙";
}

const saved = localStorage.getItem('sgc_theme');
setTheme(saved === 'dark');

themeToggle?.addEventListener('click', () => {
  setTheme(!document.body.classList.contains('dark'));
});

// ===== Mobile menu + dropdown (mesma pegada do seu) =====
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
sidebarToggle?.addEventListener('click', () => sidebar.classList.toggle('collapsed'));

const mobileBtn = document.getElementById('mobile-menu-btn');
const mobileOverlay = document.getElementById('mobile-overlay');

function closeMobile(){
  sidebar.classList.remove('mobile-open');
  mobileOverlay.classList.remove('active');
}
mobileBtn?.addEventListener('click', () => {
  sidebar.classList.toggle('mobile-open');
  mobileOverlay.classList.toggle('active');
});
mobileOverlay?.addEventListener('click', closeMobile);

const userAvatar = document.querySelector('[data-dropdown="user-dropdown"]');
const userDropdown = document.getElementById('user-dropdown');

userAvatar?.addEventListener('click', (e) => {
  e.stopPropagation();
  userDropdown?.classList.toggle('show');
});
document.addEventListener('click', () => userDropdown?.classList.remove('show'));

// inicializa preview
syncPreview();