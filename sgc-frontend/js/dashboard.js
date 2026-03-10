// dashboard.js
// Sistema de Gestão de Contratos e Medições - Heca Engenharia
// Dashboard com visão global e por contrato

let contratos = [];
let contratoSelecionado = null;
let chartInstance = null; // para destruir o gráfico anterior

document.addEventListener('DOMContentLoaded', function() {
    if (typeof api === 'undefined') {
        console.error('Erro: objeto api não está definido. Verifique se o arquivo api.js foi carregado corretamente.');
        mostrarErro('Falha na inicialização: API não disponível. Recarregue a página ou contate o suporte.');
        return;
    }
    carregarContratos();
    configurarEventos();
    restaurarContratoSelecionado(); // Tenta restaurar a seleção anterior
});

// ---------- Restaurar contrato selecionado anteriormente ----------
async function restaurarContratoSelecionado() {
    const savedId = sessionStorage.getItem('contratoSelecionado');
    if (savedId) {
        const select = document.getElementById('contrato-selector');
        if (select) {
            select.value = savedId;
            // Dispara o evento change para carregar os dados
            const event = new Event('change', { bubbles: true });
            select.dispatchEvent(event);
        }
    }
}

// ---------- Configuração de Eventos ----------
function configurarEventos() {
    const selector = document.getElementById('contrato-selector');
    if (selector) {
        selector.addEventListener('change', async (e) => {
            const id = e.target.value;
            // Salva a seleção para futura restauração
            sessionStorage.setItem('contratoSelecionado', id);
            if (!id) {
                contratoSelecionado = null;
                await carregarResumoGlobal();
                mostrarElementosGlobais(true);
            } else {
                contratoSelecionado = contratos.find(c => c.id == id);
                await carregarDadosContrato(id);
                mostrarElementosGlobais(false);
            }
        });
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const tabId = btn.dataset.tab;
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            const pane = document.getElementById(`tab-${tabId}`);
            if (pane) pane.classList.add('active');
        });
    });

    // Evento para mudança de período do gráfico
    document.getElementById('periodo-grafico')?.addEventListener('change', async (e) => {
        const meses = e.target.value;
        if (contratoSelecionado) {
            const dados = await carregarDadosGrafico(contratoSelecionado.id, meses);
            renderizarGrafico(dados);
        } else {
            const dados = await carregarDadosGrafico(null, meses);
            renderizarGrafico(dados);
        }
    });
}

function mostrarElementosGlobais(mostrar) {
    const detalhes = document.getElementById('contrato-detalhes');
    const recentes = document.getElementById('recentes-container');
    const alertas = document.getElementById('alertas-recentes-container');
    const cardRitmo = document.getElementById('card-ritmo');
    if (detalhes) detalhes.style.display = mostrar ? 'none' : 'block';
    if (recentes) recentes.style.display = mostrar ? 'block' : 'none';
    if (alertas) alertas.style.display = mostrar ? 'block' : 'none';
    if (cardRitmo) cardRitmo.style.display = mostrar ? 'none' : 'block';
}

// ===== Funções do Gráfico =====
async function carregarDadosGrafico(contratoId, meses = 12) {
    try {
        let url;
        if (contratoId) {
            url = `/graficos/evolucao-contrato/${contratoId}?meses=${meses}`;
        } else {
            url = `/graficos/evolucao-global?meses=${meses}`;
        }
        const response = await api.get(url);
        if (!response.ok) throw new Error('Erro ao carregar dados do gráfico');
        return await response.json();
    } catch (error) {
        console.error('Erro no gráfico:', error);
        return null;
    }
}

function renderizarGrafico(dados) {
    const canvas = document.getElementById('grafico-evolucao');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    if (chartInstance) chartInstance.destroy();

    if (!dados || !dados.labels || dados.labels.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = '14px Inter, sans-serif';
        ctx.fillStyle = '#999';
        ctx.textAlign = 'center';
        ctx.fillText('Sem dados para exibir', canvas.width/2, canvas.height/2);
        return;
    }

    const datasets = [];
    if (dados.fisico) {
        datasets.push({
            label: '% Físico',
            data: dados.fisico,
            borderColor: '#4e73df',
            backgroundColor: 'rgba(78, 115, 223, 0.05)',
            tension: 0.1
        });
    }
    if (dados.financeiro) {
        datasets.push({
            label: '% Financeiro',
            data: dados.financeiro,
            borderColor: '#1cc88a',
            backgroundColor: 'rgba(28, 200, 138, 0.05)',
            tension: 0.1
        });
    }
    if (dados.tempo) {
        datasets.push({
            label: '% Tempo',
            data: dados.tempo,
            borderColor: '#f6c23e',
            backgroundColor: 'rgba(246, 194, 62, 0.05)',
            tension: 0.1
        });
    }

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dados.labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { callback: value => value + '%' }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${ctx.raw}%`
                    }
                }
            }
        }
    });
}

// ===== Painel de Ritmo e Projeção (COM PRAZO ORIGINAL) =====
function atualizarPainelRitmo(resumo, desempenho, diasMedidos) {
  if (!resumo || !desempenho) return;

  // Dados básicos
  const percExecutado = resumo.percentual_fisico || 0;
  const percExecutar = 100 - percExecutado;
  
  // Valores financeiros
  const valorTotal = resumo.valor_total_contrato || 0;
  const valorExecutado = resumo.valor_executado || 0;
  const valorRestante = valorTotal - valorExecutado;

  // Dias transcorridos (prioridade para diasMedidos)
  const diasTranscorridos = (diasMedidos !== undefined && diasMedidos !== null) ? diasMedidos : desempenho.dias_decorridos || 0;

  // Dias totais: primeiro tenta do backend, depois usa prazo_original_dias
  let diasTotais = desempenho.dias_totais;
  if (!diasTotais && desempenho.prazo_original_dias) {
    diasTotais = desempenho.prazo_original_dias;
    // TODO: somar aditivos de prazo se houver
  }

  const temPrazo = diasTotais !== null && diasTotais !== undefined && diasTotais > 0;
  const temDiasTranscorridos = diasTranscorridos > 0;

  let diasRestantes = 0;
  let ritmoPlanejado = 0;
  let ritmoRealValor = 0;
  let ritmoNecessarioValor = 0;
  let percRitmoRealVsPlanejado = 0;
  let diasNecessarios = 0;
  let dataTermino = '-';
  let statusRitmo = '';

  if (temPrazo && temDiasTranscorridos) {
    diasRestantes = diasTotais - diasTranscorridos;
    
    // Ritmo planejado (escopo) = valor total / prazo total (R$/dia)
    ritmoPlanejado = valorTotal / diasTotais;

    // Ritmo real (executado/dia) baseado nos dias transcorridos
    ritmoRealValor = valorExecutado / diasTranscorridos;

    // Ritmo necessário para cumprir o prazo restante
    ritmoNecessarioValor = diasRestantes > 0 ? valorRestante / diasRestantes : 0;

    // Comparação percentual do ritmo real em relação ao planejado
    percRitmoRealVsPlanejado = ritmoPlanejado > 0 ? (ritmoRealValor / ritmoPlanejado) * 100 : 0;

    // Cálculo de dias necessários para terminar no ritmo atual
    if (ritmoRealValor > 0) {
      diasNecessarios = Math.ceil(valorRestante / ritmoRealValor);
      const novaData = new Date();
      novaData.setDate(novaData.getDate() + diasNecessarios);
      dataTermino = novaData.toLocaleDateString('pt-BR');

      // Classificação do ritmo
      if (ritmoNecessarioValor > ritmoRealValor * 1.2) {
        statusRitmo = '🔴 Ritmo insuficiente (atraso)';
      } else if (ritmoNecessarioValor > ritmoRealValor) {
        statusRitmo = '🟡 Ritmo abaixo do necessário (atenção)';
      } else if (ritmoRealValor >= ritmoNecessarioValor) {
        statusRitmo = '🟢 Ritmo adequado (no prazo)';
      }
    } else {
      if (diasTranscorridos > 0 && valorExecutado === 0) {
        statusRitmo = '🔴 Nenhuma execução (atrasado)';
      }
    }
  } else {
    // Sem prazo ou sem dias transcorridos
    diasRestantes = 0;
    ritmoPlanejado = 0;
    ritmoRealValor = 0;
    ritmoNecessarioValor = 0;
    percRitmoRealVsPlanejado = 0;
    diasNecessarios = 0;
    dataTermino = '—';
    statusRitmo = temPrazo ? (temDiasTranscorridos ? '⚪ Aguardando dados' : '⚪ Sem medições') : '⚪ Sem prazo definido';
  }

  // Prepara os valores para exibição
  const elementos = {
    'perc-executado': `${percExecutado.toFixed(2)}%`,
    'perc-executar': `${percExecutar.toFixed(2)}%`,
    'ritmo-real': temPrazo && temDiasTranscorridos ? `${percRitmoRealVsPlanejado.toFixed(2)}%` : '—',
    'ritmo-necessario': temPrazo && temDiasTranscorridos ? (ritmoNecessarioValor > 0 ? `${ritmoNecessarioValor.toFixed(2)} R$/dia` : '0 R$/dia') : '—',
    'dias-transcorridos': temDiasTranscorridos ? `${diasTranscorridos} dias` : '0 dias',
    'dias-restantes': temPrazo ? `${diasRestantes} dias` : '—',
    'dias-necessarios': temPrazo && temDiasTranscorridos ? `${diasNecessarios} dias` : '—',
    'data-termino': dataTermino,
    'status-ritmo': statusRitmo,
    'ritmo-real-valor': temPrazo && temDiasTranscorridos ? formatarMoeda(ritmoRealValor) + '/dia' : '—'
  };

  // Atualiza os elementos
  for (const [id, valor] of Object.entries(elementos)) {
    const el = document.getElementById(id);
    if (el) {
      el.innerText = valor;
    } else {
      console.warn(`Elemento com id "${id}" não encontrado`);
    }
  }
}

// ---------- Carregar Lista de Contratos para o Seletor ----------
async function carregarContratos() {
    try {
        const response = await api.get('/contratos/?incluir_resumo=true');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        contratos = await response.json();
        preencherSeletor(contratos);
        // Após carregar os contratos, carrega o resumo global (Todos)
        await carregarResumoGlobal();
    } catch (error) {
        console.error('Erro ao carregar contratos:', error);
        mostrarErro('Não foi possível carregar a lista de contratos.');
    }
}

function preencherSeletor(contratos) {
    const select = document.getElementById('contrato-selector');
    if (!select) return;
    select.innerHTML = '<option value="">Todos os Projetos</option>';
    contratos.forEach(c => {
        const option = document.createElement('option');
        option.value = c.id;
        option.textContent = `${c.numero_contrato} - ${c.nome || 'Sem nome'}`;
        select.appendChild(option);
    });
}

// ---------- Resumo Global (Todos os Projetos) ----------
async function carregarResumoGlobal() {
    try {
        // Usa o endpoint consolidado do backend — inclui métricas da prateleira e alertas reais
        const response = await api.get('/dashboard/resumo');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        atualizarKPIsGlobais(data);

        // Carrega o gráfico global
        const meses = document.getElementById('periodo-grafico')?.value || 12;
        const dadosGrafico = await carregarDadosGrafico(null, meses);
        renderizarGrafico(dadosGrafico);

    } catch (error) {
        console.error('Erro ao carregar resumo global:', error);
        mostrarErro('Falha ao carregar dados do dashboard.');
    }
    await carregarProjecao(null); // null = projeção global
}

function atualizarKPIsGlobais(data) {
    const kpis = {
        '#kpi-valor-total .kpi-value': data.valor_total_contratado,
        '#kpi-executado .kpi-value': data.valor_executado_total,
        '#kpi-faturado .kpi-value': data.valor_faturado_total,
        '#kpi-recebido .kpi-value': data.valor_recebido_total,
        '#kpi-perc-fisico .kpi-value': data.percentual_global_fisico,
        '#kpi-perc-financeiro .kpi-value': data.percentual_global_faturado
    };
    for (const [selector, valor] of Object.entries(kpis)) {
        const el = document.querySelector(selector);
        if (el) {
            if (selector.includes('perc')) {
                el.innerText = formatarPercentual(valor);
            } else {
                el.innerText = formatarMoeda(valor);
            }
        }
    }
    preencherContratosRecentes(data.contratos_recentes || []);
    preencherAlertasRecentes(data.alertas_recentes || []);
    preencherAlertasDestaque(data.alertas_recentes || []);

    // KPIs da Prateleira de Execuções
    const elValorPrat = document.getElementById('kpi-prateleira-valor-val');
    const elQtdPrat = document.getElementById('kpi-prateleira-qtd-val');
    const elVencidosPrat = document.getElementById('kpi-prateleira-vencidos-val');

    if (elValorPrat) elValorPrat.innerText = formatarMoeda(data.valor_total_em_prateleira || 0);
    if (elQtdPrat) elQtdPrat.innerText = data.qtd_execucoes_prateleira ?? 0;
    if (elVencidosPrat) {
        const vencidos = data.execucoes_sem_medicao_30dias ?? 0;
        elVencidosPrat.innerText = vencidos;
        elVencidosPrat.style.color = vencidos > 0 ? 'var(--danger, #d32f2f)' : 'inherit';
    }
}

function preencherContratosRecentes(contratos) {
    const tbody = document.querySelector('#tabela-contratos-recentes');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!contratos || contratos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Nenhum contrato encontrado.</td></tr>';
        return;
    }
    contratos.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="font-medium">${c.numero_contrato || ''}</td>
            <td>${c.cliente_nome || '-'}</td>
            <td>
                <div class="flex items-center gap-2">
                    <div class="progress" style="width: 60px;">
                        <div class="progress-bar ${getClasseProgresso(c.percentual_fisico)}" style="width: ${c.percentual_fisico}%;"></div>
                    </div>
                    <span class="text-xs">${formatarPercentual(c.percentual_fisico)}</span>
                </div>
            </td>
            <td><span class="badge badge-${getClasseStatus(c.status_desempenho)}">${getTextoStatus(c.status_desempenho)}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function preencherAlertasRecentes(alertas) {
    const container = document.getElementById('lista-alertas-recentes');
    if (!container) return;
    container.innerHTML = '';
    if (!alertas || alertas.length === 0) {
        container.innerHTML = '<div class="notification-item">Nenhum alerta recente.</div>';
        return;
    }
    alertas.forEach(a => {
        const div = document.createElement('div');
        div.className = 'notification-item';
        div.innerHTML = `
            <div class="notification-icon ${a.tipo || ''}">${getIconeAlerta(a.tipo)}</div>
            <div class="notification-content">
                <div class="notification-title">${a.titulo || ''}</div>
                <div class="notification-text">${a.mensagem || ''}</div>
                <div class="notification-time">${a.data || ''}</div>
            </div>
        `;
        container.appendChild(div);
    });
}

function preencherAlertasDestaque(alertas) {
    const container = document.getElementById('lista-alertas-destaque');
    if (!container) return;
    container.innerHTML = '';
    if (!alertas || alertas.length === 0) {
        container.innerHTML = '<div class="notification-item">Nenhum alerta recente.</div>';
        return;
    }
    alertas.forEach(a => {
        const div = document.createElement('div');
        div.className = 'notification-item';
        div.innerHTML = `
            <div class="notification-icon ${a.tipo || ''}">${getIconeAlerta(a.tipo)}</div>
            <div class="notification-content">
                <div class="notification-title">${a.titulo || ''}</div>
                <div class="notification-text">${a.mensagem || ''}</div>
                <div class="notification-time">${a.data || ''}</div>
            </div>
        `;
        container.appendChild(div);
    });
}

// ---------- Dados de um Contrato Específico ----------
async function carregarDadosContrato(contratoId) {
    try {
        // Resumo financeiro (crítico - se falhar, não continua)
        const resumoResp = await api.get(`/contratos/${contratoId}/resumo-financeiro`);
        if (!resumoResp.ok) throw new Error('Erro ao carregar resumo');
        const resumo = await resumoResp.json();
            atualizarKPIsContrato(resumo);

        // Desempenho básico (pode ser complementado pelos boletins)
        const desempenho = {
            dias_decorridos: resumo.dias_decorridos,
            dias_totais: resumo.dias_totais,
            percentual_tempo: resumo.percentual_tempo,
            status_desempenho: resumo.status_desempenho,
            prazo_original_dias: contratoSelecionado?.prazo_original_dias || null
        };

        // Carrega os boletins para calcular dias efetivamente medidos
        let diasMedidos = 0;
        try {
            const bmsResp = await api.get(`/contratos/${contratoId}/boletins`);
            const bms = bmsResp.ok ? await bmsResp.json() : [];
                preencherTabelaBoletins(bms);

            // Calcula a soma dos períodos (dias) de boletins aprovados/faturados
            diasMedidos = bms
                .filter(bm => ['APROVADO', 'FATURADO'].includes(bm.status))
                .reduce((total, bm) => {
                    if (bm.periodo_inicio && bm.periodo_fim) {
                        const inicio = new Date(bm.periodo_inicio);
                        const fim = new Date(bm.periodo_fim);
                        // Adiciona 1 para incluir o dia final
                        const diff = Math.ceil((fim - inicio) / (1000 * 60 * 60 * 24)) + 1;
                                    return total + diff;
                    }
                    return total;
                }, 0);
            } catch (e) {
            console.warn('Erro ao carregar boletins', e);
            preencherTabelaBoletins([]);
        }

        // Atualiza o painel de ritmo com os dias calculados a partir dos boletins
        atualizarPainelRitmo(resumo, desempenho, diasMedidos);

        // Notas fiscais
        let nfs = [];
        try {
            const nfsResp = await api.get(`/faturamentos?contrato_id=${contratoId}`);
            nfs = nfsResp.ok ? await nfsResp.json() : [];
            preencherTabelaNFs(nfs);
        } catch (e) {
            console.warn('Erro ao carregar notas fiscais', e);
            preencherTabelaNFs([]);
        }

        // Pagamentos
        try {
            const pagamentosResp = await api.get(`/pagamentos?contrato_id=${contratoId}`);
            const pagamentos = pagamentosResp.ok ? await pagamentosResp.json() : [];
            preencherTabelaPagamentos(pagamentos, nfs);
        } catch (e) {
            console.warn('Erro ao carregar pagamentos', e);
            preencherTabelaPagamentos([], nfs);
        }

        // Alertas
        try {
            const alertasResp = await api.get(`/alertas?contrato_id=${contratoId}`);
            const alertas = alertasResp.ok ? await alertasResp.json() : [];
            preencherAlertasContrato(alertas);
        } catch (e) {
            console.warn('Erro ao carregar alertas', e);
            preencherAlertasContrato([]);
        }

        // Aditivos
        try {
            const aditivosResp = await api.get(`/contratos/${contratoId}/aditivos`);
            const aditivos = aditivosResp.ok ? await aditivosResp.json() : [];
            preencherTabelaAditivos(aditivos);
        } catch (e) {
            console.warn('Erro ao carregar aditivos', e);
            preencherTabelaAditivos([]);
        }

        // Carrega o gráfico do contrato
        const meses = document.getElementById('periodo-grafico')?.value || 12;
        const dadosGrafico = await carregarDadosGrafico(contratoId, meses);
        renderizarGrafico(dadosGrafico);

        // Carrega a projeção financeira
        await carregarProjecao(contratoId);

    } catch (error) {
        console.error('Erro crítico ao carregar dados do contrato:', error);
        mostrarErro('Falha ao carregar detalhes do contrato.');
    }
}

function atualizarKPIsContrato(resumo) {
    const kpis = {
        '#kpi-valor-total .kpi-value': resumo.valor_total_contrato,
        '#kpi-executado .kpi-value': resumo.valor_executado,
        '#kpi-faturado .kpi-value': resumo.valor_faturado,
        '#kpi-recebido .kpi-value': resumo.valor_recebido,
        '#kpi-perc-fisico .kpi-value': resumo.percentual_fisico,
        '#kpi-perc-financeiro .kpi-value': resumo.percentual_financeiro
    };
    for (const [selector, valor] of Object.entries(kpis)) {
        const el = document.querySelector(selector);
        if (el) {
            if (selector.includes('perc')) {
                el.innerText = formatarPercentual(valor);
            } else {
                el.innerText = formatarMoeda(valor);
            }
        }
    }

    // KPIs secundários
    const percTempoEl = document.querySelector('#kpi-perc-tempo .kpi-value');
    if (percTempoEl) {
        if (resumo.percentual_tempo !== null && resumo.percentual_tempo !== undefined) {
            percTempoEl.innerText = formatarPercentual(resumo.percentual_tempo);
        } else {
            percTempoEl.innerText = '—'; // ou 'Sem prazo'
        }
    }
    const riscoEl = document.querySelector('#kpi-risco .kpi-value');
    if (riscoEl) {
        const status = resumo.status_desempenho;
        if (status === 'ATRASADO') riscoEl.innerText = '🔴 Alto';
        else if (status === 'EM_DIA') riscoEl.innerText = '🟢 Baixo';
        else if (status === 'ADIANTADO') riscoEl.innerText = '🟡 Moderado';
        else if (status === 'SEM_PRAZO') riscoEl.innerText = '⚪ Sem prazo'; // adicionar essa linha
        else riscoEl.innerText = '⚪ Desconhecido';
    }
    const statusEl = document.querySelector('#kpi-status .kpi-value');
    if (statusEl) statusEl.innerText = getTextoStatus(resumo.status_desempenho);
}

// Função auxiliar para formatar o período
function formatarPeriodo(inicio, fim) {
    if (!inicio || !fim) return '-';
    return `${formatarData(inicio)} a ${formatarData(fim)}`;
}

function preencherTabelaNFs(nfs) {
    const tbody = document.querySelector('#tabela-nfs tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!nfs || nfs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhuma nota fiscal encontrada.</td></tr>';
        return;
    }
    nfs.forEach(nf => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${nf.numero_nf || ''}</td>
            <td>${formatarData(nf.data_emissao)}</td>
            <td>${formatarMoeda(nf.valor_bruto_nf)}</td>
            <td>${formatarMoeda(nf.valor_liquido_nf)}</td>
            <td><span class="badge badge-${getClasseStatusNF(nf.status)}">${nf.status || ''}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function preencherTabelaPagamentos(pagamentos, nfs) {
    const tbody = document.querySelector('#tabela-pagamentos tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!pagamentos || pagamentos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Nenhum pagamento registrado.</td></tr>';
        return;
    }
    pagamentos.forEach(pg => {
        const nf = nfs.find(n => n.id === pg.faturamento_id);
        const nfNumero = nf ? nf.numero_nf : pg.faturamento_id;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${formatarData(pg.data_pagamento)}</td>
            <td>${formatarMoeda(pg.valor_pago)}</td>
            <td>${nfNumero}</td>
            <td>${pg.comprovante_url ? `<a href="${pg.comprovante_url}" target="_blank">Ver</a>` : '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function preencherAlertasContrato(alertas) {
    const container = document.getElementById('lista-alertas-contrato');
    if (!container) return;
    container.innerHTML = '';
    if (!alertas || alertas.length === 0) {
        container.innerHTML = '<div class="notification-item">Nenhum alerta para este contrato.</div>';
        return;
    }
    alertas.forEach(a => {
        const div = document.createElement('div');
        div.className = 'notification-item';
        div.innerHTML = `
            <div class="notification-icon ${a.tipo || ''}">${getIconeAlerta(a.tipo)}</div>
            <div class="notification-content">
                <div class="notification-title">${a.titulo || ''}</div>
                <div class="notification-text">${a.mensagem || ''}</div>
                <div class="notification-time">${a.data || ''}</div>
            </div>
        `;
        container.appendChild(div);
    });
}

// ---------- Utilitários ----------
function formatarMoeda(valor) {
    if (valor === null || valor === undefined) return 'R$ 0,00';
    return parseFloat(valor).toLocaleString('pt-BR', { 
        style: 'currency', 
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatarPercentual(valor) {
    if (valor === null || valor === undefined) return '—';
    // Backend sempre envia percentuais como 0-100 (ex: 60.5 = 60,5%)
    // toLocaleString com style:'percent' espera fração (0.605), então divide por 100
    const num = parseFloat(valor) / 100;
    return num.toLocaleString('pt-BR', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    });
}

function formatarData(dataStr) {
    if (!dataStr) return '-';
    const d = new Date(dataStr);
    return d.toLocaleDateString('pt-BR');
}

function getClasseProgresso(percentual) {
    if (percentual >= 80) return 'success';
    if (percentual >= 50) return 'primary';
    if (percentual >= 20) return 'warning';
    return 'danger';
}

function getClasseStatus(status) {
    const mapa = {
        'EM_DIA': 'success',
        'ATRASADO': 'danger',
        'ADIANTADO': 'warning',
        'SEM_PRAZO': 'secondary',
        'SEM_MEDICAO': 'secondary'
    };
    return mapa[status] || 'secondary';
}

function getTextoStatus(status) {
    const mapa = {
        'EM_DIA': 'Em dia',
        'ATRASADO': 'Atrasado',
        'ADIANTADO': 'Adiantado',
        'SEM_PRAZO': 'Sem prazo',
        'SEM_MEDICAO': 'Sem medição'
    };
    return mapa[status] || status || 'Desconhecido';
}

function getClasseStatusBM(status) {
    const mapa = {
        'APROVADO': 'success',
        'FATURADO': 'primary',
        'RASCUNHO': 'secondary',
        'CANCELADO': 'danger'
    };
    return mapa[status] || 'secondary';
}

function getClasseStatusNF(status) {
    const mapa = {
        'QUITADO': 'success',
        'PARCIAL': 'warning',
        'PENDENTE': 'secondary',
        'CANCELADA': 'danger',
        'VENCIDO': 'danger'
    };
    return mapa[status] || 'secondary';
}

function getIconeAlerta(tipo) {
    if (tipo === 'danger') {
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
    } else if (tipo === 'warning') {
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    } else {
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
    }
}

function mostrarErro(mensagem) {
    alert(mensagem);
}


function preencherTabelaAditivos(aditivos) {
    const tbody = document.querySelector('#tabela-aditivos tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!aditivos || aditivos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum aditivo encontrado.</td></tr>';
        return;
    }
    
    aditivos.forEach(ad => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${ad.numero_emenda || '-'}</td>
            <td>${formatarData(ad.data_aprovacao)}</td>
            <td>${ad.tipo || '-'}</td>
            <td>${formatarMoeda(ad.valor_acrescimo)}</td>
            <td>${ad.dias_acrescimo || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function preencherTabelaBoletins(bms) {
    const tbody = document.querySelector('#tabela-boletins tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!bms || bms.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum boletim encontrado.</td></tr>';
        return;
    }
    bms.forEach(bm => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${bm.numero_sequencial || ''}</td>
            <td>${formatarPeriodo(bm.periodo_inicio, bm.periodo_fim)}</td>
            <td>${formatarMoeda(bm.valor_total_medido)}</td>
            <td>${formatarMoeda(bm.valor_aprovado)}</td>
            <td><span class="badge badge-${getClasseStatusBM(bm.status)}">${bm.status || ''}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

async function carregarProjecao(contratoId) {
  try {
    const url = contratoId ? `/contratos/${contratoId}/projecao-financeira` : '/dashboard/projecao-global';
    const response = await api.get(url);
    if (!response.ok) throw new Error('Erro ao carregar projeção');
    const dados = await response.json();
    atualizarCardProjecao(dados);
  } catch (error) {
    console.error('Erro na projeção:', error);
  }
}

function atualizarCardProjecao(dados) {
  // Se dados não existir ou estiver vazio, define valores padrão
  if (!dados) {
    dados = {
      ritmo_medio_mensal: 0,
      saldo_a_executar: 0,
      previsao_termino: '—',
      faturamento_30d: 0,
      faturamento_60d: 0,
      faturamento_90d: 0
    };
  }

  document.getElementById('ritmo-medio').innerText = formatarMoeda(dados.ritmo_medio_mensal);
  document.getElementById('saldo-executar').innerText = formatarMoeda(dados.saldo_a_executar);
  document.getElementById('previsao-termino').innerText = dados.previsao_termino || '—';

  const maxValor = Math.max(dados.faturamento_30d, dados.faturamento_60d, dados.faturamento_90d) || 1;
  document.getElementById('barra-30d').style.width = (dados.faturamento_30d / maxValor * 80) + '%';
  document.getElementById('barra-30d').innerText = formatarMoeda(dados.faturamento_30d);
  document.getElementById('barra-60d').style.width = (dados.faturamento_60d / maxValor * 80) + '%';
  document.getElementById('barra-60d').innerText = formatarMoeda(dados.faturamento_60d);
  document.getElementById('barra-90d').style.width = (dados.faturamento_90d / maxValor * 80) + '%';
  document.getElementById('barra-90d').innerText = formatarMoeda(dados.faturamento_90d);
}