// ===== FINANCEIRO =====

// Dados mockados de notas fiscais
const faturasMock = [
  {
    id: 1,
    numeroNf: "NF-2024-0125",
    bmId: 1,
    contratoNumero: "CT-2024-001",
    contratoNome: "Plataforma P-80",
    cliente: "Petrobras",
    clienteId: 1,
    empresaEmissoraId: 1,
    empresaEmissora: "Heca Engenharia",
    dataEmissao: "2024-01-15",
    dataVencimento: "2024-02-15",
    valorBruto: 1500000.00,
    valorLiquido: 1282500.00,
    issRetido: 75000.00,
    inssRetido: 165000.00,
    irrfRetido: 22500.00,
    csllRetido: 15000.00,
    pisRetido: 9750.00,
    cofinsRetido: 45000.00,
    status: "PAGO"
  },
  {
    id: 2,
    numeroNf: "NF-2024-0126",
    bmId: 2,
    contratoNumero: "CT-2024-001",
    contratoNome: "Plataforma P-80",
    cliente: "Petrobras",
    clienteId: 1,
    empresaEmissoraId: 1,
    empresaEmissora: "Heca Engenharia",
    dataEmissao: "2024-02-15",
    dataVencimento: "2024-03-15",
    valorBruto: 1250000.00,
    valorLiquido: 1068750.00,
    issRetido: 62500.00,
    inssRetido: 137500.00,
    irrfRetido: 18750.00,
    csllRetido: 12500.00,
    pisRetido: 8125.00,
    cofinsRetido: 37500.00,
    status: "PAGO"
  },
  {
    id: 3,
    numeroNf: "NF-2024-0127",
    bmId: 3,
    contratoNumero: "CT-2024-002",
    contratoNome: "Terminal Portuário",
    cliente: "Vale S.A.",
    clienteId: 2,
    empresaEmissoraId: 1,
    empresaEmissora: "Heca Engenharia",
    dataEmissao: "2024-03-01",
    dataVencimento: "2024-04-01",
    valorBruto: 2100000.00,
    valorLiquido: 1795500.00,
    issRetido: 105000.00,
    inssRetido: 231000.00,
    irrfRetido: 31500.00,
    csllRetido: 21000.00,
    pisRetido: 13650.00,
    cofinsRetido: 63000.00,
    status: "PENDENTE"
  },
  {
    id: 4,
    numeroNf: "NF-2024-0128",
    bmId: 4,
    contratoNumero: "CT-2024-004",
    contratoNome: "Conjunto Habitacional",
    cliente: "CDHU",
    clienteId: 4,
    empresaEmissoraId: 1,
    empresaEmissora: "Heca Engenharia",
    dataEmissao: "2024-01-15",
    dataVencimento: "2024-02-15",
    valorBruto: 850000.00,
    valorLiquido: 726750.00,
    issRetido: 42500.00,
    inssRetido: 93500.00,
    irrfRetido: 12750.00,
    csllRetido: 8500.00,
    pisRetido: 5525.00,
    cofinsRetido: 25500.00,
    status: "VENCIDO"
  },
  {
    id: 5,
    numeroNf: "NF-2024-0129",
    bmId: 5,
    contratoNumero: "CT-2024-003",
    contratoNome: "Subestação 230kV",
    cliente: "Eletrobras",
    clienteId: 3,
    empresaEmissoraId: 1,
    empresaEmissora: "Heca Engenharia",
    dataEmissao: "2024-03-20",
    dataVencimento: "2024-04-20",
    valorBruto: 3200000.00,
    valorLiquido: 2736000.00,
    issRetido: 160000.00,
    inssRetido: 352000.00,
    irrfRetido: 48000.00,
    csllRetido: 32000.00,
    pisRetido: 20800.00,
    cofinsRetido: 96000.00,
    status: "PENDENTE"
  }
];

// Dados mockados de pagamentos
const pagamentosMock = [
  {
    id: 1,
    faturamentoId: 1,
    dataPagamento: "2024-02-10",
    valorPago: 1282500.00,
    observacao: "Pagamento integral"
  },
  {
    id: 2,
    faturamentoId: 2,
    dataPagamento: "2024-03-10",
    valorPago: 1068750.00,
    observacao: ""
  }
];

// Funções auxiliares
function formatarMoeda(valor) {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarData(dataStr) {
  const data = new Date(dataStr + 'T12:00:00');
  return data.toLocaleDateString('pt-BR');
}

function getStatusBadgeNF(status) {
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

// Atualizar KPI cards
function atualizarKPI() {
  const totalRecebido = pagamentosMock.reduce((acc, p) => acc + p.valorPago, 0);
  const totalPendente = faturasMock
    .filter(f => f.status === 'PENDENTE')
    .reduce((acc, f) => acc + f.valorLiquido, 0);
  const totalVencido = faturasMock
    .filter(f => f.status === 'VENCIDO')
    .reduce((acc, f) => acc + f.valorLiquido, 0);
  const totalNotas = faturasMock.length;

  document.getElementById('total-recebido').textContent = formatarMoeda(totalRecebido);
  document.getElementById('total-pendente').textContent = formatarMoeda(totalPendente);
  document.getElementById('total-vencido').textContent = formatarMoeda(totalVencido);
  document.getElementById('total-notas').textContent = totalNotas;
}

// Carregar tabela de notas fiscais
function carregarNotas() {
  const tbody = document.querySelector('#invoices-table tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  faturasMock.forEach(fat => {
    const row = document.createElement('tr');
    row.className = 'invoice-row';
    row.setAttribute('data-id', fat.id);
    row.setAttribute('data-status', fat.status);

    row.innerHTML = `
      <td class="font-semibold">${fat.numeroNf}</td>
      <td>${fat.contratoNumero}</td>
      <td>${fat.cliente}</td>
      <td>${formatarData(fat.dataEmissao)}</td>
      <td>${formatarData(fat.dataVencimento)}</td>
      <td>${formatarMoeda(fat.valorBruto)}</td>
      <td>${formatarMoeda(fat.valorLiquido)}</td>
      <td>${getStatusBadgeNF(fat.status)}</td>
      <td style="text-align: right;">
        <button class="btn-view-more" onclick="abrirDetalhesNF(${fat.id})">
          <span>Detalhes</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </td>
    `;
    tbody.appendChild(row);
  });

  document.getElementById('invoices-count').textContent = `Mostrando ${faturasMock.length} de ${faturasMock.length} notas`;
}

// Carregar tabela de pagamentos
function carregarPagamentos() {
  const tbody = document.querySelector('#payments-table tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  pagamentosMock.forEach(pag => {
    const fatura = faturasMock.find(f => f.id === pag.faturamentoId);
    if (!fatura) return;

    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${formatarData(pag.dataPagamento)}</td>
      <td>${fatura.numeroNf}</td>
      <td>${fatura.contratoNumero}</td>
      <td>${fatura.cliente}</td>
      <td>${formatarMoeda(pag.valorPago)}</td>
      <td>—</td>
      <td>${pag.observacao || '-'}</td>
    `;
    tbody.appendChild(row);
  });
}

// Atualizar impostos
function atualizarImpostos() {
  const iss = faturasMock.reduce((acc, f) => acc + f.issRetido, 0);
  const inss = faturasMock.reduce((acc, f) => acc + f.inssRetido, 0);
  const irrf = faturasMock.reduce((acc, f) => acc + f.irrfRetido, 0);
  const csll = faturasMock.reduce((acc, f) => acc + f.csllRetido, 0);
  const pis = faturasMock.reduce((acc, f) => acc + f.pisRetido, 0);
  const cofins = faturasMock.reduce((acc, f) => acc + f.cofinsRetido, 0);

  document.getElementById('tax-iss').textContent = formatarMoeda(iss);
  document.getElementById('tax-inss').textContent = formatarMoeda(inss);
  document.getElementById('tax-irrf').textContent = formatarMoeda(irrf);
  document.getElementById('tax-csll').textContent = formatarMoeda(csll);
  document.getElementById('tax-pis').textContent = formatarMoeda(pis);
  document.getElementById('tax-cofins').textContent = formatarMoeda(cofins);
  document.getElementById('tax-total').textContent = formatarMoeda(iss+inss+irrf+csll+pis+cofins);
}

// Abrir detalhes da NF
function abrirDetalhesNF(id) {
  const fat = faturasMock.find(f => f.id === id);
  if (!fat) return;

  document.getElementById('detail-invoice-title').textContent = `Detalhes da NF`;
  document.getElementById('detail-invoice-subtitle').textContent = fat.numeroNf;
  document.getElementById('detail-valor-bruto').textContent = formatarMoeda(fat.valorBruto);
  document.getElementById('detail-valor-liquido').textContent = formatarMoeda(fat.valorLiquido);
  document.getElementById('detail-status').innerHTML = getStatusBadgeNF(fat.status);
  document.getElementById('detail-bm').textContent = `${fat.contratoNumero} / BM-${fat.bmId}`;
  document.getElementById('detail-cliente').textContent = fat.cliente;
  document.getElementById('detail-emissao').textContent = formatarData(fat.dataEmissao);
  document.getElementById('detail-vencimento').textContent = formatarData(fat.dataVencimento);
  document.getElementById('detail-emissora').textContent = fat.empresaEmissora;
  document.getElementById('detail-iss').textContent = formatarMoeda(fat.issRetido);
  document.getElementById('detail-inss').textContent = formatarMoeda(fat.inssRetido);
  document.getElementById('detail-irrf').textContent = formatarMoeda(fat.irrfRetido);
  document.getElementById('detail-csll').textContent = formatarMoeda(fat.csllRetido);
  document.getElementById('detail-pis').textContent = formatarMoeda(fat.pisRetido);
  document.getElementById('detail-cofins').textContent = formatarMoeda(fat.cofinsRetido);

  const pagamentos = pagamentosMock.filter(p => p.faturamentoId === id);
  const tbody = document.getElementById('detail-pagamentos');
  tbody.innerHTML = '';
  if (pagamentos.length > 0) {
    pagamentos.forEach(p => {
      tbody.innerHTML += `
        <tr>
          <td>${formatarData(p.dataPagamento)}</td>
          <td>${formatarMoeda(p.valorPago)}</td>
          <td>${p.observacao || '-'}</td>
        </tr>
      `;
    });
  } else {
    tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;">Nenhum pagamento registrado</td></tr>';
  }

  document.getElementById('invoice-details-modal').classList.add('active');
}

// Filtros (simples)
function filtrarNotas() {
  const statusFiltro = document.getElementById('filter-invoice-status').value;
  const termo = document.getElementById('search-invoices').value.toLowerCase();
  const rows = document.querySelectorAll('.invoice-row');

  rows.forEach(row => {
    const status = row.getAttribute('data-status');
    const texto = row.innerText.toLowerCase();
    let show = true;

    if (statusFiltro && status !== statusFiltro) show = false;
    if (termo && !texto.includes(termo)) show = false;

    row.style.display = show ? '' : 'none';
  });

  const visiveis = document.querySelectorAll('.invoice-row:not([style*="display: none"])').length;
  document.getElementById('invoices-count').textContent = `Mostrando ${visiveis} de ${faturasMock.length} notas`;
}

// Salvar nova NF (mock)
function salvarNovaNF(event) {
  event.preventDefault();
  alert('NF criada com sucesso (simulação)!');
  document.getElementById('new-invoice-modal').classList.remove('active');
  event.target.reset();
}

// Salvar novo pagamento (mock)
function salvarNovoPagamento(event) {
  event.preventDefault();
  alert('Pagamento registrado com sucesso (simulação)!');
  document.getElementById('new-payment-modal').classList.remove('active');
  event.target.reset();
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  carregarNotas();
  carregarPagamentos();
  atualizarKPI();
  atualizarImpostos();

  // Event listeners para abas
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

  // Filtros
  document.getElementById('filter-invoice-status')?.addEventListener('change', filtrarNotas);
  document.getElementById('search-invoices')?.addEventListener('input', filtrarNotas);

  // Formulários
  document.getElementById('new-invoice-form')?.addEventListener('submit', salvarNovaNF);
  document.getElementById('new-payment-form')?.addEventListener('submit', salvarNovoPagamento);
});