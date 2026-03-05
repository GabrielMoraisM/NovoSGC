// js/medicoes.js
import { getBoletins, createBoletim, updateBoletim, getContratos } from './api.js';

// ===== Variáveis globais =====
let contratos = [];
let boletins = [];
let currentBoletimId = null;

// ===== Funções auxiliares =====
function formatarMoeda(valor) {
  if (valor == null || isNaN(valor)) return 'R$ 0,00';
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarData(dataStr) {
  if (!dataStr) return '—';
  const data = new Date(dataStr + 'T12:00:00');
  return data.toLocaleDateString('pt-BR');
}

function getStatusBadge(status) {
  const classes = {
    'RASCUNHO': 'badge-warning',
    'APROVADO': 'badge-primary',
    'FATURADO': 'badge-success',
    'CANCELADO': 'badge-danger'
  };
  const labels = {
    'RASCUNHO': 'Aguardando aprovação',
    'APROVADO': 'Aprovado',
    'FATURADO': 'Faturado',
    'CANCELADO': 'Cancelado'
  };
  return `<span class="badge ${classes[status] || 'badge-secondary'}">${labels[status] || status}</span>`;
}

// ===== Carregar contratos para o select de filtro e de criação =====
// ===== Carregar contratos para o select de criação e para o filtro =====
async function carregarContratosSelect() {
  try {
    contratos = await getContratos();
    // Select do formulário de criação (name="contrato_id")
    const selectCriar = document.querySelector('select[name="contrato_id"]');
    if (selectCriar) {
      selectCriar.innerHTML = '<option value="">Selecione um contrato</option>';
      contratos.forEach(c => {
        const option = document.createElement('option');
        option.value = c.id;
        option.textContent = `${c.numero_contrato} - ${c.nome_projeto || 'Sem nome'}`;
        selectCriar.appendChild(option);
      });
    }

    // Select do filtro (id="filter-contract")
    const selectFiltro = document.getElementById('filter-contract');
    if (selectFiltro) {
      selectFiltro.innerHTML = '<option value="">Todos os contratos</option>';
      contratos.forEach(c => {
        const option = document.createElement('option');
        option.value = c.id;
        option.textContent = `${c.numero_contrato} - ${c.nome_projeto || 'Sem nome'}`;
        selectFiltro.appendChild(option);
      });
    }
  } catch (error) {
    console.error('Erro ao carregar contratos:', error);
  }
}

// ===== Carregar todos os boletins (percorrendo contratos) =====
async function carregarBoletins() {
  boletins = [];
  try {
    // Se houver um endpoint global de boletins, use-o. Caso contrário, itera sobre contratos.
    if (typeof getBoletins === 'function' && getBoletins.length === 0) {
      // getBoletins sem parâmetros (endpoint global)
      boletins = await getBoletins();
    } else {
      // Fallback: busca boletins de cada contrato
      const contratos = await getContratos();
      for (const c of contratos) {
        try {
          const bmList = await getBoletins(c.id); // função que espera contrato_id
          boletins.push(...bmList);
        } catch (e) {
          console.warn(`Erro ao buscar boletins do contrato ${c.id}:`, e);
        }
      }
    }
    renderizarBoletins(boletins);
  } catch (error) {
    console.error('Erro ao carregar boletins:', error);
    alert('Não foi possível carregar as medições.');
  }
}

// ===== Renderizar cards de boletins =====
function renderizarBoletins(boletinsParaMostrar) {
  const grid = document.getElementById('measurements-grid');
  if (!grid) return;

  grid.innerHTML = '';
  boletinsParaMostrar.forEach(bm => {
    const card = document.createElement('div');
    card.className = `measurement-card ${bm.status === 'FATURADO' ? 'locked' : ''}`;
    card.setAttribute('data-id', bm.id);
    card.setAttribute('data-contrato', bm.contrato_id);
    card.setAttribute('data-status', bm.status);

    // Definir etapas do status
    const etapas = ['RASCUNHO', 'APROVADO', 'FATURADO'];
    const statusIndex = etapas.indexOf(bm.status);
    const statusSteps = etapas.map((etapa, index) => {
      let stepClass = '';
      if (index < statusIndex) stepClass = 'completed';
      else if (index === statusIndex) stepClass = 'current';
      return `<div class="status-step ${stepClass}" data-label="${etapa.substring(0,3)}"></div>`;
    }).join('');

    // Buscar número do contrato (opcional)
    const contrato = contratos.find(c => c.id === bm.contrato_id);
    const contratoNumero = contrato ? contrato.numero_contrato : bm.contrato_id;

    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="measurement-number">BM-${bm.numero_sequencial.toString().padStart(3, '0')}</div>
        ${bm.status === 'FATURADO' ? `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" style="color: var(--text-muted);">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
        ` : ''}
      </div>
      <div class="text-xs text-muted mt-1">Contrato: ${contratoNumero}</div>
      <div class="text-xs text-muted">${formatarData(bm.periodo_inicio)} a ${formatarData(bm.periodo_fim)}</div>
      
      <div class="measurement-status">
        ${statusSteps}
      </div>
      
      <div class="measurement-values">
        <div class="measurement-value">
          <span>Medido</span>
          <strong>${formatarMoeda(bm.valor_total_medido ?? 0)}</strong>
        </div>
        <div class="measurement-value">
          <span>Aprovado</span>
          <strong>${formatarMoeda(bm.valor_aprovado ?? 0)}</strong>
        </div>
      </div>
      
      <div style="margin-top: 1rem; display: flex; align-items: center; justify-content: space-between;">
        <div>${getStatusBadge(bm.status)}</div>
        <button class="btn-view-more" onclick="abrirDetalhesBoletim(${bm.id})">
          <span>Detalhes</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
    `;
    grid.appendChild(card);
  });

  atualizarResumo(boletinsParaMostrar);
}

// ===== Atualizar resumo acumulado =====
function atualizarResumo(boletinsFiltrados) {
  const total = boletinsFiltrados.length;
  const valorTotalMedido = boletinsFiltrados.reduce((acc, b) => acc + (b.valor_total_medido || 0), 0);
  const valorTotalAprovado = boletinsFiltrados.reduce((acc, b) => acc + (b.valor_aprovado || 0), 0);
  const valorTotalFaturado = boletinsFiltrados
    .filter(b => b.status === 'FATURADO')
    .reduce((acc, b) => acc + (b.valor_aprovado || 0), 0);

  document.getElementById('total-medicoes').textContent = total;
  document.getElementById('valor-total-medido').textContent = formatarMoeda(valorTotalMedido);
  document.getElementById('valor-total-aprovado').textContent = formatarMoeda(valorTotalAprovado);
  document.getElementById('valor-total-faturado').textContent = formatarMoeda(valorTotalFaturado);
}

// ===== Filtros =====
function filtrarBoletins() {
  const contratoFiltro = document.getElementById('filter-contract').value;
  const statusFiltro = document.getElementById('filter-status').value;
  const termo = document.getElementById('search-measurements').value.toLowerCase();

  const filtrados = boletins.filter(bm => {
    const contratoMatch = !contratoFiltro || bm.contrato_id == contratoFiltro; // comparação com ID numérico
    const statusMatch = !statusFiltro || bm.status === statusFiltro;
    // textoMatch pode permanecer baseado no número sequencial e, se quiser, no nome do contrato
    const contrato = contratos.find(c => c.id === bm.contrato_id);
    const textoContrato = contrato ? contrato.numero_contrato.toLowerCase() : '';
    const textoMatch = termo === '' || 
      bm.numero_sequencial.toString().includes(termo) ||
      textoContrato.includes(termo);
    return contratoMatch && statusMatch && textoMatch;
  });

  renderizarBoletins(filtrados);
}

// ===== FUNÇÕES DE MÁSCARA (copiadas de contratos.js) =====
function mascaraMoeda(valor) {
  let v = valor.replace(/\D/g, '');

  if (!v) return '0,00';

  v = (parseInt(v) / 100).toFixed(2);
  let partes = v.split('.');
  let inteiro = partes[0];
  let decimal = partes[1];

  inteiro = inteiro.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

  return inteiro + ',' + decimal;
}

function aplicarMascaraMoeda(event) {
  let input = event.target;
  input.value = mascaraMoeda(input.value);
}

function limparMascaraMoeda(valorFormatado) {
  let numero = valorFormatado.replace(/\./g, '').replace(',', '.');
  return parseFloat(numero) || 0;
}

// ===== Abrir detalhes do boletim =====
window.abrirDetalhesBoletim = function(boletimId) {
  const bm = boletins.find(b => b.id === boletimId);
  if (!bm) return;

  currentBoletimId = boletimId;

  document.getElementById('detail-measurement-title').textContent = `BM-${bm.numero_sequencial.toString().padStart(3, '0')}`;
  document.getElementById('detail-measurement-subtitle').textContent = `Contrato: ${bm.contrato_id}`;
  document.getElementById('detail-valor-medido').textContent = formatarMoeda(bm.valor_total_medido ?? 0);
  document.getElementById('detail-glosa').textContent = formatarMoeda(bm.valor_glosa ?? 0);
  document.getElementById('detail-valor-aprovado').textContent = formatarMoeda(bm.valor_aprovado ?? 0);
  document.getElementById('detail-contrato').textContent = bm.contrato_id;
  document.getElementById('detail-periodo').textContent = `${formatarData(bm.periodo_inicio)} a ${formatarData(bm.periodo_fim)}`;
  document.getElementById('detail-status').innerHTML = getStatusBadge(bm.status);
  document.getElementById('detail-observacoes').textContent = bm.observacoes || '—';

  const actionsDiv = document.getElementById('detail-actions');
  actionsDiv.innerHTML = '';

  if (bm.status === 'RASCUNHO') {
    actionsDiv.innerHTML = `
      <button class="btn btn-primary" onclick="alterarStatusBoletim(${bm.id}, 'APROVADO')">Aprovar</button>
      <button class="btn btn-secondary" onclick="editarBoletim(${bm.id})">Editar</button>
      <button class="btn btn-danger" onclick="alterarStatusBoletim(${bm.id}, 'CANCELADO')">Cancelar</button>
    `;
  } else if (bm.status === 'APROVADO') {
    actionsDiv.innerHTML = `
      <button class="btn btn-success" onclick="alterarStatusBoletim(${bm.id}, 'FATURADO')">Faturar</button>
      <button class="btn btn-secondary" onclick="editarBoletim(${bm.id})">Editar</button>
      <button class="btn btn-danger" onclick="alterarStatusBoletim(${bm.id}, 'CANCELADO')">Cancelar</button>
    `;
  } else if (bm.status === 'FATURADO') {
    actionsDiv.innerHTML = `<span class="text-sm text-muted">Medição já faturada – não pode ser alterada.</span>`;
  } else if (bm.status === 'CANCELADO') {
    actionsDiv.innerHTML = `<span class="text-sm text-muted">Medição cancelada.</span>`;
  }

  document.getElementById('measurement-details-modal').classList.add('active');
};

// ===== Alterar status do boletim (aprovar/cancelar/faturar) =====
window.alterarStatusBoletim = async function(id, novoStatus) {
  try {
    let motivo = null;
    if (novoStatus === 'CANCELADO') {
      motivo = prompt('Motivo do cancelamento:');
      if (motivo === null) return; // cancelou
    }
    const dados = { status: novoStatus };
    if (motivo) dados.cancelado_motivo = motivo;

    await updateBoletim(id, dados);
    alert(`Boletim ${novoStatus.toLowerCase()} com sucesso!`);
    await carregarBoletins(); // recarrega a lista
    if (document.getElementById('measurement-details-modal').classList.contains('active')) {
      abrirDetalhesBoletim(id);
    }
  } catch (error) {
    alert('Erro ao alterar status: ' + error.message);
  }
};

// ===== Editar boletim (placeholder) =====
window.editarBoletim = function(id) {
  alert('Edição não implementada ainda.');
};

// ===== Salvar novo boletim =====
async function salvarNovaMedicao(event) {
  event.preventDefault();
  
  const valorMedido = limparMascaraMoeda(
    document.querySelector('[name="valor_total_medido"]').value
  );

  const valorGlosa = limparMascaraMoeda(
    document.querySelector('[name="valor_glosa"]').value || '0'
  );

  const contratoId = document.querySelector('[name="contrato_id"]').value;

  const dados = {
    periodo_inicio: document.querySelector('[name="periodo_inicio"]').value,
    periodo_fim: document.querySelector('[name="periodo_fim"]').value,
    valor_total_medido: valorMedido,
    valor_glosa: valorGlosa,
    contrato_id: contratoId
    // observacoes removido por enquanto
  };
  
  try {
    await createBoletim(contratoId, dados);
    alert('Medição criada com sucesso!');
    document.getElementById('new-measurement-modal').classList.remove('active');
    await carregarBoletins();
  } catch (error) {
    alert('Erro: ' + error.message);
  }
}

// ===== Inicialização =====
document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'index.html';
    return;
  }

    document.querySelectorAll('.money-mask').forEach(campo => {
    campo.addEventListener('input', aplicarMascaraMoeda);
    // Bloqueia teclas não numéricas (opcional)
    campo.addEventListener('keydown', function(e) {
      const teclasPermitidas = [
        'Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight', 'Home', 'End'
      ];
      if (teclasPermitidas.includes(e.key)) return;
      if (e.key === ' ' || isNaN(Number(e.key))) {
        e.preventDefault();
      }
    });
  });
  await carregarContratosSelect();
  await carregarBoletins();

  document.getElementById('filter-contract')?.addEventListener('change', filtrarBoletins);
  document.getElementById('filter-status')?.addEventListener('change', filtrarBoletins);
  document.getElementById('search-measurements')?.addEventListener('input', filtrarBoletins);
  document.getElementById('new-measurement-form')?.addEventListener('submit', salvarNovaMedicao);
});