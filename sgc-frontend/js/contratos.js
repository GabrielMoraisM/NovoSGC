// ===== CONTRATOS =====

// Dados mockados (simulação de API)
const contratosMock = [
  {
    id: 1,
    numero: "CT-2024-001",
    nome: "Plataforma P-80",
    cliente: "Petrobras",
    tipo: "heca",
    valor: 12500000,
    progresso: 72,
    prazoRestante: 320,
    dataFim: "2025-12-30",
    status: "em-dia",
    clienteId: 1,
    dataInicio: "2024-01-01",
    issPadrao: 5.0,
    objeto: "Construção de plataforma offshore",
    gestor: "Eng. Carlos Silva"
  },
  {
    id: 2,
    numero: "CT-2024-002",
    nome: "Terminal Portuário",
    cliente: "Vale S.A.",
    tipo: "consorcio",
    valor: 8750000,
    progresso: 45,
    prazoRestante: 450,
    dataFim: "2026-03-15",
    status: "em-dia",
    clienteId: 2,
    dataInicio: "2024-03-01",
    issPadrao: 5.0,
    objeto: "Ampliação do terminal de minério",
    gestor: "Eng. Ana Souza"
  },
  {
    id: 3,
    numero: "CT-2024-003",
    nome: "Subestação 230kV",
    cliente: "Eletrobras",
    tipo: "scp",
    valor: 15200000,
    progresso: 58,
    prazoRestante: 230,
    dataFim: "2025-09-20",
    status: "atencao",
    clienteId: 3,
    dataInicio: "2024-02-15",
    issPadrao: 5.0,
    objeto: "Instalação de subestação",
    gestor: "Eng. Pedro Lima"
  },
  {
    id: 4,
    numero: "CT-2024-004",
    nome: "Conjunto Habitacional",
    cliente: "CDHU",
    tipo: "heca",
    valor: 6800000,
    progresso: 35,
    prazoRestante: -15,
    dataFim: "2025-06-10",
    status: "critico",
    clienteId: 4,
    dataInicio: "2024-01-15",
    issPadrao: 5.0,
    objeto: "Construção de 500 unidades",
    gestor: "Eng. Mariana Costa"
  },
  {
    id: 5,
    numero: "CT-2024-005",
    nome: "Rodovia BR-101",
    cliente: "DNIT",
    tipo: "consorcio",
    valor: 22100000,
    progresso: 88,
    prazoRestante: 45,
    dataFim: "2025-02-28",
    status: "em-dia",
    clienteId: 5,
    dataInicio: "2023-03-01",
    issPadrao: 5.0,
    objeto: "Duplicação de trecho rodoviário",
    gestor: "Eng. João Santos"
  }
];

// Carregar contratos na tabela
function carregarContratos() {
  const tbody = document.querySelector('#contratos-table tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  contratosMock.forEach(contrato => {
    const row = document.createElement('tr');
    row.className = 'contract-row';
    row.setAttribute('data-id', contrato.id);
    row.setAttribute('data-type', contrato.tipo);
    row.setAttribute('data-status', contrato.status);
    row.setAttribute('data-numero', contrato.numero);
    row.setAttribute('data-cliente', contrato.cliente);

    const progressBarClass = 
      contrato.status === 'em-dia' ? 'success' : 
      contrato.status === 'atencao' ? 'warning' : 'danger';

    const badgeClass = 
      contrato.status === 'em-dia' ? 'badge-success' : 
      contrato.status === 'atencao' ? 'badge-warning' : 'badge-danger';

    const statusText = 
      contrato.status === 'em-dia' ? 'Em dia' : 
      contrato.status === 'atencao' ? 'Atenção' : 'Crítico';

    const tipoBadge = 
      contrato.tipo === 'heca' ? 'Heca 100%' : 
      contrato.tipo === 'consorcio' ? 'Consórcio' : 'SCP';

    const tipoClass = 
      contrato.tipo === 'heca' ? 'badge-primary' : 
      contrato.tipo === 'consorcio' ? 'badge-secondary' : 'badge-warning';

    const prazoText = contrato.prazoRestante >= 0 
      ? `${contrato.prazoRestante} dias restantes` 
      : `${Math.abs(contrato.prazoRestante)} dias atrasado`;

    row.innerHTML = `
      <td>
        <div class="font-semibold">${contrato.numero}</div>
        <div class="text-xs text-muted">${contrato.nome}</div>
      </td>
      <td>${contrato.cliente}</td>
      <td><span class="badge ${tipoClass}">${tipoBadge}</span></td>
      <td>R$ ${(contrato.valor / 1e6).toFixed(1)}M</td>
      <td>
        <div class="flex items-center gap-2">
          <div class="progress" style="width: 80px;">
            <div class="progress-bar ${progressBarClass}" style="width: ${contrato.progresso}%;"></div>
          </div>
          <span class="text-xs font-medium">${contrato.progresso}%</span>
        </div>
      </td>
      <td>
        <div class="text-sm">${new Date(contrato.dataFim).toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })}</div>
        <div class="text-xs ${contrato.prazoRestante < 0 ? 'text-danger' : 'text-muted'}">${prazoText}</div>
      </td>
      <td><span class="badge ${badgeClass}">${statusText}</span></td>
      <td style="text-align: right;">
        <button class="btn-view-more" onclick="abrirDetalhes(${contrato.id})">
          <span>Ver detalhes</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </td>
    `;
    tbody.appendChild(row);
  });

  // Atualizar contador
  document.getElementById('contratos-count').textContent = `Mostrando ${contratosMock.length} de ${contratosMock.length} contratos`;
}

// Filtrar contratos
function filtrarContratos() {
  const tipoFiltro = document.getElementById('filter-type').value;
  const statusFiltro = document.getElementById('filter-status').value;
  const rows = document.querySelectorAll('.contract-row');

  rows.forEach(row => {
    const tipo = row.getAttribute('data-type');
    const status = row.getAttribute('data-status');
    let show = true;

    if (tipoFiltro && tipo !== tipoFiltro) show = false;
    if (statusFiltro && status !== statusFiltro) show = false;

    row.style.display = show ? '' : 'none';
  });

  // Atualizar contador
  const visibleRows = document.querySelectorAll('.contract-row:not([style*="display: none"])').length;
  document.getElementById('contratos-count').textContent = `Mostrando ${visibleRows} de ${contratosMock.length} contratos`;
}

// Buscar contratos por texto
function buscarContratos() {
  const termo = document.getElementById('search-contracts').value.toLowerCase();
  const rows = document.querySelectorAll('.contract-row');

  rows.forEach(row => {
    const numero = row.getAttribute('data-numero')?.toLowerCase() || '';
    const cliente = row.getAttribute('data-cliente')?.toLowerCase() || '';
    const show = numero.includes(termo) || cliente.includes(termo);
    row.style.display = show ? '' : 'none';
  });

  const visibleRows = document.querySelectorAll('.contract-row:not([style*="display: none"])').length;
  document.getElementById('contratos-count').textContent = `Mostrando ${visibleRows} de ${contratosMock.length} contratos`;
}

// Abrir modal de detalhes
function abrirDetalhes(contratoId) {
  const contrato = contratosMock.find(c => c.id === contratoId);
  if (!contrato) return;

  // Preencher modal
  document.getElementById('detail-modal-title').textContent = contrato.numero;
  document.getElementById('detail-modal-subtitle').textContent = contrato.nome;
  document.getElementById('detail-valor').textContent = `R$ ${contrato.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
  document.getElementById('detail-executado').textContent = `R$ ${(contrato.valor * contrato.progresso / 100).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
  document.getElementById('detail-saldo').textContent = `R$ ${(contrato.valor * (100 - contrato.progresso) / 100).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
  document.getElementById('detail-cliente').textContent = contrato.cliente;
  document.getElementById('detail-inicio').textContent = new Date(contrato.dataInicio).toLocaleDateString('pt-BR');
  document.getElementById('detail-termino').textContent = new Date(contrato.dataFim).toLocaleDateString('pt-BR');
  document.getElementById('detail-gestor').textContent = contrato.gestor;
  document.getElementById('detail-progresso').style.width = `${contrato.progresso}%`;
  document.getElementById('detail-progresso-texto').textContent = `${contrato.progresso}%`;

  // Atualizar histórico de aditivos (mock)
  const aditivosBody = document.getElementById('aditivos-list');
  aditivosBody.innerHTML = `
    <tr>
      <td>TA-01</td>
      <td>Prazo</td>
      <td>15/06/2024</td>
      <td>-</td>
      <td>+60 Dias</td>
      <td><span class="badge badge-success">Aprovado</span></td>
    </tr>
    <tr>
      <td>TA-02</td>
      <td>Valor</td>
      <td>20/08/2024</td>
      <td>R$ 500.000</td>
      <td>-</td>
      <td><span class="badge badge-warning">Em Análise</span></td>
    </tr>
  `;

  // Abrir modal
  document.getElementById('contract-details-modal').classList.add('active');
}

// Salvar novo contrato (mock)
function salvarNovoContrato(event) {
  event.preventDefault();
  // Aqui você pegaria os dados do formulário e enviaria para a API
  alert('Contrato criado com sucesso (simulação)!');
  document.getElementById('new-contract-modal').classList.remove('active');
  // Recarregar lista (simulado)
  carregarContratos();
}

// Salvar novo aditivo (mock)
function salvarAditivo(event) {
  event.preventDefault();
  alert('Aditivo registrado com sucesso (simulação)!');
  document.getElementById('aditivo-modal').classList.remove('active');
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
  carregarContratos();

  // Event listeners
  document.getElementById('add-seguro-form')?.addEventListener('submit', adicionarSeguro);
  document.getElementById('filter-type')?.addEventListener('change', filtrarContratos);
  document.getElementById('filter-status')?.addEventListener('change', filtrarContratos);
  document.getElementById('search-contracts')?.addEventListener('input', buscarContratos);
  document.getElementById('new-contract-form')?.addEventListener('submit', salvarNovoContrato);
  document.getElementById('aditivo-form')?.addEventListener('submit', salvarAditivo);
});

// ===== SEGUROS =====

// Dados mock de seguradoras (empresas com tipo 'SEGURADORA')
const seguradorasMock = [
  { id: 8, razao_social: "Porto Seguro", cnpj: "88.888.888/0001-88", tipo: "SEGURADORA" },
  { id: 9, razao_social: "Bradesco Seguros", cnpj: "99.999.999/0001-99", tipo: "SEGURADORA" },
  { id: 10, razao_social: "Allianz", cnpj: "10.101.010/0001-10", tipo: "SEGURADORA" }
];

// Dados mock de clientes (empresas com tipo 'CLIENTE') – já temos no empresasMock
// Vamos aproveitar as empresas existentes: Petrobras (2), Vale (3), Eletrobras (4), CDHU (5)

// Dados mock de tomadores (geralmente a Heca)
const tomadoresMock = [
  { id: 1, razao_social: "Heca Engenharia", tipo: "MATRIZ" }
];

// Dados mock de seguros por contrato (chave = contratoId)
const segurosPorContrato = {
  1: [
    {
      id: 1,
      seguradora_id: 8,
      numero_apolice: "AP-2024-001",
      tipo: "GARANTIA_CONTRATUAL",
      valor: 5000000.00,
      data_vencimento: "2025-12-31",
      cliente_id: 2, // Petrobras
      tomador_id: 1, // Heca
      objeto_segurado: "Garantia de execução do contrato",
      possui_clausula_retomada: true,
      observacoes: "Cláusula de retomada ativa"
    },
    {
      id: 2,
      seguradora_id: 9,
      numero_apolice: "AP-2024-002",
      tipo: "RISCO_ENGENHARIA",
      valor: 2000000.00,
      data_vencimento: "2024-12-31",
      cliente_id: 2,
      tomador_id: 1,
      objeto_segurado: "Riscos durante a construção",
      possui_clausula_retomada: false,
      observacoes: ""
    }
  ],
  2: [
    {
      id: 3,
      seguradora_id: 10,
      numero_apolice: "AP-2024-003",
      tipo: "RC",
      valor: 1000000.00,
      data_vencimento: "2025-06-30",
      cliente_id: 3, // Vale
      tomador_id: 1,
      objeto_segurado: "Responsabilidade civil",
      possui_clausula_retomada: false,
      observacoes: ""
    }
  ]
};

// Variável para armazenar o contrato atual em edição
let currentSegurosContratoId = null;

// Abrir modal de seguros
function abrirModalSeguros() {
  const contratoId = window.currentContratoId;
  if (!contratoId) {
    alert('Nenhum contrato selecionado.');
    return;
  }
  currentSegurosContratoId = contratoId;
  carregarSeguradorasDisponiveis();
  carregarClientesDisponiveis();
  carregarTomadoresDisponiveis();
  carregarSeguros(contratoId);
  document.getElementById('seguros-modal').classList.add('active');
}

// Fechar modal de seguros
function fecharModalSeguros() {
  document.getElementById('seguros-modal').classList.remove('active');
}

// Carregar seguradoras no select
function carregarSeguradorasDisponiveis() {
  const select = document.getElementById('seguro-seguradora');
  select.innerHTML = '<option value="">Selecione...</option>';
  seguradorasMock.forEach(seg => {
    const option = document.createElement('option');
    option.value = seg.id;
    option.textContent = `${seg.razao_social}`;
    select.appendChild(option);
  });
}

// Carregar clientes no select (empresas tipo CLIENTE)
function carregarClientesDisponiveis() {
  const select = document.getElementById('seguro-cliente');
  select.innerHTML = '<option value="">Selecione...</option>';
  const clientes = empresasMock.filter(e => e.tipo === 'CLIENTE');
  clientes.forEach(cli => {
    const option = document.createElement('option');
    option.value = cli.id;
    option.textContent = cli.razao_social;
    select.appendChild(option);
  });
}

// Carregar tomadores no select (geralmente a Heca, mas pode incluir outros)
function carregarTomadoresDisponiveis() {
  const select = document.getElementById('seguro-tomador');
  select.innerHTML = '<option value="">Selecione...</option>';
  tomadoresMock.forEach(tom => {
    const option = document.createElement('option');
    option.value = tom.id;
    option.textContent = tom.razao_social;
    select.appendChild(option);
  });
}

// Carregar seguros do contrato na tabela
function carregarSeguros(contratoId) {
  const tbody = document.getElementById('seguros-list');
  tbody.innerHTML = '';

  const seguros = segurosPorContrato[contratoId] || [];

  seguros.forEach(seg => {
    const seguradora = seguradorasMock.find(s => s.id === seg.seguradora_id);
    const cliente = empresasMock.find(e => e.id === seg.cliente_id);
    const tomador = tomadoresMock.find(t => t.id === seg.tomador_id) || { razao_social: 'N/A' };

    const tipoLabel = {
      'GARANTIA_CONTRATUAL': 'Garantia Contratual',
      'RISCO_ENGENHARIA': 'Risco de Engenharia',
      'RC': 'Responsabilidade Civil'
    }[seg.tipo] || seg.tipo;

    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${seg.numero_apolice}</td>
      <td>${seguradora ? seguradora.razao_social : '-'}</td>
      <td>${tipoLabel}</td>
      <td>${new Date(seg.data_vencimento).toLocaleDateString('pt-BR')}</td>
      <td>R$ ${seg.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
      <td>${cliente ? cliente.razao_social : '-'}</td>
      <td>${tomador.razao_social}</td>
      <td style="text-align: right;">
        <button class="btn btn-danger btn-sm" onclick="removerSeguro(${contratoId}, ${seg.id})">Remover</button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

// Adicionar seguro (mock)
function adicionarSeguro(event) {
  event.preventDefault();

  const seguradora_id = parseInt(document.getElementById('seguro-seguradora').value);
  const numero_apolice = document.getElementById('seguro-apolice').value;
  const tipo = document.getElementById('seguro-tipo').value;
  const valor = parseFloat(document.getElementById('seguro-valor').value);
  const data_vencimento = document.getElementById('seguro-vencimento').value;
  const cliente_id = parseInt(document.getElementById('seguro-cliente').value);
  const tomador_id = parseInt(document.getElementById('seguro-tomador').value);
  const objeto_segurado = document.getElementById('seguro-objeto').value;
  const possui_clausula_retomada = document.getElementById('seguro-clausula-retomada').checked;
  const observacoes = document.getElementById('seguro-observacoes').value;

  if (!seguradora_id || !numero_apolice || !tipo || isNaN(valor) || !data_vencimento || !cliente_id || !tomador_id || !objeto_segurado) {
    alert('Preencha todos os campos obrigatórios.');
    return;
  }

  // Gerar novo ID
  const novoId = Math.max(...Object.values(segurosPorContrato).flat().map(s => s.id), 0) + 1;

  const novoSeguro = {
    id: novoId,
    seguradora_id,
    numero_apolice,
    tipo,
    valor,
    data_vencimento,
    cliente_id,
    tomador_id,
    objeto_segurado,
    possui_clausula_retomada,
    observacoes
  };

  // Adicionar ao mock
  if (!segurosPorContrato[currentSegurosContratoId]) {
    segurosPorContrato[currentSegurosContratoId] = [];
  }
  segurosPorContrato[currentSegurosContratoId].push(novoSeguro);

  // Recarregar tabela
  carregarSeguros(currentSegurosContratoId);

  // Limpar formulário
  document.getElementById('add-seguro-form').reset();
}

// Remover seguro
function removerSeguro(contratoId, seguroId) {
  let seguros = segurosPorContrato[contratoId] || [];
  seguros = seguros.filter(s => s.id !== seguroId);
  segurosPorContrato[contratoId] = seguros;
  carregarSeguros(contratoId);
}

// Expor funções globalmente
window.abrirModalSeguros = abrirModalSeguros;
window.fecharModalSeguros = fecharModalSeguros;
window.removerSeguro = removerSeguro;
window.adicionarSeguro = adicionarSeguro;