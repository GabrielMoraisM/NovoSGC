// ===== ALERTAS =====

// Dados mockados de alertas
const alertasMock = [
  {
    id: 1,
    tipo: 'danger',
    titulo: 'Prazo crítico',
    mensagem: 'O contrato CT-2024-004 (Conjunto Habitacional) está com 15 dias de atraso.',
    data: '2026-02-13T10:30:00',
    lido: false,
    link: 'contratos.html?id=4'
  },
  {
    id: 2,
    tipo: 'warning',
    titulo: 'Desequilíbrio físico-financeiro',
    mensagem: 'CT-2024-003 (Subestação 230kV) apresenta variação de 8,5% entre físico e financeiro.',
    data: '2026-02-13T09:15:00',
    lido: false,
    link: 'contratos.html?id=3'
  },
  {
    id: 3,
    tipo: 'warning',
    titulo: 'Seguro próximo ao vencimento',
    mensagem: 'A apólice do contrato CT-2024-001 vence em 15 dias.',
    data: '2026-02-12T16:45:00',
    lido: true,
    link: 'contratos.html?id=1'
  },
  {
    id: 4,
    tipo: 'info',
    titulo: 'Medição aprovada',
    mensagem: 'A BM-005 do contrato CT-2024-001 foi aprovada e aguarda faturamento.',
    data: '2026-02-12T14:20:00',
    lido: true,
    link: 'medicoes.html?id=5'
  },
  {
    id: 5,
    tipo: 'success',
    titulo: 'Pagamento recebido',
    mensagem: 'NF-2024-0127 (Vale S.A.) foi quitada integralmente.',
    data: '2026-02-11T11:05:00',
    lido: false,
    link: 'financeiro.html?id=3'
  },
  {
    id: 6,
    tipo: 'info',
    titulo: 'Novo aditivo registrado',
    mensagem: 'TA-03 do contrato CT-2024-002 foi adicionado com +60 dias de prazo.',
    data: '2026-02-10T09:30:00',
    lido: true,
    link: 'contratos.html?id=2'
  }
];

// Função para formatar data relativa
function timeAgo(dataISO) {
  const data = new Date(dataISO);
  const agora = new Date();
  const diffMs = agora - data;
  const diffMin = Math.floor(diffMs / 60000);
  const diffHora = Math.floor(diffMs / 3600000);
  const diffDia = Math.floor(diffMs / 86400000);

  if (diffMin < 1) return 'Agora mesmo';
  if (diffMin < 60) return `Há ${diffMin} minuto${diffMin > 1 ? 's' : ''}`;
  if (diffHora < 24) return `Há ${diffHora} hora${diffHora > 1 ? 's' : ''}`;
  if (diffDia < 7) return `Há ${diffDia} dia${diffDia > 1 ? 's' : ''}`;
  return data.toLocaleDateString('pt-BR');
}

// Renderizar lista de alertas
function renderizarAlertas() {
  const container = document.getElementById('alerts-list');
  const emptyState = document.getElementById('alerts-empty');
  if (!container) return;

  // Obter filtros
  const tipoFiltro = document.getElementById('filter-type').value;
  const readFiltro = document.getElementById('filter-read').value;
  const termo = document.getElementById('search-alerts').value.toLowerCase();

  const alertasFiltrados = alertasMock.filter(alerta => {
    if (tipoFiltro && alerta.tipo !== tipoFiltro) return false;
    if (readFiltro === 'unread' && alerta.lido) return false;
    if (readFiltro === 'read' && !alerta.lido) return false;
    if (termo && !alerta.titulo.toLowerCase().includes(termo) && !alerta.mensagem.toLowerCase().includes(termo)) return false;
    return true;
  });

  // Limpar container (exceto empty state)
  container.innerHTML = '';

  if (alertasFiltrados.length === 0) {
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';
  alertasFiltrados.sort((a, b) => new Date(b.data) - new Date(a.data));

  alertasFiltrados.forEach(alerta => {
    const card = document.createElement('div');
    card.className = `alert-card ${!alerta.lido ? 'unread' : ''}`;
    card.setAttribute('data-id', alerta.id);

    const icone = {
      warning: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
      danger: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
      success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`,
      info: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`
    };

    const badgeTipo = {
      warning: '<span class="badge badge-warning">Atenção</span>',
      danger: '<span class="badge badge-danger">Crítico</span>',
      success: '<span class="badge badge-success">Sucesso</span>',
      info: '<span class="badge badge-primary">Informativo</span>'
    };

    card.innerHTML = `
      <div class="alert-icon ${alerta.tipo}">
        ${icone[alerta.tipo] || ''}
      </div>
      <div class="alert-content">
        <div class="alert-title">
          ${alerta.titulo}
          ${!alerta.lido ? badgeTipo[alerta.tipo] : ''}
        </div>
        <div class="alert-message">${alerta.mensagem}</div>
        <div class="alert-meta">
          <span>${timeAgo(alerta.data)}</span>
          ${alerta.link ? `<a href="${alerta.link}" class="text-primary">Ver detalhes</a>` : ''}
        </div>
      </div>
      <div class="alert-actions">
        ${!alerta.lido ? `
          <button class="btn btn-ghost btn-sm" onclick="marcarComoLido(${alerta.id})" title="Marcar como lido">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 12 9 20 23 4"/></svg>
          </button>
        ` : ''}
      </div>
    `;
    container.appendChild(card);
  });
}

// Marcar alerta como lido
function marcarComoLido(id) {
  const alerta = alertasMock.find(a => a.id === id);
  if (alerta) {
    alerta.lido = true;
    renderizarAlertas();
    atualizarBadge();
  }
}

// Marcar todos como lidos
function marcarTodosLidos() {
  alertasMock.forEach(a => a.lido = true);
  renderizarAlertas();
  atualizarBadge();
}

// Atualizar badge de notificações na topbar
function atualizarBadge() {
  const naoLidos = alertasMock.filter(a => !a.lido).length;
  const badge = document.querySelector('.notification-badge');
  if (badge) {
    badge.style.display = naoLidos > 0 ? 'block' : 'none';
  }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  renderizarAlertas();
  atualizarBadge();

  // Event listeners para filtros
  document.getElementById('filter-type')?.addEventListener('change', renderizarAlertas);
  document.getElementById('filter-read')?.addEventListener('change', renderizarAlertas);
  document.getElementById('search-alerts')?.addEventListener('input', renderizarAlertas);
});

// Expor funções globalmente para uso nos botões
window.marcarComoLido = marcarComoLido;
window.marcarTodosLidos = marcarTodosLidos;