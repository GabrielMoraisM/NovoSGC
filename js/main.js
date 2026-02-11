// ============================================
// SGC - Sistema de Gestão de Contratos
// Main JavaScript
// ============================================

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  initTheme();
  initSidebar();
  initDropdowns();
  initModals();
  initTabs();
  initUserProfile();
  initSearch();
  initTooltips();
  initAnimations();
});

// ============================================
// Theme Management
// ============================================

function initTheme() {
  const savedTheme = localStorage.getItem('sgc-theme') || 'light';
  setTheme(savedTheme);
  
  // Theme toggle button
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('sgc-theme', theme);
  updateThemeIcon(theme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  setTheme(newTheme);
}

function updateThemeIcon(theme) {
  const sunIcon = document.getElementById('theme-sun');
  const moonIcon = document.getElementById('theme-moon');
  
  if (sunIcon && moonIcon) {
    if (theme === 'dark') {
      sunIcon.style.display = 'block';
      moonIcon.style.display = 'none';
    } else {
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'block';
    }
  }
}

// ============================================
// Sidebar Management
// ============================================

function initSidebar() {
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileOverlay = document.getElementById('mobile-overlay');
  
  // Desktop toggle
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      sidebar.classList.toggle('collapsed');
      localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
    });
  }
  
  // Restore sidebar state
  const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
  if (isCollapsed && window.innerWidth > 768) {
    sidebar.classList.add('collapsed');
  }
  
  // Mobile menu
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', function() {
      sidebar.classList.add('mobile-open');
      mobileOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  }
  
  if (mobileOverlay) {
    mobileOverlay.addEventListener('click', closeMobileMenu);
  }
  
  // Close on nav item click (mobile)
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', function() {
      if (window.innerWidth <= 768) {
        closeMobileMenu();
      }
    });
  });
}

function closeMobileMenu() {
  const sidebar = document.getElementById('sidebar');
  const mobileOverlay = document.getElementById('mobile-overlay');
  
  sidebar.classList.remove('mobile-open');
  mobileOverlay.classList.remove('active');
  document.body.style.overflow = '';
}

// ============================================
// Dropdown Management
// ============================================

function initDropdowns() {
  const dropdownTriggers = document.querySelectorAll('[data-dropdown]');
  
  dropdownTriggers.forEach(trigger => {
    trigger.addEventListener('click', function(e) {
      e.stopPropagation();
      const dropdownId = this.getAttribute('data-dropdown');
      const dropdown = document.getElementById(dropdownId);
      
      // Close other dropdowns
      document.querySelectorAll('.dropdown.active').forEach(d => {
        if (d.id !== dropdownId) {
          d.classList.remove('active');
        }
      });
      
      dropdown.classList.toggle('active');
    });
  });
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', function() {
    document.querySelectorAll('.dropdown.active').forEach(d => {
      d.classList.remove('active');
    });
  });
  
  // Prevent dropdown from closing when clicking inside
  document.querySelectorAll('.dropdown').forEach(dropdown => {
    dropdown.addEventListener('click', function(e) {
      e.stopPropagation();
    });
  });
}

// ============================================
// Modal Management
// ============================================

function initModals() {
  // Open modal buttons
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', function() {
      const modalId = this.getAttribute('data-modal-open');
      openModal(modalId);
    });
  });
  
  // Close modal buttons
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', function() {
      const modal = this.closest('.modal-overlay');
      closeModal(modal.id);
    });
  });
  
  // Close on overlay click
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function(e) {
      if (e.target === this) {
        closeModal(this.id);
      }
    });
  });
  
  // Close on escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.active').forEach(modal => {
        closeModal(modal.id);
      });
    }
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// ============================================
// Tabs Management
// ============================================

function initTabs() {
  const tabContainers = document.querySelectorAll('[data-tabs]');
  
  tabContainers.forEach(container => {
    const tabs = container.querySelectorAll('.tab');
    const tabId = container.getAttribute('data-tabs');
    
    tabs.forEach(tab => {
      tab.addEventListener('click', function() {
        // Remove active from all tabs
        tabs.forEach(t => t.classList.remove('active'));
        
        // Add active to clicked tab
        this.classList.add('active');
        
        // Get target panel
        const targetId = this.getAttribute('data-tab-target');
        
        // Hide all panels
        document.querySelectorAll(`[data-tab-panel="${tabId}"]`).forEach(panel => {
          panel.style.display = 'none';
        });
        
        // Show target panel
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) {
          targetPanel.style.display = 'block';
        }
        
        // Trigger custom event
        document.dispatchEvent(new CustomEvent('tabChange', {
          detail: { tabId, targetId }
        }));
      });
    });
  });
}

// ============================================
// User Profile Management
// ============================================

function initUserProfile() {
  loadUserProfile();
  
  // Avatar upload
  const avatarInput = document.getElementById('avatar-input');
  if (avatarInput) {
    avatarInput.addEventListener('change', handleAvatarUpload);
  }
  
  // Profile form
  const profileForm = document.getElementById('profile-form');
  if (profileForm) {
    profileForm.addEventListener('submit', saveUserProfile);
  }
}

function loadUserProfile() {
  const userData = JSON.parse(localStorage.getItem('sgc-user') || '{}');
  
  // Update avatar
  const avatars = document.querySelectorAll('.user-avatar');
  avatars.forEach(avatar => {
    if (userData.avatar) {
      avatar.innerHTML = `<img src="${userData.avatar}" alt="Avatar">`;
    } else {
      avatar.textContent = userData.initials || 'HC';
    }
  });
  
  // Update profile form
  const nameInput = document.getElementById('profile-name');
  const emailInput = document.getElementById('profile-email');
  const roleInput = document.getElementById('profile-role');
  
  if (nameInput) nameInput.value = userData.name || 'Heca Admin';
  if (emailInput) emailInput.value = userData.email || 'admin@heca.com.br';
  if (roleInput) roleInput.value = userData.role || 'Diretor';
  
  // Update display name
  const displayNames = document.querySelectorAll('.user-display-name');
  displayNames.forEach(el => {
    el.textContent = userData.name || 'Heca Admin';
  });
}

function handleAvatarUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  
  if (!file.type.startsWith('image/')) {
    alert('Por favor, selecione uma imagem.');
    return;
  }
  
  const reader = new FileReader();
  reader.onload = function(event) {
    const imageData = event.target.result;
    
    // Update preview
    const previews = document.querySelectorAll('.avatar-preview, .user-avatar');
    previews.forEach(preview => {
      preview.innerHTML = `<img src="${imageData}" alt="Avatar">`;
    });
    
    // Save to localStorage
    const userData = JSON.parse(localStorage.getItem('sgc-user') || '{}');
    userData.avatar = imageData;
    localStorage.setItem('sgc-user', JSON.stringify(userData));
  };
  
  reader.readAsDataURL(file);
}

function saveUserProfile(e) {
  e.preventDefault();
  
  const nameInput = document.getElementById('profile-name');
  const emailInput = document.getElementById('profile-email');
  const roleInput = document.getElementById('profile-role');
  
  const userData = JSON.parse(localStorage.getItem('sgc-user') || '{}');
  userData.name = nameInput.value;
  userData.email = emailInput.value;
  userData.role = roleInput.value;
  userData.initials = nameInput.value.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  
  localStorage.setItem('sgc-user', JSON.stringify(userData));
  
  // Update UI
  loadUserProfile();
  
  // Close modal
  closeModal('profile-modal');
  
  // Show feedback
  showToast('Perfil atualizado com sucesso!', 'success');
}

// ============================================
// Search
// ============================================

function initSearch() {
  const searchInputs = document.querySelectorAll('[data-search]');
  
  searchInputs.forEach(input => {
    input.addEventListener('input', debounce(function() {
      const searchTerm = this.value.toLowerCase();
      const targetSelector = this.getAttribute('data-search');
      const items = document.querySelectorAll(targetSelector);
      
      items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(searchTerm) ? '' : 'none';
      });
    }, 300));
  });
}

// ============================================
// Tooltips
// ============================================

function initTooltips() {
  const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
  
  tooltipTriggers.forEach(trigger => {
    trigger.addEventListener('mouseenter', showTooltip);
    trigger.addEventListener('mouseleave', hideTooltip);
  });
}

function showTooltip(e) {
  const text = e.target.getAttribute('data-tooltip');
  const tooltip = document.createElement('div');
  tooltip.className = 'tooltip';
  tooltip.textContent = text;
  tooltip.style.cssText = `
    position: fixed;
    background: var(--text-primary);
    color: var(--surface);
    padding: 0.5rem 0.75rem;
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    z-index: 1000;
    pointer-events: none;
    animation: fadeIn 0.2s ease;
  `;
  
  document.body.appendChild(tooltip);
  
  const rect = e.target.getBoundingClientRect();
  tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
  tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
  
  e.target._tooltip = tooltip;
}

function hideTooltip(e) {
  if (e.target._tooltip) {
    e.target._tooltip.remove();
    delete e.target._tooltip;
  }
}

// ============================================
// Animations
// ============================================

function initAnimations() {
  // Intersection Observer for scroll animations
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-fade-in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  
  document.querySelectorAll('.card, .kpi-card, .alert-card').forEach(el => {
    observer.observe(el);
  });
}

// ============================================
// Toast Notifications
// ============================================

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container') || createToastContainer();
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  `;
  
  toast.style.cssText = `
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem 1.25rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    animation: slideIn 0.3s ease;
    border-left: 4px solid ${type === 'success' ? 'var(--success)' : type === 'error' ? 'var(--danger)' : 'var(--accent)'};
  `;
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'fadeIn 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.style.cssText = `
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    z-index: 1000;
  `;
  document.body.appendChild(container);
  return container;
}

// ============================================
// Utility Functions
// ============================================

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func.apply(this, args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
}

function formatDate(date) {
  return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
}

function formatPercent(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 1
  }).format(value / 100);
}

// ============================================
// Data & Charts (Mock)
// ============================================

// Sample data for charts
const chartData = {
  progressoFisicoFinanceiro: [
    { mes: 'Jan', fisico: 5, financeiro: 4 },
    { mes: 'Fev', fisico: 12, financeiro: 10 },
    { mes: 'Mar', fisico: 22, financeiro: 18 },
    { mes: 'Abr', fisico: 35, financeiro: 30 },
    { mes: 'Mai', fisico: 48, financeiro: 42 },
    { mes: 'Jun', fisico: 58, financeiro: 52 }
  ]
};

// Simple chart rendering (can be replaced with Chart.js)
function renderSimpleChart(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const maxValue = Math.max(...data.map(d => Math.max(d.fisico, d.financeiro)));
  const chartHeight = 200;
  const barWidth = 30;
  const gap = 20;
  
  let html = `
    <svg width="100%" height="${chartHeight + 50}" viewBox="0 0 ${data.length * (barWidth * 2 + gap) + 50} ${chartHeight + 50}">
      <style>
        .chart-bar { transition: height 0.5s ease, y 0.5s ease; }
        .chart-bar:hover { opacity: 0.8; }
        .chart-label { font-size: 12px; fill: var(--text-secondary); }
        .chart-value { font-size: 10px; fill: var(--text-primary); }
      </style>
  `;
  
  data.forEach((d, i) => {
    const x = i * (barWidth * 2 + gap) + 30;
    const fisicoHeight = (d.fisico / maxValue) * chartHeight;
    const financeiroHeight = (d.financeiro / maxValue) * chartHeight;
    
    html += `
      <rect class="chart-bar" x="${x}" y="${chartHeight - fisicoHeight}" width="${barWidth}" height="${fisicoHeight}" fill="var(--primary)" rx="4"/>
      <rect class="chart-bar" x="${x + barWidth + 4}" y="${chartHeight - financeiroHeight}" width="${barWidth}" height="${financeiroHeight}" fill="var(--success)" rx="4"/>
      <text class="chart-label" x="${x + barWidth}" y="${chartHeight + 20}" text-anchor="middle">${d.mes}</text>
    `;
  });
  
  html += '</svg>';
  html += `
    <div style="display: flex; gap: 1.5rem; justify-content: center; margin-top: 1rem;">
      <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem;">
        <div style="width: 12px; height: 12px; background: var(--primary); border-radius: 2px;"></div>
        <span>Fisico</span>
      </div>
      <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem;">
        <div style="width: 12px; height: 12px; background: var(--success); border-radius: 2px;"></div>
        <span>Financeiro</span>
      </div>
    </div>
  `;
  
  container.innerHTML = html;
}

// Initialize charts on page load
document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('progress-chart')) {
    renderSimpleChart('progress-chart', chartData.progressoFisicoFinanceiro);
  }
});
 // Script para filtrar contratos
    document.getElementById('filter-type').addEventListener('change', filterContracts);
    document.getElementById('filter-status').addEventListener('change', filterContracts);
    
    function filterContracts() {
      const typeFilter = document.getElementById('filter-type').value;
      const statusFilter = document.getElementById('filter-status').value;
      
      document.querySelectorAll('.contract-row').forEach(row => {
        const type = row.dataset.type;
        const status = row.dataset.status;
        
        const typeMatch = !typeFilter || type === typeFilter;
        const statusMatch = !statusFilter || status === statusFilter;
        
        row.style.display = typeMatch && statusMatch ? '' : 'none';
      });
    }

    // Script para popular o Modal de Detalhes dinamicamente
    function abrirDetalhes(button) {
        // Encontra a linha pai do botão clicado
        const row = button.closest('tr');
        const contractId = row.dataset.id;
        const contractName = row.dataset.name;
        
        // Atualiza o título do modal
        document.getElementById('detail-modal-title').textContent = contractName;
        document.getElementById('detail-modal-subtitle').textContent = contractId + " - Visão Geral";
        
        // Abre o modal
        const modal = document.getElementById('contract-details-modal');
        modal.classList.add('active');
    }
    
    document.addEventListener('DOMContentLoaded', () => {
    // 1. Sidebar Toggle (Mobile)
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-overlay');
    const sidebarToggle = document.getElementById('sidebar-toggle');

    function toggleSidebar() {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('active');
    }

    if(mobileMenuBtn) mobileMenuBtn.addEventListener('click', toggleSidebar);
    if(overlay) overlay.addEventListener('click', toggleSidebar);
    
    if(sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            document.body.classList.toggle('sidebar-collapsed');
        });
    }

    // 2. Dropdown User
    const userAvatar = document.querySelector('.user-avatar');
    const userDropdown = document.getElementById('user-dropdown');
    
    if(userAvatar && userDropdown) {
        userAvatar.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('active');
        });
        document.addEventListener('click', () => {
            userDropdown.classList.remove('active');
        });
    }

    // 3. Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    const iconSun = document.getElementById('theme-sun');
    const iconMoon = document.getElementById('theme-moon');

    if(themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            if(currentTheme === 'dark') {
                html.removeAttribute('data-theme');
                iconMoon.style.display = 'block';
                iconSun.style.display = 'none';
            } else {
                html.setAttribute('data-theme', 'dark');
                iconMoon.style.display = 'none';
                iconSun.style.display = 'block';
            }
        });
    }
});

// 4. LÓGICA DAS ABAS DE CONFIGURAÇÃO
// Esta função precisa estar fora do DOMContentLoaded para ser acessível via onclick
function showSection(event, sectionId) {
    event.preventDefault();
    
    // Remove active dos links
    document.querySelectorAll('.settings-menu-item').forEach(link => {
      link.classList.remove('active');
    });
    
    // Adiciona active no link clicado
    event.currentTarget.classList.add('active');
    
    // Esconde todas as seções
    document.querySelectorAll('.settings-section').forEach(section => {
      section.classList.remove('active');
    });
    
    // Mostra a seção alvo
    const target = document.getElementById(sectionId);
    if(target) {
        target.classList.add('active');
    }
}

