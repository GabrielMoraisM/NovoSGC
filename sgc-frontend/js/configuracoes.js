import { apiFetch } from './api.js';

// ===== Estado =====
let logs = [];
let usuarios = []; // para preencher o filtro
let currentPage = 1;
let pageSize = 20;
let total = 0;
let filtros = {
    usuarioId: '',
    modulo: '',
    usuarioNome: ''
};

// ===== Carregar lista de usuários para o filtro =====
async function carregarUsuarios() {
    try {
        const response = await apiFetch('/usuarios/');
        usuarios = await response.json();
        const select = document.getElementById('filter-usuario');
        usuarios.forEach(u => {
            const option = document.createElement('option');
            option.value = u.id;
            option.textContent = `${u.nome} (${u.email})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
    }
}

// ===== Carregar logs do backend =====
async function carregarLogs() {
    const params = new URLSearchParams({
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
        ...(filtros.usuarioId && { usuario_id: filtros.usuarioId }),
        ...(filtros.modulo && { entidade: filtros.modulo }),
        ...(filtros.usuarioNome && { usuario_email_like: filtros.usuarioNome })
    });

    try {
        const response = await apiFetch(`/logs/?${params}`);
        logs = await response.json();
        // Idealmente, o backend retornaria também o total de registros
        // Por enquanto, assumimos que se veio menos que o limite, é a última página
        total = logs.length < pageSize ? (currentPage - 1) * pageSize + logs.length : currentPage * pageSize + 1;
        renderizarTabela();
        atualizarPaginacao();
    } catch (error) {
        console.error('Erro ao carregar logs:', error);
    }
}

// ===== Renderizar tabela =====
function renderizarTabela() {
    const tbody = document.querySelector('#logs-table tbody');
    tbody.innerHTML = '';

    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhum log encontrado.</td></tr>';
        return;
    }

    logs.forEach(log => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${new Date(log.created_at).toLocaleString('pt-BR')}</td>
            <td>${log.usuario_email || 'Sistema'}</td>
            <td><span class="badge badge-${log.acao.toLowerCase()}">${log.acao}</span></td>
            <td>${log.entidade}</td>
            <td>${formatarDescricao(log)}</td>
            <td><button class="btn-view-details" onclick="verDetalhes(${log.id})">Detalhes</button></td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('logs-count').textContent = `Mostrando ${logs.length} registros`;
}

function formatarDescricao(log) {
    if (log.acao === 'CREATE') {
        return `Criou ${log.entidade}`;
    } else if (log.acao === 'UPDATE') {
        return `Atualizou ${log.entidade}`;
    } else if (log.acao === 'DELETE') {
        return `Removeu ${log.entidade}`;
    } else if (log.acao === 'LOGIN') {
        return 'Fez login';
    } else if (log.acao === 'LOGOUT') {
        return 'Fez logout';
    }
    return `Ação ${log.acao} em ${log.entidade}`;
}

// ===== Paginação =====
function atualizarPaginacao() {
    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = logs.length < pageSize; // se veio menos, é última página
    document.getElementById('page-info').textContent = currentPage;
}

// ===== Event listeners =====
document.getElementById('btn-filtrar')?.addEventListener('click', () => {
    filtros.usuarioId = document.getElementById('filter-usuario').value;
    filtros.modulo = document.getElementById('filter-modulo').value;
    filtros.usuarioNome = document.getElementById('filter-usuario-nome').value;
    currentPage = 1;
    carregarLogs();
});

document.getElementById('btn-limpar')?.addEventListener('click', () => {
    document.getElementById('filter-usuario').value = '';
    document.getElementById('filter-modulo').value = '';
    document.getElementById('filter-usuario-nome').value = '';
    filtros = { usuarioId: '', modulo: '', usuarioNome: '' };
    currentPage = 1;
    carregarLogs();
});

document.getElementById('btn-atualizar')?.addEventListener('click', () => {
    carregarLogs();
});

document.getElementById('prev-page')?.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        carregarLogs();
    }
});

document.getElementById('next-page')?.addEventListener('click', () => {
    currentPage++;
    carregarLogs();
});

// ===== Função global para ver detalhes =====
window.verDetalhes = (logId) => {
    const log = logs.find(l => l.id === logId);
    if (!log) return;
    const modal = document.getElementById('log-details-modal');
    const content = document.getElementById('log-details-content');
    content.textContent = JSON.stringify(log.dados_novos || log.dados_antigos || log, null, 2);
    modal.classList.add('active');
};

// ===== Inicialização =====
document.addEventListener('DOMContentLoaded', () => {
    carregarUsuarios(); // opcional, pode ser removido se não quiser o filtro por ID
    carregarLogs();
});