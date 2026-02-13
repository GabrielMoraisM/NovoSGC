// js/empresas.js

// Dados mockados de empresas
let empresasMock = [
  { id: 1, razao_social: "Heca Engenharia", cnpj: "00.000.000/0001-91", tipo: "MATRIZ" },
  { id: 2, razao_social: "Petrobras", cnpj: "11.111.111/0001-11", tipo: "CLIENTE" },
  { id: 3, razao_social: "Vale S.A.", cnpj: "22.222.222/0001-22", tipo: "CLIENTE" },
  { id: 4, razao_social: "Eletrobras", cnpj: "33.333.333/0001-33", tipo: "CLIENTE" },
  { id: 5, razao_social: "CDHU", cnpj: "44.444.444/0001-44", tipo: "CLIENTE" },
  { id: 6, razao_social: "Construtora Beta", cnpj: "55.555.555/0001-55", tipo: "PARCEIRO_CONSORCIO" },
  { id: 7, razao_social: "Construtora Gamma", cnpj: "66.666.666/0001-66", tipo: "SCP" },
  { id: 8, razao_social: "Porto Seguro", cnpj: "77.777.777/0001-77", tipo: "SEGURADORA" }
];

// Função para formatar CNPJ (máscara simples)
function formatarCNPJ(cnpj) {
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5");
}

// Renderizar tabela de empresas
function renderizarEmpresas(empresas) {
  const tbody = document.getElementById('empresas-list');
  if (!tbody) return;
  
  tbody.innerHTML = '';
  empresas.forEach(emp => {
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
  document.getElementById('empresas-count').textContent = `Mostrando ${empresas.length} de ${empresas.length} empresas`;
}

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

// Filtrar empresas por busca
function buscarEmpresas() {
  const termo = document.getElementById('search-empresas').value.toLowerCase();
  const filtradas = empresasMock.filter(emp => 
    emp.razao_social.toLowerCase().includes(termo) || 
    emp.cnpj.includes(termo)
  );
  renderizarEmpresas(filtradas);
}

// Salvar nova empresa (mock)
function salvarNovaEmpresa(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  
  // Validar CNPJ (apenas simulação)
  const cnpj = formData.get('cnpj');
  if (!cnpj || cnpj.length < 14) {
    alert('CNPJ inválido');
    return;
  }

  const novaEmpresa = {
    id: empresasMock.length + 1,
    razao_social: formData.get('razao_social'),
    cnpj: cnpj,
    tipo: formData.get('tipo')
  };

  empresasMock.push(novaEmpresa);
  renderizarEmpresas(empresasMock);
  form.reset();
  document.getElementById('new-empresa-modal').classList.remove('active');
  alert('Empresa cadastrada com sucesso!');
}

// Editar empresa (mock)
window.editarEmpresa = function(id) {
  const empresa = empresasMock.find(e => e.id === id);
  if (!empresa) return;
  // Simples: abre um prompt para editar (poderia ser um modal de edição)
  const novaRazao = prompt('Nova razão social:', empresa.razao_social);
  if (novaRazao) {
    empresa.razao_social = novaRazao;
    renderizarEmpresas(empresasMock);
  }
};

// Excluir empresa (mock)
window.excluirEmpresa = function(id) {
  if (confirm('Deseja realmente excluir esta empresa?')) {
    empresasMock = empresasMock.filter(e => e.id !== id);
    renderizarEmpresas(empresasMock);
  }
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  renderizarEmpresas(empresasMock);
  document.getElementById('search-empresas')?.addEventListener('input', buscarEmpresas);
  document.getElementById('new-empresa-form')?.addEventListener('submit', salvarNovaEmpresa);
});