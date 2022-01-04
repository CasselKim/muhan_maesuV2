import json
import sys
import pyupbit as pu
from utils import coin
from datetime import datetime
import time

def main(upbit) :
    initial = []
    if len(sys.argv)==1 : 
        while True : 
            while True : 
                ticker = input("Coin ticker(Ex:BTC) : ")
                if not ticker.isalpha() : 
                    print("Please check ticker format")
                else : 
                    break

            while True : 
                principal = input("Principal(Ex:40000) : ")
                if not principal.isdigit() : 
                    print("Please check principal format")
                else : 
                    if int(principal) < 400000 :
                        print("principal should be more than 400,000Won.")
                        continue
                    else : 
                        break

            while True : 
                first_buy = input("Do you want to execute initial buy?[Y/N] : ")
                if first_buy.lower() not in ('y','n') : 
                    print("format : y or n")
                else : 
                    break

            print("-------------------------------------------")
            print("ticker : %s"%ticker.upper())
            print("principal : %s"%principal)
            print("initial buy : %s"%first_buy.upper())
            print("===========================================")

            while True : 
                flag = input("Do you want to add more?[Y/N] : ")
                if flag.lower() not in ('y','n') : 
                    print("format : y or n")
                else : 
                    break
            print("===========================================")
            initial.append([ticker.upper(),int(principal),first_buy.upper()])
            if flag.lower() == 'y' : continue
            else : break

    elif sys.argv[1]=="-p": 
        with open(sys.argv[2],"r") as f :
            preset = json.load(f)
            for c in preset['coins'] : 
                if c['ticker'].isalpha() :
                    ticker = c['ticker'] 
                else :
                    exit("wrong format of ticker -> %s\nPlease change the format Ex) BTC"%c)

                if c['principal'].isdigit() :
                    principal = c['principal']
                    if int(principal) < 400000 : exit("초기자본은 400,000\보다 많아야합니다.")
                else :
                    exit("wrong format of principal -> %s\nPlease change the format Ex>\"400000\""%c)

                if c['first_buy'].lower() in ('y','n') : 
                    first_buy = c['first_buy'] 
                else :
                    exit("wrong format of first_buy -> %s\nPlease change the format Ex>\"y\" or \"n\""%c)

                initial.append([ticker.upper(),int(principal),first_buy.upper()])

    print("\n[Order]\n")
    print("{:<8s}{:<18s}{:<14s}".format("ticker","principal","initial buy"))
    print("-------------------------------------------")
    for x in initial : 
        print("{:<8s}{:<18s}{:<14s}".format(x[0],format(x[1], ',')+'Won',x[2]))
    print("-------------------------------------------")

    if sum([int(x[1]) for x in initial]) > int(upbit.get_balance('KRW')) : 
        print("[Warning] the sum of principals is bigger than balance of upbit account!!! The process can be end earlier before 40 days")

    return initial
    
if __name__ == "__main__":

    with open('secret.json','r') as f : 
        secrets = json.load(f)
        access_key = secrets["access_key"]
        secret_key = secrets["secret_key"]
        token = secrets["token"]
    
    upbit = pu.Upbit(access_key, secret_key)
    initial = main(upbit)
    
    coins = [coin(upbit, token, *x) for x in initial]
    while True : 
        if str(datetime.now())[11:19] == '00:00:00' : 
            for coin in coins :
                if coin.already : 
                    coin.already = False
                    time.sleep(1)
                    continue
                else : 
                    coin.buy_LOC()

        for coin in coins : 
            if str(datetime.now())[19:21] == '.0' : # for every second
                # End session
                if coin.remain <= 10000 : 
                    result = coin.sell_end()
                    if result == False : 
                        coins.remove(coin)

                # Check session
                else : 
                    if not coin.already :
                        coin.buy_lower()
                    coin.sell_over()