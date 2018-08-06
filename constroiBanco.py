#Constroi novo banco clientesTemp com base no banco de backup de clientes, ramos e tags Clientes
from funcoesREST import *
from config import *
from bson.objectid import ObjectId

estados=['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
        'MA', 'MT', 'MS','MG', 'PA', 'PB', 'PR', 'PE', 'PI',
        'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

#Conecta ao banco
album = mongoDB.conectaBanco()

#busca clientes
clientes = mongoDB.buscaBanco(album)

documento = funcoesTwitter.montaDicionario(estados)

client = authMongo()
banco = client['dbteste']
album = banco['Clientes']

documentos = []
for cliente in clientes:
    documento['_id'] = ObjectId()
    documento['nome'] = cliente['nome']
    documento['ramos'] = cliente['ramos']
    documento['tags'] = cliente['tags']
    documentos.append(documento)
    album.insert_one(documento)


