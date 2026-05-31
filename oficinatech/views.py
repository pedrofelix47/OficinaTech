from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

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