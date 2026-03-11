import { apiFetch } from './api.js';

// ============================================================
// Labels legíveis por humanos
// ============================================================
const MODULO_LABELS = {
    contratos:    'Contratos',
    empresas:     'Empresas',
    boletins:     'Medições (BMs)',
    prateleira:   'Prateleira',
    arquivos:     'Arquivos',
    faturamentos: 'Faturamentos (NFs)',
    pagamentos:   'Pagamentos',
    usuarios:     'Usuários',
};

const ACAO_LABELS = {
    CREATE:        'Criação',
    UPDATE:        'Atualização',
    DELETE:        'Exclusão',
    APPROVE:       'Aprovação',
    CANCEL:        'Cancelamento',
    UPLOAD:        'Upload',
    STATUS_UPDATE: 'Mudança de Status',
    LOGIN:         'Login',
    LOGOUT:        'Logout',
};

// ============================================================
// Estado
// ============================================================
let logs = [];
let currentPage = 1;
const pageSize = 20;

let filtros = {
    usuarioId:    '',
    modulo:       '',
    acao:         '',
    dataInicio:   '',
    dataFim:      '',
    usuarioNome:  '',
};

// ============================================================
// Helpers
// ============================================================
function getBadgeClass(acao) {
    if (!acao) return '';
    return `badge badge-${acao.toLowerCase()}`;
}

function formatarDataHora(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('pt-BR', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
    });
}

function nomeModulo(entidade) {
    return MODULO_LABELS[entidade] || entidade || '—';
}

function nomeAcao(acao) {
    return ACAO_LABELS[acao] || acao || '—';
}

// ============================================================
// Descrição legível por linha
// ============================================================
function formatarDescricao(log) {
    const entidade = nomeModulo(log.entidade);
    const id = log.entidade_id ? ` #${log.entidade_id}` : '';

    switch (log.acao) {
        case 'CREATE':
            return `Criou ${entidade}${id}`;
        case 'UPDATE':
            return `Atualizou ${entidade}${id}`;
        case 'DELETE':
            return `Removeu ${entidade}${id}`;
        case 'APPROVE':
            return `Aprovou ${entidade}${id}`;
        case 'CANCEL': {
            const motivo = log.dados_novos?.motivo || log.dados_antigos?.motivo || '';
            return motivo
                ? `Cancelou ${entidade}${id} — ${motivo}`
                : `Cancelou ${entidade}${id}`;
        }
        case 'UPLOAD': {
            const nome = log.dados_novos?.nome_original || '';
            return nome ? `Upload: ${nome}` : `Upload em ${entidade}${id}`;
        }
        case 'STATUS_UPDATE': {
            const status = log.dados_novos?.status || '';
            return status
                ? `Mudou status de ${entidade}${id} para ${status}`
                : `Mudou status de ${entidade}${id}`;
        }
        case 'LOGIN':
            return 'Fez login no sistema';
        case 'LOGOUT':
            return 'Saiu do sistema';
        default:
            return `${nomeAcao(log.acao)} em ${entidade}${id}`;
    }
}

// ============================================================
// Carregar lista de usuários para o filtro
// ============================================================
async function carregarUsuarios() {
    try {
        const response = await apiFetch('/usuarios/');
        const usuarios = await response.json();
        const select = document.getElementById('filter-usuario');
        if (!Array.isArray(usuarios)) return;
        usuarios.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u.id;
            opt.textContent = `${u.nome || u.email} (${u.email})`;
            select.appendChild(opt);
        });
    } catch (err) {
        console.warn('Erro ao carregar usuários para filtro:', err);
    }
}

// ============================================================
// Carregar logs do backend
// ============================================================
async function carregarLogs() {
    const params = new URLSearchParams({
        skip:  (currentPage - 1) * pageSize,
        limit: pageSize,
    });

    if (filtros.usuarioId)   params.set('usuario_id',  filtros.usuarioId);
    if (filtros.modulo)      params.set('entidade',     filtros.modulo);
    if (filtros.acao)        params.set('acao',         filtros.acao);
    if (filtros.dataInicio)  params.set('data_inicio',  filtros.dataInicio);
    if (filtros.dataFim)     params.set('data_fim',     filtros.dataFim);

    try {
        const response = await apiFetch(`/logs/?${params}`);
        if (!response.ok) {
            if (response.status === 403) {
                renderizarErro('Acesso negado. Apenas ADMIN/TI podem visualizar os logs.');
            } else {
                renderizarErro(`Erro ao carregar logs (${response.status}).`);
            }
            return;
        }
        logs = await response.json();
        renderizarTabela();
        atualizarPaginacao();
    } catch (err) {
        console.error('Erro ao carregar logs:', err);
        renderizarErro('Falha de conexão ao carregar os logs.');
    }
}

// ============================================================
// Renderizar tabela
// ============================================================
function renderizarErro(msg) {
    const tbody = document.querySelector('#logs-table tbody');
    tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="color:var(--danger)">${msg}</td></tr>`;
}

function renderizarTabela() {
    const tbody = document.querySelector('#logs-table tbody');
    tbody.innerHTML = '';

    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-secondary">Nenhum log encontrado.</td></tr>';
        document.getElementById('logs-count').textContent = 'Mostrando 0 registros';
        return;
    }

    logs.forEach(log => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="white-space:nowrap;font-size:0.8rem">${formatarDataHora(log.created_at)}</td>
            <td style="font-size:0.82rem">${log.usuario_email || '<em style="color:var(--text-secondary)">Sistema</em>'}</td>
            <td><span class="${getBadgeClass(log.acao)}">${nomeAcao(log.acao)}</span></td>
            <td style="font-size:0.82rem">${nomeModulo(log.entidade)}</td>
            <td style="font-size:0.82rem;max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"
                title="${formatarDescricao(log).replace(/"/g, '&quot;')}">${formatarDescricao(log)}</td>
            <td style="text-align:center">
                <button class="btn btn-sm btn-secondary" onclick="verDetalhes(${log.id})" title="Ver detalhes">🔎</button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('logs-count').textContent = `Mostrando ${logs.length} registro${logs.length !== 1 ? 's' : ''}`;
}

// ============================================================
// Paginação
// ============================================================
function atualizarPaginacao() {
    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = logs.length < pageSize;
    document.getElementById('page-info').textContent = currentPage;
}

// ============================================================
// Modal de detalhes — diff side-by-side
// ============================================================
window.verDetalhes = (logId) => {
    const log = logs.find(l => l.id === logId);
    if (!log) return;

    const modal = document.getElementById('log-details-modal');
    const title = document.getElementById('log-details-title');
    const body  = document.getElementById('log-details-body');

    title.textContent = `${nomeAcao(log.acao)} — ${nomeModulo(log.entidade)}${log.entidade_id ? ' #' + log.entidade_id : ''}`;

    const temAntigos = log.dados_antigos && Object.keys(log.dados_antigos).length > 0;
    const temNovos   = log.dados_novos   && Object.keys(log.dados_novos).length > 0;
    const single     = (temAntigos && !temNovos) || (!temAntigos && temNovos);

    let diffHTML = '';

    if (!temAntigos && !temNovos) {
        diffHTML = `<div class="log-diff single">
            <div class="diff-panel unico">
                <h4>Informações</h4>
                <p class="diff-empty">Sem dados adicionais registrados para esta ação.</p>
            </div>
        </div>`;
    } else if (single) {
        const isNovo   = temNovos;
        const dados    = isNovo ? log.dados_novos : log.dados_antigos;
        const panelCls = isNovo ? 'depois' : 'antes';
        const panelLbl = isNovo ? 'Dados registrados' : 'Dados anteriores';
        diffHTML = `<div class="log-diff single">
            <div class="diff-panel ${panelCls}">
                <h4>${panelLbl}</h4>
                <pre>${JSON.stringify(dados, null, 2)}</pre>
            </div>
        </div>`;
    } else {
        diffHTML = `<div class="log-diff">
            <div class="diff-panel antes">
                <h4>&#10007; Antes</h4>
                <pre>${JSON.stringify(log.dados_antigos, null, 2)}</pre>
            </div>
            <div class="diff-panel depois">
                <h4>&#10003; Depois</h4>
                <pre>${JSON.stringify(log.dados_novos, null, 2)}</pre>
            </div>
        </div>`;
    }

    const metaIP    = log.ip         ? `<span>🌐 IP: ${log.ip}</span>` : '';
    const metaAgent = log.user_agent ? `<span>💻 ${log.user_agent}</span>` : '';

    body.innerHTML = `
        <div class="log-detail-header">
            <div class="detail-item">
                <span class="detail-label">Data / Hora</span>
                <span class="detail-value">${formatarDataHora(log.created_at)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Usuário</span>
                <span class="detail-value">${log.usuario_email || 'Sistema'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Ação</span>
                <span class="detail-value"><span class="${getBadgeClass(log.acao)}">${nomeAcao(log.acao)}</span></span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Módulo / ID</span>
                <span class="detail-value">${nomeModulo(log.entidade)}${log.entidade_id ? ' #' + log.entidade_id : ''}</span>
            </div>
        </div>
        ${diffHTML}
        ${(metaIP || metaAgent) ? `<div class="log-meta">${metaIP}${metaAgent}</div>` : ''}
    `;

    modal.classList.add('active');
};

// ============================================================
// Listeners dos filtros
// ============================================================
function coletarFiltros() {
    filtros.usuarioId   = document.getElementById('filter-usuario').value;
    filtros.modulo      = document.getElementById('filter-modulo').value;
    filtros.acao        = document.getElementById('filter-acao').value;
    filtros.dataInicio  = document.getElementById('filter-data-inicio').value;
    filtros.dataFim     = document.getElementById('filter-data-fim').value;
    filtros.usuarioNome = document.getElementById('filter-usuario-nome').value;
}

function limparFiltrosUI() {
    document.getElementById('filter-usuario').value      = '';
    document.getElementById('filter-modulo').value       = '';
    document.getElementById('filter-acao').value         = '';
    document.getElementById('filter-data-inicio').value  = '';
    document.getElementById('filter-data-fim').value     = '';
    document.getElementById('filter-usuario-nome').value = '';
    filtros = { usuarioId: '', modulo: '', acao: '', dataInicio: '', dataFim: '', usuarioNome: '' };
}

document.getElementById('btn-filtrar')?.addEventListener('click', () => {
    coletarFiltros();
    currentPage = 1;
    carregarLogs();
});

document.getElementById('btn-limpar')?.addEventListener('click', () => {
    limparFiltrosUI();
    currentPage = 1;
    carregarLogs();
});

document.getElementById('btn-atualizar')?.addEventListener('click', () => {
    carregarLogs();
});

document.getElementById('prev-page')?.addEventListener('click', () => {
    if (currentPage > 1) { currentPage--; carregarLogs(); }
});

document.getElementById('next-page')?.addEventListener('click', () => {
    currentPage++;
    carregarLogs();
});

// Permitir Enter nos filtros de texto
['filter-usuario-nome'].forEach(id => {
    document.getElementById(id)?.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
            coletarFiltros();
            currentPage = 1;
            carregarLogs();
        }
    });
});

// ============================================================
// Inicialização
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    carregarUsuarios();
    carregarLogs();
});
