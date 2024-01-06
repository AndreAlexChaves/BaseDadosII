from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.urls import reverse_lazy
import json
from io import TextIOWrapper
from django.urls import reverse
from django.http import JsonResponse
from django.db import connections
from django.shortcuts import render, redirect
from .forms import EquipamentosForm

from myproject.database import valores_atributos_equipamentos_create, get_equipamento_by_id, update_by_id_equipamento, get_atributos_by_id_equipamento, delete_by_id_equipamento
from .forms import PerfilForm, UtilizadoresForm, ClientesForm, FichaProducaoForm, FornecedoresForm, MaoObraForm, ArmazensForm, ComponentesForm,TipoEquipamentoForm, EquipamentosForm
cursor = connection.cursor()

from django.db import connections

def get_database_connection(perms):
    if perms == 1:
        return connections['normal']
    else:
        return connections['default']


def check_user(username, password):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT check_user(%s, %s)', [username, password])
            user_exists = cursor.fetchone()[0]
        return user_exists
    except Exception as e:
        print(f"Error checking user: {e}")
        return False

def getperms(username):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT get_idperfil_by_username(%s)', [username])
            perms = cursor.fetchone()[0]
        return perms
    except Exception as e:
        print(f"Error checking perms: {e}")
        return 0

def getuserid(username):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT get_user_id(%s)', [username])
            id = cursor.fetchone()[0]
        return id
    except Exception as e:
        print(f"Error checking perms: {e}")
        return 0 

def login_user(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    if username is not None:
        return redirect('list_equipamentos') 
    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']
        
        user_exists = check_user(username, password)

        if user_exists:
            id=getuserid(username)
            perms=getperms(id)
            if(perms != 0):
                request.session['id']=id
                request.session['perms']=perms
                request.session['username']=username
            return redirect('list_utilizador')
        else:
            messages.success(request, "Erro ao realizar o login")
            return redirect('login')

    else:
        return render(request, 'login.html', {})
 
def logout_user(request):
    # Remove the username from the session
    if 'username' in request.session:
        del request.session['username']

    # Redirect to the login page or any other page you prefer
    return redirect('login')

def perfil(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if (perms <2):
        return redirect('list_equipamentos')   
    if request.method == 'POST':
        form = PerfilForm(request.POST)
        if form.is_valid():  
            perfil = form.cleaned_data['Perfil']
            perms = form.cleaned_data['Perms']
            with connection.cursor() as cursor:
                cursor.execute('CALL sp_perfil_CREATE(%s, %s)', [perfil, perms])
            return redirect('list_perfil')  
    else:
        form = PerfilForm()

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_perfil_READALL()')
            data = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []

    return render(request, 'perfis.html', {'form': form, 'data': data})

def editar_perfil(request, perfil_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try: 
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        if request.method == 'POST':
            form = PerfilForm(request.POST)
            if form.is_valid():
                perfil = form.cleaned_data['Perfil']
                perms = form.cleaned_data['Perms']
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('CALL sp_perfil_UPDATE(%s, %s, %s)', [perfil_id, perfil, perms])
                    return redirect('list_perfil')
                except Exception as e:
                    return redirect('list_perfil')
        else:
            pass
    except Exception as e:
        print(f"Error: {e}")
        return redirect('list_perfil')

def apagar_perfil(request, perfil_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.execute('CALL sp_perfil_DELETE(%s)', [perfil_id])
        return redirect('list_perfil')
    except Exception as e:
        # Handle exceptions here
        print(f"Error: {e}")
        return redirect('list_perfil')

def utilizador(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if (perms <2):
        return redirect('list_equipamentos')   
    if request.method == 'POST':
            form = UtilizadoresForm(request.POST)
            if form.is_valid():  
                username = form.cleaned_data['Username']
                password = form.cleaned_data['Password']
                nome = form.cleaned_data['Nome']
                email = form.cleaned_data['Email']
                contacto = form.cleaned_data['Contacto']
                ID_Perfil = form.cleaned_data['ID_Perfil']
                with connection.cursor() as cursor:
                    cursor.execute('CALL sp_utilizadores_CREATE(%s, %s, %s, %s, %s, %s)',[username, password, nome, email, contacto, ID_Perfil])
                return redirect('list_utilizador')  
    else:
            form = UtilizadoresForm()

    try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM View_Utilizador_Perfil')
                data = cursor.fetchall()
                cursor.execute('SELECT * FROM fn_perfil_READALL()')
                perfis = cursor.fetchall()
    except Exception as e:
            print(f"Erro ao obter dados do banco de dados: {e}")
            data = []
            perfis = []
    return render(request, 'utilizadores.html', {'form': form, 'data': data, 'perfis': perfis})

def editar_utilizador(request, utilizador_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        if request.method == 'POST':
            form = UtilizadoresForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['Username']
                password = form.cleaned_data['Password']
                nome = form.cleaned_data['Nome']
                email = form.cleaned_data['Email']
                contacto = form.cleaned_data['Contacto']
                ID_Perfil = form.cleaned_data['ID_Perfil']
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('CALL sp_utilizadores_UPDATE(%s, %s, %s, %s, %s, %s, %s)', [utilizador_id, username, password, nome, email, contacto, ID_Perfil])
                    return redirect('list_utilizador') 
                except Exception as e:
                    return redirect('list_utilizador')
        else:
            pass
    except Exception as e:
        print(f"Error: {e}")
        return redirect('list_utilizador') 

def apagar_utilizador(request, utilizador_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.execute('CALL sp_utilizadores_DELETE(%s)', [utilizador_id])
        return redirect('list_utilizador') 
    except Exception as e:
        print(f"Error: {e}")
        return redirect('list_utilizador') 

def cliente(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if (perms <2):
        return redirect('list_equipamentos')   
    if request.method == 'POST':
        form = ClientesForm(request.POST)
        if form.is_valid():  
            nome = form.cleaned_data['Nome']
            morada = form.cleaned_data['Morada']
            contacto = form.cleaned_data['Contacto'] 
            nif = form.cleaned_data['NIF']
            with connection.cursor() as cursor:
                cursor.execute('CALL sp_Clientes_CREATE(%s, %s, %s, %s)',[nome, morada, contacto, nif])
            return redirect('list_cliente')  
    else:
        form = ClientesForm()

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            data = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []

    return render(request, 'clientes.html', {'form': form, 'data': data})

def editar_cliente(request, cliente_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        if request.method == 'POST':
            form = ClientesForm(request.POST)
            if form.is_valid():
                nome = form.cleaned_data['Nome']
                morada = form.cleaned_data['Morada']
                contacto = form.cleaned_data['Contacto'] 
                nif = form.cleaned_data['NIF']
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('CALL sp_Clientes_UPDATE(%s, %s, %s, %s, %s)', [cliente_id, nome, morada, contacto, nif])
                    return redirect('list_cliente') 
                except Exception as e:
                    return redirect('list_cliente')
        else:
            pass
    except Exception as e:
        print(f"Error: {e}")
        return redirect('list_cliente') 

def apagar_cliente(request, cliente_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.execute('CALL sp_Clientes_DELETE(%s)', [cliente_id])
        return redirect('list_cliente') 
    except Exception as e:
        # Handle exceptions here
        print(f"Error: {e}")
        return redirect('list_cliente') 
    
def fornecedor(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if (perms <2):
        return redirect('list_equipamentos')   
    if request.method == 'POST':
        form = FornecedoresForm(request.POST)
        if form.is_valid():  
            nome = form.cleaned_data['Nome']
            morada = form.cleaned_data['Morada']
            contacto = form.cleaned_data['Contacto'] 
            nif = form.cleaned_data['NIF']
            with connection.cursor() as cursor:
                cursor.execute('CALL sp_Fornecedores_CREATE(%s, %s, %s, %s)', [nome, morada, contacto, nif])
            return redirect('list_fornecedor')  
    else:
        form = FornecedoresForm()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            data = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []

    return render(request, 'fornecedores.html', {'form': form, 'data': data})

def editar_fornecedor(request, fornecedor_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        if request.method == 'POST':
            form = FornecedoresForm(request.POST)
            if form.is_valid():
                nome = form.cleaned_data['Nome']
                morada = form.cleaned_data['Morada']
                contacto = form.cleaned_data['Contacto'] 
                nif = form.cleaned_data['NIF']
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('CALL sp_Fornecedores_UPDATE(%s, %s, %s, %s, %s)', [fornecedor_id, nome, morada, contacto, nif])
                    return redirect('list_fornecedor') 
                except Exception as e:
                    return redirect('list_fornecedor')
        else:
            pass
    except Exception as e:
        print(f"Error: {e}")
        return redirect('list_fornecedor') 

def apagar_fornecedor(request, fornecedor_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.execute('CALL sp_Fornecedores_DELETE(%s)', [fornecedor_id])
        return redirect('list_fornecedor') 
    except Exception as e:
        # Handle exceptions here
        print(f"Error: {e}")
        return redirect('list_fornecedor') 

def maoobra(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if (perms <2):
        return redirect('list_equipamentos')   
    if request.method == 'POST':
        form = MaoObraForm(request.POST)
        if form.is_valid():  
            tipo = form.cleaned_data['Tipo']
            custo = form.cleaned_data['Custo']
            with connection.cursor() as cursor:
                cursor.execute('CALL sp_Mao_Obra_CREATE(%s, %s)',[tipo, custo])
            return redirect('list_maoobra')  
    else:
        form = MaoObraForm()

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_Mao_Obra_READALL()')
            data = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []

    return render(request, 'maoobra.html', {'form': form, 'data': data})

def editar_maoobra(request, mao_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        if request.method == 'POST':
            form = MaoObraForm(request.POST)
            if form.is_valid():
                tipo = form.cleaned_data['Tipo']
                custo = form.cleaned_data['Custo']
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('CALL sp_Mao_Obra_UPDATE(%s, %s, %s)', [mao_id, tipo, custo])
                    return redirect('list_maoobra') 
                except Exception as e:
                    return redirect('list_maoobra')
        else:
            pass
    except Exception as e:
        print(f"Error: {e}")
        return redirect('list_maoobra') 

def apagar_maoobra(request, mao_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.execute('CALL sp_Mao_Obra_DELETE(%s)', [mao_id])
        return redirect('list_maoobra') 
    except Exception as e:
        # Handle exceptions here
        print(f"Error: {e}")
        return redirect('list_maoobra') 

def armazem(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if (perms <2):
        return redirect('list_equipamentos')   
    if request.method == 'POST':
        form = ArmazensForm(request.POST)
        if form.is_valid():  
            local = form.cleaned_data['Localizacao']
            with connection.cursor() as cursor:
                cursor.execute('CALL sp_Armazens_CREATE(%s)',[local])
            return redirect('list_armazem')  
    else:
        form = ArmazensForm()

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_Armazens_READALL()')
            data = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []

    return render(request, 'armazens.html', {'form': form, 'data': data})

def editar_armazem(request, armazem_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        if request.method == 'POST':
            form = ArmazensForm(request.POST)
            if form.is_valid():
                local = form.cleaned_data['Localizacao']
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('CALL sp_Armazens_UPDATE(%s, %s)', [armazem_id, local])
                    return redirect('list_armazem') 
                except Exception as e:
                    return redirect('list_armazem')
        else:
            pass
    except Exception as e:
        print(f"Error: {e}")
        return redirect('list_armazem') 

def apagar_armazem(request, armazem_id):
    e = ""
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.execute('CALL sp_Armazens_DELETE(%s)', [armazem_id])
            return redirect('list_armazem')
        return redirect('list_armazem') 
    except Exception as error:
        e = f"Error: {error}" 
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_Armazens_READALL()')
            data = cursor.fetchall()
        return render(request, 'armazens.html', {'erro': e, 'data': data})

def tipo_equipamento(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if (perms <2):
        return redirect('list_equipamentos')   
    if request.method == 'POST':
        form = TipoEquipamentoForm(request.POST)
        if form.is_valid():  
            tipo = form.cleaned_data['tipo']
            with connection.cursor() as cursor:
                cursor.execute('CALL sp_tipo_equipamento_CREATE(%s)',[tipo])
            return redirect('list_tipo_equipamento')  
    else:
        form = TipoEquipamentoForm()

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_tipo_equipamento_readall()')
            data = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []

    return render(request, 'list_tipo_equipamento.html', {'form': form, 'data': data})

def editar_tipo_equipamento(request, id_tipo_equipamento):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        if request.method == 'POST':
            form = TipoEquipamentoForm(request.POST)
            if form.is_valid():
                tipo = form.cleaned_data['tipo']
                print(tipo)
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('CALL sp_tipo_equipamento_UPDATE(%s, %s)', [id_tipo_equipamento, tipo])
                    return redirect('list_tipo_equipamento') 
                except Exception as e:
                    return redirect('list_tipo_equipamento')
        else:
            pass
    except Exception as e:
        print(f"Error: {e}")
        return redirect('list_tipo_equipamento') 

def apagar_tipo_equipamento(request, id_tipo_equipamento):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.execute('CALL sp_tipo_equipamento_DELETE(%s)', [id_tipo_equipamento])
        return redirect('list_tipo_equipamento') 
    except Exception as e:
        # Handle exceptions here
        print(f"Error: {e}")
        return redirect('list_tipo_equipamento') 

def apagar_equipamento(request, equip_id):
    e = ""
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)  
    try:
        if username is None:
            return redirect('login') 
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.execute('CALL sp_equipamentos_DELETE(%s)', [equip_id])
            deleted = delete_by_id_equipamento(equip_id)
            print("Deleted: ",deleted)
            return redirect('list_equipamentos') 
    except Exception as error:
        e = f"Error: {error}" 
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_equipamentos_READALL()')
            equip = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_tipo_equipamento_readall()')
            tipos = cursor.fetchall()
    return render(request, 'list_equipamento.html', {'erro': e, 'tipos': tipos, 'data': equip})

def criar_equipamentos(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login')
    if (perms <2):
        return redirect('list_equipamentos') 
    if request.method == 'POST':
        atributos = {}

        atributo_names = request.POST.getlist('atributo_name')
        valores = request.POST.getlist('valor')
        for nome_atributo, valor in zip(atributo_names, valores):
            if valor and nome_atributo:
                if ',' in valor:
                    valor = [v.strip() for v in valor.split(',')]
                atributos[nome_atributo] = valor

        form = EquipamentosForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['Nome']
            desc = form.cleaned_data['Descricao']
            preco = form.cleaned_data['Preco_Venda']
            tipo = form.cleaned_data['Tipo_Equipamento']

            with connection.cursor() as cursor:
                cursor.execute('CALL sp_equipamentos_CREATE(%s,%s,%s,%s, %s)', [nome, desc, preco, tipo, None])
                novo_id = cursor.fetchone()[0]  

                if atributos and novo_id:
                    createdMongo = valores_atributos_equipamentos_create(novo_id, atributos)
                    if createdMongo:
                        return redirect('list_equipamentos')
                
                return redirect('list_equipamentos')
    
    else:
        form = EquipamentosForm()

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_tipo_equipamento_readall()')
            tipo = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        tipo = []

    return render(request, 'criar_equipamento.html', {'form': form, 'tipos': tipo})

def equipamentos_por_preco(request, preco1, preco2):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)  
    try:
        if username is None:
            return redirect('login')  
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Equipamentos_view WHERE Preco_Venda BETWEEN %s AND %s', (preco1, preco2))
            data = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_tipo_equipamento_readall()')
            tipos = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []
        tipos = []
    return render(request, 'list_equipamento.html', {'data': data, 'tipos': tipos})
    
    
def equipamentos_por_tipo(request, tipo):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)  
    try:
        if username is None:
            return redirect('login') 
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Equipamentos_view WHERE tipo= %s', [tipo])
            data = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_tipo_equipamento_readall()')
            tipos = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []
        tipos = []
    return render(request, 'list_equipamento.html', {'data': data, 'tipos': tipos})


def equipamento_por_tipo_preco(request, preco1, preco2 , tipo):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Equipamentos_view WHERE Preco_Venda BETWEEN %s AND %s AND tipo = %s', [preco1, preco2, tipo])
            data = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_tipo_equipamento_readall()')
            tipos = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []
        tipos = []
    return render(request, 'list_equipamento.html', {'data': data, 'tipos': tipos})
    
def editar_equipamentos(request, equip_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if (perms <2):
        return redirect('list_equipamentos')  
        
    equipamento_cursor = get_equipamento_by_id(equip_id)
        
    equipamento = equipamento_cursor[0] if equipamento_cursor else None
    
    array_attributes = {}
    non_array_attributes = {}
    new_atributos = {}
    atributo_names = request.POST.getlist('atributo_name')
    valores = request.POST.getlist('valor')
    for nome_atributo, valor in zip(atributo_names, valores):
        if valor and nome_atributo and nome_atributo not in new_atributos:
            if ',' in valor:
                valor = [v.strip() for v in valor.split(',')]
            new_atributos[nome_atributo] = valor
            
    for atributo, valor in equipamento['atributos'].items():
        if isinstance(valor, list):
            array_attributes[atributo] = valor
        else:
            non_array_attributes[atributo] = valor
    
    print("array_attributes: ",array_attributes)
    print("non_array_attributes: ",non_array_attributes)

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM fn_equipamentos_READ(%s)', [equip_id])
        result = cursor.fetchall() 
        tipo_id = result[0][4]
        tipo = get_nome_tipo_equipamento(request, tipo_id)
        cursor.execute('SELECT * FROM fn_tipo_equipamento_readall()')
        tiposEquip = cursor.fetchall()

    if request.method == 'POST':
        novos_atributos = {}

        for atributo in request.POST:
            if atributo == 'atributo_name' or atributo == 'valor':
                break
            
            if atributo != 'csrfmiddlewaretoken':
                valores = request.POST.getlist(atributo)

                if '[' in atributo:
                    atributo_nome, _ = atributo.split('[')
                    novos_atributos[atributo_nome] = valores
                else:
                    novos_atributos[atributo] = valores[0] if len(valores) == 1 else valores
        novos_atributos.update(new_atributos)

        print("update: ",novos_atributos)
        success = update_by_id_equipamento(equip_id, novos_atributos)

        if success:
            return redirect('list_equipamentos')
        else:
           pass

        form = EquipamentosForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['Nome']
            desc = form.cleaned_data['Descricao']
            preco = form.cleaned_data['Preco_Venda']
            tipo = form.cleaned_data['Tipo_Equipamento']

            with connection.cursor() as cursor:
                cursor.execute('CALL sp_equipamentos_update(%s,%s,%s,%s, %s)', [equip_id, nome, desc, preco, tipo])
                return redirect('list_equipamentos')
    
    else:
        form = EquipamentosForm()

    return render(request, 'editar_equipamento.html', {'detalhes': result, 'tipo': tipo, 'tiposEquip': tiposEquip, 'equipamento': equipamento, 'arrays': array_attributes, 'notarrays': non_array_attributes})
    
def attribute_type(value):
    if isinstance(value, list):
        return 'array'
    elif isinstance(value, str):
        return 'string'

def separate_object(tipos_atributos):
    arrays = {}
    not_arrays = {}

    for atributo, tipo in tipos_atributos.items():
        if tipo == 'array':
            arrays[atributo] = tipo
        else:
            not_arrays[atributo] = tipo

    return arrays, not_arrays

def get_nome_tipo_equipamento(request, p_id_tipo_equipamento):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT get_nome_tipo_equipamento(%s)', [p_id_tipo_equipamento])
            nome_tipo = cursor.fetchone()[0]
            return nome_tipo
    except Exception as e:
        print(f"Error calling the stored function: {e}")
        return None

def ver_equipamento(request, p_id_equip):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_equipamentos_READ(%s)', [p_id_equip])
            result = cursor.fetchall()
            atributos = get_atributos_by_id_equipamento(p_id_equip)
            tipo_id = result[0][4]
            price = round(result[0][3], 2)
            tipo = get_nome_tipo_equipamento(request, tipo_id)
            cursor.execute('SELECT * FROM View_FichasProducao_Equipamentos WHERE ID_Equip = (%s)', (p_id_equip,))
            fichasproducao = cursor.fetchall()
            dados_agrupados = {}

            for ficha in fichasproducao:
                id_ficha_prod = ficha[0]  

                if id_ficha_prod not in dados_agrupados:
                    dados_agrupados[id_ficha_prod] = {'ficha': ficha, 'componentes': []}

                dados_agrupados[id_ficha_prod]['componentes'].append({
                    'ID_Comp_Fich': ficha[10], 
                    'ID_Comp': ficha[11],
                    'Nome_Componente': ficha[13],
                    'Quantidade': ficha[15],
                    'Componente_Armazem': ficha[16],
                })
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        result = []
        tipo = None  
        fichasproducao = []
        price = []
        dados_agrupados = []
        atributos = []
    return render(request, 'ver_equipamento.html', {'detalhes': result, 'tipo': tipo, 'price': price, 'dados_agrupados': dados_agrupados, 'atributos': atributos})


def equipamentos(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login')
    connection= get_database_connection(perms)

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_equipamentos_READALL()')
            equip = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_tipo_equipamento_readall()')
            tipos = cursor.fetchall()

    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        equip = []
        tipos = []

    return render(request, 'list_equipamento.html', {'data': equip, 'tipos': tipos})
    
def componente(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login')
    if request.method == 'POST':
        form = ComponentesForm(request.POST)
        if form.is_valid():  
            descricao = form.cleaned_data['Descricao']
            nome = form.cleaned_data['Nome']
            id_fornecedor = form.cleaned_data['ID_Fornecedor'] 
            with connection.cursor() as cursor:
                cursor.execute('CALL sp_componentes_CREATE(%s, %s, %s)', [descricao, nome, id_fornecedor])
            return redirect('list_componentes')  
    else:
        form = ComponentesForm()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM View_Componentes_Fornecedores')
            data = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_fornecedores_READALL()')
            fornecedores = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados do banco de dados: {e}")
        data = []
        fornecedores = []
    return render(request, 'componentes.html', {'form': form, 'data': data, 'fornecedores': fornecedores})

def editar_componente(request, componente_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login') 
        if (perms < 2):
            return redirect('list_equipamentos')   
        if request.method == 'POST':
            form = ComponentesForm(request.POST)
            if form.is_valid(): 
                print(componente_id)
                descricao = form.cleaned_data['Descricao']
                nome = form.cleaned_data['Nome']
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('CALL sp_componentes_UPDATE(%s, %s, %s)', [componente_id, descricao, nome])
                except Exception as e:
                    print(f"Error in editar_componente: {e}")
    except Exception as e:
        print(f"Error in editar_componente: {e}")
    return redirect('list_componentes') 
        
def apagar_componente(request, componente_id):
    e = ""
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login')
        if (perms <2):
            return redirect('list_equipamentos')
        with connection.cursor() as cursor:
            cursor.execute('CALL sp_componentes_DELETE(%s)', [componente_id])
            return redirect('list_componentes') 
        return redirect('list_componentes') 
    except Exception as error:
        e = f"Error: {error}" 
        print("HELP")
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM View_Componentes_Fornecedores')
            data = cursor.fetchall()
            print("HELP2")
            cursor.execute('SELECT * FROM fn_fornecedores_READALL()')
            fornecedores = cursor.fetchall()
            print("HELP2")
        return render(request, 'componentes.html', {'erro': e, 'data': data, 'fornecedores': fornecedores})

def encomendaComponentes(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados dos fornecedores: {e}")
        fornecedores = []
        
    componentes = []  
    fornecedor_id = None
    if 'fornecedor' in request.GET:
        fornecedor_id = request.GET['fornecedor']
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM fn_Componente_READForn(%s)', [fornecedor_id])
                componentes = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter componentes do fornecedor: {e}")
            componentes = []

    return render(request, 'encomendarComponentes.html', {'fornecedores': fornecedores, 'componentes': componentes, 'ID_Fornecedor': fornecedor_id})

def realizarEncomendaCompra(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    id = request.session.get('id', None)
    if username is None:
        return redirect('login') 
    if request.method == 'POST':
        componentes_json  = request.POST.get('componentes',[])
        try:
            componentes = json.loads(componentes_json)
            with connection.cursor() as cursor:
              
                comp = componentes[0]
                cursor.execute('CALL sp_encomenda_compra_create(%s, %s, %s)', [id, comp[0], None])
                id_encomenda = cursor.fetchone()[0]
               
                for componente in componentes:
                    id_comp = componente[1]
                    preco = componente[3]
                    quantidade = componente[4]
                    cursor.execute('CALL sp_Componentes_Encomenda_Compra_CREATE(%s, %s, %s, %s)',[id_encomenda, id_comp, preco, quantidade])

            return redirect('encomendas') 
        except Exception as e:
            print(f"Erro ao realizar a compra: {e}")
            return redirect('encomendaComponentes') 
    return redirect('encomendaComponentes')  

def encomendaEquipamentos(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM VIEW_stocks_read_equipamentos')
            equipamentos = cursor.fetchall()
            
            cursor.execute('SELECT * FROM fn_clientes_READALL()')
            clientes = cursor.fetchall()
            updated_equipamentos = []
            for equipamento in equipamentos:
                atributos = get_atributos_by_id_equipamento(equipamento[2])
                updated_equipamento = list(equipamento)  
                updated_equipamento.append(atributos)
                updated_equipamentos.append(updated_equipamento)
        print("Equipamentos: ",equipamentos)
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        equipamentos = []        
        clientes = []   
        updated_equipamentos = []
    return render(request, 'encomendarEquipamentos.html', {'equipamentos': updated_equipamentos, 'clientes': clientes})

def realizarEncomendaVenda(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    id = request.session.get('id', None)
    if username is None:
        return redirect('login') 
    
    if request.method == 'POST':
        equipamentos_json  = request.POST.get('equipamentos_venda',[])
        ID_Cliente  = request.POST.get('ID_Cliente')
        try:
            equipamentos = json.loads(equipamentos_json)
            with connection.cursor() as cursor:
                cursor.execute('CALL sp_encomenda_venda_create(%s, %s, %s)', [id, ID_Cliente, None])
                id_encomenda = cursor.fetchone()[0]
               
                for equipamento in equipamentos:
                    id_equip = equipamento[0]
                    id_armazem = equipamento[1]
                    quantidade = equipamento[3]
                    preco = equipamento[4]
                    precoTotal = quantidade * preco
                    cursor.execute('CALL sp_Equipamentos_Encomenda_Venda_CREATE(%s, %s, %s, %s, %s)',[id_encomenda, id_equip, precoTotal, quantidade, id_armazem])

            return redirect('encomendas') 
        except Exception as e:
            print(f"Erro ao realizar a venda: {e}")
    return redirect('encomendaEquipamentos') 

def encomendas(request):
    e=''
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if (perms <2):
        return redirect('login') 
    estado = request.GET.get('estado', None)
    fornecedor_id = request.GET.get('fornecedor', None)
    estado2 = request.GET.get('estado2', None)
    cliente_id = request.GET.get('cliente', None)
     
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM View_Encomendas_Compras WHERE 1=1'
            params = []

            if estado:
                sql += ' AND estado = %s'
                params.append(estado)
            if fornecedor_id:
                sql += ' AND id_fornecedor = %s'
                params.append(fornecedor_id)
            
            cursor.execute(sql,params)
            compras = cursor.fetchall()

            sql = 'SELECT * FROM View_Encomendas_Vendas WHERE 1=1'
            params = []

            if estado2:
                sql += ' AND estado = %s'
                params.append(estado2)
            if cliente_id:
                sql += ' AND id_cliente = %s'
                params.append(cliente_id)

            cursor.execute(sql,params)
            vendas = cursor.fetchall()

            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()

            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()
            
    except Exception as e:
        print(f"Erro ao obter dados dos fornecedores: {e}")
        compras = []
        vendas = []
        fornecedores = []
        clientes = []
        
    return render(request, 'encomendas.html', {'compras': compras, 'vendas': vendas, 'fornecedores': fornecedores, 'clientes': clientes, 'erro': e})

def minhasencomendas(request):
    e=''
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    id = request.session.get('id', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    
    estado = request.GET.get('estado', None)
    fornecedor_id = request.GET.get('fornecedor', None)
    estado2 = request.GET.get('estado2', None)
    cliente_id = request.GET.get('cliente', None)
     
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM View_Encomendas_Compras WHERE ID_Utilizador = %s', [id])
            compras = cursor.fetchall()
            print("HELP2")
            cursor.execute('SELECT * FROM View_Encomendas_Vendas WHERE ID_Utilizador = %s', [id])
            vendas = cursor.fetchall()
            print("HELP3")
            print(compras, vendas)
        
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM View_Encomendas_Compras WHERE ID_Utilizador= %s'
            params = [id]

            if estado:
                sql += ' AND estado = %s'
                params.append(estado)
            if fornecedor_id:
                sql += ' AND id_fornecedor = %s'
                params.append(fornecedor_id)
            
            cursor.execute(sql,params)
            compras = cursor.fetchall()

            sql = 'SELECT * FROM View_Encomendas_Vendas WHERE ID_Utilizador= %s'
            params = [id]

            if estado2:
                sql += ' AND estado = %s'
                params.append(estado2)
            if cliente_id:
                sql += ' AND id_cliente = %s'
                params.append(cliente_id)

            cursor.execute(sql,params)
            vendas = cursor.fetchall()

            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()

            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()
            
       
    except Exception as e:
        print(f"Erro ao obter dados dos fornecedores: {e}")
        print(e)
        compras = []
        vendas = []
        
    return render(request, 'minhasencomendas.html', {'compras': compras, 'vendas': vendas, 'erro': e})

def apagar_compra(request, encomenda_id):
    e = ""
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection = get_database_connection(perms)  
    try:
        if username is None:
            return redirect('login')

        with connection.cursor() as cursor:
            cursor.execute('CALL sp_encomenda_compra_delete(%s)', [encomenda_id])
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()
        return redirect('encomendas')

    except Exception as error:
        e = f"Error: {error}"
        print(e)
        with connection.cursor() as cursor:
            print("pe")
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()

    return render(request, 'encomendas.html', {'erro': e, 'fornecedores': fornecedores, 'clientes': clientes})

    
def apagar_venda(request, encomenda_id):
    e = ""
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection = get_database_connection(perms)  
    try:
        if username is None:
            return redirect('login')

        with connection.cursor() as cursor:
            cursor.execute('CALL sp_encomenda_venda_delete(%s)', [encomenda_id])
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()
        return redirect('encomendas')

    except Exception as error:
        e = f"Error: {error}"
        print(e)
        with connection.cursor() as cursor:
            print("pe")
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()

    return render(request, 'encomendas.html', {'erro': e, 'fornecedores': fornecedores, 'clientes': clientes})

def apagar_compra_minhasencomendas(request, encomenda_id):
    e = ""
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection = get_database_connection(perms)  
    try:
        if username is None:
            return redirect('login')

        with connection.cursor() as cursor:
            cursor.execute('CALL sp_encomenda_compra_delete(%s)', [encomenda_id])
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()
        return redirect('minhasencomendas')

    except Exception as error:
        e = f"Error: {error}"
        print(e)
        with connection.cursor() as cursor:
            print("pe")
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()

    return render(request, 'minhasencomendas.html', {'erro': e, 'fornecedores': fornecedores, 'clientes': clientes})

def apagar_venda_minhasencomendas(request, encomenda_id):
    e = ""
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection = get_database_connection(perms)  
    try:
        if username is None:
            return redirect('login')

        with connection.cursor() as cursor:
            cursor.execute('CALL sp_encomenda_venda_delete(%s)', [encomenda_id])
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()
        return redirect('encomendas')

    except Exception as error:
        e = f"Error: {error}"
        print(e)
        with connection.cursor() as cursor:
            print("pe")
            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_Clientes_READALL()')
            clientes = cursor.fetchall()

    return render(request, 'encomendas.html', {'erro': e, 'fornecedores': fornecedores, 'clientes': clientes})
    

def ver_compra(request, encomenda_id): 
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login')
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM View_Encomendas_Compras WHERE ID_Enc_compra = %s', (encomenda_id,))
            compra = cursor.fetchall()

            cursor.execute('SELECT * FROM View_Componentes_Encomenda_Compra WHERE ID_Enc_compra = %s', (encomenda_id,))
            componentes = cursor.fetchall()

            cursor.execute('SELECT * FROM View_Guias_e_Componentes_Compras WHERE ID_Enc_compra = %s', (encomenda_id,))
            dados_guias = cursor.fetchall()

            dados_agrupados = {}
            for guia in dados_guias:
                id_remessa_compra = guia[0]  

                if id_remessa_compra not in dados_agrupados:
                    dados_agrupados[id_remessa_compra] = {'guia': guia, 'componentes': []}

                dados_agrupados[id_remessa_compra]['componentes'].append({
                    'ID_Componentes_Guia_Remessa_Compra': guia[4],  
                    'ID_Comp': guia[5],
                    'Nome_Componente': guia[6],
                    'Quantidade': guia[7],
                    'Localizacao_Armazem': guia[8],
                })
            return render(request, 'ver_compra.html', {
                'compras': compra,
                'encomenda_id': encomenda_id,
                'componentes': componentes,
                'dados_agrupados': dados_agrupados,

            })

    except Exception as e:
        print(f"Error: {e}")
        return redirect('encomendas')

def ver_venda(request, encomenda_id): 
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login')
        if (perms <2):
            return redirect('list_equipamentos')
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM View_Encomendas_Vendas WHERE ID_Enc_Venda = %s', (encomenda_id,))
            venda = cursor.fetchall()

            cursor.execute('SELECT * FROM View_Equipamentos_Encomenda_Venda WHERE ID_Enc_Venda = %s', (encomenda_id,))
            equipamentos = cursor.fetchall()

            cursor.execute('SELECT * FROM View_Guias_e_Equipamentos_Vendas WHERE ID_Enc_Venda = %s', (encomenda_id,))
            dados_guias = cursor.fetchall()

            dados_agrupados = {}
            for guia in dados_guias:
                id_remessa_venda = guia[0] 

                if id_remessa_venda not in dados_agrupados:
                    dados_agrupados[id_remessa_venda] = {'guia': guia, 'equipamentos': []}

                dados_agrupados[id_remessa_venda]['equipamentos'].append({
                    'ID_Equipamento_Guia_Remessa_Venda': guia[4],  
                    'ID_Equipamento': guia[5],
                    'Nome_Equipamento': guia[6],
                    'Quantidade': guia[7],
                    'Morada': guia[8]
                })
            return render(request, 'ver_venda.html', {
                'vendas': venda,
                'encomenda_id': encomenda_id,
                'equipamentos': equipamentos,
                'dados_agrupados': dados_agrupados,

            })

    except Exception as e:
        print(f"Error: {e}")
        return redirect('encomendas')


def export_encomenda_compra_xml(request, encomenda_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login')
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.callproc('exportar_encomenda_compra_xml', [encomenda_id])
            xml_content = cursor.fetchone()[0]
            
            response = HttpResponse(xml_content, content_type='application/xml')
            response['Content-Disposition'] = f'attachment; filename="Compra_{encomenda_id}.xml"'
            return response
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponse(status=500)
    
def export_encomenda_venda_xml(request, encomenda_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login')
        if (perms <2):
            return redirect('list_equipamentos')  
        with connection.cursor() as cursor:
            cursor.callproc('exportar_encomenda_venda_xml', [encomenda_id])
            xml_content = cursor.fetchone()[0]
            
            response = HttpResponse(xml_content, content_type='application/xml')
            response['Content-Disposition'] = f'attachment; filename="Venda_{encomenda_id}.xml"'
            return response
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponse(status=500)

def add_compraguia_remessa(request, encomenda_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login')
        if (perms <2):
            return redirect('list_equipamentos')
        with connection.cursor() as cursor:
            if request.method == 'POST':
                nif = request.POST.get('nif')

                form_data_str = request.POST.get('formData')
                if form_data_str:
                    form_data = json.loads(form_data_str)
                    if not form_data:
                        return redirect('add_compraguia_remessa', encomenda_id)
                    cursor.execute('CALL sp_guia_remessa_compra_create(%s, %s, %s)', [encomenda_id, nif, None])
                    id_guia = cursor.fetchone()[0]
                    for entry in form_data:
                        id_componente = entry[0]
                        quantidade = entry[1]
                        id_armazem = entry[2]
                        cursor.execute('CALL sp_Componentes_Guia_Remessa_Compra_CREATE(%s, %s, %s, %s)', [id_guia, id_componente, quantidade, id_armazem])

                return redirect('ver_encomendacompra', encomenda_id)

            cursor.execute('SELECT * FROM View_Componentes_Encomenda_Compra WHERE ID_Enc_compra = (%s)', (encomenda_id,))
            componentes = cursor.fetchall()
            cursor.execute('SELECT * FROM fn_Armazens_READALL()')
            armazens = cursor.fetchall()
            return render(request, 'guiacompra.html', {'encomenda_id': encomenda_id, 'componentes': componentes, 'armazens': armazens})
    except Exception as e:
        print(f"Error: {e}")
        return redirect('ver_encomendacompra', encomenda_id)

def importxml_compraguia_remessa(request, encomenda_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login')
        if (perms <2):
            return redirect('list_equipamentos')
        if request.method == 'POST':
            uploaded_file = request.FILES.get('xml_file')
            if uploaded_file:
                xml_data = TextIOWrapper(uploaded_file, encoding='utf-8').read()
                with connection.cursor() as cursor:
                   cursor.execute("SELECT fn_guiacompra_importar_xml(%s)", (xml_data,))
                return redirect('ver_encomendacompra', encomenda_id)
    except Exception as e:
        print(f"Error: {e}")
    return redirect('add_compraguia_remessa', encomenda_id)

def importxml_vendaguia_remessa(request, encomenda_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login')
        if (perms <2):
            return redirect('list_equipamentos')
        if request.method == 'POST':
            uploaded_file = request.FILES.get('xml_file')
            if uploaded_file:
                xml_data = TextIOWrapper(uploaded_file, encoding='utf-8').read()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT fn_guiavenda_importar_xml(%s)", (xml_data,))
                return redirect('ver_encomendavenda', encomenda_id)
    except Exception as e:
        print(f"Error: {e}")
    return redirect('add_vendaguia_remessa', encomenda_id)

def add_vendaguia_remessa(request, encomenda_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    try:
        if username is None:
            return redirect('login')
        if (perms <2):
            return redirect('list_equipamentos')
        with connection.cursor() as cursor:
            if request.method == 'POST':
                nif = request.POST.get('nif')

                form_data_str = request.POST.get('formData')
                if form_data_str:
                    form_data = json.loads(form_data_str)
                    if not form_data:
                        return redirect('add_vendaguia_remessa', encomenda_id)

                cursor.execute('CALL sp_guia_remessa_venda_create(%s, %s, %s)', [encomenda_id, nif, None])
                id_guia = cursor.fetchone()[0]

                for entry in form_data:
                    id_equipamento = entry[0]
                    quantidade = entry[1]
                    destino = entry[2]
                    cursor.execute('CALL sp_Equipamentos_Guia_Remessa_Venda_CREATE(%s, %s, %s, %s)', [id_guia, id_equipamento, quantidade, destino])

                return redirect('ver_encomendavenda', encomenda_id)

            cursor.execute('SELECT * FROM View_Equipamentos_Encomenda_Venda WHERE ID_Enc_venda = (%s)', (encomenda_id,))
            equipamentos = cursor.fetchall()
            return render(request, 'guiavenda.html', {'encomenda_id': encomenda_id, 'equipamentos': equipamentos})
    except Exception as e:
        print(f"Error: {e}")
        return redirect('ver_encomendavenda', encomenda_id)

def stocks(request):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if perms < 2:
        return redirect('list_equipamentos')   

    armazem_id = request.GET.get('armazem', None)
    fornecedor_id = request.GET.get('fornecedor', None)
    nome_id = request.GET.get('nome', None)
    armazem_id2 = request.GET.get('armazem2', None)
    tipo_id = request.GET.get('tipo', None)
    preco_minimo = request.GET.get('precoMinimo', None)
    preco_maximo = request.GET.get('precoMaximo', None)
    
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM VIEW_stocks_read_componentes WHERE 1=1'

            params = []

            if armazem_id:
                sql += ' AND ID_Armazem = %s'
                params.append(armazem_id)

            if nome_id:
                sql += ' AND ID_COMP = %s'
                params.append(nome_id)

            if fornecedor_id:
                sql += ' AND ID_FORNECEDOR = %s'
                params.append(fornecedor_id)

            cursor.execute(sql, params)
            componentes = cursor.fetchall()

            sql = 'SELECT * FROM VIEW_stocks_read_equipamentos WHERE 1=1'
            if armazem_id2:
                sql += ' AND ID_Armazem = %s'
                params.append(armazem_id2)
            if tipo_id:
                sql += ' AND tipo = %s'
                params.append(tipo_id)
            if preco_minimo:
                sql += ' AND preco >= %s'
                params.append(preco_minimo)
            if preco_maximo:
                sql += ' AND preco <= %s'
                params.append(preco_maximo)
            cursor.execute(sql, params)
            equipamentos = cursor.fetchall()

            cursor.execute('SELECT * FROM fn_Armazens_READALL()')
            armazens = cursor.fetchall()

            cursor.execute('SELECT * FROM fn_Fornecedores_READALL()')
            fornecedores = cursor.fetchall()

            cursor.execute('SELECT * FROM fn_Componentes_READALL()') 
            nomes = cursor.fetchall()

            cursor.execute('SELECT * FROM fn_Armazens_READALL()')
            armazens2 = cursor.fetchall()

            cursor.execute('SELECT * FROM fn_tipo_equipamento_READALL()') 
            tipos = cursor.fetchall()

    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        componentes = []
        equipamentos = []
        armazens = []
        fornecedores = []
        nomes = []
        armazens2 = []
        tipos = []
 
    return render(request, 'stocks.html', {'componentes': componentes, 'equipamentos': equipamentos, 'armazens': armazens,'fornecedores': fornecedores, 'nomes': nomes,'armazens2': armazens2, 'tipos': tipos})
    
def novafichaproducao(request, equipamento_id, equipamento_nome):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if perms < 2:
        return redirect('list_equipamentos')   
    try:
        with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM VIEW_stocks_read_componentes')
                componentes = cursor.fetchall()
                cursor.execute('SELECT * FROM fn_Mao_Obra_READALL()')
                maoobra = cursor.fetchall()
                cursor.execute('SELECT * FROM fn_Armazens_READALL()')
                armazens = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        componentes = []
        maoobra = []
        armazens = []

    return render(request, 'novafichaproducao.html', {'componentes': componentes, 'equipamento_id': equipamento_id, 'equipamento_nome': equipamento_nome, 'armazens': armazens, 'maoobra': maoobra})

def processar_fichaproducao(request, equipamento_id):
    username = request.session.get('username', None)
    perms = request.session.get('perms', None)
    id = request.session.get('id', None)
    connection= get_database_connection(perms)
    if username is None:
        return redirect('login') 
    if perms < 2:
        return redirect('list_equipamentos') 
    try:
        if request.method == 'POST':
            form = FichaProducaoForm(request.POST)
            
            componentes_json = request.POST.get('componentes', '[]')
            componentes = json.loads(componentes_json)

            if form.is_valid():
                id_mao_obra = form.cleaned_data['ID_Mao_Obra']
                data_hora_inicio = form.cleaned_data['Data_Hora_Inicio'].strftime('%Y-%m-%d %H:%M:%S')
                data_hora_fim = form.cleaned_data['Data_Hora_Fim'].strftime('%Y-%m-%d %H:%M:%S')
                quantidade = form.cleaned_data['Quantidade']
                id_armazem = form.cleaned_data['ID_Armazem']
                print(equipamento_id, id_mao_obra, id, data_hora_inicio, data_hora_fim, quantidade, id_armazem, None)
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('CALL sp_ficha_producao_create(%s, %s, %s, %s::timestamp, %s::timestamp, %s, %s, %s)', [equipamento_id, id_mao_obra, id, data_hora_inicio, data_hora_fim, quantidade, id_armazem, None])
                        id_ficha_prod = cursor.fetchone()[0]
                        for componente in componentes:
                            cursor.execute('CALL sp_Componentes_Ficha_Producao_CREATE(%s,%s,%s,%s)', [id_ficha_prod, componente['componenteId'], componente['quantidade'], componente['armazemId']])
                            print(f"Componente ID: {componente['componenteId']}, Armazém ID: {componente['armazemId']}, Quantidade: {componente['quantidade']}")
                except Exception as e:
                    print(f"Error: {e}")
    except Exception as e:
        print(f"Error in processar_fichaproducao: {e}")
    return redirect('ver_equipamento', equipamento_id)