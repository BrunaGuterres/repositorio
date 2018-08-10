from requests_oauthlib import OAuth1
import pymongo
import json     
import requests
from config import *
from bson.objectid import ObjectId
from googletrans import Translator
import sys
import calendar
import time

#Cria diciionÃ¡rio com os ids dos estamos para acelerar as buscas utilizando tweepy
estadosId = {'AC': '3c42576594e748ff',
            'AL': '35caf3cf30eba1ad',
            'AP': '72c1b85a11f23685',
            'AM': '0091fbb6411059dd',
            'BA': '8ee88bd36514f636',
            'CE': '7a0985d843b92380',
            'DF': '72ee18b0510eb501',
            'ES': 'ca1ac90b0cff479a',
            'GO': 'c42167e3bba1e99d',
            'MA': 'd9e7a568db83d7e6',
            'MT': '31c646c9d2b0efbb',
            'MS': '292dedf68951e239',
            'MG': 'ce0385aee84dbdf9',
            'PA': '6cf2fd60a82329fc',
            'PB': 'b9999f7f6f548ce7',
            'PR': 'c0d0b98719f1c884',
            'PE': '6f6c3cc945b95a32',
            'PI': '6a8eb83785196df9',
            'RJ': 'e433fbca595f29e5',
            'RN': 'd219658b53f37d2d',
            'RS': 'a4b227ce2060cf5e',
            'RO': '074042a860d58d75',
            'RR': 'dcfd7d224dcf9668',
            'SC': 'f82af1e2ebdb0f2e',
            'SP': '8cd72e7876a6c73d',
            'SE': 'ec32cf627c142984',
            'TO': '9c0db54ac37eb12e'}

#FunÃ§Ãµes de conexÃ£o, busca e atualizaÃ§Ã£o no banco
class mongoDB:
    
    def conectaBanco():
        client = authMongo()
        banco = client['dbteste']
        album = banco['clientesDados']
        print('Conecta Banco')
        return album

    def buscaBanco(album):
        print('Busca Banco')
        clientes = []
        for cliente in album.find({}):
            clientes.append(cliente)
        return clientes

    def insereDb (album, documento):
        print('InsereBanco')
        album.insert_one(documento)

    def atualizaCliente(album, empresa, documento):
        print('Atualiza Cliente')
        album.replace_one({"nome": empresa}, documento)

class funcoesTwitter:

    def montaDicionario(estados):
        #Monta estrutura de analise
        auxAnalise = {}
        aux = 0
        for x in estados:
            auxAnalise.update({estados[aux]:{'bons': 0, 'ruins': 0, 'neutros': 0, 'mistos':0, 'quantidade': 0, 'ultimoId': '' }})
            aux += 1
        #Termina estrutura do cliente a ser colocado no banco
        estrutura = {'_id': ObjectId(),'nome': '', 'ramos': [], 'tags': [], 'analise': auxAnalise, 'tweets': []}
        return estrutura            

    def criaAPI():
        return authTwitter()

    def constroiQuery(estado, chaves):
        #Encontra o ID referente ao estado
        lugarId = estadosId[estado]                                                 

        #ConstrÃ³i Query de Busca 
        parametros = "place:" + lugarId + " ("
        aux = 0
        for chave in chaves:
            if (aux == 0):
                parametros += chave
            else:
                parametros += " OR " + chave
            aux+= 1
        parametros += ")"
        return parametros
    
    def buscaTwittes(query, auth, quantidade, ide, estado):
        #query - query de busca
        #auth - acesso ao api do Twitter
        #quantidade de twittes a serem buscados
        #id do twitte mais novo cadastrado

        #monta carga com a query de busca e parametros
        carga = {'q': query, 'tweet_mode': 'extended', 'lang': 'pt', 'result_type': 'recent', 'count': quantidade, 'since_id': ide ,'include_entities':'false'}

        #Tenta buscar Tweets, senÃ£o espera os 15 min  tenta novamente        
        try:
            print('try')
            twittes = requests.get('https://api.twitter.com/1.1/search/tweets.json', params=carga, auth=auth).json()
            aux = twittes["statuses"]
        except:
            print('except')
            #Se nÃ£o deu, verifica o tempo necessÃ¡rio para novas requisiÃ§Ãµes e aguarda
                #Ve os limites de busca
            resultado=requests.get('https://api.twitter.com/1.1/application/rate_limit_status.json?resources=search', auth=auth).json()
                #Ve o tempo em segundos desde 1970
            tempo_reset=int(resultado['resources']['search']['/search/tweets']['reset'])    #Pegamos o tempo esperado pro prÃ³ximo reset
            tempo_atual=calendar.timegm(time.gmtime())                                      #O tempo atual
            espera=tempo_reset-tempo_atual+10                                               #Tempo necessÃ¡rio mais 10 segundos
            print('Aguardando '+str(espera)+' segundos.')
            time.sleep(espera)        
            twittes = requests.get('https://api.twitter.com/1.1/search/tweets.json', params=carga, auth=auth).json()
            
        #cria variavel para anotar o Ãºltimo tweet
        ultimo = 0
        #Anota as informaÃ§Ãµes desejadas dos twittes
        tw = []
        if(len(twittes['statuses'])):
            for twitte in twittes['statuses']:
                if(ultimo==0):
                    #O primeiro tweet que chega Ã© o mais novo, logo pegamos o id
                    ultimo = twitte['id_str']
                #cria o dicionario com as informaÃ§Ãµes desejada
                dicionario = {'usuario':twitte['user']['name'],'id': twitte['id_str'] ,'estado':estado,'data':twitte['created_at'],'resultado':0, 'ironia': '','tweet':twitte['full_text']}
                tw.append(dicionario)
        #Retorna o dicionario com todos os twittes e o Ãºltimo ID
        return (tw, ultimo)

    def veLimite():
        apiTwitter = funcoesTwitter.criaAPI()
        resultado=requests.get('https://api.twitter.com/1.1/application/rate_limit_status.json?resources=search', auth=apiTwitter).json()
        print(resultado)

       
def analisaSentimentos(tweets, bons, ruins, neutros):
    translator = Translator()   #Chamamos nosso tradutor
    sens=[]                     #Onde vamos guardar nossa traduÃ§Ã£o
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd) 
    for tweet in tweets:
        trad=translator.translate(tweet['tweet'].translate(non_bmp_map)).text   #Traduzimos o texto
        sentimento=requests.post("http://text-processing.com/api/sentiment/",{"text":trad}).json()['label'] #Analisamos
        tweet['resultado']=sentimento                                                                       #Atualizamos
        # sens.append(sentimento)    
        if (sentimento =="neg"):
            ruins+=1
        elif(sentimento =="neutral"):
            neutros+=1
        else:
            bons+=1
    return (tweets,bons, ruins, neutros)

def analisaSentimentosMC(tweets, bons, ruins, neutros):
    url = "http://api.meaningcloud.com/sentiment-2.1"
    for tweet in tweets:
            carga = authMeaningCloud(tweet['tweet'])
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            sentimento = requests.request("POST", url, data=carga, headers=headers).json()
            #Sleep para nao estourar a limitacao da API
            time.sleep(0.5)
            
            if(sentimento['score_tag'] == "P+"):
                tweet['resultado']= 10
                bons+=1
            elif (sentimento['score_tag'] == "P"):
                tweet['resultado']= 5
                bons+=1
            elif(sentimento['score_tag'] == "N+"):
                tweet['resultado']= -10
                ruins+=1
            elif(sentimento['score_tag'] == "N"):
                ruins+=1
                tweet['resultado']= -5
            elif(sentimento['score_tag'] == "NEU" or sentimento['score_tag'] == "NONE"):
                neutros+=1
                tweet['resultado']= 0
            tweet['ironia']= sentimento['irony']
    return (tweets,bons, ruins, neutros)

class atualiza:    
    def atualizaClientes():
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

        #busca Clientes
        clientes = mongoDB.buscaBanco(album)
        aux = 0
        #Atualiza cada cliente no Banco
        for cliente in clientes:
            empresa = cliente['nome']
            print('EMp: ' + empresa)
            #Cria documento como uma cÃ³pia do atual cliente + atualizaÃ§Ãµes
            documento = atualiza.atualizaCliente(cliente, estados, apiTwitter, quantidade)
            #Escreve o cliente atualizado no banco
            mongoDB.atualizaCliente(album, empresa, documento)
            print('escreveu' + str(aux))
            aux+=1

    def atualizaCliente(documento, estados, apiTwitter, quantidade):
        #Define chaves de busca com base no banco
        chaves = documento['tags']
        for estado in estados:
                query = funcoesTwitter.constroiQuery(estado, chaves)
                ide = documento['analise'][estado]['ultimoId']
                tweets, ultimo = funcoesTwitter.buscaTwittes(query, apiTwitter, quantidade, ide, estado)
                print( documento['nome'] + '  ' + estado + ' : ' + str(len(tweets)))
                if(len(tweets)!=0):
                        #Atualiza o Ãºltimo id
                        documento['analise'][estado]['ultimoId'] = ultimo
                        #Atualiza a quantidade de tweets do banco
                        documento['analise'][estado]['quantidade'] = documento['analise'][estado]['quantidade'] + len(tweets)
                        #Pega a quantidade de bons ruins e neutros a fim de atualizar com base na analise de sentimento
                        bons = documento['analise'][estado]['bons']
                        ruins = documento['analise'][estado]['ruins']
                        neutros = documento['analise'][estado]['neutros']
                        #Analisa sentimentos e gera os valores de bons ruins e neutros atualizados
                        (tweets, bons, ruins, neutros) = analisaSentimentosMC(tweets, bons, ruins, neutros)
                        #atualiza valores de bons ruins e neutros no documento
                        documento['analise'][estado]['bons'] = bons
                        documento['analise'][estado]['ruins'] = ruins
                        documento['analise'][estado]['neutros'] = neutros
                        #Adiciona ao documento os tweets jÃ¡ analisados
                        for tweet in tweets:
                                documento['tweets'].append(tweet)
        return documento

class novoCliente:
    #gera Tag com base no nome
    def geraTags(chaves):
        auxChaves = []
        for chave in chaves:
            if ' ' in chave:
                auxChaves.append('#' + chave.replace(' ', ''))
                auxChaves.append('#' + chave.replace(' ', '_'))
                auxChaves.append('@' + chave.replace(' ', '_'))
            else:
                auxChaves.append('#'+chave)
                auxChaves.append('@'+chave)

            auxChaves.append(chave)
        return auxChaves

    def novoCliente(nome, tags):
        #Lista de estados
        estados=['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
                'MA', 'MT', 'MS','MG', 'PA', 'PB', 'PR', 'PE', 'PI',
                'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
        
        #Cria API do Tweepy 
        apiTwitter = funcoesTwitter.criaAPI()
        
        #define quantidade de tweets a serem buscados por estado
        quantidade = 100

        #Cria estrutura do cliente a ser inserido no banco
        cliente = funcoesTwitter.montaDicionario(estados)

        cliente['nome'] = nome

        #Se nenhuma tag foi informada, gera as tags com base no nome
        if(not(tags)):
            tags = geraTags(nome)
        for tag in tags:
            cliente['tags'].append(tag)
                
        #Atualiza cliente com base em novos tweets e analises
        documento = atualiza.atualizaCliente(cliente, estados, apiTwitter, quantidade)

        #Conecta no Banco
        album = mongoDB.conectaBanco()

        #Insere no Banco
        mongoDB.insereDb (album, documento)
