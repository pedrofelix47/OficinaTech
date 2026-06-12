from django.contrib.auth.models import User, Group
from oficinatech01.models import Funcionario

username = 'admin@admin.com'
password = 'admin'
email = username

u = User.objects.filter(username=username).first()
if u is None:
    u = User.objects.create_user(username=username, email=email, password=password)
    print('Created user', username)
else:
    u.set_password(password)
    u.email = email
    u.save()
    print('Updated password for', username)

# create group
g, created = Group.objects.get_or_create(name='Administrador')
if created:
    print('Created group Administrador')

u.groups.add(g)
# ensure not superuser
u.is_superuser = False
u.is_staff = False
u.save()

# create or update funcionario
f = Funcionario.objects.filter(user=u).first()
if f is None:
    f = Funcionario.objects.create(user=u, nome_funcionario='Administrador Sistema', email_funcionario=email, cargo_funcionario='Administrador', ativo=True)
    print('Created Funcionario', f.id_funcionario)
else:
    f.nome_funcionario = 'Administrador Sistema'
    f.email_funcionario = email
    f.cargo_funcionario = 'Administrador'
    f.ativo = True
    f.save()
    print('Updated Funcionario', f.id_funcionario)

print('Done')
