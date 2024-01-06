from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=255, label='Email')
    password = forms.CharField(max_length=255, widget=forms.PasswordInput(), label='Password')

class TipoEquipamentoForm(forms.Form):
    tipo = forms.CharField(max_length=255)

class AtributosForm(forms.Form):
    Atributo = forms.CharField(max_length=255)
    Descricao = forms.CharField(max_length=255)

class ValoresAtributosForm(forms.Form):
    Valor = forms.CharField(max_length=255)

class UtilizadoresForm(forms.Form):
    Username = forms.CharField(max_length=50)
    Password = forms.CharField(widget=forms.PasswordInput())
    Nome = forms.CharField(max_length=255)
    Email = forms.EmailField(max_length=255)
    Contacto = forms.CharField(max_length=20, required=False)
    ID_Perfil = forms.IntegerField()

class FornecedoresForm(forms.Form):
    Nome = forms.CharField(max_length=255)
    Morada = forms.CharField(max_length=255, required=False)
    Contacto = forms.CharField(max_length=20, required=False)
    NIF = forms.CharField(max_length=20)

class ArmazensForm(forms.Form):
    Localizacao = forms.CharField(max_length=255)

class ComponentesForm(forms.Form):
    Descricao = forms.CharField(max_length=255)
    Nome = forms.CharField(max_length=255)
    ID_Fornecedor = forms.IntegerField()

class EncomendaCompraForm(forms.Form):
    Estado = forms.CharField(max_length=255)
    Data = forms.DateField()
    ID_Utilizador = forms.IntegerField()
    ID_Fornecedor = forms.IntegerField()

class ComponentesEncomendaCompraForm(forms.Form):
    ID_Enc_compra = forms.IntegerField()
    ID_Comp = forms.IntegerField()
    Preco = forms.DecimalField(max_digits=10, decimal_places=2)
    Quantidade = forms.IntegerField()

class GuiaRemessaCompraForm(forms.Form):
    Data = forms.DateField()
    NIF = forms.CharField(max_length=20)
    ID_Enc_compra = forms.IntegerField()

class ComponentesGuiaRemessaCompraForm(forms.Form):
    ID_Remessa_compra = forms.IntegerField()
    ID_Comp = forms.IntegerField()
    Quantidade = forms.IntegerField()
    ID_Armazem = forms.IntegerField()

class MaoObraForm(forms.Form):
    Tipo = forms.CharField(max_length=255)
    Custo = forms.DecimalField(max_digits=10, decimal_places=2)

class EquipamentosForm(forms.Form):
    Nome = forms.CharField(max_length=255)
    Descricao = forms.CharField(max_length=255)
    Preco_Venda = forms.DecimalField(max_digits=10, decimal_places=2)
    Tipo_Equipamento = forms.IntegerField()

class FichaProducaoForm(forms.Form):
    ID_Mao_Obra = forms.IntegerField()
    Data_Hora_Inicio = forms.DateTimeField()
    Data_Hora_Fim = forms.DateTimeField()
    Quantidade = forms.IntegerField()
    ID_Armazem = forms.IntegerField()

class ComponentesFichaProducaoForm(forms.Form):
    ID_Ficha_prod = forms.IntegerField()
    ID_Comp = forms.IntegerField()
    Quantidade = forms.IntegerField()
    Custo_Final = forms.DecimalField(max_digits=10, decimal_places=2)
    ID_Armazem = forms.IntegerField()

class ClientesForm(forms.Form):
    Nome = forms.CharField(max_length=255)
    Morada = forms.CharField(max_length=255, required=False)
    Contacto = forms.CharField(max_length=20, required=False)
    NIF = forms.CharField(max_length=20)

class EncomendaVendaForm(forms.Form):
    ID_Utilizador = forms.IntegerField()
    ID_Cliente = forms.IntegerField()
    Estado = forms.CharField(max_length=255)
    Data = forms.DateField()

class EquipamentosEncomendaVendaForm(forms.Form):
    ID_Enc_Venda = forms.IntegerField()
    ID_Equipamento = forms.IntegerField()
    Preco_Total = forms.DecimalField(max_digits=10, decimal_places=2)
    Quantidade = forms.IntegerField()
    ID_Armazem = forms.IntegerField()

class GuiaRemessaVendaForm(forms.Form):
    ID_Enc_Venda = forms.IntegerField()
    Data = forms.DateField()
    NIF = forms.CharField(max_length=20)

class EquipamentosGuiaRemessaVendaForm(forms.Form):
    ID_Remessa_Venda = forms.IntegerField()
    ID_Equipamento = forms.IntegerField()
    Quantidade = forms.IntegerField()

class PerfilForm(forms.Form):
    Perfil = forms.CharField(max_length=100)
    Perms = forms.CharField(max_length=100)


