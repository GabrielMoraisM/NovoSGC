// api.js
const API_BASE_URL = 'http://localhost:8000';

// ---------- Função interna para fetch com autenticação ----------
async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  // Para status 204 (sem conteúdo), retorna response vazia
  if (response.status === 204) return response;

  // Se a resposta não for OK, captura o erro e lança
  if (!response.ok) {
    let errorData = {};
    try {
      errorData = await response.json();
    } catch (e) {
      // Se não conseguir parsear, usa texto
      const text = await response.text();
      throw new Error(`Erro ${response.status}: ${text || response.statusText}`);
    }

    console.error('❌ URL:', `${API_BASE_URL}${endpoint}`);
    console.error('❌ Payload enviado:', options.body);
    console.error('❌ Resposta de erro completa:', errorData);

    let message = `Erro ${response.status}: ${response.statusText}`;
    if (errorData.detail) {
      if (Array.isArray(errorData.detail)) {
        message = errorData.detail.map(e => e.msg).join('; ');
      } else if (typeof errorData.detail === 'string') {
        message = errorData.detail;
      } else {
        message = JSON.stringify(errorData.detail);
      }
    }
    throw new Error(message);
  }

  return response;
}

// ---------- Função para requisições que já retornam JSON (usada pelas funções específicas) ----------
async function apiRequest(endpoint, options = {}) {
  const response = await apiFetch(endpoint, options);
  // Se for 204, retorna null
  if (response.status === 204) return null;
  // Caso contrário, retorna o JSON
  return await response.json();
}

// ==================== OBJETO GLOBAL API (para uso em scripts não-module) ====================
window.api = {
  get: (endpoint) => apiFetch(endpoint, { method: 'GET' }),
  post: (endpoint, data) => apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  put: (endpoint, data) => apiFetch(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  delete: (endpoint) => apiFetch(endpoint, { method: 'DELETE' })
};

// ==================== AUTENTICAÇÃO ====================
export async function login(email, password) {
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
    console.error('Erro no login:', data);
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

export async function updateSeguro(seguroId, seguroData) {
  return apiRequest(`/seguros/${seguroId}`, {
    method: 'PUT',
    body: JSON.stringify(seguroData)
  });
}

export async function deleteSeguro(seguroId) {
  return apiRequest(`/seguros/${seguroId}`, {
    method: 'DELETE'
  });
}

// ==================== ADITIVOS ====================
export async function getAditivos(contratoId) {
  return apiRequest(`/contratos/${contratoId}/aditivos`);
}

export async function createAditivo(contratoId, aditivoData) {
  return apiRequest(`/contratos/${contratoId}/aditivos`, {
    method: 'POST',
    body: JSON.stringify(aditivoData)
  });
}

export async function updateAditivo(aditivoId, aditivoData) {
  return apiRequest(`/aditivos/${aditivoId}`, {
    method: 'PUT',
    body: JSON.stringify(aditivoData)
  });
}

export async function deleteAditivo(aditivoId) {
  return apiRequest(`/aditivos/${aditivoId}`, {
    method: 'DELETE'
  });
}

// ==================== MEDIÇÕES (BOLETINS) ====================
export async function getBoletins(filtros = {}) {
  const params = new URLSearchParams(filtros).toString();
  const url = params ? `/boletins/?${params}` : '/boletins/';
  return apiRequest(url);
}

export async function createBoletim(contratoId, boletimData) {
  return apiRequest(`/contratos/${contratoId}/boletins`, {
    method: 'POST',
    body: JSON.stringify(boletimData)
  });
}

export async function updateBoletim(boletimId, boletimData) {
  return apiRequest(`/boletins/${boletimId}`, {
    method: 'PUT',
    body: JSON.stringify(boletimData)
  });
}

export async function deleteBoletim(boletimId) {
  return apiRequest(`/boletins/${boletimId}`, {
    method: 'DELETE'
  });
}

// ==================== FATURAMENTO ====================
export async function getFaturamentos(filtros = {}) {
  const params = new URLSearchParams(filtros).toString();
  const url = params ? `/faturamentos/?${params}` : '/faturamentos/';
  return apiRequest(url);
}

export async function createFaturamento(faturamentoData) {
  return apiRequest('/faturamentos/', {
    method: 'POST',
    body: JSON.stringify(faturamentoData)
  });
}

// ==================== PAGAMENTOS ====================
export async function getPagamentos(filtros = {}) {
  const params = new URLSearchParams(filtros).toString();
  const url = params ? `/pagamentos/?${params}` : '/pagamentos/';
  return apiRequest(url);
}

export async function createPagamento(pagamentoData) {
  return apiRequest('/pagamentos/', {
    method: 'POST',
    body: JSON.stringify(pagamentoData)
  });
}

// Em api.js
export async function getAlertas(contrato_id) {
  const url = contrato_id ? `/alertas?contrato_id=${contrato_id}` : '/alertas/';
  return apiRequest(url);
}

