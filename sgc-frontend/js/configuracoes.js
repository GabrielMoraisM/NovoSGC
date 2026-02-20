// ===== Navegação das abas da tela de configurações =====
function showSection(event, sectionId) {
  event.preventDefault();

  document.querySelectorAll('.settings-menu-item').forEach(a => a.classList.remove('active'));
  event.currentTarget.classList.add('active');

  document.querySelectorAll('.settings-section').forEach(sec => sec.classList.remove('active'));
  const target = document.getElementById(sectionId);
  if (target) target.classList.add('active');
}

// ===== Sidebar (recolher) =====
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');

if (sidebarToggle) {
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
}

// ===== Mobile menu =====
const mobileBtn = document.getElementById('mobile-menu-btn');
const mobileOverlay = document.getElementById('mobile-overlay');

function closeMobile() {
  sidebar.classList.remove('mobile-open');
  mobileOverlay.classList.remove('active');
}

if (mobileBtn) {
  mobileBtn.addEventListener('click', () => {
    sidebar.classList.toggle('mobile-open');
    mobileOverlay.classList.toggle('active');
  });
}

if (mobileOverlay) mobileOverlay.addEventListener('click', closeMobile);

// ===== Dropdown do usuário =====
const userAvatar = document.querySelector('[data-dropdown="user-dropdown"]');
const userDropdown = document.getElementById('user-dropdown');

if (userAvatar && userDropdown) {
  userAvatar.addEventListener('click', (e) => {
    e.stopPropagation();
    userDropdown.classList.toggle('show');
  });

  document.addEventListener('click', () => {
    userDropdown.classList.remove('show');
  });
}

// ===== Theme toggle (dark) =====
const themeToggle = document.getElementById('theme-toggle');
const moon = document.getElementById('theme-moon');
const sun = document.getElementById('theme-sun');

function setTheme(isDark) {
  document.body.classList.toggle('dark', isDark);
  if (moon && sun) {
    moon.style.display = isDark ? 'none' : 'block';
    sun.style.display = isDark ? 'block' : 'none';
  }
  localStorage.setItem('sgc_theme', isDark ? 'dark' : 'light');
}

const saved = localStorage.getItem('sgc_theme');
setTheme(saved === 'dark');

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    setTheme(!document.body.classList.contains('dark'));
  });
}

// ===== Dados DEMO (trocar por dados reais do backend depois) =====
const demo = {
  empresas:   { count: 3, trendText: "+2", trendDir: "up",   last: "Editado: Empresa ACME • por João • há 12 min" },
  contratos:  { count: 1, trendText: "+1", trendDir: "up",   last: "Atualizado: Contrato #1029 • por Maria • há 2 h" },
  medicoes:   { count: 4, trendText: "+4", trendDir: "up",   last: "Nova medição: Obra Alfa • por Pedro • ontem" },
  financeiro: { count: 1, trendText: "-1", trendDir: "down", last: "Ajuste: Centro de custo • por Ana • há 3 dias" },
  alertas:    { count: 3, trendText: "3",  trendDir: "down", last: "Vencimento próximo: Contrato #998 • hoje" }
};

function applyCard(key, data) {
  const valueEl = document.getElementById(`value-${key}`);
  const trendEl = document.getElementById(`trend-${key}`);
  const lastEl  = document.getElementById(`last-${key}`);

  if (valueEl) valueEl.textContent = data.count;
  if (lastEl)  lastEl.textContent  = (key === 'alertas' ? 'Último alerta: ' : 'Última alteração: ') + data.last;

  if (trendEl) {
    trendEl.classList.remove('up', 'down');
    trendEl.classList.add(data.trendDir === 'down' ? 'down' : 'up');
    trendEl.textContent = (data.trendDir === 'down' ? '↘ ' : '↗ ') + data.trendText;
  }
}

Object.entries(demo).forEach(([key, val]) => applyCard(key, val));

// ===== MODAL "VER MAIS" =====
const sectionTitle = {
  empresas: "Empresas",
  contratos: "Contratos",
  medicoes: "Medições",
  financeiro: "Financeiro",
  alertas: "Últimos alertas",
};

// Mock (trocar por API depois)
const changesData = {
  contratos: [
    { when: "há 2 h", what: "Atualizou Contrato #1029 (prazo)", who: "Maria" },
    { when: "ontem",  what: "Criou Contrato #1030",            who: "João"  },
  ],
  empresas: [
    { when: "há 12 min", what: "Editou Empresa ACME", who: "João" },
    { when: "hoje 09:10", what: "Criou Empresa Beta", who: "Maria" },
  ],
  medicoes: [
    { when: "ontem", what: "Nova medição da Obra Alfa", who: "Pedro" },
  ],
  financeiro: [
    { when: "há 3 dias", what: "Alterou centro de custo (Obra Alfa)", who: "Ana" },
  ],
  alertas: [
    { when: "hoje", what: "Vencimento próximo: Contrato #998", who: "Sistema" },
  ],
};

function openChanges(ev, key) {
  ev.preventDefault();
  ev.stopPropagation();

  const modal = document.getElementById("changes-modal");
  const title = document.getElementById("changes-title");
  const subtitle = document.getElementById("changes-subtitle");
  const slot = document.getElementById("changes-table-slot");

  const rows = changesData[key] || [];

  if (title) title.textContent = "Detalhes • " + (sectionTitle[key] || "Alterações");
  if (subtitle) subtitle.textContent = rows.length ? `${rows.length} registro(s)` : "Nenhum registro encontrado";

  if (slot) slot.innerHTML = renderDefaultTable(rows);

  if (modal) {
    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");
  }
}

function renderDefaultTable(rows){
  return `
    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>Quando</th>
            <th>O que mudou</th>
            <th>Por</th>
          </tr>
        </thead>
        <tbody>
          ${rows.map(r => `
            <tr>
              <td>${r.when}</td>
              <td>${r.what}</td>
              <td>${r.who}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function closeChanges() {
  const modal = document.getElementById("changes-modal");
  if (!modal) return;
  modal.classList.remove("active");
  modal.setAttribute("aria-hidden", "true");
}

// fechar clicando fora
document.addEventListener("click", (e) => {
  const modal = document.getElementById("changes-modal");
  if (!modal || !modal.classList.contains("active")) return;
  if (e.target === modal) closeChanges();
});

// fechar com ESC
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeChanges();
});

// IMPORTANTe: como seus botões chamam openChanges/showSection no HTML,
// precisamos expor essas funções no escopo global:
window.showSection = showSection;
window.openChanges = openChanges;
window.closeChanges = closeChanges;