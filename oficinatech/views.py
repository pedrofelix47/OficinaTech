from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from oficinatech01.models import Funcionario

def cadastro_view(request):
    if request.method == 'POST':
        # 1. Capturar os dados do formulário HTML
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('password')
        confirmar_senha = request.POST.get('password_confirm')

        # 2. Validações básicas
        if senha != confirmar_senha:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'cadastro.html')

        # Verificar se o e-mail já está a ser utilizado
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está registado no sistema.")
            return render(request, 'cadastro.html')

        try:
            # 3. Criar o utilizador padrão do Django (usamos o email como username)
            user = User.objects.create_user(username=email, email=email, password=senha)
            
            # 4. Criar o Funcionário na sua tabela personalizada, vinculando ao utilizador acima
            Funcionario.objects.create(
                user=user,
                nome_funcionario=nome,
                email_funcionario=email,
                cargo_funcionario="Mecânico",  # Defina um cargo padrão ou remova se preferir
                ativo=True
            )

            # Envia uma mensagem de sucesso e manda o utilizador para a tela de login
            messages.success(request, "Conta criada com sucesso! Faça o seu login.")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Erro ao criar a conta: {str(e)}")
            
    return render(request, 'cadastro.html')

def login_view(request):
    if request.method == 'POST':
        # 1. Capturar os dados enviados pelo seu formulário HTML
        email_digitado = request.POST.get('email')
        senha_digitada = request.POST.get('password')

        # 2. Como o Django autentica por 'username', vamos procurar o username pelo email
        try:
            user_obj = User.objects.get(email=email_digitado)
            username = user_obj.username
        except User.DoesNotExist:
            username = None

        # 3. Autenticar o utilizador
        user = authenticate(request, username=username, password=senha_digitada)

        if user is not None:
            # 4. Verificar se o funcionário associado está ativo
            if hasattr(user, 'funcionario') and not user.funcionario.ativo:
                messages.error(request, "Este funcionário está inativo no sistema.")
                return render(request, 'login.html') # Altere para o nome do seu HTML
            
            # 5. Fazer o login (iniciar sessão)
            login(request, user)
            return redirect('dashboard')  # Altere para a página que deseja abrir após o login
        else:
            # Erro de credenciais
            messages.error(request, "E-mail ou palavra-passe incorretos.")
            
    return render(request, 'login.html') # Nome da sua página de login existente

def index(request):
    return render(request, 'index.html', {
    })

def saidas(request):
    return render(request, 'saidas.html', {
    })

def estoque(request):
    return render(request, 'estoque.html', {
    })

def dashboard(request):
    return render(request, 'dashboard.html', {
    })