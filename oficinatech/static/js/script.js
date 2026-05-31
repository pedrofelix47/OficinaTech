document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault(); // Impede o envio do formulário e recarregamento da página

            const email = document.getElementById('emailInput').value;
            const password = document.getElementById('passwordInput').value;

            // Aqui adiciona a lógica para validar o login.
            console.log(`Tentativa de login com email: ${email}`);

            // Exemplo simples para feedback ao usuário (opcional, pode remover depois)
            // alert('Login submetido com sucesso! (Ação simulada)');
        });
    }
});