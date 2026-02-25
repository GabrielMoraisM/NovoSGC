// alertas.js
console.log('alertas.js carregado');

async function carregarAlertas() {
  try {
    const response = await api.get('/alertas/');
    if (!response.ok) throw new Error('Erro ao carregar alertas');
    const alertas = await response.json();
    console.log('Alertas recebidos:', alertas);
    // Aqui você pode chamar uma função para renderizar os alertas na tela
    renderizarAlertas(alertas);
  } catch (error) {
    console.error('Erro ao carregar alertas:', error);
    mostrarMensagemVazia();
  }
}

function renderizarAlertas(alertas) {
  const container = document.getElementById('alerts-list');
  const spinner = document.getElementById('loading-spinner');
  const empty = document.getElementById('alerts-empty');
  
  if (spinner) spinner.style.display = 'none';
  
  if (!alertas || alertas.length === 0) {
    if (empty) empty.style.display = 'block';
    return;
  }
  
  if (empty) empty.style.display = 'none';
  
  container.innerHTML = ''; // remove o spinner e outros
  alertas.forEach(alerta => {
    const card = document.createElement('div');
    card.className = `alert-card ${alerta.lido ? '' : 'unread'}`;
    card.innerHTML = `
      <div class="alert-icon ${alerta.tipo}">${getIconeAlerta(alerta.tipo)}</div>
      <div class="alert-content">
        <div class="alert-title">
          ${alerta.titulo}
          ${alerta.contrato_nome ? `<span class="badge">${alerta.contrato_nome}</span>` : ''}
        </div>
        <div class="alert-message">${alerta.mensagem}</div>
        <div class="alert-meta">
          <span>${alerta.data}</span>
        </div>
      </div>
      <div class="alert-actions">
        <button class="btn btn-secondary btn-sm" onclick="marcarLido(${alerta.id})">Marcar lido</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function getIconeAlerta(tipo) {
  // retorna SVG correspondente (igual ao do dashboard)
  if (tipo === 'danger') return `<svg ...>...</svg>`;
  if (tipo === 'warning') return `<svg ...>...</svg>`;
  return `<svg ...>...</svg>`;
}

function mostrarMensagemVazia() {
  const spinner = document.getElementById('loading-spinner');
  const empty = document.getElementById('alerts-empty');
  if (spinner) spinner.style.display = 'none';
  if (empty) empty.style.display = 'block';
}

// Funções globais para os botões
window.marcarLido = async function(id) {
  // implementar chamada para marcar como lido se existir endpoint
  console.log('Marcar lido:', id);
};

window.marcarTodosLidos = async function() {
  // implementar
  console.log('Marcar todos lidos');
};

window.recarregarAlertas = function() {
  carregarAlertas();
};

document.addEventListener('DOMContentLoaded', carregarAlertas);