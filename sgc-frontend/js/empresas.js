import { getEmpresas, createEmpresa, updateEmpresa, deleteEmpresa } from './api.js';

let empresas = []; // armazena os dados reais carregados da API

// Função para obter a classe do badge conforme o tipo
function getBadgeClass(tipo) {
  const classes = {
    'MATRIZ': 'badge-primary',
    'FILIAL': 'badge-secondary',
    'PARCEIRO_CONSORCIO': 'badge-warning',
    'SCP': 'badge-info',
    'CLIENTE': 'badge-success',
    'SEGURADORA': 'badge-danger'
  };
  return classes[tipo] || 'badge-secondary';
}

// Renderizar tabela com as empresas fornecidas
function renderizarEmpresas(empresasParaMostrar) {
  const tbody = document.getElementById('empresas-list');
  if (!tbody) return;
  
  tbody.innerHTML = '';
  empresasParaMostrar.forEach(emp => {
    const row = document.createElement('tr');
    row.setAttribute('data-id', emp.id);
    row.innerHTML = `
      <td class="font-semibold">${emp.razao_social}</td>
      <td>${emp.cnpj}</td>
      <td><span class="badge ${getBadgeClass(emp.tipo)}">${emp.tipo}</span></td>
      <td style="text-align: right;">
        <button class="btn-view-more" onclick="editarEmpresa(${emp.id})">
          <span>Editar</span>
        </button>
        <button class="btn-view-more" onclick="excluirEmpresa(${emp.id})">
          <span>Excluir</span>
        </button>
      </td>
    `;
    tbody.appendChild(row);
  });
  document.getElementById('empresas-count').textContent = `Mostrando ${empresasParaMostrar.length} de ${empresas.length} empresas`;
}

// Carregar empresas da API
async function carregarEmpresas() {
  try {
    empresas = await getEmpresas();
    renderizarEmpresas(empresas);
  } catch (error) {
    console.error('Erro ao carregar empresas:', error);
    alert('Não foi possível carregar as empresas. Verifique sua conexão.');
  }
}

// Filtrar empresas conforme o termo de busca
function buscarEmpresas() {
  const termo = document.getElementById('search-empresas').value.toLowerCase();
  const filtradas = empresas.filter(emp => 
    emp.razao_social.toLowerCase().includes(termo) || 
    emp.cnpj.includes(termo)
  );
  renderizarEmpresas(filtradas);
}

// Salvar nova empresa (chama a API)
async function salvarNovaEmpresa(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  
  const novaEmpresa = {
    razao_social: formData.get('razao_social'),
    cnpj: formData.get('cnpj'),
    tipo: formData.get('tipo')
  };

  try {
    await createEmpresa(novaEmpresa);
    await carregarEmpresas(); // recarrega a lista para incluir a nova
    form.reset();
    document.getElementById('new-empresa-modal').classList.remove('active');
    alert('Empresa cadastrada com sucesso!');
  } catch (error) {
    alert('Erro ao cadastrar empresa: ' + error.message);
  }
}

// Editar empresa (abre prompt – pode ser melhorado com modal de edição)
window.editarEmpresa = async function(id) {
  const empresa = empresas.find(e => e.id === id);
  if (!empresa) return;
  const novaRazao = prompt('Nova razão social:', empresa.razao_social);
  if (!novaRazao) return;
  try {
    await updateEmpresa(id, { razao_social: novaRazao });
    await carregarEmpresas();
  } catch (error) {
    alert('Erro ao editar empresa: ' + error.message);
  }
};

// Excluir empresa (com confirmação)
window.excluirEmpresa = async function(id) {
  if (confirm('Deseja realmente excluir esta empresa?')) {
    try {
      await deleteEmpresa(id);
      await carregarEmpresas();
    } catch (error) {
      alert('Erro ao excluir empresa: ' + error.message);
    }
  }
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  carregarEmpresas();
  document.getElementById('search-empresas')?.addEventListener('input', buscarEmpresas);
  document.getElementById('new-empresa-form')?.addEventListener('submit', salvarNovaEmpresa);
});