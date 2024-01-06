import pymongo
# Conexão com o MongoDB

conexaomongo = pymongo.MongoClient(host='mongodb+srv://DadosVids:LoCX4rRQdXJaWYb0@computronix.2riqt1s.mongodb.net/')

# Obtenção da coleção

banco_de_dados = conexaomongo["Computronix"]
colecao = banco_de_dados["Computronix"]

def valores_atributos_equipamentos_create(id_equipamento, lista_atributos):

    try:
        documento = {
            "id_equip": id_equipamento,
            "atributos": lista_atributos
        }

        resultado = colecao.insert_one(documento)
        print("database.py: ", lista_atributos)

        if resultado.inserted_id:
            return True
        else:
            return False
    except Exception as e:
        print("Error:", e)
        return False

def read_by_id_equipamento(id_equipamento):
    try:
        resultados = colecao.find({'id_equip': id_equipamento})
        return list(resultados)
    except Exception as e:
        print(e)
        return []

def get_atributos_by_id_equipamento(id_equipamento):
    try:
        resultados = colecao.find({'id_equip': id_equipamento})
        atributos_list = [result['atributos'] for result in resultados]
        return atributos_list
    except Exception as e:
        print(e)
        return []

def get_equipamento_by_id(id_equipamento):
    try:
        resultados = colecao.find({'id_equip': id_equipamento})
        return resultados
    except Exception as e:
        print(e)
        return None

def read_all():
    try:
        # Retorna todos os documentos na coleção
        resultados = colecao.find()
        return list(resultados)
    except Exception as e:
        print(e)
        return []

def update_by_id_equipamento(id_equipamento, novos_atributos):
    try:
        # Encontra o documento com base no id_equipamento
        documento = colecao.find_one({'id_equip': id_equipamento})

        if documento:
            keys_to_remove = ['Nome', 'Tipo_Equipamento', 'Preco_Venda', 'Descricao']
            for key in keys_to_remove:
                novos_atributos.pop(key, None)

            # Atualiza os atributos do documento encontrado
            colecao.update_one({'id_equip': id_equipamento}, {'$set': {'atributos': novos_atributos}})
            print("database.py: ", novos_atributos)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def delete_by_id_equipamento(id_equipamento):
    try:
        # Deleta o documento com base no id_equipamento
        resultado = colecao.delete_one({'id_equip': id_equipamento})
        
        if resultado.deleted_count > 0:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
