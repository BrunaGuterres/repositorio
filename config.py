from requests_oauthlib import OAuth1
from repustate import Client
import pymongo
import os

def authTwitter():
    
    #Le as chaves de acesso da API do Twitter. Devem ser setadas nas variaveis de ambiente do USUARIO com os nomes iguais aos das variaveis abaixo
    CONSUMER_KEY = os.environ['CONSUMER_KEY']
    CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']  
    ACCESS_SECRET = os.environ['ACCESS_SECRET']

    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

    return auth

def authRepustate():
    
    #Le as chaves de acesso da API do Repustate. Devem ser setadas nas variaveis de ambiente do USUARIO com os nomes iguais aos das variaveis abaixo
    REPUSTATE_KEY = os.environ['REPUSTATE_KEY']  
    cliente = Client(api_key = REPUSTATE_KEY, version= 'v4')
    return cliente

def authMongo():
    
    MONGO_KEY = os.environ['MONGO_KEY']
    client = pymongo.MongoClient(MONGO_KEY)
    return client

def authMeaningCloud(frase):
    
    MEANING_CLOUD_KEY = os.environ['MEANING_CLOUD_KEY']
    carga = {'key': MEANING_CLOUD_KEY, 'lang': 'pt', 'txt': frase}
    return carga
    