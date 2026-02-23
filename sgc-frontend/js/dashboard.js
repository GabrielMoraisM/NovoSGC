// dashboard.js
// Sistema de Gestão de Contratos e Medições - Heca Engenharia
// Dashboard com visão global e por contrato

let contratos = [];
let contratoSelecionado = null;

document.addEventListener('DOMContentLoaded', function() {
    if (typeof api === 'undefined') {
        console.error('Erro: objeto api não está definido. Verifique se o arquivo api.js foi carregado corretamente.');
        mostrarErro('Falha na inicialização: API não disponível. Recarregue a página ou contate o suporte.');
        return;
    }
    carregarContratos();
    configurarEventos();
});

// ---------- Configuração de Eventos ----------
function configurarEventos() {
    const selector = document.getElementById('contrato-selector');
    if (selector) {
        selector.addEventListener('change', async (e) => {
            const id = e.target.value;
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
}

function mostrarElementosGlobais(mostrar) {
    const detalhes = document.getElementById('contrato-detalhes');
    const recentes = document.getElementById('recentes-container');
    const alertas = document.getElementById('alertas-recentes-container');
    if (detalhes) detalhes.style.display = mostrar ? 'none' : 'block';
    if (recentes) recentes.style.display = mostrar ? 'block' : 'none';
    if (alertas) alertas.style.display = mostrar ? 'block' : 'none';
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
        // Reutiliza a lista de contratos já carregada (com resumo incluso)
        const totalContratos = contratos.length;
        const valorTotalContratado = contratos.reduce((acc, c) => acc + (parseFloat(c.valor_total) || 0), 0);
        const valorExecutadoTotal = contratos.reduce((acc, c) => acc + (parseFloat(c.valor_executado) || 0), 0);
        const valorFaturadoTotal = contratos.reduce((acc, c) => acc + (parseFloat(c.valor_faturado) || 0), 0);
        const valorRecebidoTotal = contratos.reduce((acc, c) => acc + (parseFloat(c.valor_recebido) || 0), 0);
        const percFisico = valorTotalContratado ? (valorExecutadoTotal / valorTotalContratado * 100) : 0;
        const percFinanceiro = valorTotalContratado ? (valorRecebidoTotal / valorTotalContratado * 100) : 0;

        // Contratos recentes (ordenar por id decrescente e pegar os 5 primeiros)
        const contratosRecentes = [...contratos]
            .sort((a, b) => b.id - a.id)
            .slice(0, 5)
            .map(c => ({
                numero_contrato: c.numero_contrato,
                cliente_nome: c.cliente_nome,
                percentual_fisico: parseFloat(c.percentual_fisico) || 0,
                status_desempenho: c.status_desempenho || 'SEM_PRAZO'
            }));

        // Alertas mock (podem vir de um endpoint futuro)
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

// ---------- Dados de um Contrato Específico ----------
async function carregarDadosContrato(contratoId) {
    try {
        const resumoResp = await api.get(`/contratos/${contratoId}/resumo-financeiro`);
        if (!resumoResp.ok) throw new Error('Erro ao carregar resumo');
        const resumo = await resumoResp.json();
        atualizarKPIsContrato(resumo);
        
        // Comente ou remova as chamadas abaixo até que os endpoints existam
        /*
        const bmsResp = await api.get(`/boletins?contrato_id=${contratoId}`);
        const bms = bmsResp.ok ? await bmsResp.json() : [];
        preencherTabelaBoletins(bms);
        
        const nfsResp = await api.get(`/faturamentos?contrato_id=${contratoId}`);
        const nfs = nfsResp.ok ? await nfsResp.json() : [];
        preencherTabelaNFs(nfs);
        
        const pagamentosResp = await api.get(`/pagamentos?contrato_id=${contratoId}`);
        const pagamentos = pagamentosResp.ok ? await pagamentosResp.json() : [];
        preencherTabelaPagamentos(pagamentos, nfs);
        
        const alertasResp = await api.get(`/alertas?contrato_id=${contratoId}`);
        const alertas = alertasResp.ok ? await alertasResp.json() : [];
        preencherAlertasContrato(alertas);
        */
    } catch (error) {
        console.error('Erro ao carregar dados do contrato:', error);
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
            <td>${bm.numero || ''}</td>
            <td>${formatarData(bm.data_medicao)}</td>
            <td>${formatarMoeda(bm.valor_total_medido)}</td>
            <td>${formatarMoeda(bm.valor_aprovado)}</td>
            <td><span class="badge badge-${getClasseStatusBM(bm.status)}">${bm.status || ''}</span></td>
        `;
        tbody.appendChild(tr);
    });
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
    if (valor === null || valor === undefined) return '0%';
    return parseFloat(valor).toLocaleString('pt-BR', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).replace('%', ' %'); // ou só retorna com %
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