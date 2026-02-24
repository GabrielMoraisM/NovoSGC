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

// ===== Estado global =====
let empresas = [];
let contratos = [];
let boletinsAprovados = [];
let faturas = [];
let pagamentos = [];

let contratoSelecionado = null; // ID do contrato selecionado (null = todos)

// Paginação
let invoicesPage = 1;
let invoicesLimit = 10;
let paymentsPage = 1;
let paymentsLimit = 10;

// Filtros atuais
let currentInvoiceFilter = { status: '', search: '', startDate: '', endDate: '' };
let currentPaymentFilter = { search: '' };
// Filtros de impostos
let taxFilterStart = '';
let taxFilterEnd = '';

// ===== Utilitários =====
function formatarMoeda(valor) {
  if (valor == null || isNaN(valor)) return 'R$ 0,00';
  return parseFloat(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarData(dataStr) {
  if (!dataStr) return '—';
  const data = new Date(dataStr + 'T12:00:00');
  return data.toLocaleDateString('pt-BR');
}

function getStatusBadge(status) {
  const classes = {
    'QUITADO': 'badge badge-pago',
    'PAGO': 'badge badge-pago',
    'PARCIAL': 'badge badge-warning',
    'PENDENTE': 'badge badge-pendente',
    'VENCIDO': 'badge badge-vencido',
    'CANCELADA': 'badge badge-secondary',
    'CANCELADO': 'badge badge-secondary'
  };
  const labels = {
    'QUITADO': 'Quitado',
    'PAGO': 'Pago',
    'PARCIAL': 'Parcial',
    'PENDENTE': 'Pendente',
    'VENCIDO': 'Vencido',
    'CANCELADA': 'Cancelado',
    'CANCELADO': 'Cancelado'
  };
  return `<span class="${classes[status] || 'badge'}">${labels[status] || status}</span>`;
}

// ===== Funções auxiliares de cálculo =====
function calcularTotalPago(faturaId) {
    return pagamentos
        .filter(p => Number(p.faturamento_id) === Number(faturaId))
        .reduce((acc, p) => acc + (Number(p.valor_pago) || 0), 0);
}

function calcularSaldoDevedor(fatura) {
    // Se a nota estiver cancelada, saldo é zero
    if (fatura.status === 'CANCELADA' || fatura.status === 'CANCELADO') return 0;
    const totalPago = calcularTotalPago(fatura.id);
    return (Number(fatura.valor_liquido_nf) || 0) - totalPago;
}


function isVencida(dataVencimento) {
  if (!dataVencimento) return false;
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  const venc = new Date(dataVencimento + 'T12:00:00');
  return venc < hoje;
}

function mostrarToast(mensagem, tipo = 'success') {
  const toast = document.getElementById('toast');
  if (!toast) {
    alert(mensagem);
    return;
  }
  toast.textContent = mensagem;
  toast.className = `toast toast-${tipo} show`;
  setTimeout(() => {
    toast.className = 'toast hidden';
  }, 3000);
}

// ===== Carregar dados iniciais =====
async function carregarEmpresas() {
  try {
    empresas = await getEmpresas();
    console.log('Empresas carregadas:', empresas.length);
  } catch (error) {
    console.error('Erro ao carregar empresas:', error);
    mostrarToast('Erro ao carregar empresas', 'error');
  }
}

async function carregarContratos() {
  try {
    contratos = await getContratos();
    console.log('Contratos carregados:', contratos.length);
    preencherSeletorContratos();
  } catch (error) {
    console.error('Erro ao carregar contratos:', error);
    mostrarToast('Erro ao carregar contratos', 'error');
  }
}

function preencherSeletorContratos() {
  const select = document.getElementById('contrato-selector');
  if (!select) return;
  select.innerHTML = '<option value="">Todos os Contratos</option>';
  contratos.forEach(c => {
    const option = document.createElement('option');
    option.value = c.id;
    option.textContent = `${c.numero_contrato} - ${c.nome || 'Sem nome'}`;
    select.appendChild(option);
  });
}

async function carregarBoletinsAprovados() {
  try {
    const filtros = { status: 'APROVADO' };
    if (contratoSelecionado) {
      filtros.contrato_id = contratoSelecionado;
    }
    boletinsAprovados = await getBoletins(filtros);
    console.log('✅ Boletins aprovados carregados:', boletinsAprovados.length);
  } catch (error) {
    console.error('❌ Erro ao carregar boletins aprovados:', error);
  }
}

// ===== Controle de carregamento síncrono =====
let loadingFaturas = false;
let loadingPagamentos = false;

async function carregarFaturamentos() {
    loadingFaturas = true;
    try {
        const filtros = { limit: 1000 };
        if (contratoSelecionado) {
            filtros.contrato_id = contratoSelecionado;
        }
        faturas = await getFaturamentos(filtros);
        console.log('Faturas carregadas:', faturas.length);

        // Atualizar status VENCIDO
        const hoje = new Date().toISOString().split('T')[0];
        faturas.forEach(f => {
            if (f.status === 'PENDENTE' && f.data_vencimento < hoje) {
                f.status = 'VENCIDO';
            }
        });
    } catch (error) {
        console.error('Erro ao carregar faturamentos:', error);
        mostrarToast('Erro ao carregar notas fiscais', 'error');
    } finally {
        loadingFaturas = false;
        tentarRenderizar();
    }
}

async function carregarPagamentos() {
    loadingPagamentos = true;
    try {
        const filtros = { limit: 1000 };
        if (contratoSelecionado) {
            filtros.contrato_id = contratoSelecionado;
        }
        pagamentos = await getPagamentos(filtros);
        console.log('Pagamentos carregados:', pagamentos.length);
    } catch (error) {
        console.error('Erro ao carregar pagamentos:', error);
        mostrarToast('Erro ao carregar pagamentos', 'error');
    } finally {
        loadingPagamentos = false;
        tentarRenderizar();
    }
}

// ===== Filtros e renderização de notas =====
function aplicarFiltrosFaturamentos() {
  let lista = [...faturas];

  // Filtro por status
  if (currentInvoiceFilter.status) {
    lista = lista.filter(f => f.status === currentInvoiceFilter.status);
  }

  // Filtro por texto (busca em número da NF, contrato, cliente)
  if (currentInvoiceFilter.search) {
    const termo = currentInvoiceFilter.search.toLowerCase();
    lista = lista.filter(f => {
      const boletim = boletinsAprovados.find(b => b.id === f.bm_id);
      const contrato = boletim ? contratos.find(c => c.id === boletim.contrato_id) : null;
      const cliente = empresas.find(e => e.id === f.cliente_id)?.razao_social || '';
      return (f.numero_nf && f.numero_nf.toLowerCase().includes(termo)) ||
             (contrato?.numero_contrato && contrato.numero_contrato.toLowerCase().includes(termo)) ||
             cliente.toLowerCase().includes(termo);
    });
  }

  // Filtro por data de emissão
  if (currentInvoiceFilter.startDate) {
    lista = lista.filter(f => f.data_emissao >= currentInvoiceFilter.startDate);
  }
  if (currentInvoiceFilter.endDate) {
    lista = lista.filter(f => f.data_emissao <= currentInvoiceFilter.endDate);
  }

  renderizarFaturamentosPaginado(lista);
}

function renderizarFaturamentosPaginado(lista) {
  const total = lista.length;
  const start = (invoicesPage - 1) * invoicesLimit;
  const end = start + invoicesLimit;
  const pagina = lista.slice(start, end);

  renderizarTabelaFaturamentos(pagina);

  document.getElementById('invoices-count').textContent =
    `Mostrando ${start + 1}-${Math.min(end, total)} de ${total} notas`;
  document.getElementById('invoices-page-info').textContent = invoicesPage;

  document.getElementById('prev-invoices-page').disabled = invoicesPage === 1;
  document.getElementById('next-invoices-page').disabled = end >= total;
}

function renderizarTabelaFaturamentos(lista) {
    const tbody = document.querySelector('#invoices-table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center">Nenhuma nota fiscal encontrada.</td></tr>';
        return;
    }

    lista.forEach(f => {
        const boletim = boletinsAprovados.find(b => b.id === f.bm_id);
        const contrato = boletim ? contratos.find(c => c.id === boletim.contrato_id) : null;
        const contratoNumero = contrato?.numero_contrato || '—';
        const cliente = empresas.find(e => e.id === f.cliente_id)?.razao_social || '—';

        const totalPago = calcularTotalPago(f.id);
        const saldoDevedor = calcularSaldoDevedor(f);

        // Determina status real
        let statusReal = f.status;
        if (f.status !== 'CANCELADA' && f.status !== 'CANCELADO') {
            if (saldoDevedor <= 0.01) {
                statusReal = 'QUITADO';
            } else if (totalPago > 0) {
                statusReal = 'PARCIAL';
            } else if (isVencida(f.data_vencimento) && f.status === 'PENDENTE') {
                statusReal = 'VENCIDO';
            }
        }

        const rowClass = statusReal === 'VENCIDO' ? 'vencido' : '';

        const row = document.createElement('tr');
        row.className = rowClass;
        row.innerHTML = `
            <td class="font-semibold">${f.numero_nf || '—'}</td>
            <td>${contratoNumero}</td>
            <td>${cliente}</td>
            <td>${formatarData(f.data_emissao)}</td>
            <td>${formatarData(f.data_vencimento)}</td>
            <td>${formatarMoeda(f.valor_bruto_nf)}</td>
            <td>${formatarMoeda(f.valor_liquido_nf)}</td>
            <td>${formatarMoeda(saldoDevedor)}</td>
            <td>${getStatusBadge(statusReal)}</td>
            <td style="text-align: right;">
                <button class="btn-view-more" onclick="abrirDetalhesFaturamento(${f.id})">Detalhes</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// ===== Filtros e renderização de pagamentos =====
function aplicarFiltrosPagamentos() {
  let lista = [...pagamentos];

  if (currentPaymentFilter.search) {
    const termo = currentPaymentFilter.search.toLowerCase();
    lista = lista.filter(p => {
      const fatura = faturas.find(f => f.id === p.faturamento_id);
      return (fatura?.numero_nf && fatura.numero_nf.toLowerCase().includes(termo)) ||
             p.observacao?.toLowerCase().includes(termo);
    });
  }

  renderizarPagamentosPaginado(lista);
}

function renderizarPagamentosPaginado(lista) {
  const total = lista.length;
  const start = (paymentsPage - 1) * paymentsLimit;
  const end = start + paymentsLimit;
  const pagina = lista.slice(start, end);

  renderizarTabelaPagamentos(pagina);

  document.getElementById('payments-count').textContent =
    `Mostrando ${start + 1}-${Math.min(end, total)} de ${total} pagamentos`;
  document.getElementById('payments-page-info').textContent = paymentsPage;

  document.getElementById('prev-payments-page').disabled = paymentsPage === 1;
  document.getElementById('next-payments-page').disabled = end >= total;
}

function renderizarTabelaPagamentos(lista) {
  const tbody = document.querySelector('#payments-table tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (lista.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center">Nenhum pagamento encontrado.</td></tr>';
    return;
  }

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
      <td>${p.observacao || '-'}</td>
      <td style="text-align: right;">
        ${p.comprovante_url ? `<a href="${p.comprovante_url}" target="_blank">Ver</a>` : '-'}
      </td>
    `;
    tbody.appendChild(row);
  });
}

// ===== KPIs =====
function atualizarKPIs() {
  const totalRecebido = pagamentos.reduce((acc, p) => acc + (Number(p.valor_pago) || 0), 0);
  const totalAReceber = faturas
    .filter(f => f.status !== 'CANCELADA' && f.status !== 'QUITADO')
    .reduce((acc, f) => acc + calcularSaldoDevedor(f), 0);
  const totalPendente = faturas
    .filter(f => f.status === 'PENDENTE')
    .reduce((acc, f) => acc + calcularSaldoDevedor(f), 0);
  const totalVencido = faturas
    .filter(f => f.status === 'VENCIDO')
    .reduce((acc, f) => acc + calcularSaldoDevedor(f), 0);
  const totalNotas = faturas.length;

  document.getElementById('total-recebido').textContent = formatarMoeda(totalRecebido);
  document.getElementById('total-pendente').textContent = formatarMoeda(totalPendente);
  document.getElementById('total-vencido').textContent = formatarMoeda(totalVencido);
  document.getElementById('total-notas').textContent = totalNotas;

  // Opcional: adicionar um novo card de "A Receber"
  const aReceberEl = document.getElementById('total-a-receber');
  if (aReceberEl) aReceberEl.textContent = formatarMoeda(totalAReceber);
}

// ===== Impostos =====
function atualizarImpostos() {
  console.log('Faturas para impostos:', faturas);
  
  // Aplica filtro de período
  let faturasFiltradas = [...faturas];
  if (taxFilterStart) {
    faturasFiltradas = faturasFiltradas.filter(f => f.data_emissao >= taxFilterStart);
  }
  if (taxFilterEnd) {
    faturasFiltradas = faturasFiltradas.filter(f => f.data_emissao <= taxFilterEnd);
  }

  const iss = faturasFiltradas.reduce((acc, f) => acc + (Number(f.iss_retido) || 0), 0);
  const inss = faturasFiltradas.reduce((acc, f) => acc + (Number(f.inss_retido) || 0), 0);
  const irrf = faturasFiltradas.reduce((acc, f) => acc + (Number(f.irrf_retido) || 0), 0);
  const csll = faturasFiltradas.reduce((acc, f) => acc + (Number(f.csll_retido) || 0), 0);
  const pis = faturasFiltradas.reduce((acc, f) => acc + (Number(f.pis_retido) || 0), 0);
  const cofins = faturasFiltradas.reduce((acc, f) => acc + (Number(f.cofins_retido) || 0), 0);

  console.log('Totais calculados:', { iss, inss, irrf, csll, pis, cofins });

  document.getElementById('tax-iss').textContent = formatarMoeda(iss);
  document.getElementById('tax-inss').textContent = formatarMoeda(inss);
  document.getElementById('tax-irrf').textContent = formatarMoeda(irrf);
  document.getElementById('tax-csll').textContent = formatarMoeda(csll);
  document.getElementById('tax-pis').textContent = formatarMoeda(pis);
  document.getElementById('tax-cofins').textContent = formatarMoeda(cofins);
  document.getElementById('tax-total').textContent = formatarMoeda(iss + inss + irrf + csll + pis + cofins);

  // Renderiza tabela detalhada e gráfico com as faturas filtradas
  renderizarTabelaImpostos(faturasFiltradas);
  renderizarGraficoImpostos(faturasFiltradas);
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
      Object.values(panels).forEach(p => p?.classList.remove('active'));
      if (panels[target]) panels[target].classList.add('active');
    });
  });
}

// ===== Modais =====
async function abrirModalNovaNF() {
  const selectBM = document.getElementById('invoice-bm');
  selectBM.innerHTML = '<option value="">Selecione...</option>';

  const boletinsFiltrados = contratoSelecionado
    ? boletinsAprovados.filter(b => {
        const contrato = contratos.find(c => c.id === b.contrato_id);
        return contrato && contrato.id === contratoSelecionado;
      })
    : boletinsAprovados;

  if (boletinsFiltrados.length === 0) {
    mostrarToast('Não há boletins aprovados disponíveis para este contrato.', 'info');
    return;
  }

  boletinsFiltrados.forEach(b => {
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
    mostrarToast('Selecione um boletim.', 'error');
    return;
  }

  const boletim = boletinsAprovados.find(b => b.id === bm_id);
  if (!boletim) {
    mostrarToast('Boletim inválido.', 'error');
    return;
  }

  const contrato = contratos.find(c => c.id === boletim.contrato_id);
  if (!contrato) {
    mostrarToast('Contrato não encontrado para este boletim.', 'error');
    return;
  }

  const valorBruto = parseFloat(formData.get('valorBruto'));
  if (valorBruto > boletim.valor_aprovado) {
    mostrarToast('Valor da NF não pode ser maior que o valor aprovado do boletim.', 'error');
    return;
  }

  const nfData = {
    bm_id,
    numero_nf: formData.get('numeroNf'),
    empresa_emissora_id: parseInt(formData.get('empresaEmissoraId')),
    cliente_id: contrato.cliente_id,
    valor_bruto_nf: valorBruto,
    data_emissao: formData.get('dataEmissao'),
    data_vencimento: formData.get('dataVencimento')
  };

  try {
    await createFaturamento(nfData);
    mostrarToast('NF criada com sucesso!');
    document.getElementById('new-invoice-modal').classList.remove('active');
    form.reset();
    await carregarFaturamentos();
    await carregarPagamentos();
  } catch (error) {
    console.error(error);
    mostrarToast('Erro ao criar NF: ' + error.message, 'error');
  }
}

async function abrirModalNovoPagamento() {
  const notasDisponiveis = faturas.filter(f =>
    f.status !== 'QUITADO' && f.status !== 'CANCELADA' && calcularSaldoDevedor(f) > 0
  );

  if (notasDisponiveis.length === 0) {
    mostrarToast('Não há notas fiscais disponíveis para pagamento.', 'info');
    return;
  }

  const selectNF = document.getElementById('payment-invoice');
  selectNF.innerHTML = '<option value="">Selecione...</option>';

  notasDisponiveis.forEach(f => {
    const opt = document.createElement('option');
    opt.value = f.id;
    const saldo = calcularSaldoDevedor(f);
    opt.textContent = `${f.numero_nf} - Saldo: ${formatarMoeda(saldo)} (${f.status})`;
    selectNF.appendChild(opt);
  });

  selectNF.addEventListener('change', function() {
    const selectedId = parseInt(this.value);
    if (selectedId) {
      const fatura = faturas.find(f => f.id === selectedId);
      if (fatura) {
        const saldo = calcularSaldoDevedor(fatura);
        document.getElementById('payment-valor').value = saldo.toFixed(2);
      }
    }
  });

  document.getElementById('new-payment-modal').classList.add('active');
}

async function salvarNovoPagamento(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);

  const faturamento_id = parseInt(formData.get('faturamentoId'));
  if (!faturamento_id) {
    mostrarToast('Selecione uma nota fiscal.', 'error');
    return;
  }

  const fatura = faturas.find(f => f.id === faturamento_id);
  if (!fatura) {
    mostrarToast('Nota fiscal não encontrada.', 'error');
    return;
  }

  const saldoDevedor = calcularSaldoDevedor(fatura);
  const valorPago = parseFloat(formData.get('valorPago'));

  if (valorPago <= 0) {
    mostrarToast('Valor pago deve ser maior que zero.', 'error');
    return;
  }

  if (valorPago > saldoDevedor + 0.01) {
    mostrarToast(`Valor pago (${formatarMoeda(valorPago)}) excede o saldo devedor (${formatarMoeda(saldoDevedor)}).`, 'error');
    return;
  }

  const pagData = {
    faturamento_id,
    data_pagamento: formData.get('dataPagamento'),
    valor_pago: valorPago,
    observacao: formData.get('observacao') || ''
  };

  try {
    await createPagamento(pagData);
    mostrarToast('Pagamento registrado!');
    document.getElementById('new-payment-modal').classList.remove('active');
    form.reset();
    await carregarFaturamentos();
    await carregarPagamentos();
  } catch (error) {
    console.error(error);
    mostrarToast('Erro ao registrar pagamento: ' + error.message, 'error');
  }
}

// ===== Detalhes da NF =====
window.abrirDetalhesFaturamento = function(id) {
  console.log('🔍 abrirDetalhesFaturamento chamado com id:', id);

  const modal = document.getElementById('invoice-details-modal');
  if (!modal) {
    console.error('Modal de detalhes não encontrado!');
    return;
  }

  const fatura = faturas.find(f => f.id === id);
  if (!fatura) {
    console.error('Fatura não encontrada com id:', id);
    alert('Fatura não encontrada.');
    return;
  }
  console.log('Fatura encontrada:', fatura);

  document.getElementById('detail-invoice-title').textContent = `Detalhes da NF`;
  document.getElementById('detail-invoice-subtitle').textContent = fatura.numero_nf || '—';
  document.getElementById('detail-valor-bruto').textContent = formatarMoeda(fatura.valor_bruto_nf);
  document.getElementById('detail-valor-liquido').textContent = formatarMoeda(fatura.valor_liquido_nf);

  const totalPago = calcularTotalPago(id);
  const saldoDevedor = calcularSaldoDevedor(fatura);
  console.log('💰 Total pago calculado:', totalPago);
  console.log('💰 Saldo devedor:', saldoDevedor);

  let statusExibicao = fatura.status;
  if (saldoDevedor <= 0.01) {
    statusExibicao = 'QUITADO';
  } else if (totalPago > 0) {
    statusExibicao = 'PARCIAL';
  }
  document.getElementById('detail-status').innerHTML = getStatusBadge(statusExibicao);

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
  console.log('📋 Pagamentos desta NF:', pagamentosNF);
  const tbody = document.getElementById('detail-pagamentos');
  if (!tbody) {
    console.error('Tbody de pagamentos não encontrado!');
    return;
  }
  tbody.innerHTML = '';
  if (pagamentosNF.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3">Nenhum pagamento registrado.</td></tr>';
  } else {
    pagamentosNF.forEach(p => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${formatarData(p.data_pagamento)}</td>
        <td>${formatarMoeda(p.valor_pago)}</td>
        <td>${p.observacao || '-'}</td>
      `;
      tbody.appendChild(row);
    });
    const rowTotal = document.createElement('tr');
    rowTotal.style.fontWeight = 'bold';
    rowTotal.innerHTML = `
      <td colspan="2">Total Pago:</td>
      <td>${formatarMoeda(totalPago)}</td>
    `;
    tbody.appendChild(rowTotal);
  }

  modal.classList.add('active');
  console.log('✅ Modal de detalhes aberto para NF', id);
};

// ===== Eventos do seletor de contrato =====
async function onContratoChange() {
  const select = document.getElementById('contrato-selector');
  contratoSelecionado = select.value ? parseInt(select.value) : null;
  invoicesPage = 1;
  paymentsPage = 1;
  await carregarBoletinsAprovados();
  await carregarFaturamentos();
  await carregarPagamentos();
}

// ===== Eventos de filtro =====
function configurarFiltros() {
  document.getElementById('search-invoices')?.addEventListener('input', (e) => {
    currentInvoiceFilter.search = e.target.value;
    invoicesPage = 1;
    aplicarFiltrosFaturamentos();
  });

  document.getElementById('filter-invoice-status')?.addEventListener('change', (e) => {
    currentInvoiceFilter.status = e.target.value;
    invoicesPage = 1;
    aplicarFiltrosFaturamentos();
  });

  document.getElementById('filter-invoice-date-start')?.addEventListener('change', (e) => {
    currentInvoiceFilter.startDate = e.target.value;
    invoicesPage = 1;
    aplicarFiltrosFaturamentos();
  });

  document.getElementById('filter-invoice-date-end')?.addEventListener('change', (e) => {
    currentInvoiceFilter.endDate = e.target.value;
    invoicesPage = 1;
    aplicarFiltrosFaturamentos();
  });

  document.getElementById('search-payments')?.addEventListener('input', (e) => {
    currentPaymentFilter.search = e.target.value;
    paymentsPage = 1;
    aplicarFiltrosPagamentos();
  });
  // Filtro de impostos
  document.getElementById('apply-tax-filter')?.addEventListener('click', () => {
    taxFilterStart = document.getElementById('filter-tax-date-start').value;
    taxFilterEnd = document.getElementById('filter-tax-date-end').value;
    atualizarImpostos();
  });
}

// ===== Paginação =====
function configurarPaginacao() {
  document.getElementById('prev-invoices-page')?.addEventListener('click', () => {
    if (invoicesPage > 1) {
      invoicesPage--;
      aplicarFiltrosFaturamentos();
    }
  });

  document.getElementById('next-invoices-page')?.addEventListener('click', () => {
    invoicesPage++;
    aplicarFiltrosFaturamentos();
  });

  document.getElementById('prev-payments-page')?.addEventListener('click', () => {
    if (paymentsPage > 1) {
      paymentsPage--;
      aplicarFiltrosPagamentos();
    }
  });

  document.getElementById('next-payments-page')?.addEventListener('click', () => {
    paymentsPage++;
    aplicarFiltrosPagamentos();
  });
}

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
  configurarFiltros();
  configurarPaginacao();
  configurarModais();

  document.getElementById('contrato-selector')?.addEventListener('change', onContratoChange);
  document.querySelector('[data-modal-open="new-invoice-modal"]')?.addEventListener('click', abrirModalNovaNF);
  document.querySelector('[data-modal-open="new-payment-modal"]')?.addEventListener('click', abrirModalNovoPagamento);

  document.getElementById('new-invoice-form')?.addEventListener('submit', salvarNovaNF);
  document.getElementById('new-payment-form')?.addEventListener('submit', salvarNovoPagamento);
});

// ===== Gerenciamento de Modais =====
function fecharModal(modal) {
  if (modal) {
    modal.classList.remove('active');
  }
}

function fecharModalAtual() {
  const modalAtivo = document.querySelector('.modal-overlay.active');
  if (modalAtivo) {
    fecharModal(modalAtivo);
  }
}

function configurarModais() {
  // Fechar ao clicar no botão com data-modal-close
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const modal = btn.closest('.modal-overlay');
      fecharModal(modal);
    });
  });

  // Fechar ao clicar no overlay (fundo escuro) - opcional
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        fecharModal(overlay);
      }
    });
  });

  // Fechar com tecla ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      fecharModalAtual();
    }
  });
}

// ===== Impostos =====
function renderizarTabelaImpostos(faturasFiltradas) {
  const tbody = document.querySelector('#taxes-detail-table tbody');
  if (!tbody) return; // Se a tabela não existir, sai sem erro
  tbody.innerHTML = '';

  if (faturasFiltradas.length === 0) {
    tbody.innerHTML = '<tr><td colspan="11" class="text-center">Nenhuma nota fiscal no período.</td></tr>';
    return;
  }

  faturasFiltradas.forEach(f => {
    const totalImpostos = (f.iss_retido || 0) + (f.inss_retido || 0) + (f.irrf_retido || 0) +
                          (f.csll_retido || 0) + (f.pis_retido || 0) + (f.cofins_retido || 0);
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${f.numero_nf || '—'}</td>
      <td>${formatarData(f.data_emissao)}</td>
      <td>${formatarMoeda(f.valor_bruto_nf)}</td>
      <td>${formatarMoeda(f.valor_liquido_nf)}</td>
      <td>${formatarMoeda(f.iss_retido)}</td>
      <td>${formatarMoeda(f.inss_retido)}</td>
      <td>${formatarMoeda(f.irrf_retido)}</td>
      <td>${formatarMoeda(f.csll_retido)}</td>
      <td>${formatarMoeda(f.pis_retido)}</td>
      <td>${formatarMoeda(f.cofins_retido)}</td>
      <td>${formatarMoeda(totalImpostos)}</td>
    `;
    tbody.appendChild(row);
  });
}

function renderizarGraficoImpostos(faturasFiltradas) {
  const canvas = document.getElementById('tax-chart');
  if (!canvas) {
    console.warn('Canvas tax-chart não encontrado');
    return;
  }

  // Calcular totais dos impostos
  const valores = {
    iss: faturasFiltradas.reduce((acc, f) => acc + (Number(f.iss_retido) || 0), 0),
    inss: faturasFiltradas.reduce((acc, f) => acc + (Number(f.inss_retido) || 0), 0),
    irrf: faturasFiltradas.reduce((acc, f) => acc + (Number(f.irrf_retido) || 0), 0),
    csll: faturasFiltradas.reduce((acc, f) => acc + (Number(f.csll_retido) || 0), 0),
    pis: faturasFiltradas.reduce((acc, f) => acc + (Number(f.pis_retido) || 0), 0),
    cofins: faturasFiltradas.reduce((acc, f) => acc + (Number(f.cofins_retido) || 0), 0)
  };

  const dadosGrafico = Object.values(valores);
  const temDados = dadosGrafico.some(v => v > 0);

  const ctx = canvas.getContext('2d');

  // Destroi gráfico anterior se existir
  if (window.taxChart) {
    window.taxChart.destroy();
    window.taxChart = null;
  }

  if (!temDados) {
    // Exibe mensagem de ausência de dados no canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '14px Inter, sans-serif';
    ctx.fillStyle = '#999';
    ctx.textAlign = 'center';
    ctx.fillText('Nenhum imposto retido no período', canvas.width/2, canvas.height/2);
    return;
  }

  // Cria o gráfico
  window.taxChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['ISS', 'INSS', 'IRRF', 'CSLL', 'PIS', 'COFINS'],
      datasets: [{
        data: dadosGrafico,
        backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}

function tentarRenderizar() {
    if (!loadingFaturas && !loadingPagamentos) {
        aplicarFiltrosFaturamentos();
        aplicarFiltrosPagamentos();
        atualizarKPIs();
        atualizarImpostos();
    }
}
