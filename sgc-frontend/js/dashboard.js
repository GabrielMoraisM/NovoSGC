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

// ===== Painel de Ritmo e Projeção =====
function atualizarPainelRitmo(resumo, desempenho) {
    if (!resumo || !desempenho) return;
    const percExecutado = resumo.percentual_fisico || 0;
    const percExecutar = 100 - percExecutado;
    const diasTranscorridos = desempenho.dias_decorridos || 0;
    const diasRestantes = desempenho.dias_totais - diasTranscorridos;

    const ritmoReal = diasTranscorridos > 0 ? (percExecutado / diasTranscorridos) : 0;
    const ritmoNecessario = diasRestantes > 0 ? (percExecutar / diasRestantes) : 0;

    let diasNecessarios = 0;
    let dataTermino = '-';
    let statusRitmo = '';

    if (ritmoReal > 0) {
        diasNecessarios = Math.ceil(percExecutar / ritmoReal);
        const novaData = new Date();
        novaData.setDate(novaData.getDate() + diasNecessarios);
        dataTermino = novaData.toLocaleDateString('pt-BR');

        if (ritmoNecessario > ritmoReal * 1.2) {
            statusRitmo = '🔴 Ritmo insuficiente';
        } else if (ritmoNecessario > ritmoReal) {
            statusRitmo = '🟡 Ritmo abaixo do necessário';
        } else {
            statusRitmo = '🟢 Ritmo adequado';
        }
    }

    document.getElementById('perc-executado').innerText = percExecutado.toFixed(2) + '%';
    document.getElementById('perc-executar').innerText = percExecutar.toFixed(2) + '%';
    document.getElementById('ritmo-real').innerText = ritmoReal.toFixed(4) + '%';
    document.getElementById('ritmo-necessario').innerText = ritmoNecessario.toFixed(4) + '%';
    document.getElementById('dias-transcorridos').innerText = diasTranscorridos + ' dias';
    document.getElementById('dias-restantes').innerText = diasRestantes + ' dias';
    document.getElementById('dias-necessarios').innerText = diasNecessarios + ' dias';
    document.getElementById('data-termino').innerText = dataTermino;
    document.getElementById('status-ritmo').innerText = statusRitmo;
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
        const totalContratos = contratos.length;
        const valorTotalContratado = contratos.reduce((acc, c) => acc + (parseFloat(c.valor_total) || 0), 0);
        const valorExecutadoTotal = contratos.reduce((acc, c) => acc + (parseFloat(c.valor_executado) || 0), 0);
        const valorFaturadoTotal = contratos.reduce((acc, c) => acc + (parseFloat(c.valor_faturado) || 0), 0);
        const valorRecebidoTotal = contratos.reduce((acc, c) => acc + (parseFloat(c.valor_recebido) || 0), 0);
        const percFisico = valorTotalContratado ? (valorExecutadoTotal / valorTotalContratado * 100) : 0;
        const percFinanceiro = valorTotalContratado ? (valorRecebidoTotal / valorTotalContratado * 100) : 0;

        const contratosRecentes = [...contratos]
            .sort((a, b) => b.id - a.id)
            .slice(0, 5)
            .map(c => ({
                numero_contrato: c.numero_contrato,
                cliente_nome: c.cliente_nome,
                percentual_fisico: parseFloat(c.percentual_fisico) || 0,
                status_desempenho: c.status_desempenho || 'SEM_PRAZO'
            }));

        const alertasRecentes = [
            {
                tipo: 'warning',
                titulo: 'Desequilíbrio Financeiro',
                mensagem: 'CT-2024-003 com variação de 8.5%',
                data: 'Há 2 horas'
            },
            {
                tipo: 'danger',
                titulo: 'Prazo Crítico',
                mensagem: 'CT-2024-004 com atraso de 15 dias',
                data: 'Há 30 minutos'
            }
        ];

        atualizarKPIsGlobais({
            valor_total_contratado: valorTotalContratado,
            valor_executado_total: valorExecutadoTotal,
            valor_faturado_total: valorFaturadoTotal,
            valor_recebido_total: valorRecebidoTotal,
            percentual_global_fisico: percFisico,
            percentual_global_recebido: percFinanceiro,
            contratos_recentes: contratosRecentes,
            alertas_recentes: alertasRecentes
        });

        // Carrega o gráfico global
        const meses = document.getElementById('periodo-grafico')?.value || 12;
        const dadosGrafico = await carregarDadosGrafico(null, meses);
        renderizarGrafico(dadosGrafico);

    } catch (error) {
        console.error('Erro ao carregar resumo global:', error);
        mostrarErro('Falha ao carregar dados do dashboard.');
    }
}

function atualizarKPIsGlobais(data) {
    const kpis = {
        '#kpi-valor-total .kpi-value': data.valor_total_contratado,
        '#kpi-executado .kpi-value': data.valor_executado_total,
        '#kpi-faturado .kpi-value': data.valor_faturado_total,
        '#kpi-recebido .kpi-value': data.valor_recebido_total,
        '#kpi-perc-fisico .kpi-value': data.percentual_global_fisico,
        '#kpi-perc-financeiro .kpi-value': data.percentual_global_recebido
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

        // Chama o painel de ritmo
        const desempenho = {
            dias_decorridos: resumo.dias_decorridos,
            dias_totais: resumo.dias_totais,
            percentual_tempo: resumo.percentual_tempo,
            status_desempenho: resumo.status_desempenho
        };
        atualizarPainelRitmo(resumo, desempenho);

        // Boletins
        try {
            const bmsResp = await api.get(`/contratos/${contratoId}/boletins`);
            const bms = bmsResp.ok ? await bmsResp.json() : [];
            preencherTabelaBoletins(bms);
        } catch (e) {
            console.warn('Erro ao carregar boletins', e);
            preencherTabelaBoletins([]);
        }

        // Notas fiscais (declaramos nfs fora para usar nos pagamentos)
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
    if (percTempoEl) percTempoEl.innerText = formatarPercentual(resumo.percentual_tempo);
    const riscoEl = document.querySelector('#kpi-risco .kpi-value');
    if (riscoEl) {
        const status = resumo.status_desempenho;
        if (status === 'ATRASADO') riscoEl.innerText = '🔴 Alto';
        else if (status === 'EM_DIA') riscoEl.innerText = '🟢 Baixo';
        else if (status === 'ADIANTADO') riscoEl.innerText = '🟡 Moderado';
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
    console.log('Preenchendo tabela de NFs:', nfs);
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
    console.log('Preenchendo tabela de pagamentos:', pagamentos);
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
    if (valor === null || valor === undefined) return '0%';
    return parseFloat(valor).toLocaleString('pt-BR', {
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

// Aditivos
async function carregarAditivos(contratoId) {
    console.log('Carregando aditivos para contrato:', contratoId);
    try {
        const response = await api.get(`/contratos/${contratoId}/aditivos`);
        console.log('Resposta de aditivos:', response);
        if (response.ok) {
            const aditivos = await response.json();
            console.log('Dados de aditivos recebidos:', aditivos);
            preencherTabelaAditivos(aditivos);
        } else {
            console.warn('Erro ao carregar aditivos. Status:', response.status);
            preencherTabelaAditivos([]);
        }
    } catch (error) {
        console.error('Erro ao carregar aditivos:', error);
        preencherTabelaAditivos([]);
    }
}

function preencherTabelaAditivos(aditivos) {
    const tbody = document.querySelector('#tabela-aditivos tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!aditivos || aditivos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum aditivo encontrado.</td></tr>';
        return;
    }
    
    console.log('Aditivos recebidos:', aditivos);
    
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
    console.log('Preenchendo boletins:', bms);
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