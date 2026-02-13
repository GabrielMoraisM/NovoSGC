// ===== GLOBAL FUNCTIONS =====

// Toggle sidebar (recolher/expandir)
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('collapsed');
}

// Toggle mobile sidebar
function toggleMobileSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('mobile-overlay');
  sidebar.classList.toggle('mobile-open');
  overlay.classList.toggle('active');
}

// Fechar sidebar ao clicar no overlay (mobile)
document.getElementById('mobile-overlay')?.addEventListener('click', toggleMobileSidebar);

// Botão de menu mobile
document.getElementById('mobile-menu-btn')?.addEventListener('click', toggleMobileSidebar);

// Botão de recolher sidebar (desktop)
document.getElementById('sidebar-toggle')?.addEventListener('click', toggleSidebar);

// Toggle tema (claro/escuro)
function toggleTheme() {
  document.body.classList.toggle('dark');
  const moon = document.getElementById('theme-moon');
  const sun = document.getElementById('theme-sun');
  if (moon && sun) {
    moon.style.display = moon.style.display === 'none' ? 'block' : 'none';
    sun.style.display = sun.style.display === 'none' ? 'block' : 'none';
  }
}

document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);

// Logout
function fazerLogout(event) {
  event.preventDefault();
  sessionStorage.clear();
  localStorage.clear();
  window.location.replace("index.html");
}

// Dropdowns
document.querySelectorAll('[data-dropdown]').forEach(button => {
  button.addEventListener('click', (e) => {
    e.stopPropagation();
    const dropdownId = button.getAttribute('data-dropdown');
    const dropdown = document.getElementById(dropdownId);
    if (dropdown) {
      dropdown.classList.toggle('show');
    }
  });
});

// Fechar dropdowns ao clicar fora
document.addEventListener('click', () => {
  document.querySelectorAll('.dropdown.show').forEach(dropdown => {
    dropdown.classList.remove('show');
  });
});

// Modais
document.querySelectorAll('[data-modal-open]').forEach(button => {
  button.addEventListener('click', (e) => {
    e.preventDefault();
    const modalId = button.getAttribute('data-modal-open');
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
    }
  });
});

document.querySelectorAll('[data-modal-close]').forEach(button => {
  button.addEventListener('click', () => {
    const modal = button.closest('.modal-overlay');
    if (modal) {
      modal.classList.remove('active');
    }
  });
});

// Fechar modal ao clicar no overlay
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.classList.remove('active');
    }
  });
});