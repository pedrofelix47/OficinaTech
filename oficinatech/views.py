from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F
from django.shortcuts import redirect, render
from django.urls import reverse

from oficinatech01.models import Entrada, Funcionario, Peca, Venda
from oficinatech01.models import Fornecedor
from oficinatech01.models import Peca as PecaModel
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, Permission
import json
from django.http import JsonResponse


def is_admin_user(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return user.groups.filter(name='Administrador').exists()


@user_passes_test(is_admin_user)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_fornecedores = Fornecedor.objects.count()
    total_pecas = Peca.objects.count()
    return render(request, 'admin/dashboard.html', {'total_users': total_users, 'total_fornecedores': total_fornecedores, 'total_pecas': total_pecas})


@user_passes_test(is_admin_user)
def admin_users(request):
    users = User.objects.order_by('id')
    create_form = UserCreationForm()
    # load all permissions and groups for suggestion lists
    all_permissions = list(Permission.objects.order_by('content_type__app_label', 'codename').values('id', 'name'))
    all_groups = list(Group.objects.order_by('name').values('id', 'name'))
    return render(request, 'admin/users.html', {
        'users': users,
        'create_form': create_form,
        'all_permissions_json': json.dumps(all_permissions),
        'all_groups_json': json.dumps(all_groups),
    })


@user_passes_test(is_admin_user)
def admin_user_create(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # optional: save first name
            first_name = request.POST.get('first_name')
            if first_name:
                user.first_name = first_name
                user.save()
            # optional: add groups
            group_ids = request.POST.getlist('groups')
            if group_ids:
                user.groups.set(Group.objects.filter(pk__in=group_ids))
            # optional: add user permissions
            perm_ids = request.POST.getlist('user_permissions')
            if perm_ids:
                user.user_permissions.set(Permission.objects.filter(pk__in=perm_ids))
            # optional: create Funcionario record when requested
            create_func = request.POST.get('create_funcionario')
            if create_func in ['on', 'true', '1', 'True']:
                try:
                    if not hasattr(user, 'funcionario') and not Funcionario.objects.filter(user=user).exists():
                        Funcionario.objects.create(
                            user=user,
                            nome_funcionario=first_name or user.username,
                            email_funcionario=user.email,
                            cargo_funcionario=request.POST.get('cargo') or 'Mecânico',
                            ativo=True
                        )
                        # if a 'Funcionario' group exists, add user to it
                        func_group = Group.objects.filter(name='Funcionario').first()
                        if func_group:
                            user.groups.add(func_group)
                except Exception:
                    # non-fatal: creation failure should not block user creation
                    pass
            messages.success(request, 'Usuário criado com sucesso.')
            return redirect('admin_users')
    else:
        # when GET, redirect to users list and open modal
        return redirect(reverse('admin_users') + '?create=1')


@user_passes_test(is_admin_user)
def admin_user_edit(request, user_id):
    user_obj = User.objects.filter(pk=user_id).first()
    if not user_obj:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('admin_users')
    if request.method == 'POST':
        # Update fields manually from modal
        user_obj.username = request.POST.get('username') or user_obj.username
        user_obj.first_name = request.POST.get('first_name') or ''
        user_obj.last_name = request.POST.get('last_name') or ''
        user_obj.email = request.POST.get('email') or ''
        user_obj.is_staff = True if request.POST.get('is_staff') == 'on' or request.POST.get('is_staff') == 'true' else False
        user_obj.is_active = True if request.POST.get('is_active') == 'on' or request.POST.get('is_active') == 'true' else False
        user_obj.is_superuser = True if request.POST.get('is_superuser') == 'on' or request.POST.get('is_superuser') == 'true' else False
        user_obj.save()
        # update groups
        group_ids = request.POST.getlist('groups')
        if group_ids:
            user_obj.groups.set(Group.objects.filter(pk__in=group_ids))
        else:
            user_obj.groups.clear()
        # update permissions
        perm_ids = request.POST.getlist('user_permissions')
        if perm_ids:
            user_obj.user_permissions.set(Permission.objects.filter(pk__in=perm_ids))
        else:
            user_obj.user_permissions.clear()
        # create or update associated Funcionario when requested or if already present
        create_func = request.POST.get('create_funcionario')
        cargo = request.POST.get('cargo')
        try:
            if hasattr(user_obj, 'funcionario') and user_obj.funcionario is not None:
                func = user_obj.funcionario
                func.nome_funcionario = user_obj.first_name or func.nome_funcionario
                func.email_funcionario = user_obj.email or func.email_funcionario
                if cargo:
                    func.cargo_funcionario = cargo
                func.save()
            elif create_func in ['on', 'true', '1', 'True']:
                Funcionario.objects.create(
                    user=user_obj,
                    nome_funcionario=user_obj.first_name or user_obj.username,
                    email_funcionario=user_obj.email,
                    cargo_funcionario=cargo or 'Mecânico',
                    ativo=True
                )
                func_group = Group.objects.filter(name='Funcionario').first()
                if func_group:
                    user_obj.groups.add(func_group)
        except Exception:
            pass
        messages.success(request, 'Usuário atualizado.')
        return redirect('admin_users')
    else:
        # redirect to list and open the edit modal for this user
        return redirect(reverse('admin_users') + f'?edit={user_id}')


@user_passes_test(is_admin_user)
def admin_user_delete(request, user_id):
    user_obj = User.objects.filter(pk=user_id).first()
    if user_obj:
        user_obj.delete()
        messages.success(request, 'Usuário excluído.')
    return redirect('admin_users')


@user_passes_test(is_admin_user)
def admin_fornecedores(request):
    fornecedores = Fornecedor.objects.order_by('nome_fornecedor')
    return render(request, 'admin/fornecedores.html', {'fornecedores': fornecedores})


@user_passes_test(is_admin_user)
def admin_pecas(request):
    pecas = Peca.objects.prefetch_related('fornecedores').order_by('nome_peca')
    fornecedores = Fornecedor.objects.filter(ativo=True).order_by('nome_fornecedor')
    return render(request, 'admin/pecas.html', {'pecas': pecas, 'fornecedores': fornecedores})


@user_passes_test(is_admin_user)
def admin_peca_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome_peca')
        descricao = request.POST.get('descricao_peca')
        custo = request.POST.get('custo_peca')
        quantidade = request.POST.get('quant_peca')
        alerta = request.POST.get('alerta_quant')
        fornecedor_ids = request.POST.getlist('fornecedores')

        if not nome:
            messages.error(request, 'Nome da peça é obrigatório.')
            return redirect('admin_pecas')

        try:
            custo_val = float(custo) if custo else 0.0
            quant_val = int(quantidade) if quantidade else 0
            alerta_val = int(alerta) if alerta else 5
            p = Peca.objects.create(
                nome_peca=nome,
                descricao_peca=descricao or None,
                custo_peca=custo_val,
                quant_peca=quant_val,
                alerta_quant=alerta_val,
                ativo=True
            )
            if fornecedor_ids:
                p.fornecedores.set(fornecedor_ids)

            # If AJAX request, return JSON with the created peça
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                fornecs = [{'id': f.pk, 'nome': f.nome_fornecedor} for f in p.fornecedores.all()]
                return JsonResponse({'success': True, 'peca': {
                    'id': p.pk,
                    'nome_peca': p.nome_peca,
                    'descricao_peca': p.descricao_peca,
                    'custo_peca': str(p.custo_peca),
                    'quant_peca': p.quant_peca,
                    'alerta_quant': p.alerta_quant,
                    'fornecedores': fornecs,
                }}, status=201)

            messages.success(request, 'Peça criada com sucesso.')
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
            messages.error(request, f'Erro ao criar peça: {e}')

    return redirect('admin_pecas')


@user_passes_test(is_admin_user)
def admin_peca_edit(request, pk):
    p = Peca.objects.filter(pk=pk).first()
    if not p:
        messages.error(request, 'Peça não encontrada.')
        return redirect('admin_pecas')
    if request.method == 'POST':
        p.nome_peca = request.POST.get('nome_peca') or p.nome_peca
        p.descricao_peca = request.POST.get('descricao_peca')
        custo = request.POST.get('custo_peca')
        quantidade = request.POST.get('quant_peca')
        alerta = request.POST.get('alerta_quant')
        fornecedor_ids = request.POST.getlist('fornecedores')
        try:
            if custo:
                p.custo_peca = float(custo)
            if quantidade:
                p.quant_peca = int(quantidade)
            if alerta:
                p.alerta_quant = int(alerta)
            p.save()
            if fornecedor_ids:
                p.fornecedores.set(fornecedor_ids)
            else:
                p.fornecedores.clear()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                fornecs = [{'id': f.pk, 'nome': f.nome_fornecedor} for f in p.fornecedores.all()]
                return JsonResponse({'success': True, 'peca': {
                    'id': p.pk,
                    'nome_peca': p.nome_peca,
                    'descricao_peca': p.descricao_peca,
                    'custo_peca': str(p.custo_peca),
                    'quant_peca': p.quant_peca,
                    'alerta_quant': p.alerta_quant,
                    'fornecedores': fornecs,
                }})

            messages.success(request, 'Peça atualizada.')
            return redirect('admin_pecas')
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
            messages.error(request, f'Erro ao atualizar peça: {e}')
            return redirect('admin_pecas')

    return render(request, 'admin/peca_form.html', {'peca': p, 'fornecedores': Fornecedor.objects.filter(ativo=True)})


@user_passes_test(is_admin_user)
def admin_peca_delete(request, pk):
    p = Peca.objects.filter(pk=pk).first()
    if p:
        p.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, 'Peça excluída.')
    return redirect('admin_pecas')


@user_passes_test(is_admin_user)
def admin_fornecedor_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome_fornecedor')
        email = request.POST.get('email_fornecedor')
        telefone = request.POST.get('telefone_fornecedor')
        cnpj = request.POST.get('cnpj_fornecedor')
        if not nome:
            messages.error(request, 'Nome é obrigatório.')
            return redirect('admin_fornecedores')
        Fornecedor.objects.create(nome_fornecedor=nome, email_fornecedor=email, telefone_fornecedor=telefone, cnpj_fornecedor=cnpj)
        messages.success(request, 'Fornecedor criado.')
    return redirect('admin_fornecedores')


@user_passes_test(is_admin_user)
def admin_fornecedor_edit(request, pk):
    f = Fornecedor.objects.filter(pk=pk).first()
    if not f:
        messages.error(request, 'Fornecedor não encontrado.')
        return redirect('admin_fornecedores')
    if request.method == 'POST':
        f.nome_fornecedor = request.POST.get('nome_fornecedor') or f.nome_fornecedor
        f.email_fornecedor = request.POST.get('email_fornecedor')
        f.telefone_fornecedor = request.POST.get('telefone_fornecedor')
        f.cnpj_fornecedor = request.POST.get('cnpj_fornecedor')
        f.save()
        messages.success(request, 'Fornecedor atualizado.')
        return redirect('admin_fornecedores')
    return render(request, 'admin/fornecedor_form.html', {'fornecedor': f})


@user_passes_test(is_admin_user)
def admin_fornecedor_delete(request, pk):
    f = Fornecedor.objects.filter(pk=pk).first()
    if f:
        f.delete()
        messages.success(request, 'Fornecedor excluído.')
    return redirect('admin_fornecedores')

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
            # salvar o nome no próprio User (first_name)
            if nome:
                user.first_name = nome
                user.save()
            
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

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email_digitado = (request.POST.get('email') or '').strip().lower()
        senha_digitada = request.POST.get('password') or ''

        if not email_digitado or not senha_digitada:
            messages.error(request, 'Informe e-mail e senha para entrar.')
            return render(request, 'index.html')

        try:
            user_obj = User.objects.get(email=email_digitado)
            username = user_obj.username
        except User.DoesNotExist:
            username = None

        user = authenticate(request, username=username, password=senha_digitada)

        if user is not None:
            if hasattr(user, 'funcionario') and not user.funcionario.ativo:
                messages.error(request, 'Este funcionário está inativo no sistema.')
                return render(request, 'index.html')

            login(request, user)
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)

        messages.error(request, 'E-mail ou senha incorretos. Verifique os dados e tente novamente.')

    return render(request, 'index.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sessão.')
    return redirect('login')


@login_required
def dashboard(request):
    hoje = date.today()
    total_pecas = Peca.objects.filter(ativo=True).count()
    vendas_mes = Venda.objects.filter(data_venda__month=hoje.month, data_venda__year=hoje.year).count()
    alertas = Peca.objects.filter(ativo=True, quant_peca__lt=F('alerta_quant')).order_by('quant_peca')[:5]

    return render(request, 'dashboard.html', {
        'total_pecas': total_pecas,
        'vendas_mes': vendas_mes,
        'alertas': alertas,
        'alertas_qtd': alertas.count(),
        'is_admin': is_admin_user(request.user),
    })


@login_required
def estoque(request):
    from django.http import JsonResponse
    from oficinatech01.models import Fornecedor
    
    # Cadastro de peça via AJAX
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tipo = request.POST.get('tipo_requisicao')
        if tipo == 'cadastro_peca':
            nome = request.POST.get('nome_peca')
            descricao = request.POST.get('descricao_peca')
            custo = request.POST.get('custo_peca')
            quantidade = request.POST.get('quant_peca')
            alerta = request.POST.get('alerta_quant')
            fornecedor_ids = request.POST.getlist('fornecedores')

            if not nome or not custo or not quantidade:
                return JsonResponse({'success': False, 'message': 'Informe nome, custo e quantidade.'})

            try:
                peca = Peca.objects.create(
                    nome_peca=nome,
                    descricao_peca=descricao or None,
                    custo_peca=float(custo),
                    quant_peca=int(quantidade),
                    alerta_quant=int(alerta) if alerta else 5,
                    ativo=True
                )
                if fornecedor_ids:
                    peca.fornecedores.set(fornecedor_ids)
                return JsonResponse({'success': True, 'message': f'Peça "{nome}" cadastrada com sucesso!'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Erro ao cadastrar: {str(e)}'})
    
    pecas = Peca.objects.filter(ativo=True).prefetch_related('fornecedores').order_by('nome_peca')
    fornecedores = Fornecedor.objects.filter(ativo=True)
    return render(request, 'estoque.html', {'pecas': pecas, 'fornecedores': fornecedores})


@login_required
def saidas(request):
    pecas = Peca.objects.filter(ativo=True).order_by('nome_peca')
    vendas_recentes = Venda.objects.select_related('id_peca', 'id_funcionario').order_by('-id_venda')[:8]

    if request.method == 'POST':
        peca_id = request.POST.get('peca')
        quantidade_raw = request.POST.get('quantidade', '')
        try:
            quantidade = int(float(quantidade_raw))
        except Exception:
            quantidade = 0

        if not peca_id or quantidade <= 0:
            messages.error(request, 'Selecione uma peça e informe uma quantidade válida.')
            return redirect('saidas')

        if not hasattr(request.user, 'funcionario') or request.user.funcionario is None:
            messages.error(request, 'Não foi possível registrar a saída porque o usuário não está vinculado a um funcionário.')
            return redirect('saidas')

        peca = Peca.objects.filter(pk=peca_id, ativo=True).first()
        if not peca:
            messages.error(request, 'Peça não encontrada.')
            return redirect('saidas')

        if peca.quant_peca < quantidade:
            messages.error(request, 'Quantidade insuficiente em estoque para registrar esta saída.')
            return redirect('saidas')

        # decrement stock and ensure it doesn't go negative
        new_q = peca.quant_peca - quantidade
        if new_q < 0:
            messages.error(request, 'Quantidade insuficiente em estoque para registrar esta saída.')
            return redirect('saidas')
        peca.quant_peca = new_q
        peca.save(update_fields=['quant_peca'])

        Venda.objects.create(
            quant_venda=quantidade,
            id_funcionario=request.user.funcionario,
            id_peca=peca,
        )

        messages.success(request, f'Saída registrada com sucesso: {quantidade} unidade(s) de {peca.nome_peca}.')
        return redirect('saidas')

    return render(request, 'saidas.html', {
        'pecas': pecas,
        'vendas_recentes': vendas_recentes,
    })