const API_BASE_URL = 'http://localhost:8000';

// Função genérica para requisições autenticadas
async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('token'); // ou sessionStorage
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  // Se a resposta for 204 No Content, retorna null
  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    // Se o erro tiver detalhes, usa; senão, mensagem genérica
    const message = data.detail || `Erro ${response.status}: ${response.statusText}`;
    throw new Error(message);
  }

  return data;
}

// ==================== AUTENTICAÇÃO ====================
export async function login(email, password) {
  // O endpoint /auth/login espera application/x-www-form-urlencoded
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Erro no login');
  }

  localStorage.setItem('token', data.access_token);
  return data;
}

// ==================== EMPRESAS ====================
export async function getEmpresas() {
  return apiRequest('/empresas/');
}

export async function getEmpresa(id) {
  return apiRequest(`/empresas/${id}`);
}

export async function createEmpresa(empresaData) {
  return apiRequest('/empresas/', {
    method: 'POST',
    body: JSON.stringify(empresaData)
  });
}

export async function updateEmpresa(id, empresaData) {
  return apiRequest(`/empresas/${id}`, {
    method: 'PUT',
    body: JSON.stringify(empresaData)
  });
}

export async function deleteEmpresa(id) {
  return apiRequest(`/empresas/${id}`, {
    method: 'DELETE'
  });
}

// ==================== CONTRATOS ====================
export async function getContratos() {
  return apiRequest('/contratos/');
}

export async function getContrato(id) {
  return apiRequest(`/contratos/${id}`);
}

export async function createContrato(contratoData) {
  return apiRequest('/contratos/', {
    method: 'POST',
    body: JSON.stringify(contratoData)
  });
}

export async function updateContrato(id, contratoData) {
  return apiRequest(`/contratos/${id}`, {
    method: 'PUT',
    body: JSON.stringify(contratoData)
  });
}

export async function deleteContrato(id) {
  return apiRequest(`/contratos/${id}`, {
    method: 'DELETE'
  });
}

// ==================== PARTICIPANTES ====================
export async function getParticipantes(contratoId) {
  return apiRequest(`/contratos/${contratoId}/participantes`);
}

export async function updateParticipantes(contratoId, participantes) {
  return apiRequest(`/contratos/${contratoId}/participantes`, {
    method: 'PUT',
    body: JSON.stringify({ participantes })
  });
}

// ==================== MEDIÇÕES (BOLETINS) ====================
export async function getBoletins(contratoId) {
  return apiRequest(`/contratos/${contratoId}/boletins`);
}

export async function createBoletim(contratoId, boletimData) {
  return apiRequest(`/contratos/${contratoId}/boletins`, {
    method: 'POST',
    body: JSON.stringify(boletimData)
  });
}

// (outros métodos conforme necessidade)

// ==================== FATURAMENTO ====================
export async function getFaturamentos(filtros) {
  // Exemplo: /faturamentos/?skip=0&limit=100
  const params = new URLSearchParams(filtros).toString();
  return apiRequest(`/faturamentos/?${params}`);
}

export async function createFaturamento(faturamentoData) {
  return apiRequest('/faturamentos/', {
    method: 'POST',
    body: JSON.stringify(faturamentoData)
  });
}

// ==================== PAGAMENTOS ====================
export async function getPagamentos(faturamentoId) {
  return apiRequest(`/pagamentos/?faturamento_id=${faturamentoId}`);
}

export async function createPagamento(pagamentoData) {
  return apiRequest('/pagamentos/', {
    method: 'POST',
    body: JSON.stringify(pagamentoData)
  });
}

// ==================== ARTs ====================
export async function getArts(contratoId) {
  return apiRequest(`/contratos/${contratoId}/arts`);
}

export async function createArt(contratoId, artData) {
  return apiRequest(`/contratos/${contratoId}/arts`, {
    method: 'POST',
    body: JSON.stringify(artData)
  });
}

export async function updateArt(artId, artData) {
  return apiRequest(`/arts/${artId}`, {
    method: 'PUT',
    body: JSON.stringify(artData)
  });
}

export async function deleteArt(artId) {
  return apiRequest(`/arts/${artId}`, {
    method: 'DELETE'
  });
}

// ==================== SEGUROS ====================
export async function getSeguros(contratoId) {
  return apiRequest(`/contratos/${contratoId}/seguros`);
}

export async function createSeguro(contratoId, seguroData) {
  return apiRequest(`/contratos/${contratoId}/seguros`, {
    method: 'POST',
    body: JSON.stringify(seguroData)
  });
}
// etc.