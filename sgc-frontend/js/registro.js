import { apiFetch } from './api.js';

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const userData = {
        nome: formData.get('nome'),
        email: formData.get('email'),
        senha: formData.get('password'),
        perfil: formData.get('perfil')
    };

    try {
        const response = await apiFetch('/usuarios/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Erro ao criar usuário');
        alert('Usuário criado com sucesso! Faça login.');
        window.location.href = '/index.html';
    } catch (error) {
        alert('Erro: ' + error.message);
        console.error(error);
    }
});