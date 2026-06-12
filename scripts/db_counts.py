import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oficinatech.settings')
django.setup()
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group
from oficinatech01.models import Funcionario, Fornecedor, Peca, Venda, Entrada

print('User:', User.objects.count())
print('Funcionario:', Funcionario.objects.count())
print('Fornecedor:', Fornecedor.objects.count())
print('Peca:', Peca.objects.count())
print('Venda:', Venda.objects.count())
print('Entrada:', Entrada.objects.count())
print('Session:', Session.objects.count())
print('ContentType:', ContentType.objects.count())
print('Permission:', Permission.objects.count())
print('Group:', Group.objects.count())
from django.db import connection
with connection.cursor() as c:
    c.execute('SELECT COUNT(*) FROM django_migrations')
    row = c.fetchone()
    print('django_migrations:', row[0] if row else 0)
