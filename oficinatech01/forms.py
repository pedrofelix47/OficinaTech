from django import forms
from .models import Fornecedor

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        # Definimos os campos que vão aparecer na tela de cadastro/edição
        fields = ['nome_fornecedor', 'email_fornecedor', 'telefone_fornecedor', 'ativo']
        
        # Adicionando classes CSS (como o Bootstrap) para o formulário ficar bonito no HTML
        widgets = {
            'nome_fornecedor': forms.TextInput(attrs={'class': 'form-control'}),
            'email_fornecedor': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone_fornecedor': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
