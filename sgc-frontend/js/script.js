// =================================================================
// ARQUIVO: js/script.js
// DESCRIÇÃO: Controla Login, Recuperação de Senha e Animações
// =================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ----------------------------------------------------------------
    // 1. LÓGICA DA TELA DE LOGIN (index.html)
    // ----------------------------------------------------------------
    const loginForm = document.getElementById('loginForm');
    
    // O "if" garante que este bloco só roda na tela de login
    if (loginForm) {
        const forgotPassword = document.getElementById('forgotPassword');
        const usernameInput = document.getElementById('username');
        const passwordInput = document.getElementById('password');

        // UX: Validação visual (Borda azul quando digita)
        [usernameInput, passwordInput].forEach(input => {
            if(input) {
                input.addEventListener('input', function() {
                    this.style.borderColor = this.value ? '#1d4ed8' : '#e2e8f0';
                });
            }
        });

    }

    // ----------------------------------------------------------------
    // 2. LÓGICA DA TELA DE REDEFINIR SENHA (redefinir.html)
    // ----------------------------------------------------------------
    const recoveryForm = document.getElementById('recoveryForm');

    // O "if" garante que este bloco só roda na tela de redefinir
    if (recoveryForm) {
        const emailInput = document.getElementById('email');
        const submitBtn = document.getElementById('submitBtn');
        const successMessage = document.getElementById('successMessage');
        const instructions = document.querySelector('.instruction-text');
        const backLink = document.querySelector('.forgot-password');

        // UX: Validação visual do email
        emailInput.addEventListener('input', function() {
            // Verifica se tem "@" e "." para pintar a borda
            const isValid = this.value.includes('@') && this.value.includes('.');
            this.style.borderColor = isValid ? '#1d4ed8' : '#e2e8f0';
        });

        // Evento de Enviar Link
        recoveryForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = emailInput.value;

            if (email) {
                // A. ESTADO DE CARREGAMENTO (LOADING)
                const textoOriginal = submitBtn.innerText;
                submitBtn.innerText = 'Enviando solicitação...';
                submitBtn.disabled = true;       // Impede clique duplo
                submitBtn.style.opacity = '0.7'; // Efeito visual desabilitado
                submitBtn.style.cursor = 'wait'; // Mouse de ampulheta
                emailInput.disabled = true;      // Trava o input

                try {
                    // B. CHAMADA DA API (Simulada)
                    // Aguarda a resposta da função lá embaixo
                    await simularEnvioAPI(email);

                    // C. SUCESSO
                    // 1. Esconde instruções e campos do formulário
                    if(instructions) instructions.style.display = 'none';
                    
                    // Esconde inputs e botão, mas mantém o link de voltar
                    Array.from(recoveryForm.children).forEach(child => {
                        if (!child.classList.contains('forgot-password')) {
                            child.style.display = 'none';
                        }
                    });

                    // 2. Mostra a mensagem verde
                    successMessage.style.display = 'block';
                    
                    // 3. Altera o link de "Voltar" para ficar mais evidente
                    if(backLink) {
                        backLink.innerHTML = 'Ir para a tela de Login';
                        backLink.style.marginTop = '20px';
                        backLink.style.display = 'block'; 
                        backLink.href = 'index.html';
                    }

                } catch (erro) {
                    // D. ERRO (Caso a API falhe)
                    console.error(erro);
                    alert('Erro de conexão. Tente novamente.');
                    
                    // Restaura os botões para tentar de novo
                    submitBtn.innerText = textoOriginal;
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                    submitBtn.style.cursor = 'pointer';
                    emailInput.disabled = false;
                }
            }
        });
    }

    // ----------------------------------------------------------------
    // 3. EFEITOS VISUAIS (Rodam em ambas as telas)
    // ----------------------------------------------------------------
    
    // Inicia animação das janelas
    createWindowsAnimation();

    // Inicia partículas flutuantes
    createParticleStyles();
    setInterval(createConstructionParticle, 800);
});


// =================================================================
// FUNÇÕES AUXILIARES E SIMULAÇÕES (Backend Mock)
// =================================================================

/**
 * Simula uma requisição ao servidor para enviar o email
 * Futuramente, substitua isso pelo fetch() real.
 */
function simularEnvioAPI(email) {
    return new Promise((resolve, reject) => {
        console.log(`[API] Processando envio para: ${email}...`);
        
        // Simula delay de rede de 2 segundos
        setTimeout(() => {
            // Aqui simulamos sucesso (resolve)
            console.log('[API] Sucesso: Email enviado.');
            resolve({ status: 200, message: 'Email enviado' });
            
            // Se quiser testar erro, descomente a linha abaixo:
            // reject('Erro 500: Servidor indisponível');
        }, 2000);
    });
}

// Cria as janelas do prédio dinamicamente
function createWindowsAnimation() {
    const windowsContainer = document.querySelector('.building-windows');
    if (!windowsContainer) return; // Evita erro se não houver o container
    
    windowsContainer.innerHTML = '';
    
    // Cria 32 janelas com delays aleatórios
    for (let i = 0; i < 32; i++) {
        const windowEl = document.createElement('div');
        windowEl.className = 'window';
        windowEl.style.animationDelay = `${(i * 0.1) + (Math.random() * 0.5)}s`;
        windowsContainer.appendChild(windowEl);
    }
}

// Injeta o CSS das partículas no head
function createParticleStyles() {
    if (!document.getElementById('particle-styles')) {
        const style = document.createElement('style');
        style.id = 'particle-styles';
        style.textContent = `
            @keyframes particle-float {
                0% { transform: translateY(0) rotate(0deg); opacity: 1; }
                100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

// Cria uma partícula azul flutuante
function createConstructionParticle() {
    const buildingSection = document.querySelector('.building-section');
    if (!buildingSection) return;

    const particle = document.createElement('div');
    particle.className = 'construction-particle';
    particle.style.cssText = `
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(59, 130, 246, 0.8);
        border-radius: 50%;
        pointer-events: none;
        animation: particle-float 3s linear infinite;
        left: ${Math.random() * 100}%;
        top: 100%;
        z-index: 10;
    `;
    
    buildingSection.appendChild(particle);

    // Remove a partícula do DOM após a animação para não pesar a memória
    setTimeout(() => {
        if (particle.parentNode) {
            particle.remove();
        }
    }, 3000);
}