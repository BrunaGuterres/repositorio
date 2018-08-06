from requests_oauthlib import OAuth1
import winreg
import pymongo
import json     
import requests
from config import *
from bson.objectid import ObjectId
from googletrans import Translator
import sys
import calendar
import time

#Cria diciionário com os ids dos estamos para acelerar as buscas utilizando tweepy
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

#Funções de conexão, busca e atualização no banco
class mongoDB:
    
    def conectaBanco():
        client = authMongo()
        banco = client['dbteste']
        album = banco['clientesTemp']
        print('Conecta Banco')
        return album

    def buscaBanco(album):
        print('Busca Banco')
        clientes = []
        for cliente in album.find({}):
            clientes.append(cliente)
        return clientes

    def insereDb (empresa, album, documento):
        print('InsereBanco')
        album.update({"nome": empresa}, {"$set": {"analise": documento}})

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

        #Constrói Query de Busca 
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

        #Tenta buscar Tweets, senão espera os 15 min  tenta novamente        
        try:
            twittes = requests.get('https://api.twitter.com/1.1/search/tweets.json', params=carga, auth=auth).json()
            aux = twittes["statuses"]
        except:
            #Se não deu, verifica o tempo necessário para novas requisições e aguarda
                #Ve os limites de busca
            resultado=requests.get('https://api.twitter.com/1.1/application/rate_limit_status.json?resources=search', auth=auth).json()
                #Ve o tempo em segundos desde 1970
            tempo_reset=int(resultado['resources']['search']['/search/tweets']['reset'])    #Pegamos o tempo esperado pro próximo reset
            tempo_atual=calendar.timegm(time.gmtime())                                      #O tempo atual
            espera=tempo_reset-tempo_atual+10                                               #Tempo necessário mais 10 segundos
            print('Aguardando '+str(espera)+' segundos.')
            time.sleep(espera)        
            twittes = requests.get('https://api.twitter.com/1.1/search/tweets.json', params=carga, auth=auth).json()
            
        #cria variavel para anotar o último tweet
        ultimo = 0
        #Anota as informações desejadas dos twittes
        tw = []
        for twitte in twittes["statuses"]:
            if(ultimo==0):
                #O primeiro tweet que chega é o mais novo, logo pegamos o id
                ultimo = twitte['id_str']
            #cria o dicionario com as informações desejada
            dicionario = {'usuario':twitte['user']['name'],'estado':estado,'data':twitte['created_at'],'resultado':'','tweet':twitte['full_text']}
            tw.append(dicionario)
        #Retorna o dicionario com todos os twittes e o último ID
        return (tw, ultimo)
    def veLimite():
        apiTwitter = funcoesTwitter.criaAPI()
        resultado=requests.get('https://api.twitter.com/1.1/application/rate_limit_status.json?resources=search', auth=apiTwitter).json()
        print(resultado)

       
def analisaSentimentos(tweets, bons, ruins, neutros):
    translator = Translator()   #Chamamos nosso tradutor
    sens=[]                     #Onde vamos guardar nossa tradução
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