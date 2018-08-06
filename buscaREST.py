from funcoesREST import *
import urllib.parse

#Cria API do Tweepy 
apiTwitter = funcoesTwitter.criaAPI()

#Lista de estados
estados=['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
        'MA', 'MT', 'MS','MG', 'PA', 'PB', 'PR', 'PE', 'PI',
        'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

#quantidade de tweets por estado
quantidade = 100

#Conecta ao album do banco
album = mongoDB.conectaBanco()

#busca clientes
clientes = mongoDB.buscaBanco(album)
aux = 0
for cliente in clientes:
        empresa = cliente['nome']
        print('EMp: ' + empresa)
        #Cria documento como uma cópia do atual cliente
        documento = cliente
        #Define chaves de busca com base no banco
        chaves = cliente['tags']
        for estado in estados:
                query = funcoesTwitter.constroiQuery(estado, chaves)
                ide = cliente['analise'][estado]['ultimoId']
                tweets, ultimo = funcoesTwitter.buscaTwittes(query, apiTwitter, quantidade, ide, estado)
                print( cliente['nome'] + '  ' + estado + ' : ' + str(len(tweets)))
                if(len(tweets)!=0):
                        #Atualiza o último id
                        documento['analise'][estado]['ultimoId'] = ultimo
                        #Atualiza a quantidade de tweets do banco
                        documento['analise'][estado]['quantidade'] = documento['analise'][estado]['quantidade'] + len(tweets)
                        #Pega a quantidade de bons ruins e neutros a fim de atualizar com base na analise de sentimento
                        bons = documento['analise'][estado]['bons']
                        ruins = documento['analise'][estado]['ruins']
                        neutros = documento['analise'][estado]['neutros']
                        #Analisa sentimentos e gera os valores de bons ruins e neutros atualizados
                        (tweets, bons, ruins, neutros) = analisaSentimentos(tweets, bons, ruins, neutros)
                        #atualiza valores de bons ruins e neutros no documento
                        documento['analise'][estado]['bons'] = bons
                        documento['analise'][estado]['ruins'] = ruins
                        documento['analise'][estado]['neutros'] = neutros
                        #Adiciona ao documento os tweets já analisados
                        for tweet in tweets:
                                documento['tweets'].append(tweet)
        #Escreve o cliente atualizado no banco
        album.replace_one({"nome": empresa}, documento)
        print('escreveu' + str(aux))
        aux+=1
                     
