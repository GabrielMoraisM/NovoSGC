// js/financeiro.js
import {
  getEmpresas,
  getContratos,
  getBoletins,
  getFaturamentos,
  getPagamentos,
  createFaturamento,
  createPagamento
} from './api.js';

let empresas = [];
let contratos = [];
let boletinsAprovados = [];
let faturas = [];
let pagamentos = [];

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
    'PAGO': 'badge badge-pago',
    'PENDENTE': 'badge badge-pendente',
    'VENCIDO': 'badge badge-vencido'
  };
  const labels = {
    'PAGO': 'Pago',
    'PENDENTE': 'Pendente',
    'VENCIDO': 'Vencido'
  };
  return `<span class="${classes[status] || 'badge'}">${labels[status] || status}</span>`;
}

// ===== Carregar dados iniciais =====
async function carregarEmpresas() {
  try {
    empresas = await getEmpresas();
    console.log('Empresas carregadas:', empresas.length);
  } catch (error) {
    console.error('Erro ao carregar empresas:', error);
  }
}

async function carregarContratos() {
  try {
    contratos = await getContratos();
    console.log('Contratos carregados:', contratos.length);
  } catch (error) {
    console.error('Erro ao carregar contratos:', error);
  }
}

async function carregarBoletinsAprovados() {
  try {
    boletinsAprovados = await getBoletins({ status: 'APROVADO' });
    console.log('✅ Boletins aprovados carregados:', boletinsAprovados);
  } catch (error) {
    console.error('❌ Erro ao carregar boletins aprovados:', error);
  }
}

async function carregarFaturamentos() {
  try {
    faturas = await getFaturamentos({ limit: 1000 });
    console.log('Faturas carregadas:', faturas);
    renderizarFaturamentos(faturas);
    atualizarKPIs();
    atualizarImpostos();
  } catch (error) {
    console.error('Erro ao carregar faturamentos:', error);
  }
}

function renderizarFaturamentos(lista) {
  const tbody = document.querySelector('#invoices-table tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  lista.forEach(f => {
    const boletim = boletinsAprovados.find(b => b.id === f.bm_id);
    const contrato = boletim ? contratos.find(c => c.id === boletim.contrato_id) : null;
    const contratoNumero = contrato?.numero_contrato || '—';
    const cliente = empresas.find(e => e.id === f.cliente_id)?.razao_social || '—';

    const row = document.createElement('tr');
    row.innerHTML = `
      <td class="font-semibold">${f.numero_nf || '—'}</td>
      <td>${contratoNumero}</td>
      <td>${cliente}</td>
      <td>${formatarData(f.data_emissao)}</td>
      <td>${formatarData(f.data_vencimento)}</td>
      <td>${formatarMoeda(f.valor_bruto_nf)}</td>
      <td>${formatarMoeda(f.valor_liquido_nf)}</td>
      <td>${getStatusBadge(f.status)}</td>
      <td style="text-align: right;">
        <button class="btn-view-more" onclick="abrirDetalhesFaturamento(${f.id})">Detalhes</button>
      </td>
    `;
    tbody.appendChild(row);
  });
  document.getElementById('invoices-count').textContent = `Mostrando ${lista.length} de ${faturas.length} notas`;
}

async function carregarPagamentos() {
  try {
    pagamentos = await getPagamentos({ limit: 1000 }); // ou skip:0, limit:100
    renderizarPagamentos(pagamentos);
  } catch (error) {
    console.error('Erro ao carregar pagamentos:', error);
  }
}

function renderizarPagamentos(lista) {
  const tbody = document.querySelector('#payments-table tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  lista.forEach(p => {
    const fatura = faturas.find(f => f.id === p.faturamento_id);
    const boletim = fatura ? boletinsAprovados.find(b => b.id === fatura.bm_id) : null;
    const contrato = boletim ? contratos.find(c => c.id === boletim.contrato_id) : null;
    const cliente = fatura ? empresas.find(e => e.id === fatura.cliente_id)?.razao_social : '—';
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${formatarData(p.data_pagamento)}</td>
      <td>${fatura?.numero_nf || '—'}</td>
      <td>${contrato?.numero_contrato || '—'}</td>
      <td>${cliente}</td>
      <td>${formatarMoeda(p.valor_pago)}</td>
      <td>—</td>
      <td>${p.observacao || '-'}</td>
    `;
    tbody.appendChild(row);
  });
}

// ===== KPIs =====
function atualizarKPIs() {
  const totalRecebido = pagamentos.reduce((acc, p) => acc + p.valor_pago, 0);
  const totalPendente = faturas
    .filter(f => f.status === 'PENDENTE')
    .reduce((acc, f) => acc + f.valor_liquido_nf, 0);
  const totalVencido = faturas
    .filter(f => f.status === 'VENCIDO')
    .reduce((acc, f) => acc + f.valor_liquido_nf, 0);
  const totalNotas = faturas.length;

  document.getElementById('total-recebido').textContent = formatarMoeda(totalRecebido);
  document.getElementById('total-pendente').textContent = formatarMoeda(totalPendente);
  document.getElementById('total-vencido').textContent = formatarMoeda(totalVencido);
  document.getElementById('total-notas').textContent = totalNotas;
}

// ===== Impostos =====
function atualizarImpostos() {
  const iss = faturas.reduce((acc, f) => acc + (f.iss_retido || 0), 0);
  const inss = faturas.reduce((acc, f) => acc + (f.inss_retido || 0), 0);
  const irrf = faturas.reduce((acc, f) => acc + (f.irrf_retido || 0), 0);
  const csll = faturas.reduce((acc, f) => acc + (f.csll_retido || 0), 0);
  const pis = faturas.reduce((acc, f) => acc + (f.pis_retido || 0), 0);
  const cofins = faturas.reduce((acc, f) => acc + (f.cofins_retido || 0), 0);

  document.getElementById('tax-iss').textContent = formatarMoeda(iss);
  document.getElementById('tax-inss').textContent = formatarMoeda(inss);
  document.getElementById('tax-irrf').textContent = formatarMoeda(irrf);
  document.getElementById('tax-csll').textContent = formatarMoeda(csll);
  document.getElementById('tax-pis').textContent = formatarMoeda(pis);
  document.getElementById('tax-cofins').textContent = formatarMoeda(cofins);
  document.getElementById('tax-total').textContent = formatarMoeda(iss+inss+irrf+csll+pis+cofins);
}

// ===== Abas =====
function initTabs() {
  const tabs = document.querySelectorAll('.tab');
  const panels = {
    'invoices-panel': document.getElementById('invoices-panel'),
    'payments-panel': document.getElementById('payments-panel'),
    'taxes-panel': document.getElementById('taxes-panel')
  };
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.getAttribute('data-tab-target');
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      Object.values(panels).forEach(p => p.classList.remove('active'));
      if (panels[target]) panels[target].classList.add('active');
    });
  });
}

// ===== Filtros =====
function filtrarNotas() {
  const statusFiltro = document.getElementById('filter-invoice-status').value;
  const termo = document.getElementById('search-invoices').value.toLowerCase();
  const rows = document.querySelectorAll('#invoices-table tbody tr');
  rows.forEach(row => {
    const status = row.children[7].innerText; // coluna status
    const texto = row.innerText.toLowerCase();
    let show = true;
    if (statusFiltro && !status.includes(statusFiltro)) show = false;
    if (termo && !texto.includes(termo)) show = false;
    row.style.display = show ? '' : 'none';
  });
  const visible = [...rows].filter(r => r.style.display !== 'none').length;
  document.getElementById('invoices-count').textContent = `Mostrando ${visible} de ${faturas.length} notas`;
}

// ===== Modais =====
async function abrirModalNovaNF() {
  const selectBM = document.getElementById('invoice-bm');
  selectBM.innerHTML = '<option value="">Selecione...</option>';
  boletinsAprovados.forEach(b => {
    const opt = document.createElement('option');
    opt.value = b.id;
    const contrato = contratos.find(c => c.id === b.contrato_id);
    opt.textContent = `BM-${b.numero_sequencial} - ${contrato?.numero_contrato || 'Contrato'} - R$ ${b.valor_aprovado}`;
    selectBM.appendChild(opt);
  });

  const selectEmissora = document.getElementById('invoice-emissora');
  selectEmissora.innerHTML = '<option value="">Selecione...</option>';
  const emissoras = empresas.filter(e => ['MATRIZ', 'FILIAL'].includes(e.tipo));
  emissoras.forEach(e => {
    const opt = document.createElement('option');
    opt.value = e.id;
    opt.textContent = e.razao_social;
    selectEmissora.appendChild(opt);
  });

  document.getElementById('new-invoice-modal').classList.add('active');
}

async function salvarNovaNF(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);

  const bm_id = parseInt(formData.get('bmId'));
  if (!bm_id) {
    alert('Selecione um boletim.');
    return;
  }

  const boletim = boletinsAprovados.find(b => b.id === bm_id);
  if (!boletim) {
    alert('Boletim inválido.');
    return;
  }

  const contrato = contratos.find(c => c.id === boletim.contrato_id);
  if (!contrato) {
    alert('Contrato não encontrado para este boletim.');
    return;
  }

  const nfData = {
    bm_id,
    numero_nf: formData.get('numeroNf'),
    empresa_emissora_id: parseInt(formData.get('empresaEmissoraId')),
    cliente_id: contrato.cliente_id,
    valor_bruto_nf: parseFloat(formData.get('valorBruto')),
    data_emissao: formData.get('dataEmissao'),
    data_vencimento: formData.get('dataVencimento')
  };

  try {
    await createFaturamento(nfData);
    alert('NF criada com sucesso!');
    document.getElementById('new-invoice-modal').classList.remove('active');
    form.reset();
    await carregarFaturamentos();
    await carregarPagamentos();
  } catch (error) {
    alert('Erro: ' + error.message);
  }
}

async function abrirModalNovoPagamento() {
  // Filtra notas não quitadas e não canceladas
  const notasDisponiveis = faturas.filter(f => 
    f.status !== 'QUITADO' && f.status !== 'CANCELADO'
  );

  if (notasDisponiveis.length === 0) {
    alert('Não há notas fiscais disponíveis para pagamento.');
    return;
  }

  const selectNF = document.getElementById('payment-invoice');
  selectNF.innerHTML = '<option value="">Selecione...</option>';
  
  notasDisponiveis.forEach(f => {
    const opt = document.createElement('option');
    opt.value = f.id;
    opt.textContent = `${f.numero_nf} - ${formatarMoeda(f.valor_liquido_nf)} (${f.status})`;
    selectNF.appendChild(opt);
  });
  
  document.getElementById('new-payment-modal').classList.add('active');
}

async function salvarNovoPagamento(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);

  const pagData = {
    faturamento_id: parseInt(formData.get('faturamentoId')),
    data_pagamento: formData.get('dataPagamento'),
    valor_pago: parseFloat(formData.get('valorPago')),
    observacao: formData.get('observacao') || ''
  };

  try {
    await createPagamento(pagData);
    alert('Pagamento registrado!');
    document.getElementById('new-payment-modal').classList.remove('active');
    await carregarFaturamentos();
    await carregarPagamentos();
  } catch (error) {
    alert('Erro: ' + error.message);
  }
}

// ===== Detalhes da NF =====
window.abrirDetalhesFaturamento = function(id) {
  const fatura = faturas.find(f => f.id === id);
  if (!fatura) return;

  document.getElementById('detail-invoice-title').textContent = `Detalhes da NF`;
  document.getElementById('detail-invoice-subtitle').textContent = fatura.numero_nf || '—';
  document.getElementById('detail-valor-bruto').textContent = formatarMoeda(fatura.valor_bruto_nf);
  document.getElementById('detail-valor-liquido').textContent = formatarMoeda(fatura.valor_liquido_nf);
  document.getElementById('detail-status').innerHTML = getStatusBadge(fatura.status);

  const boletim = boletinsAprovados.find(b => b.id === fatura.bm_id);
  const contrato = boletim ? contratos.find(c => c.id === boletim.contrato_id) : null;
  document.getElementById('detail-bm').textContent = contrato ? `${contrato.numero_contrato} / BM-${boletim.numero_sequencial}` : '—';
  document.getElementById('detail-cliente').textContent = empresas.find(e => e.id === fatura.cliente_id)?.razao_social || '—';
  document.getElementById('detail-emissao').textContent = formatarData(fatura.data_emissao);
  document.getElementById('detail-vencimento').textContent = formatarData(fatura.data_vencimento);
  document.getElementById('detail-emissora').textContent = empresas.find(e => e.id === fatura.empresa_emissora_id)?.razao_social || '—';

  document.getElementById('detail-iss').textContent = formatarMoeda(fatura.iss_retido);
  document.getElementById('detail-inss').textContent = formatarMoeda(fatura.inss_retido);
  document.getElementById('detail-irrf').textContent = formatarMoeda(fatura.irrf_retido);
  document.getElementById('detail-csll').textContent = formatarMoeda(fatura.csll_retido);
  document.getElementById('detail-pis').textContent = formatarMoeda(fatura.pis_retido);
  document.getElementById('detail-cofins').textContent = formatarMoeda(fatura.cofins_retido);

  const pagamentosNF = pagamentos.filter(p => p.faturamento_id === id);
  const tbody = document.getElementById('detail-pagamentos');
  tbody.innerHTML = '';
  pagamentosNF.forEach(p => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${formatarData(p.data_pagamento)}</td>
      <td>${formatarMoeda(p.valor_pago)}</td>
      <td>${p.observacao || '-'}</td>
    `;
    tbody.appendChild(row);
  });

  document.getElementById('invoice-details-modal').classList.add('active');
};

// ===== Inicialização =====
document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'index.html';
    return;
  }

  await carregarEmpresas();
  await carregarContratos();
  await carregarBoletinsAprovados();
  await carregarFaturamentos();
  await carregarPagamentos();

  initTabs();

  document.getElementById('search-invoices')?.addEventListener('input', filtrarNotas);
  document.getElementById('filter-invoice-status')?.addEventListener('change', filtrarNotas);

  document.querySelector('[data-modal-open="new-invoice-modal"]')?.addEventListener('click', abrirModalNovaNF);
  document.querySelector('[data-modal-open="new-payment-modal"]')?.addEventListener('click', abrirModalNovoPagamento);

  document.getElementById('new-invoice-form')?.addEventListener('submit', salvarNovaNF);
  document.getElementById('new-payment-form')?.addEventListener('submit', salvarNovoPagamento);
});