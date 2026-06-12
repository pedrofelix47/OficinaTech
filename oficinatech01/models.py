from django.db import models
from django.contrib.auth.models import User  # <- Importar o utilizador padrão do Django

class Funcionario(models.Model):
    id_funcionario = models.AutoField(primary_key=True)
    # Vincula o Funcionário a um Utilizador do Django (permite fazer login)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    nome_funcionario = models.CharField(max_length=255)
    email_funcionario = models.EmailField(blank=True, null=True)
    cargo_funcionario = models.CharField(max_length=100, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_inativacao = models.DateField(blank=True, null=True)
    data_registo = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome_funcionario


class Fornecedor(models.Model):
    id_fornecedor = models.AutoField(primary_key=True)
    nome_fornecedor = models.CharField(max_length=255)
    cnpj_fornecedor = models.CharField(max_length=20, blank=True, null=True)
    email_fornecedor = models.EmailField(blank=True, null=True)
    telefone_fornecedor = models.CharField(max_length=20, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_inativacao = models.DateField(blank=True, null=True)
    data_registo = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome_fornecedor


class Peca(models.Model):
    id_peca = models.AutoField(primary_key=True)
    nome_peca = models.CharField(max_length=255)
    descricao_peca = models.TextField(blank=True, null=True)
    custo_peca = models.DecimalField(max_digits=10, decimal_places=2)  # Melhor que Float para dinheiro
    quant_peca = models.IntegerField(default=0)
    alerta_quant = models.IntegerField(default=5)
    ativo = models.BooleanField(default=True)
    data_inativacao = models.DateField(blank=True, null=True)
    data_registo = models.DateField(auto_now_add=True)
    
    # Relação Muitos-para-Muitos (Cria a tabela intermédia automaticamente)
    fornecedores = models.ManyToManyField(Fornecedor, related_name='pecas', blank=True)

    def __str__(self):
        return self.nome_peca


class Venda(models.Model):
    id_venda = models.AutoField(primary_key=True)
    data_venda = models.DateField(auto_now_add=True)
    quant_venda = models.IntegerField()
    # Quem vendeu (FK para Funcionario)
    id_funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='vendas')
    id_peca = models.ForeignKey(Peca, on_delete=models.PROTECT, related_name='vendas')

    def __str__(self):
        return f"Venda {self.id_venda} - {self.data_venda}"


class Entrada(models.Model):
    id_entrada = models.AutoField(primary_key=True)
    data_entrada = models.DateField(auto_now_add=True)
    quant_entrada = models.IntegerField()
    id_fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='entradas')
    id_peca = models.ForeignKey(Peca, on_delete=models.PROTECT, related_name='entradas')

    def __str__(self):
        return f"Entrada {self.id_entrada} - {self.data_entrada}"