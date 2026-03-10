// js/prateleira.js
import {
  getPrateleiras,
  createPrateleira,
  updatePrateleira,
  cancelarPrateleira,
  marcarAguardandoMedicao,
  getResumoPrateleira,
  getContratos
} from './api.js';

// ═══════════════════════════════════════════════════════════
// Estado global
// ═══════════════════════════════════════════════════════════
let prateleiras = [];
let contratos = [];

// ═══════════════════════════════════════════════════════════
// Helpers de formatação
// ═══════════════════════════════════════════════════════════
function formatarMoeda(valor) {
  if (valor == null || isNaN(valor)) return 'R$ 0,00';
  return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarData(dataStr) {
  if (!dataStr) return '—';
  return new Date(dataStr + 'T12:00:00').toLocaleDateString('pt-BR');
}

function mascaraMoeda(valor) {
  let v = valor.replace(/\D/g, '');
  if (!v) return '0,00';
  v = (parseInt(v) / 100).toFixed(2);
  let [inteiro, decimal] = v.split('.');
  inteiro = inteiro.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return inteiro + ',' + decimal;
}

function limparMascara(valorFormatado) {
  return parseFloat(valorFormatado.replace(/\./g, '').replace(',', '.')) || 0;
}

// ═══════════════════════════════════════════════════════════
// Badge de status
// ═══════════════════════════════════════════════════════════
const STATUS_CONFIG = {
  PENDENTE: { label: 'Pendente', cor: '#856404', bg: '#fff3cd', dot: '#f0ad4e' },
  AGUARDANDO_MEDICAO: { label: 'Aguardando Medição', cor: '#004085', bg: '#cce5ff', dot: '#007bff' },
  INCLUIDO_EM_MEDICAO: { label: 'Incluído em Medição', cor: '#155724', bg: '#d4edda', dot: '#28a745' },
  CANCELADO: { label: 'Cancelado', cor: '#721c24', bg: '#f8d7da', dot: '#dc3545' },
};

function getStatusBadge(status) {
  const cfg = STATUS_CONFIG[status] || { label: status, cor: '#383d41', bg: '#e2e3e5', dot: '#6c757d' };
  return `
    <span class="prateleira-status-badge" style="background:${cfg.bg}; color:${cfg.cor};">
      <span class="status-dot" style="background:${cfg.dot};"></span>
      ${cfg.label}
    </span>`;
}

// ═══════════════════════════════════════════════════════════
// Carregar selects de contratos
// ═══════════════════════════════════════════════════════════
async function carregarContratosSelect() {
  try {
    contratos = await getContratos();

    // Select do filtro
    const filtroSelect = document.getElementById('filter-contrato');
    if (filtroSelect) {
      filtroSelect.innerHTML = '<option value="">Todos os contratos</option>';
      contratos.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = `${c.numero_contrato}`;
        filtroSelect.appendChild(opt);
      });
    }

    // Select do modal de criação
    const newSelect = document.getElementById('new-contrato-select');
    if (newSelect) {
      newSelect.innerHTML = '<option value="">Selecione um contrato</option>';
      contratos.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = `${c.numero_contrato}`;
        newSelect.appendChild(opt);
      });
    }
  } catch (err) {
    console.error('Erro ao carregar contratos:', err);
  }
}

// ═══════════════════════════════════════════════════════════
// Carregar resumo/métricas
// ═══════════════════════════════════════════════════════════
async function carregarResumo() {
  try {
    const resumo = await getResumoPrateleira();
    document.getElementById('summary-valor-total').textContent = formatarMoeda(resumo.valor_total_em_prateleira);
    document.getElementById('summary-qtd-pendentes').textContent = resumo.qtd_execucoes_pendentes;
    document.getElementById('summary-qtd-aguardando').textContent = resumo.qtd_execucoes_aguardando;
    document.getElementById('summary-antigas').textContent = resumo.qtd_execucoes_antigas_30dias;
  } catch (err) {
    console.error('Erro ao carregar resumo da prateleira:', err);
  }
}

// ═══════════════════════════════════════════════════════════
// Carregar lista de execuções
// ═══════════════════════════════════════════════════════════
async function carregarPrateleiras() {
  try {
    prateleiras = await getPrateleiras();
    renderizarPrateleiras(prateleiras);
  } catch (err) {
    console.error('Erro ao carregar prateleira:', err);
    document.getElementById('prateleira-list').innerHTML = `
      <tr><td colspan="8">
        <div class="empty-state">
          <p style="color: var(--danger);">Erro ao carregar dados. Verifique a conexão com a API.</p>
        </div>
      </td></tr>`;
  }
}

// ═══════════════════════════════════════════════════════════
// Renderizar tabela
// ═══════════════════════════════════════════════════════════
function renderizarPrateleiras(lista) {
  const tbody = document.getElementById('prateleira-list');
  if (!tbody) return;

  if (!lista || lista.length === 0) {
    tbody.innerHTML = `
      <tr><td colspan="8">
        <div class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
            <path d="M2 20h20"></path><path d="M5 20V8h14v12"></path>
            <path d="M9 20v-5h6v5"></path><path d="M2 8l10-6 10 6"></path>
          </svg>
          <p>Nenhuma execução encontrada na prateleira.</p>
          <p class="text-xs">Clique em "Nova Execução" para registrar um serviço executado.</p>
        </div>
      </td></tr>`;
    document.getElementById('prateleira-count').textContent = '0 registros';
    return;
  }

  tbody.innerHTML = '';
  lista.forEach(item => {
    const saldo = Number(item.saldo_disponivel ?? (item.valor_estimado - item.valor_medido_acumulado));
    const pctMedido = item.valor_estimado > 0
      ? Math.min(100, (item.valor_medido_acumulado / item.valor_estimado) * 100)
      : 0;

    const contrato = contratos.find(c => c.id === item.contrato_id);
    const contratoLabel = item.contrato_numero || (contrato ? contrato.numero_contrato : `#${item.contrato_id}`);

    const podeEditar = !['INCLUIDO_EM_MEDICAO', 'CANCELADO'].includes(item.status);
    const podeAguardar = item.status === 'PENDENTE';
    const podeCancelar = !['INCLUIDO_EM_MEDICAO', 'CANCELADO'].includes(item.status);

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <span class="font-semibold text-sm">${contratoLabel}</span>
      </td>
      <td>
        <div style="max-width: 280px;">
          <div class="text-sm font-semibold" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${item.descricao_servico}">
            ${item.descricao_servico}
          </div>
          ${item.percentual_executado != null ? `<div class="text-xs text-muted">${item.percentual_executado}% executado</div>` : ''}
        </div>
      </td>
      <td class="text-sm">${formatarData(item.data_execucao)}</td>
      <td class="text-sm" style="text-align:right;">${formatarMoeda(item.valor_estimado)}</td>
      <td style="text-align:right;">
        <div class="text-sm">${formatarMoeda(item.valor_medido_acumulado)}</div>
        <div class="saldo-bar" style="width: 80px; margin-left: auto;">
          <div class="saldo-bar-fill" style="width: ${pctMedido.toFixed(0)}%;"></div>
        </div>
      </td>
      <td class="text-sm font-semibold" style="text-align:right; color: ${saldo > 0 ? 'var(--primary)' : 'var(--text-muted)'};">
        ${formatarMoeda(saldo)}
      </td>
      <td>${getStatusBadge(item.status)}</td>
      <td style="text-align:right; white-space: nowrap;">
        ${podeAguardar ? `
          <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size:0.75rem;" onclick="window.aguardarMedicao(${item.id})" title="Marcar como Aguardando Medição">
            ⏳
          </button>` : ''}
        ${podeEditar ? `
          <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size:0.75rem;" onclick="window.abrirEdicao(${item.id})" title="Editar">
            ✏️
          </button>` : ''}
        ${podeCancelar ? `
          <button class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size:0.75rem;" onclick="window.abrirCancelamento(${item.id})" title="Cancelar">
            ✕
          </button>` : ''}
        ${!podeEditar && !podeCancelar ? `<span class="text-xs text-muted">—</span>` : ''}
      </td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById('prateleira-count').textContent =
    `${lista.length} registro${lista.length !== 1 ? 's' : ''}`;
}

// ═══════════════════════════════════════════════════════════
// Filtros
// ═══════════════════════════════════════════════════════════
function filtrar() {
  const contratoId = document.getElementById('filter-contrato').value;
  const status = document.getElementById('filter-status').value;
  const termo = document.getElementById('search-prateleira').value.toLowerCase();

  const filtrados = prateleiras.filter(item => {
    const matchContrato = !contratoId || String(item.contrato_id) === String(contratoId);
    const matchStatus = !status || item.status === status;
    const matchTermo = !termo ||
      item.descricao_servico.toLowerCase().includes(termo) ||
      (item.contrato_numero || '').toLowerCase().includes(termo);
    return matchContrato && matchStatus && matchTermo;
  });

  renderizarPrateleiras(filtrados);
}

// ═══════════════════════════════════════════════════════════
// Criar execução
// ═══════════════════════════════════════════════════════════
async function salvarNovaExecucao(event) {
  event.preventDefault();
  const form = event.target;

  const contratoId = form.querySelector('[name="contrato_id"]').value;
  if (!contratoId) {
    alert('Selecione um contrato.');
    return;
  }

  const valorStr = form.querySelector('[name="valor_estimado"]').value;
  const valorNum = limparMascara(valorStr);
  if (valorNum <= 0) {
    alert('Informe um valor estimado maior que zero.');
    return;
  }

  const pctStr = form.querySelector('[name="percentual_executado"]').value;
  const data = {
    descricao_servico: form.querySelector('[name="descricao_servico"]').value,
    data_execucao: form.querySelector('[name="data_execucao"]').value,
    percentual_executado: pctStr ? parseFloat(pctStr) : null,
    valor_estimado: valorNum,
    observacoes: form.querySelector('[name="observacoes"]').value || null,
  };

  try {
    await createPrateleira(contratoId, data);
    document.getElementById('new-execucao-modal').classList.remove('active');
    form.reset();
    await Promise.all([carregarPrateleiras(), carregarResumo()]);
  } catch (err) {
    alert('Erro ao salvar: ' + err.message);
  }
}

// ═══════════════════════════════════════════════════════════
// Editar execução
// ═══════════════════════════════════════════════════════════
window.abrirEdicao = function(id) {
  const item = prateleiras.find(p => p.id === id);
  if (!item) return;

  document.getElementById('edit-execucao-id').value = id;
  document.getElementById('edit-descricao').value = item.descricao_servico;
  document.getElementById('edit-data-execucao').value = item.data_execucao;
  document.getElementById('edit-percentual').value = item.percentual_executado ?? '';
  document.getElementById('edit-valor-estimado').value = mascaraMoeda(
    String(Math.round(item.valor_estimado * 100))
  );
  document.getElementById('edit-observacoes').value = item.observacoes ?? '';
  document.getElementById('edit-execucao-modal').classList.add('active');
};

async function salvarEdicao(event) {
  event.preventDefault();
  const form = event.target;
  const id = form.querySelector('[name="execucao_id"]').value;

  const valorStr = form.querySelector('[name="valor_estimado"]').value;
  const valorNum = limparMascara(valorStr);
  const pctStr = form.querySelector('[name="percentual_executado"]').value;

  const data = {
    descricao_servico: form.querySelector('[name="descricao_servico"]').value,
    data_execucao: form.querySelector('[name="data_execucao"]').value,
    percentual_executado: pctStr ? parseFloat(pctStr) : null,
    valor_estimado: valorNum,
    observacoes: form.querySelector('[name="observacoes"]').value || null,
  };

  try {
    await updatePrateleira(id, data);
    document.getElementById('edit-execucao-modal').classList.remove('active');
    await Promise.all([carregarPrateleiras(), carregarResumo()]);
  } catch (err) {
    alert('Erro ao atualizar: ' + err.message);
  }
}

// ═══════════════════════════════════════════════════════════
// Aguardar medição
// ═══════════════════════════════════════════════════════════
window.aguardarMedicao = async function(id) {
  const item = prateleiras.find(p => p.id === id);
  if (!item) return;
  if (!confirm(`Marcar "${item.descricao_servico.substring(0, 60)}" como Aguardando Medição?`)) return;

  try {
    await marcarAguardandoMedicao(id);
    await Promise.all([carregarPrateleiras(), carregarResumo()]);
  } catch (err) {
    alert('Erro: ' + err.message);
  }
};

// ═══════════════════════════════════════════════════════════
// Cancelar execução
// ═══════════════════════════════════════════════════════════
window.abrirCancelamento = function(id) {
  document.getElementById('cancelar-execucao-id').value = id;
  document.getElementById('cancelar-motivo').value = '';
  document.getElementById('cancelar-execucao-modal').classList.add('active');
};

async function confirmarCancelamento(event) {
  event.preventDefault();
  const form = event.target;
  const id = form.querySelector('[name="execucao_id"]').value;
  const motivo = form.querySelector('[name="motivo"]').value.trim();

  if (!motivo) {
    alert('Informe o motivo do cancelamento.');
    return;
  }

  try {
    await cancelarPrateleira(id, motivo);
    document.getElementById('cancelar-execucao-modal').classList.remove('active');
    await Promise.all([carregarPrateleiras(), carregarResumo()]);
  } catch (err) {
    alert('Erro ao cancelar: ' + err.message);
  }
}

// ═══════════════════════════════════════════════════════════
// Máscara monetária
// ═══════════════════════════════════════════════════════════
function ativarMascaras() {
  document.querySelectorAll('.money-mask').forEach(campo => {
    campo.addEventListener('input', e => { e.target.value = mascaraMoeda(e.target.value); });
    campo.addEventListener('keydown', e => {
      const permitidas = ['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight', 'Home', 'End'];
      if (!permitidas.includes(e.key) && (e.key === ' ' || isNaN(Number(e.key)))) {
        e.preventDefault();
      }
    });
  });
}

// ═══════════════════════════════════════════════════════════
// Inicialização
// ═══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'index.html';
    return;
  }

  ativarMascaras();

  // Carrega dados em paralelo
  await Promise.all([
    carregarContratosSelect(),
    carregarPrateleiras(),
    carregarResumo(),
  ]);

  // Event listeners — filtros
  document.getElementById('filter-contrato')?.addEventListener('change', filtrar);
  document.getElementById('filter-status')?.addEventListener('change', filtrar);
  document.getElementById('search-prateleira')?.addEventListener('input', filtrar);

  // Event listeners — formulários
  document.getElementById('new-execucao-form')?.addEventListener('submit', salvarNovaExecucao);
  document.getElementById('edit-execucao-form')?.addEventListener('submit', salvarEdicao);
  document.getElementById('cancelar-execucao-form')?.addEventListener('submit', confirmarCancelamento);
});
