from requests_oauthlib import OAuth1
from repustate import Client
import winreg
import pymongo

def authTwitter():
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment')
    #Le as chaves de acesso da API do Twitter. Devem ser setadas nas variaveis de ambiente do USUARIO com os nomes iguais aos das variaveis abaixo
    CONSUMER_KEY = winreg.QueryValueEx(reg_key, 'CONSUMER_KEY')[0]  
    CONSUMER_SECRET = winreg.QueryValueEx(reg_key, 'CONSUMER_SECRET')[0]  
    ACCESS_TOKEN = winreg.QueryValueEx(reg_key, 'ACCESS_TOKEN')[0]  
    ACCESS_SECRET = winreg.QueryValueEx(reg_key, 'ACCESS_SECRET')[0]

    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

    return auth

def authRepustate():
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment')
    #Le as chaves de acesso da API do Repustate. Devem ser setadas nas variaveis de ambiente do USUARIO com os nomes iguais aos das variaveis abaixo
    REPUSTATE_KEY = winreg.QueryValueEx(reg_key, 'REPUSTATE_KEY')[0]  

    cliente = Client(api_key = REPUSTATE_KEY, version= 'v4')
    return cliente

def authMongo():
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment')

    MONGO_KEY = winreg.QueryValueEx(reg_key, 'MONGO_KEY')[0]  

    client = pymongo.MongoClient(MONGO_KEY)
    
    return client