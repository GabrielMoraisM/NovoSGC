// ===== MEDIÇÕES =====

// Dados mockados de medições
const medicoesMock = [
  {
    id: 1,
    numeroSequencial: 1,
    contratoNumero: "CT-2024-001",
    contratoNome: "Plataforma P-80",
    periodoInicio: "2024-01-01",
    periodoFim: "2024-01-31",
    valorMedido: 1500000.00,
    glosa: 0,
    valorAprovado: 1500000.00,
    status: "FATURADO",
    observacoes: "Primeira medição do contrato"
  },
  {
    id: 2,
    numeroSequencial: 2,
    contratoNumero: "CT-2024-001",
    contratoNome: "Plataforma P-80",
    periodoInicio: "2024-02-01",
    periodoFim: "2024-02-28",
    valorMedido: 1250000.00,
    glosa: 0,
    valorAprovado: 1250000.00,
    status: "FATURADO",
    observacoes: ""
  },
  {
    id: 3,
    numeroSequencial: 3,
    contratoNumero: "CT-2024-001",
    contratoNome: "Plataforma P-80",
    periodoInicio: "2024-03-01",
    periodoFim: "2024-03-31",
    valorMedido: 1875000.00,
    glosa: 0,
    valorAprovado: 1875000.00,
    status: "FATURADO",
    observacoes: ""
  },
  {
    id: 4,
    numeroSequencial: 4,
    contratoNumero: "CT-2024-001",
    contratoNome: "Plataforma P-80",
    periodoInicio: "2024-04-01",
    periodoFim: "2024-04-30",
    valorMedido: 2250000.00,
    glosa: 0,
    valorAprovado: 2250000.00,
    status: "FATURADO",
    observacoes: ""
  },
  {
    id: 5,
    numeroSequencial: 5,
    contratoNumero: "CT-2024-001",
    contratoNome: "Plataforma P-80",
    periodoInicio: "2024-05-01",
    periodoFim: "2024-05-31",
    valorMedido: 1500000.00,
    glosa: 0,
    valorAprovado: 1500000.00,
    status: "APROVADO",
    observacoes: "Aguardando emissão de nota fiscal"
  },
  {
    id: 6,
    numeroSequencial: 6,
    contratoNumero: "CT-2024-001",
    contratoNome: "Plataforma P-80",
    periodoInicio: "2024-06-01",
    periodoFim: "2024-06-15",
    valorMedido: 625000.00,
    glosa: 25000.00,
    valorAprovado: 600000.00,
    status: "RASCUNHO",
    observacoes: "Glosa por serviços não conformes"
  },
  {
    id: 7,
    numeroSequencial: 1,
    contratoNumero: "CT-2024-002",
    contratoNome: "Terminal Portuário",
    periodoInicio: "2024-03-01",
    periodoFim: "2024-03-31",
    valorMedido: 2100000.00,
    glosa: 0,
    valorAprovado: 2100000.00,
    status: "FATURADO",
    observacoes: ""
  },
  {
    id: 8,
    numeroSequencial: 2,
    contratoNumero: "CT-2024-002",
    contratoNome: "Terminal Portuário",
    periodoInicio: "2024-04-01",
    periodoFim: "2024-04-30",
    valorMedido: 3200000.00,
    glosa: 0,
    valorAprovado: 3200000.00,
    status: "FATURADO",
    observacoes: ""
  },
  {
    id: 9,
    numeroSequencial: 3,
    contratoNumero: "CT-2024-002",
    contratoNome: "Terminal Portuário",
    periodoInicio: "2024-05-01",
    periodoFim: "2024-05-31",
    valorMedido: 2000000.00,
    glosa: 0,
    valorAprovado: 2000000.00,
    status: "APROVADO",
    observacoes: ""
  },
  {
    id: 10,
    numeroSequencial: 1,
    contratoNumero: "CT-2024-003",
    contratoNome: "Subestação 230kV",
    periodoInicio: "2024-03-01",
    periodoFim: "2024-03-31",
    valorMedido: 1500000.00,
    glosa: 0,
    valorAprovado: 1500000.00,
    status: "APROVADO",
    observacoes: ""
  },
  {
    id: 11,
    numeroSequencial: 2,
    contratoNumero: "CT-2024-003",
    contratoNome: "Subestação 230kV",
    periodoInicio: "2024-04-01",
    periodoFim: "2024-04-30",
    valorMedido: 3800000.00,
    glosa: 0,
    valorAprovado: 3800000.00,
    status: "APROVADO",
    observacoes: ""
  },
  {
    id: 12,
    numeroSequencial: 3,
    contratoNumero: "CT-2024-003",
    contratoNome: "Subestação 230kV",
    periodoInicio: "2024-05-01",
    periodoFim: "2024-05-31",
    valorMedido: 2100000.00,
    glosa: 0,
    valorAprovado: 2100000.00,
    status: "RASCUNHO",
    observacoes: ""
  }
];

// Função para formatar valor em reais
function formatarMoeda(valor) {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

// Função para formatar data
function formatarData(dataStr) {
  const data = new Date(dataStr + 'T12:00:00');
  return data.toLocaleDateString('pt-BR');
}

// Obter badge de status
function getStatusBadge(status) {
  const classes = {
    'RASCUNHO': 'badge-warning',
    'APROVADO': 'badge-primary',
    'FATURADO': 'badge-success',
    'CANCELADO': 'badge-danger'
  };
  const labels = {
    'RASCUNHO': 'Rascunho',
    'APROVADO': 'Aprovado',
    'FATURADO': 'Faturado',
    'CANCELADO': 'Cancelado'
  };
  return `<span class="badge ${classes[status] || 'badge-secondary'}">${labels[status] || status}</span>`;
}

// Carregar medições no grid
function carregarMedicoes() {
  const grid = document.getElementById('measurements-grid');
  if (!grid) {
    console.error('Grid de medições não encontrado!');
    return;
  }

  grid.innerHTML = '';
  medicoesMock.forEach(med => {
    const card = document.createElement('div');
    card.className = `measurement-card ${med.status === 'FATURADO' ? 'locked' : ''}`;
    card.setAttribute('data-id', med.id);
    card.setAttribute('data-contrato', med.contratoNumero);
    card.setAttribute('data-status', med.status);

    // Definir etapas do status
    const etapas = ['RASCUNHO', 'APROVADO', 'FATURADO'];
    const statusIndex = etapas.indexOf(med.status);
    const statusSteps = etapas.map((etapa, index) => {
      let stepClass = '';
      if (index < statusIndex) stepClass = 'completed';
      else if (index === statusIndex) stepClass = 'current';
      return `<div class="status-step ${stepClass}" data-label="${etapa.substring(0,3)}"></div>`;
    }).join('');

    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="measurement-number">BM-${med.numeroSequencial.toString().padStart(3, '0')}</div>
        ${med.status === 'FATURADO' ? `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" style="color: var(--text-muted);">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
        ` : ''}
      </div>
      <div class="text-xs text-muted mt-1">${med.contratoNumero} - ${med.contratoNome}</div>
      <div class="text-xs text-muted">${formatarData(med.periodoInicio)} a ${formatarData(med.periodoFim)}</div>
      
      <div class="measurement-status">
        ${statusSteps}
      </div>
      
      <div class="measurement-values">
        <div class="measurement-value">
          <span>Medido</span>
          <strong>${formatarMoeda(med.valorMedido)}</strong>
        </div>
        <div class="measurement-value">
          <span>Aprovado</span>
          <strong>${formatarMoeda(med.valorAprovado)}</strong>
        </div>
      </div>
      
      <div style="margin-top: 1rem; display: flex; align-items: center; justify-content: space-between;">
        <div>${getStatusBadge(med.status)}</div>
        <button class="btn-view-more" onclick="abrirDetalhesMedicao(${med.id})">
          <span>Detalhes</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
    `;
    grid.appendChild(card);
  });

  // Atualizar resumo
  atualizarResumo();
}

// Atualizar resumo acumulado
function atualizarResumo() {
  const total = medicoesMock.length;
  const valorTotalMedido = medicoesMock.reduce((acc, m) => acc + m.valorMedido, 0);
  const valorTotalAprovado = medicoesMock.reduce((acc, m) => acc + m.valorAprovado, 0);
  const valorTotalFaturado = medicoesMock
    .filter(m => m.status === 'FATURADO')
    .reduce((acc, m) => acc + m.valorAprovado, 0);

  document.getElementById('total-medicoes').textContent = total;
  document.getElementById('valor-total-medido').textContent = formatarMoeda(valorTotalMedido);
  document.getElementById('valor-total-aprovado').textContent = formatarMoeda(valorTotalAprovado);
  document.getElementById('valor-total-faturado').textContent = formatarMoeda(valorTotalFaturado);
}

// Filtrar medições
function filtrarMedicoes() {
  const contratoFiltro = document.getElementById('filter-contract').value;
  const statusFiltro = document.getElementById('filter-status').value;
  const termo = document.getElementById('search-measurements').value.toLowerCase();

  const cards = document.querySelectorAll('.measurement-card');
  cards.forEach(card => {
    const contrato = card.getAttribute('data-contrato') || '';
    const status = card.getAttribute('data-status') || '';
    const textoCard = card.innerText.toLowerCase();

    let show = true;
    if (contratoFiltro && contrato !== contratoFiltro) show = false;
    if (statusFiltro && status !== statusFiltro) show = false;
    if (termo && !textoCard.includes(termo)) show = false;

    card.style.display = show ? '' : 'none';
  });

  // Atualizar contagem visível (opcional)
  const visiveis = document.querySelectorAll('.measurement-card:not([style*="display: none"])').length;
  console.log(`${visiveis} medições visíveis`);
}

// Abrir modal de detalhes da medição
function abrirDetalhesMedicao(id) {
  const med = medicoesMock.find(m => m.id === id);
  if (!med) return;

  document.getElementById('detail-measurement-title').textContent = `BM-${med.numeroSequencial.toString().padStart(3, '0')}`;
  document.getElementById('detail-measurement-subtitle').textContent = `${med.contratoNumero} - ${med.contratoNome}`;
  document.getElementById('detail-valor-medido').textContent = formatarMoeda(med.valorMedido);
  document.getElementById('detail-glosa').textContent = formatarMoeda(med.glosa);
  document.getElementById('detail-valor-aprovado').textContent = formatarMoeda(med.valorAprovado);
  document.getElementById('detail-contrato').textContent = `${med.contratoNumero} - ${med.contratoNome}`;
  document.getElementById('detail-periodo').textContent = `${formatarData(med.periodoInicio)} a ${formatarData(med.periodoFim)}`;
  document.getElementById('detail-status').innerHTML = getStatusBadge(med.status);
  document.getElementById('detail-observacoes').textContent = med.observacoes || '—';

  // Botões de ação conforme status
  const actionsDiv = document.getElementById('detail-actions');
  actionsDiv.innerHTML = '';

  if (med.status === 'RASCUNHO') {
    actionsDiv.innerHTML = `
      <button class="btn btn-primary" onclick="alterarStatusMedicao(${med.id}, 'APROVAR')">Aprovar</button>
      <button class="btn btn-secondary" onclick="editarMedicao(${med.id})">Editar</button>
      <button class="btn btn-danger" onclick="alterarStatusMedicao(${med.id}, 'CANCELAR')">Cancelar</button>
    `;
  } else if (med.status === 'APROVADO') {
    actionsDiv.innerHTML = `
      <button class="btn btn-success" onclick="alterarStatusMedicao(${med.id}, 'FATURAR')">Faturar</button>
      <button class="btn btn-secondary" onclick="editarMedicao(${med.id})">Editar</button>
      <button class="btn btn-danger" onclick="alterarStatusMedicao(${med.id}, 'CANCELAR')">Cancelar</button>
    `;
  } else if (med.status === 'FATURADO') {
    actionsDiv.innerHTML = `
      <span class="text-sm text-muted">Medição já faturada – não pode ser alterada.</span>
    `;
  } else if (med.status === 'CANCELADO') {
    actionsDiv.innerHTML = `
      <span class="text-sm text-muted">Medição cancelada.</span>
    `;
  }

  document.getElementById('measurement-details-modal').classList.add('active');
}

// Funções de ação (mock)
function alterarStatusMedicao(id, acao) {
  const med = medicoesMock.find(m => m.id === id);
  if (!med) return;

  let novaStatus = '';
  if (acao === 'APROVAR') novaStatus = 'APROVADO';
  else if (acao === 'FATURAR') novaStatus = 'FATURADO';
  else if (acao === 'CANCELAR') novaStatus = 'CANCELADO';

  if (novaStatus) {
    med.status = novaStatus;
    alert(`Status da medição alterado para ${novaStatus} (simulação)`);
    carregarMedicoes();
    document.getElementById('measurement-details-modal').classList.remove('active');
  }
}

function editarMedicao(id) {
  alert(`Editar medição ${id} – funcionalidade em desenvolvimento`);
  document.getElementById('measurement-details-modal').classList.remove('active');
  // Aqui você poderia abrir um modal de edição com os dados preenchidos
}

// Salvar nova medição (mock)
function salvarNovaMedicao(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);

  // Gerar novo ID
  const novoId = medicoesMock.length + 1;
  const contrato = formData.get('contrato');
  const [contratoNumero, contratoNome] = contrato.split(' - ');

  // Encontrar próximo número sequencial para o contrato
  const medicoesContrato = medicoesMock.filter(m => m.contratoNumero === contratoNumero);
  const maxSequencial = Math.max(...medicoesContrato.map(m => m.numeroSequencial), 0);

  const valorMedido = parseFloat(formData.get('valorMedido')) || 0;
  const glosa = parseFloat(formData.get('glosa')) || 0;

  const novaMedicao = {
    id: novoId,
    numeroSequencial: maxSequencial + 1,
    contratoNumero: contratoNumero,
    contratoNome: contratoNome,
    periodoInicio: formData.get('periodoInicio'),
    periodoFim: formData.get('periodoFim'),
    valorMedido: valorMedido,
    glosa: glosa,
    valorAprovado: valorMedido - glosa,
    status: 'RASCUNHO',
    observacoes: formData.get('observacoes') || ''
  };

  medicoesMock.push(novaMedicao);
  alert('Medição criada com sucesso (simulação)!');
  document.getElementById('new-measurement-modal').classList.remove('active');
  form.reset();
  carregarMedicoes();
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM carregado, iniciando medicoes.js');
  carregarMedicoes();

  // Event listeners
  const filterContract = document.getElementById('filter-contract');
  const filterStatus = document.getElementById('filter-status');
  const searchMeasurements = document.getElementById('search-measurements');
  const newMeasurementForm = document.getElementById('new-measurement-form');

  if (filterContract) filterContract.addEventListener('change', filtrarMedicoes);
  if (filterStatus) filterStatus.addEventListener('change', filtrarMedicoes);
  if (searchMeasurements) searchMeasurements.addEventListener('input', filtrarMedicoes);
  if (newMeasurementForm) newMeasurementForm.addEventListener('submit', salvarNovaMedicao);
});