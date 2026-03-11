// arquivos.js — Gestão de Arquivos (Documentos)
import {
  getContratos,
  getArvoreArquivos,
  uploadArquivo,
  deleteArquivo
} from './api.js';

// ── Estado global ──────────────────────────────────────────────────────────
let contratoAtualId = null;

// ── Inicialização ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  await carregarContratos();

  const sel = document.getElementById('contrato-selector');
  sel.addEventListener('change', async () => {
    const id = sel.value;
    if (!id) {
      document.getElementById('tree-container').innerHTML = `
        <div class="empty-tree" id="tree-placeholder">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" width="64" height="64">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
          <p class="text-muted">Selecione um contrato para visualizar os arquivos</p>
        </div>`;
      contratoAtualId = null;
      return;
    }
    contratoAtualId = parseInt(id);
    await carregarArvore(contratoAtualId);
  });
});

async function carregarContratos() {
  try {
    const contratos = await getContratos();
    const sel = document.getElementById('contrato-selector');
    contratos.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      const label = [c.numero_contrato, c.objeto].filter(Boolean).join(' — ');
      opt.textContent = label;
      sel.appendChild(opt);
    });
  } catch (e) {
    showToast('Erro ao carregar contratos: ' + e.message, 'error');
  }
}

async function carregarArvore(contratoId) {
  const container = document.getElementById('tree-container');
  container.innerHTML = '<div class="text-center text-muted" style="padding:2rem">Carregando...</div>';
  try {
    const arvore = await getArvoreArquivos(contratoId);
    renderizarArvore(arvore, container);
  } catch (e) {
    container.innerHTML = `<div class="empty-tree"><p class="text-muted">Erro ao carregar: ${escapeHtml(e.message)}</p></div>`;
    showToast('Erro ao carregar arquivos: ' + e.message, 'error');
  }
}

function renderizarArvore(arvore, container) {
  container.innerHTML = '';
  const div = document.createElement('div');
  div.className = 'file-tree';

  // Nível 1: Contrato
  div.appendChild(criarNodeContrato(arvore.contrato));

  // Nível 2: Boletins
  if (arvore.boletins && arvore.boletins.length > 0) {
    arvore.boletins.forEach(bm => div.appendChild(criarNodeBM(bm)));
  } else {
    const empty = document.createElement('div');
    empty.style.cssText = 'padding:1rem 1.5rem;color:var(--text-muted);font-size:0.875rem;';
    empty.textContent = 'Nenhum boletim de medição cadastrado.';
    div.appendChild(empty);
  }

  container.appendChild(div);
}

function criarNodeContrato(contrato) {
  const children = document.createElement('div');
  children.className = 'tree-children collapsible-content';
  if (contrato.arquivos && contrato.arquivos.length > 0) {
    contrato.arquivos.forEach(f => children.appendChild(criarFileItem(f)));
  }
  children.appendChild(criarUploadBtn('contrato', contrato.id));
  return criarNode(
    `📋 Contrato ${escapeHtml(contrato.numero_contrato || '')}`,
    contrato.arquivos ? contrato.arquivos.length : 0,
    'var(--primary)',
    children
  );
}

function criarNodeBM(bm) {
  const periodo = bm.periodo_inicio
    ? `${formatarDataCurta(bm.periodo_inicio)} – ${formatarDataCurta(bm.periodo_fim)}`
    : '';

  const children = document.createElement('div');
  children.className = 'tree-children collapsible-content';
  if (bm.arquivos && bm.arquivos.length > 0) {
    bm.arquivos.forEach(f => children.appendChild(criarFileItem(f)));
  }
  children.appendChild(criarUploadBtn('boletim', bm.id));
  if (bm.faturamentos && bm.faturamentos.length > 0) {
    bm.faturamentos.forEach(nf => children.appendChild(criarNodeNF(nf)));
  }

  const label = `BM-${bm.numero_sequencial || bm.id}${periodo ? ` <span style="font-weight:400;color:var(--text-muted)">(${periodo})</span>` : ''}`;
  const node = criarNode(label, bm.arquivos ? bm.arquivos.length : 0, 'var(--warning)', children);
  node.style.marginLeft = '1.5rem';
  return node;
}

function criarNodeNF(nf) {
  const children = document.createElement('div');
  children.className = 'tree-children collapsible-content';
  if (nf.arquivos && nf.arquivos.length > 0) {
    nf.arquivos.forEach(f => children.appendChild(criarFileItem(f)));
  }
  children.appendChild(criarUploadBtn('faturamento', nf.id));
  if (nf.pagamentos && nf.pagamentos.length > 0) {
    nf.pagamentos.forEach(pag => children.appendChild(criarNodePagamento(pag)));
  }

  const node = criarNode(
    `NF ${escapeHtml(nf.numero_nf || String(nf.id))}`,
    nf.arquivos ? nf.arquivos.length : 0,
    'var(--success)',
    children
  );
  node.style.marginLeft = '1rem';
  return node;
}

function criarNodePagamento(pag) {
  const children = document.createElement('div');
  children.className = 'tree-children collapsible-content';
  if (pag.arquivos && pag.arquivos.length > 0) {
    pag.arquivos.forEach(f => children.appendChild(criarFileItem(f)));
  }
  children.appendChild(criarUploadBtn('pagamento', pag.id));

  const label = `Pagamento ${formatarDataCurta(pag.data_pagamento)} — ${formatarMoeda(pag.valor_pago)}`;
  const node = criarNode(label, pag.arquivos ? pag.arquivos.length : 0, '#0ea5e9', children);
  node.style.marginLeft = '1rem';
  return node;
}

function criarNode(label, count, color, children) {
  const node = document.createElement('div');
  node.className = 'tree-node';

  const header = document.createElement('div');
  header.className = 'tree-node-header';
  header.innerHTML = `
    <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
      <polyline points="6 9 12 15 18 9"></polyline>
    </svg>
    <svg class="tree-node-icon" style="color:${color}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
    </svg>
    <span class="tree-node-label">${label}</span>
    <span class="tree-node-badge">${count} arquivo(s)</span>
  `;

  header.addEventListener('click', () => {
    const icon = header.querySelector('.toggle-icon');
    children.classList.toggle('collapsed');
    icon.classList.toggle('collapsed');
  });

  node.appendChild(header);
  node.appendChild(children);
  return node;
}

function criarFileItem(arquivo) {
  const ext = (arquivo.nome_original || '').split('.').pop().toLowerCase();
  const iconColor = ext === 'pdf' ? '#ef4444'
    : ext.match(/^(doc|docx)$/) ? '#2563eb'
    : ext.match(/^(xls|xlsx)$/) ? '#16a34a'
    : '#6b7280';

  const item = document.createElement('div');
  item.className = 'file-item';
  item.innerHTML = `
    <svg class="file-icon" style="color:${iconColor}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
    </svg>
    <span class="file-name" title="${escapeHtml(arquivo.nome_original || '')}">${escapeHtml(arquivo.nome_original || 'arquivo')}</span>
    <span class="file-size">${formatarTamanho(arquivo.tamanho)}</span>
    <div class="file-actions">
      <button data-download="${arquivo.id}" data-nome="${escapeHtml(arquivo.nome_original || 'arquivo')}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        Baixar
      </button>
      <button class="danger" data-delete="${arquivo.id}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6l-1 14H6L5 6"></path>
          <path d="M10 11v6M14 11v6M9 6V4h6v2"></path>
        </svg>
        Excluir
      </button>
    </div>
  `;

  item.querySelector('[data-download]').addEventListener('click', async () => {
    await downloadArquivo(arquivo.id, arquivo.nome_original || 'arquivo');
  });
  item.querySelector('[data-delete]').addEventListener('click', async () => {
    await confirmarDeleteArquivo(arquivo.id);
  });

  return item;
}

function criarUploadBtn(entidadeTipo, entidadeId) {
  const wrapper = document.createElement('div');
  wrapper.style.padding = '0.25rem 0.75rem';

  const input = document.createElement('input');
  input.type = 'file';
  input.multiple = true;
  input.accept = '.pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip';
  input.style.display = 'none';

  const btn = document.createElement('button');
  btn.className = 'upload-btn';
  btn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="12" height="12">
      <line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line>
    </svg>
    Anexar arquivo
  `;
  btn.addEventListener('click', () => input.click());

  input.addEventListener('change', async () => {
    if (!input.files.length) return;
    const files = Array.from(input.files);
    input.value = '';
    btn.disabled = true;
    btn.textContent = 'Enviando...';
    try {
      await uploadPendingFiles(files, entidadeTipo, entidadeId);
      showToast(`${files.length} arquivo(s) enviado(s) com sucesso!`, 'success');
      if (contratoAtualId) await carregarArvore(contratoAtualId);
    } catch (e) {
      showToast('Erro ao enviar: ' + e.message, 'error');
      btn.disabled = false;
      btn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="12" height="12">
          <line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Anexar arquivo
      `;
    }
  });

  wrapper.appendChild(input);
  wrapper.appendChild(btn);
  return wrapper;
}

// ── Ações globais ─────────────────────────────────────────────────────────
async function downloadArquivo(id, nome) {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`/api/arquivos/${id}/download`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error(`Erro ${response.status}`);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nome;
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    showToast('Erro ao baixar arquivo: ' + e.message, 'error');
  }
}

async function confirmarDeleteArquivo(id) {
  if (!confirm('Tem certeza que deseja excluir este arquivo? Esta ação não pode ser desfeita.')) return;
  try {
    await deleteArquivo(id);
    showToast('Arquivo excluído.', 'success');
    if (contratoAtualId) await carregarArvore(contratoAtualId);
  } catch (e) {
    showToast('Erro ao excluir: ' + e.message, 'error');
  }
}

// ── Exportadas (usadas por outros módulos via inicializarUploadArea) ───────
export async function uploadPendingFiles(files, entidadeTipo, entidadeId) {
  for (const file of files) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('entidade_tipo', entidadeTipo);
    formData.append('entidade_id', String(entidadeId));
    await uploadArquivo(formData);
  }
}

export function inicializarUploadArea(inputId, listId) {
  const input = document.getElementById(inputId);
  const listEl = document.getElementById(listId);
  if (!input || !listEl) return;

  let pendingFiles = [];

  const renderList = () => {
    listEl.innerHTML = '';
    pendingFiles.forEach((f, idx) => {
      const item = document.createElement('div');
      item.style.cssText = 'display:flex;align-items:center;gap:0.5rem;padding:0.25rem 0;font-size:0.875rem;';
      item.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14" style="color:var(--text-muted);flex-shrink:0">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
        <span style="flex:1">${escapeHtml(f.name)} <span style="color:var(--text-muted)">(${formatarTamanho(f.size)})</span></span>
        <button style="border:none;background:none;cursor:pointer;color:var(--danger);padding:0 0.25rem;font-size:1rem;" data-remove-idx="${idx}">✕</button>
      `;
      item.querySelector('[data-remove-idx]').addEventListener('click', () => {
        pendingFiles.splice(idx, 1);
        renderList();
      });
      listEl.appendChild(item);
    });
  };

  input.addEventListener('change', () => {
    pendingFiles = pendingFiles.concat(Array.from(input.files));
    input.value = '';
    renderList();
  });

  input._getPendingFiles = () => pendingFiles;
  input._clearPendingFiles = () => { pendingFiles = []; renderList(); };
}

// ── Utilitários ───────────────────────────────────────────────────────────
function formatarTamanho(bytes) {
  if (!bytes) return '';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatarMoeda(valor) {
  if (!valor) return 'R$ 0,00';
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
}

function formatarDataCurta(dateStr) {
  if (!dateStr) return '';
  const part = dateStr.split('T')[0];
  const [y, m, d] = part.split('-');
  return `${d}/${m}/${y}`;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) { console.log(msg); return; }
  const colors = { success: '#10b981', error: '#ef4444', info: '#3b82f6', warning: '#f59e0b' };
  const toast = document.createElement('div');
  toast.style.cssText = `background:${colors[type]||colors.info};color:#fff;padding:0.75rem 1rem;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);font-size:0.875rem;max-width:320px;`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}
