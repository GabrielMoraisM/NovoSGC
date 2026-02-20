// contratos.js
import {
  getContratos,
  getContrato, // <--- ADICIONADO
  createContrato,
  updateParticipantes,
  getParticipantes,
  getArts,
  createArt,
  updateArt,
  deleteArt,
  getSeguros,
  createSeguro,
  deleteSeguro,
  getAditivos,
  createAditivo,
  updateAditivo,
  deleteAditivo,
  updateContrato,
  getEmpresas
} from './api.js';

// ===== Variáveis globais =====
let contratos = [];
let participantesTemp = [];
let currentContratoId = null;
let empresas = [];

// Abrir modal de OS
function abrirModalOS() {
  if (!currentContratoId) {
    alert('Nenhum contrato selecionado.');
    return;
  }
  // Buscar o contrato atual para preencher os campos
  const contrato = contratos.find(c => c.id === currentContratoId);
  if (contrato) {
    document.getElementById('os-numero').value = contrato.numero_os || '';
    document.getElementById('os-data').value = contrato.data_os || '';
    document.getElementById('os-descricao').value = contrato.descricao_os || '';
  }
  document.getElementById('os-modal').classList.add('active');
}

function fecharModalOS() {
  document.getElementById('os-modal').classList.remove('active');
}

// ===== ARTs =====
async function carregarArts(contratoId) {
  const tbody = document.getElementById('arts-list');
  if (!tbody) return;

  try {
    const arts = await getArts(contratoId);
    tbody.innerHTML = '';
    if (arts.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhuma ART cadastrada</td></tr>';
      return;
    }
    arts.forEach(art => {
      console.log('ART recebida:', art); 
      const row = document.createElement('tr');
      row.setAttribute('data-id', art.id);
      row.innerHTML = `
        <td>${art.nome_profissional}</td>
        <td>${art.numero_art}</td>
        <td>${art.finalizado ? '✅' : '❌'}</td>
        <td>${art.data_finalizacao ? new Date(art.data_finalizacao).toLocaleDateString('pt-BR') : '-'}</td>
        <td style="text-align: right;">
          ${!art.finalizado ? `<button class="btn-view-more" onclick="finalizarArt(${art.id})">Finalizar</button>` : ''}
          <button class="btn-view-more" onclick="editarArt(${art.id})">Editar</button>
          <button class="btn-view-more" onclick="excluirArt(${art.id})">Excluir</button>
        </td>
      `;
      tbody.appendChild(row);
    });
  } catch (error) {
    console.error('Erro ao carregar ARTs:', error);
    tbody.innerHTML = '<tr><td colspan="5" class="text-danger">Erro ao carregar ARTs</td></tr>';
  }
}

// Função para finalizar uma ART (marcar como concluída)
window.finalizarArt = async function(artId) {
  console.log('finalizarArt chamado com artId:', artId);
  console.log('currentContratoId:', currentContratoId);
  
  const dataFinalizacao = prompt('Informe a data de finalização (AAAA-MM-DD) ou deixe em branco para hoje:', new Date().toISOString().split('T')[0]);
  if (dataFinalizacao === null) return; // cancelou

  const data = dataFinalizacao || new Date().toISOString().split('T')[0];
  try {
    const payload = { finalizado: true, data_finalizacao: data };
    console.log('Enviando payload:', payload);
    await updateArt(artId, payload);
    console.log('Resposta OK');
    await carregarArts(currentContratoId);
    alert('ART finalizada com sucesso!');
  } catch (error) {
    console.error('Erro detalhado:', error);
    alert('Erro ao finalizar ART: ' + error.message);
  }
};

// Abrir modal de ARTs
function abrirModalArts() {
  if (!currentContratoId) {
    alert('Nenhum contrato selecionado.');
    return;
  }
  carregarArts(currentContratoId);
  document.getElementById('arts-modal').classList.add('active');
  // Inicializa o comportamento do checkbox de finalizado
  const chkFinalizado = document.getElementById('art-finalizado');
  const dataContainer = document.getElementById('art-data-container');
  chkFinalizado.addEventListener('change', () => {
    dataContainer.style.display = chkFinalizado.checked ? 'block' : 'none';
    if (!chkFinalizado.checked) document.getElementById('art-data').value = '';
  });
}

function fecharModalArts() {
  document.getElementById('arts-modal').classList.remove('active');
  // Limpa o formulário
  document.getElementById('art-nome').value = '';
  document.getElementById('art-numero').value = '';
  document.getElementById('art-finalizado').checked = false;
  document.getElementById('art-data').value = '';
  document.getElementById('art-data-container').style.display = 'none';
}

async function adicionarArt(event) {
  event.preventDefault();
  const nome = document.getElementById('art-nome').value.trim();
  const numero = document.getElementById('art-numero').value.trim();
  const finalizado = document.getElementById('art-finalizado').checked;
  const dataFinalizacao = finalizado ? document.getElementById('art-data').value : null;

  if (!nome || !numero) {
    alert('Preencha todos os campos');
    return;
  }



  const artData = {
    contrato_id: currentContratoId,  // <-- ADICIONADO
    nome_profissional: nome,
    numero_art: numero,
    finalizado: finalizado,
    data_finalizacao: dataFinalizacao
  };

  console.log('Enviando ART:', artData);

  try {
    await createArt(currentContratoId, artData);
    alert('ART adicionada com sucesso!');
    await carregarArts(currentContratoId);
    fecharModalArts();
  } catch (error) {
    alert('Erro ao adicionar ART: ' + error.message);
  }
}

window.editarArt = async function(artId) {
  // Para simplificar, usaremos prompt para editar. Em uma versão mais elaborada, poderíamos abrir um modal de edição.
  const novaProfissional = prompt('Nome do profissional:');
  if (!novaProfissional) return;
  const novoNumero = prompt('Número da ART:');
  if (!novoNumero) return;
  try {
    await updateArt(artId, { nome_profissional: novaProfissional, numero_art: novoNumero });
    await carregarArts(currentContratoId);
  } catch (error) {
    alert('Erro ao editar ART: ' + error.message);
  }
};

window.excluirArt = async function(artId) {
  if (confirm('Deseja realmente excluir esta ART?')) {
    try {
      await deleteArt(artId);
      await carregarArts(currentContratoId);
    } catch (error) {
      alert('Erro ao excluir ART: ' + error.message);
    }
  }
};

window.finalizarArt = async function(artId) {
  const dataFinalizacao = prompt('Informe a data de finalização (AAAA-MM-DD) ou deixe em branco para hoje:', new Date().toISOString().split('T')[0]);
  if (dataFinalizacao === null) return; // cancelou

  const data = dataFinalizacao || new Date().toISOString().split('T')[0];
  try {
    await updateArt(artId, { finalizado: true, data_finalizacao: data });
    await carregarArts(currentContratoId);
    alert('ART finalizada com sucesso!');
  } catch (error) {
    alert('Erro ao finalizar ART: ' + error.message);
  }
};

async function salvarOS(event) {
  event.preventDefault();
  if (!currentContratoId) return;

  const osData = {
    numero_os: document.getElementById('os-numero').value || null,
    data_os: document.getElementById('os-data').value || null,
    descricao_os: document.getElementById('os-descricao').value || null
  };

  try {
    await updateContrato(currentContratoId, osData);
    alert('Ordem de Serviço salva com sucesso!');
    fecharModalOS();
    // Atualiza o contrato na lista e nos detalhes
    await carregarContratos(); // recarrega a lista
    // Opcional: atualizar detalhes se o modal estiver aberto
    if (document.getElementById('contract-details-modal').classList.contains('active')) {
      abrirDetalhes(currentContratoId); // recarrega os detalhes
    }
  } catch (error) {
    alert('Erro ao salvar OS: ' + error.message);
  }
}

// Exponha as funções globalmente
window.abrirModalOS = abrirModalOS;
window.fecharModalOS = fecharModalOS;
window.salvarOS = salvarOS;

// ===== Funções de renderização (mantidas iguais) =====
function getBadgeClass(status) {
  const classes = {
    'em-dia': 'badge-success',
    'atencao': 'badge-warning',
    'critico': 'badge-danger'
  };
  return classes[status] || 'badge-secondary';
}

function getTipoBadge(tipo) {
  const classes = {
    'HECA_100': 'badge-primary',
    'CONSORCIO': 'badge-secondary',
    'SCP': 'badge-warning'
  };
  const labels = {
    'HECA_100': 'Heca 100%',
    'CONSORCIO': 'Consórcio',
    'SCP': 'SCP'
  };
  return `<span class="badge ${classes[tipo] || 'badge-secondary'}">${labels[tipo] || tipo}</span>`;
}

function formatarMoeda(valor) {
  return 'R$ ' + (valor / 1e6).toFixed(1) + 'M';
}

function calcularPrazoRestante(dataFim) {
  if (!dataFim) return null;
  const hoje = new Date();
  const fim = new Date(dataFim);
  if (isNaN(fim.getTime())) return null;
  const diff = Math.ceil((fim - hoje) / (1000 * 60 * 60 * 24));
  return diff;
}

function getProgressBarClass(status) {
  return status === 'em-dia' ? 'success' : status === 'atencao' ? 'warning' : 'danger';
}

// Renderizar tabela de contratos
function renderizarContratos(contratosParaMostrar) {
  const tbody = document.querySelector('#contratos-table tbody');
  if (!tbody) {
    console.error('Tbody não encontrado! Aguardando um pouco...');
    setTimeout(() => {
      const tbody2 = document.querySelector('#contratos-table tbody');
      if (tbody2) renderizarContratos(contratosParaMostrar);
    }, 100);
    return;
  }

  tbody.innerHTML = '';
  contratosParaMostrar.forEach(contrato => {
    // Logs para depuração (podem ser removidos depois)
    console.log('Contrato ID:', contrato.id);
    console.log('data_fim_prevista:', contrato.data_fim_prevista);
    console.log('dataFim:', contrato.dataFim);

    const cliente = empresas.find(e => e.id === contrato.cliente_id);
    const clienteNome = cliente?.razao_social || 'N/A';
    
    const status = contrato.status || 'em-dia';
    const progresso = contrato.progresso || 0;

    // Tratamento da data fim
    let dataFimStr = '—';
    let prazoStr = '—';
    let prazoRestante = null;

    let dataFimRaw = contrato.data_fim_prevista;
    if (!dataFimRaw && contrato.data_inicio && contrato.prazo_original_dias) {
      const dataInicio = new Date(contrato.data_inicio);
      dataInicio.setDate(dataInicio.getDate() + contrato.prazo_original_dias);
      dataFimRaw = dataInicio.toISOString().split('T')[0]; // formato YYYY-MM-DD
    }

    if (dataFimRaw) {
      const dataFimObj = new Date(dataFimRaw);
      if (!isNaN(dataFimObj.getTime())) {
        dataFimStr = dataFimObj.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
        prazoRestante = calcularPrazoRestante(dataFimRaw);
        if (prazoRestante !== null) {
          prazoStr = prazoRestante >= 0 
            ? `${prazoRestante} dias restantes` 
            : `${-prazoRestante} dias atrasado`;
        }
      }
    }

    const row = document.createElement('tr');
    row.className = 'contract-row';
    row.setAttribute('data-id', contrato.id);
    row.setAttribute('data-type', contrato.tipo_obra);
    row.setAttribute('data-status', status);
    row.setAttribute('data-numero', contrato.numero_contrato);
    row.setAttribute('data-cliente', clienteNome);
    row.setAttribute('data-fim', dataFimRaw || ''); // armazena a data ISO


    row.innerHTML = `
      <td>
        <div class="font-semibold">${contrato.numero_contrato}</div>
        <div class="text-xs text-muted">${contrato.nome_projeto || ''}</div>
      </td>
      <td>${clienteNome}</td>
      <td>${getTipoBadge(contrato.tipo_obra)}</td>
      <td>${formatarMoeda(contrato.valor_total || contrato.valor_original)}</td>
      <td>
        <div class="flex items-center gap-2">
          <div class="progress" style="width: 80px;">
            <div class="progress-bar ${getProgressBarClass(status)}" style="width: ${progresso}%;"></div>
          </div>
          <span class="text-xs font-medium">${progresso}%</span>
        </div>
      </td>
      <td>
  <div class="text-sm">${dataFimStr}</div>
  <div class="text-xs ${prazoRestante < 0 ? 'text-danger' : 'text-muted'} prazo-cell">${prazoStr}</div>
</td>

      <td><span class="badge ${getBadgeClass(status)}">${status}</span></td>
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

  document.getElementById('contratos-count').textContent = `Mostrando ${contratosParaMostrar.length} de ${contratos.length} contratos`;
}

// ===== Carregar dados da API =====
async function carregarContratos() {
  console.log('carregarContratos iniciada');
  try {
    contratos = await getContratos();
    console.log('Contratos recebidos:', contratos);
    renderizarContratos(contratos);
  } catch (error) {
    console.error('Erro ao carregar contratos:', error);
    alert('Não foi possível carregar os contratos.');
  }
}

// Carregar aditivos do contrato
async function carregarAditivos(contratoId) {
  const tbody = document.getElementById('aditivos-list');
  if (!tbody) return;

  try {
    const aditivos = await getAditivos(contratoId);
    tbody.innerHTML = '';
    if (aditivos.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhum aditivo cadastrado</td></tr>';
      return;
    }

    aditivos.forEach(aditivo => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td style="padding: 0.5rem 1rem;">${aditivo.numero_emenda || '—'}</td>
        <td style="padding: 0.5rem 1rem;">${aditivo.tipo}</td>
        <td style="padding: 0.5rem 1rem;">${new Date(aditivo.data_aprovacao).toLocaleDateString('pt-BR')}</td>
        <td style="padding: 0.5rem 1rem;">${aditivo.valor_acrescimo ? 'R$ ' + aditivo.valor_acrescimo.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '—'}</td>
        <td style="padding: 0.5rem 1rem;">${aditivo.dias_acrescimo ? aditivo.dias_acrescimo + ' dias' : '—'}</td>
        <td style="padding: 0.5rem 1rem;"><span class="badge badge-success">Aprovado</span></td>
      `;
      tbody.appendChild(row);
    });
  } catch (error) {
    console.error('Erro ao carregar aditivos:', error);
    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Erro ao carregar aditivos</td></tr>';
  }
}

async function carregarClientes() {
  try {
    const empresas = await getEmpresas();
    const clientes = empresas.filter(e => e.tipo === 'CLIENTE');
    const select = document.querySelector('select[name="cliente_id"]');
    if (!select) return;
    select.innerHTML = '<option value="">Selecione um cliente</option>';
    clientes.forEach(cliente => {
      const option = document.createElement('option');
      option.value = cliente.id;
      option.textContent = cliente.razao_social;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('Erro ao carregar clientes:', error);
  }
}

// ===== EMPRESAS GLOBAIS =====
async function carregarEmpresasGlobais() {
  try {
    empresas = await getEmpresas();
    console.log('Empresas carregadas:', empresas);
  } catch (error) {
    console.error('Erro ao carregar empresas:', error);
    empresas = [];
  }
}

// ===== SEGURADORAS =====
function carregarSeguradoras() {
  console.log('carregarSeguradoras executada');
  const select = document.getElementById('seguro-seguradora');
  if (!select) {
    console.error('Select não encontrado');
    return;
  }
  // Filtra empresas com tipo 'SEGURADORA' (case-insensitive)
  const seguradoras = empresas.filter(e => e.tipo && e.tipo.toUpperCase() === 'SEGURADORA');
  console.log('Seguradoras encontradas:', seguradoras);
  
  select.innerHTML = '<option value="">Selecione...</option>';
  seguradoras.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.id;
    opt.textContent = s.razao_social;
    select.appendChild(opt);
  });
}

// ===== CLIENTES (para o campo "Cliente (segurado)") =====
function carregarClientesSelect() {
  const select = document.getElementById('seguro-cliente');
  if (!select) return;
  const clientes = empresas.filter(e => e.tipo === 'CLIENTE');
  select.innerHTML = '<option value="">Selecione...</option>';
  clientes.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.razao_social;
    select.appendChild(opt);
  });
}

// ===== TOMADORES (geralmente a Heca) =====
function carregarTomadores() {
  const select = document.getElementById('seguro-tomador');
  if (!select) return;
  // Pode ser todas as MATRIZ ou um filtro específico
  const tomadores = empresas.filter(e => e.tipo === 'MATRIZ' || e.tipo === 'FILIAL');
  select.innerHTML = '<option value="">Selecione...</option>';
  tomadores.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t.id;
    opt.textContent = t.razao_social;
    select.appendChild(opt);
  });
}

// ===== ABRIR MODAL DE SEGUROS =====
async function abrirModalSeguros() {
  if (!currentContratoId) {
    alert('Nenhum contrato selecionado.');
    return;
  }
  if (empresas.length === 0) {
    await carregarEmpresasGlobais();
  }
  carregarSeguradoras();
  carregarClientesSelect();
  carregarTomadores();
  await carregarSeguros(currentContratoId);
  document.getElementById('seguros-modal').classList.add('active');
}

// ===== Filtros =====
function filtrarContratos() {
  const tipoFiltro = document.getElementById('filter-type')?.value;
  const statusFiltro = document.getElementById('filter-status')?.value;
  const rows = document.querySelectorAll('.contract-row');
  const countElement = document.getElementById('contratos-count');

  if (!countElement) {
    console.error('Elemento #contratos-count não encontrado no DOM');
    return;
  }

  rows.forEach(row => {
    const tipo = row.getAttribute('data-type');
    const status = row.getAttribute('data-status');
    let show = true;
    if (tipoFiltro && tipo !== tipoFiltro) show = false;
    if (statusFiltro && status !== statusFiltro) show = false;
    row.style.display = show ? '' : 'none';
  });

  const visibleRows = document.querySelectorAll('.contract-row:not([style*="display: none"])').length;
  countElement.textContent = `Mostrando ${visibleRows} de ${contratos.length} contratos`;
}
// ===== Busca =====
function buscarContratos() {
  const termo = document.getElementById('search-contracts')?.value.toLowerCase() || '';
  const rows = document.querySelectorAll('.contract-row');
  const countElement = document.getElementById('contratos-count');

  if (!countElement) {
    console.error('Elemento #contratos-count não encontrado');
    return;
  }

  rows.forEach(row => {
    const numero = row.getAttribute('data-numero')?.toLowerCase() || '';
    const cliente = row.getAttribute('data-cliente')?.toLowerCase() || '';
    const show = numero.includes(termo) || cliente.includes(termo);
    row.style.display = show ? '' : 'none';
  });

  const visibleRows = document.querySelectorAll('.contract-row:not([style*="display: none"])').length;
  countElement.textContent = `Mostrando ${visibleRows} de ${contratos.length} contratos`;
}

// ===== Abrir detalhes do contrato =====
/*function abrirDetalhes(contratoId) {
  const contrato = contratos.find(c => c.id === contratoId);
  if (!contrato) return;

  currentContratoId = contratoId;

  // Preencher campos do modal (já existente)
  document.getElementById('detail-modal-title').textContent = contrato.numero_contrato;
  document.getElementById('detail-modal-subtitle').textContent = contrato.nome_projeto || '';
  document.getElementById('detail-valor').textContent = `R$ ${contrato.valor_original.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
  document.getElementById('detail-executado').textContent = 'R$ 0,00';
  document.getElementById('detail-saldo').textContent = `R$ ${contrato.valor_original.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
  document.getElementById('detail-cliente').textContent = contrato.cliente?.razao_social || 'N/A';
  document.getElementById('detail-inicio').textContent = new Date(contrato.data_inicio).toLocaleDateString('pt-BR');
  document.getElementById('detail-termino').textContent = contrato.data_fim_prevista ? new Date(contrato.data_fim_prevista).toLocaleDateString('pt-BR') : '—';
  document.getElementById('detail-gestor').textContent = contrato.gestor || '—';
  document.getElementById('detail-progresso').style.width = '0%';
  document.getElementById('detail-progresso-texto').textContent = '0%';

  // Carregar aditivos
  carregarAditivos(contratoId);

  document.getElementById('contract-details-modal').classList.add('active');
}*/

// ===== Participantes (temporários para novo contrato) =====
function toggleParticipantesSection() {
  const tipo = document.querySelector('[name="tipo_obra"]').value;
  const section = document.getElementById('participantes-section');
  if (tipo === 'CONSORCIO' || tipo === 'SCP') {
    section.style.display = 'block';
    carregarEmpresasParticipantes();
  } else {
    section.style.display = 'none';
    participantesTemp = [];
    atualizarListaParticipantes();
  }
}

function carregarEmpresasParticipantes() {
  const select = document.getElementById('participante-empresa');
  if (!select) return;
  select.innerHTML = '<option value="">Selecione uma empresa</option>';
  const participantes = empresas.filter(e => ['MATRIZ', 'PARCEIRO_CONSORCIO', 'SCP'].includes(e.tipo));
  participantes.forEach(emp => {
    const option = document.createElement('option');
    option.value = emp.id;
    option.textContent = `${emp.razao_social} (${emp.tipo})`;
    select.appendChild(option);
  });
}

function atualizarListaParticipantes() {
  const container = document.getElementById('participantes-list');
  if (!container) return;
  container.innerHTML = '';
  let soma = 0;
  participantesTemp.forEach((part, index) => {
    const empresa = empresas.find(e => e.id === part.empresa_id);
    if (!empresa) return;
    soma += part.percentual_participacao;
    const div = document.createElement('div');
    div.className = 'flex items-center justify-between p-2 mb-2 bg-gray-50 rounded';
    div.innerHTML = `
      <span>${empresa.razao_social} - ${part.percentual_participacao}% ${part.is_lider ? '(Líder)' : ''}</span>
      <button type="button" class="text-danger" onclick="removerParticipanteTemp(${index})">Remover</button>
    `;
    container.appendChild(div);
  });
  document.getElementById('soma-percentuais').textContent = soma.toFixed(2) + '%';
  const somaValid = document.getElementById('soma-valid');
  if (soma === 100) {
    somaValid.style.color = 'var(--success)';
    somaValid.textContent = '✓ Válido';
  } else {
    somaValid.style.color = 'var(--danger)';
    somaValid.textContent = '✗ Deve ser 100%';
  }
}

function adicionarParticipanteTemp() {
  const empresaId = parseInt(document.getElementById('participante-empresa').value);
  const percentual = parseFloat(document.getElementById('participante-percentual').value);
  const lider = document.getElementById('participante-lider').checked;

  if (!empresaId || isNaN(percentual) || percentual <= 0) {
    alert('Selecione uma empresa e informe um percentual válido');
    return;
  }

  if (participantesTemp.some(p => p.empresa_id === empresaId)) {
    alert('Esta empresa já foi adicionada');
    return;
  }

  if (lider && participantesTemp.some(p => p.is_lider)) {
    alert('Já existe um líder definido. Remova o líder atual primeiro.');
    return;
  }

  const somaAtual = participantesTemp.reduce((acc, p) => acc + p.percentual_participacao, 0);
  if (somaAtual + percentual > 100) {
    alert('A soma dos percentuais ultrapassaria 100%');
    return;
  }

  participantesTemp.push({
    empresa_id: empresaId,
    percentual_participacao: percentual,
    is_lider: lider
  });
  atualizarListaParticipantes();
  document.getElementById('participante-empresa').value = '';
  document.getElementById('participante-percentual').value = '';
  document.getElementById('participante-lider').checked = false;
}

window.removerParticipanteTemp = function(index) {
  participantesTemp.splice(index, 1);
  atualizarListaParticipantes();
};

// ===== Salvar novo contrato =====
async function salvarNovoContrato(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);

  const tipoObra = formData.get('tipo_obra');
  if (!tipoObra) {
    alert('Tipo de obra inválido');
    return;
  }

  const clienteId = parseInt(formData.get('cliente_id'));
  if (isNaN(clienteId)) {
    alert('Selecione um cliente válido');
    return;
  }

  const dataInicio = formData.get('data_inicio');
  const diasDuracao = parseInt(formData.get('dias_duracao'));

  if (!dataInicio || isNaN(diasDuracao) || diasDuracao <= 0) {
    alert('Informe uma data inicial e uma duração válida');
    return;
  }

  const contratoData = {
    numero_contrato: formData.get('numero_contrato'),
    tipo_obra: tipoObra,
    valor_original: parseFloat(formData.get('valor_original')),
    prazo_original_dias: diasDuracao,  // agora usamos o campo diretamente
    data_inicio: dataInicio,
    cliente_id: clienteId,
    iss_percentual_padrao: parseFloat(formData.get('iss_percentual_padrao')) || null,
    status: 'ATIVO',
    objeto: formData.get('objeto') || ''
  };

  try {
    const novoContrato = await createContrato(contratoData);

    if ((tipoObra === 'CONSORCIO' || tipoObra === 'SCP') && participantesTemp.length > 0) {
      const soma = participantesTemp.reduce((acc, p) => acc + p.percentual_participacao, 0);
      if (soma !== 100) {
        alert('A soma dos percentuais dos participantes deve ser 100%. O contrato foi criado, mas os participantes não foram salvos.');
        return;
      }
      const lideres = participantesTemp.filter(p => p.is_lider);
      if (lideres.length !== 1) {
        alert('É necessário exatamente um líder no consórcio/SCP.');
        return;
      }
      await updateParticipantes(novoContrato.id, participantesTemp);
    }

    alert('Contrato criado com sucesso!');
    document.getElementById('new-contract-modal').classList.remove('active');
    form.reset();
    participantesTemp = [];
    atualizarListaParticipantes();
    await carregarContratos();
  } catch (error) {
    console.error('Erro ao criar contrato:', error);
    alert('Erro ao criar contrato: ' + error.message);
  }
}

// Salvar novo aditivo
let enviandoAditivo = false;

async function salvarAditivo(event) {
  event.preventDefault();
  
  if (enviandoAditivo) return;
  enviandoAditivo = true;

  const form = event.target;
  const formData = new FormData(form);
  const submitBtn = form.querySelector('button[type="submit"]');
  if (submitBtn) submitBtn.disabled = true;

  // Declarar aditivoData aqui para que esteja acessível no catch
  let aditivoData = null;

  try {
    if (!currentContratoId) {
      alert('Nenhum contrato selecionado.');
      return;
    }

    const numeroEmenda = formData.get('numero');
    if (!numeroEmenda || numeroEmenda.trim() === '') {
      alert('O número do aditivo é obrigatório.');
      return;
    }
    if (numeroEmenda.length > 20) {
      alert('O número da emenda deve ter no máximo 20 caracteres.');
      return;
    }

    const tipoSelecionado = formData.get('tipo');
    const tipoMap = {
      'prazo': 'PRAZO',
      'valor': 'VALOR',
      'ambos': 'AMBOS'
    };
    const tipo = tipoMap[tipoSelecionado];
    if (!tipo) {
      alert('Tipo de aditivo inválido');
      return;
    }

    aditivoData = {
      contrato_id: currentContratoId,
      tipo: tipo,
      numero_emenda: numeroEmenda.trim(),
      data_aprovacao: new Date().toISOString().split('T')[0],
      justificativa: formData.get('justificativa') || '',
      dias_acrescimo: 0,
      valor_acrescimo: 0
    };

    if (tipo === 'PRAZO' || tipo === 'AMBOS') {
      const dias = parseInt(formData.get('dias'));
      if (isNaN(dias) || dias <= 0) {
        alert('Informe um número de dias válido para aditivo de prazo');
        return;
      }
      aditivoData.dias_acrescimo = dias;
    }

    if (tipo === 'VALOR' || tipo === 'AMBOS') {
      const valor = parseFloat(formData.get('valor'));
      if (isNaN(valor) || valor <= 0) {
        alert('Informe um valor válido para aditivo de valor');
        return;
      }
      aditivoData.valor_acrescimo = valor;
    }

    console.log('Enviando aditivo:', aditivoData);

    await createAditivo(currentContratoId, aditivoData);
    alert('Aditivo registrado com sucesso!');
    
    document.getElementById('aditivo-modal').classList.remove('active');
    form.reset();
    
    await carregarAditivos(currentContratoId);
    await abrirDetalhes(currentContratoId);
    await carregarContratos();
  } catch (error) {
    console.error('Erro ao salvar aditivo:', error);
    // Se quiser mostrar detalhes do aditivo que falhou, use aditivoData (que pode ser null)
    alert('Erro ao registrar aditivo: ' + error.message);
  } finally {
    enviandoAditivo = false;
    if (submitBtn) submitBtn.disabled = false;
  }
}


async function carregarDetalhesContrato(contratoId) {
  try {
    const contrato = await getContrato(contratoId);
    if (!contrato) return;

    // Se o backend fornecer valor_total, usa; senão, calcula manualmente
    let valorTotal = contrato.valor_total;
    if (valorTotal === undefined || valorTotal === null) {
      const aditivos = await getAditivos(contratoId);
      const somaValorAditivos = aditivos.reduce((acc, a) => acc + (a.valor_acrescimo || 0), 0);
      valorTotal = contrato.valor_original + somaValorAditivos;
    }

    document.getElementById('detail-modal-title').textContent = contrato.numero_contrato;
    document.getElementById('detail-modal-subtitle').textContent = contrato.nome_projeto || '';
    document.getElementById('detail-valor').textContent = `R$ ${valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    document.getElementById('detail-cliente').textContent = contrato.cliente?.razao_social || 'N/A';
    document.getElementById('detail-inicio').textContent = new Date(contrato.data_inicio).toLocaleDateString('pt-BR');
    document.getElementById('detail-termino').textContent = contrato.data_fim_prevista ? new Date(contrato.data_fim_prevista).toLocaleDateString('pt-BR') : '—';
    document.getElementById('detail-gestor').textContent = contrato.gestor || '—';

    document.getElementById('detail-executado').textContent = 'R$ 0,00';
    document.getElementById('detail-saldo').textContent = `R$ ${valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    document.getElementById('detail-progresso').style.width = '0%';
    document.getElementById('detail-progresso-texto').textContent = '0%';
  } catch (error) {
    console.error('Erro ao carregar detalhes do contrato:', error);
  }
}
// ===== Modais de ARTs, Seguros e Participantes =====
async function abrirModalSeguros() {
  if (!currentContratoId) {
    alert('Nenhum contrato selecionado.');
    return;
  }
  // Se empresas não estiverem carregadas, carrega agora
  if (empresas.length === 0) {
    console.log('Empresas não carregadas. Carregando...');
    await carregarEmpresasGlobais();
  }
  carregarSeguradoras();
  carregarClientesSelect();
  carregarTomadores();
  await carregarSeguros(currentContratoId);
  document.getElementById('seguros-modal').classList.add('active');
}

function fecharModalSeguros() {
  document.getElementById('seguros-modal').classList.remove('active');
}

function abrirModalParticipantes() {
  if (!currentContratoId) {
    alert('Nenhum contrato selecionado.');
    return;
  }
  alert('Funcionalidade em desenvolvimento – em breve você poderá gerenciar participantes diretamente.');
}

// ===== Inicialização =====
document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'index.html';
    return;
  }

  await carregarEmpresasGlobais();
  await carregarContratos();
  await carregarClientes();

  document.getElementById('filter-type')?.addEventListener('change', filtrarContratos);
  document.getElementById('filter-status')?.addEventListener('change', filtrarContratos);
  document.getElementById('search-contracts')?.addEventListener('input', buscarContratos);
  document.getElementById('aditivo-form')?.addEventListener('submit', salvarAditivo);

  const tipoSelect = document.querySelector('[name="tipo_obra"]');
  if (tipoSelect) {
    tipoSelect.addEventListener('change', toggleParticipantesSection);
  }

  document.getElementById('add-participante-btn')?.addEventListener('click', adicionarParticipanteTemp);

  document.getElementById('new-contract-form')?.addEventListener('submit', salvarNovoContrato);

  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = btn.closest('.modal-overlay');
      if (modal) modal.classList.remove('active');
    });
  });
// Calcular e exibir data prevista de término
const dataInicioInput = document.getElementById('data_inicio');
const diasDuracaoInput = document.getElementById('dias_duracao');
const previsaoContainer = document.getElementById('previsao-container');
const previsaoTermino = document.getElementById('previsao-termino');

function atualizarPrevisao() {
  if (dataInicioInput.value && diasDuracaoInput.value) {
    const dataInicio = new Date(dataInicioInput.value);
    const dias = parseInt(diasDuracaoInput.value);
    if (!isNaN(dias) && dias > 0) {
      const dataTermino = new Date(dataInicio);
      dataTermino.setDate(dataTermino.getDate() + dias);
      previsaoTermino.value = dataTermino.toLocaleDateString('pt-BR');
      previsaoContainer.style.display = 'block';
      return;
    }
  }
  previsaoContainer.style.display = 'none';
}

dataInicioInput.addEventListener('change', atualizarPrevisao);
diasDuracaoInput.addEventListener('input', atualizarPrevisao);
});

// Função para atualizar os prazos restantes dinamicamente
function atualizarPrazos() {
  const rows = document.querySelectorAll('.contract-row');
  rows.forEach(row => {
    const dataFim = row.getAttribute('data-fim'); // vamos armazenar a data ISO
    if (!dataFim) return;

    const prazoRestante = calcularPrazoRestante(dataFim);
    const prazoCell = row.querySelector('.prazo-cell'); // precisamos identificar a célula
    if (prazoCell) {
      if (prazoRestante === null) {
        prazoCell.textContent = '—';
      } else {
        prazoCell.textContent = prazoRestante >= 0 
          ? `${prazoRestante} dias restantes` 
          : `${-prazoRestante} dias atrasado`;
        // Opcional: mudar a cor com base no valor
        prazoCell.style.color = prazoRestante < 0 ? 'var(--danger)' : 'var(--text-muted)';
      }
    }
  });
}

// Função para abrir modal de gestor (simples prompt)
function abrirModalGestor() {
  if (!currentContratoId) {
    alert('Nenhum contrato selecionado.');
    return;
  }
  const contrato = contratos.find(c => c.id === currentContratoId);
  const gestorAtual = contrato?.gestor || '';
  const novoGestor = prompt('Informe o nome do gestor:', gestorAtual);
  if (novoGestor !== null) {
    salvarGestor(novoGestor);
  }
}

async function salvarGestor(nome) {
  try {
    await updateContrato(currentContratoId, { gestor: nome });
    alert('Gestor atualizado com sucesso!');
    await carregarContratos();
    if (document.getElementById('contract-details-modal').classList.contains('active')) {
      abrirDetalhes(currentContratoId);
    }
  } catch (error) {
    alert('Erro ao salvar gestor: ' + error.message);
  }
}

// Modifique a função abrirDetalhes para incluir a OS e corrigir o cliente
async function abrirDetalhes(contratoId) {
  try {
    const contrato = await getContrato(contratoId);
    if (!contrato) return;

    currentContratoId = contratoId;

    // Preencher título
    document.getElementById('detail-modal-title').textContent = contrato.numero_contrato;
    document.getElementById('detail-modal-subtitle').textContent = contrato.nome_projeto || '';

    // Valor total (usa valor_total se existir, senão original)
    const valorTotal = contrato.valor_total ?? contrato.valor_original;
    document.getElementById('detail-valor').textContent = `R$ ${valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    document.getElementById('detail-executado').textContent = 'R$ 0,00';
    document.getElementById('detail-saldo').textContent = `R$ ${valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

    // Cliente (busca na lista de empresas)
    const cliente = empresas.find(e => e.id === contrato.cliente_id);
    document.getElementById('detail-cliente').textContent = cliente?.razao_social || 'N/A';

    // Datas
    document.getElementById('detail-inicio').textContent = new Date(contrato.data_inicio).toLocaleDateString('pt-BR');
    document.getElementById('detail-termino').textContent = contrato.data_fim_prevista ? new Date(contrato.data_fim_prevista).toLocaleDateString('pt-BR') : '—';
    document.getElementById('detail-gestor').textContent = contrato.gestor || '—';

    // OS (campos já devem vir do backend)
    document.getElementById('detail-os-numero').textContent = contrato.numero_os || '—';
    document.getElementById('detail-os-data').textContent = contrato.data_os ? new Date(contrato.data_os).toLocaleDateString('pt-BR') : '—';
    document.getElementById('detail-os-descricao').textContent = contrato.descricao_os || '—';

    // Progresso (placeholders)
    document.getElementById('detail-progresso').style.width = '0%';
    document.getElementById('detail-progresso-texto').textContent = '0%';

    // Carregar aditivos
    await carregarAditivos(contratoId);

    document.getElementById('contract-details-modal').classList.add('active');
  } catch (error) {
    console.error('Erro ao abrir detalhes do contrato:', error);
    alert('Não foi possível carregar os detalhes do contrato.');
  }
}

// Expor a função globalmente
window.abrirModalGestor = abrirModalGestor;

// Iniciar a atualização a cada 1 hora (3600000 ms)
setInterval(atualizarPrazos, 3600000); // a cada hora
// Se quiser testar mais rápido, use 60000 (1 minuto)



// Expor funções globais
window.adicionarArt = adicionarArt;
window.abrirDetalhes = abrirDetalhes;
window.abrirModalArts = abrirModalArts;
window.fecharModalArts = fecharModalArts;
window.abrirModalSeguros = abrirModalSeguros;
window.fecharModalSeguros = fecharModalSeguros;
window.abrirModalParticipantes = abrirModalParticipantes;
window.salvarAditivo = salvarAditivo;
