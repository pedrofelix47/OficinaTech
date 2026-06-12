"""Add cnpj field to Fornecedor."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oficinatech01', '0002_funcionario_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='fornecedor',
            name='cnpj_fornecedor',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
