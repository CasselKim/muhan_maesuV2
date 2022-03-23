import json
import sys
import pyupbit as pu
from legacy.utils import coin
from datetime import datetime
import time
from order import createOrder

def main() :
    orders = []
    
    # with no order sheet
    if len(sys.argv)==1 : 
        orders = createOrder()
        
    # with order sheet
    elif sys.argv[1]=="-p": 
        with open(sys.argv[2],"r") as f :
            preset = json.load(f)
            for c in preset['coins'] : 
                if c['ticker'].isalpha() :
                    ticker = c['ticker'] 
                else :
                    exit("wrong format of ticker -> %s\nPlease change the format Ex) BTC"%c)

                if str(c['principal']).isdigit() :
                    principal = c['principal']
                    if int(principal) < 400000 : exit("Initial principal should be over 400,000 Won")
                else :
                    exit("wrong format of principal -> %s\nPlease change the format Ex>\"400000\""%c)

                if c['first_buy'].lower() in ('y','n') : 
                    first_buy = c['first_buy'] 
                else :
                    exit("wrong format of first_buy -> %s\nPlease change the format Ex>\"y\" or \"n\""%c)

                orders.append([ticker.upper(),int(principal),first_buy.upper()])

    return orders
    
if __name__ == "__main__":
    with open('secret.json','r') as f : 
        secrets = json.load(f)
        access_key = secrets["access_key"]
        secret_key = secrets["secret_key"]
        token = secrets["token"]
    
    upbit = pu.Upbit(access_key, secret_key)
    orders = main()
    
    coins = [coin(upbit, token, *x) for x in orders]
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
            if str(datetime.now())[18] in ('0','2','4','6','8') : # for every two second
               
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