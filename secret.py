import pyupbit
import json
import time
import requests
from utils import post_message

def makeSecrets() : 
    secret = dict()
    while True : 
        access_key = input("Upbit Access Key : ")
        secret_key = input("Upbit Secret Key : ")
        if pyupbit.Upbit(access_key, secret_key).get_balance() == None : 
            print("Wrong Keys : Please check your inputs")
            continue
        print("Key Accepted!!")
        break

    while True : 
        token = input("\nSlack token : ")
        print("Token test....")
        post_message(token,"#notice","Connected!!")
        while True : 
            answer = input("Token Test Complete! Did you get messages on slack?[Y/N]")
            if answer.lower() not in ('y','n') : 
                print("Please check your input : it must be y or n")
            else : 
                break
        if answer.lower() == 'y' : 
            break
        else : 
            continue
            
    secret['access_key'] = access_key
    secret['secret_key'] = secret_key
    secret['token'] = token
        
    with open('secret.json', 'w', encoding="utf-8") as make_file :
        json.dump(secret, make_file, ensure_ascii=False, indent="\t")
      
if __name__ == "__main__" : 
    makeSecrets()
    