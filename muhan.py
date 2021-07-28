import json
import sys
import pyupbit as pu
from utils import coin
from datetime import datetime
import time

def main() :
    initial = []
    if len(sys.argv)==1 : 
        while True : 
            while True : 
                ticker = input("코인티커를 적어주세요(Ex:BTC) : ")
                if not ticker.isalpha() : 
                    print("티커를 정확하게 적어주세요")
                else : 
                    break

            while True : 
                balance = input("초기 자본을 적어주세요(Ex:40000) : ")
                if not balance.isdigit() : 
                    print("초기 자본을 정확하게 적어주세요")
                else : 
                    if balance < 400000 :
                        print("초기 자본은 400,000\보다 많아야합니다.")
                        continue
                    else : 
                        break

            while True : 
                first_buy = input("최초 매수를 진행하시겠습니까?[Y/N] : ")
                if first_buy.lower() not in ('y','n') : 
                    print("y 혹은 n중에 적어주세요")
                else : 
                    break

            print("-------------------------------------------")
            print("티커 : %s"%ticker.upper())
            print("초기자본 : %s"%balance)
            print("최초매수 : %s"%first_buy.upper())
            print("===========================================")

            while True : 
                flag = input("더 입력하시겠습니까?[Y/N] : ")
                if flag.lower() not in ('y','n') : 
                    print("y 혹은 n중에 적어주세요")
                else : 
                    break
            print("===========================================")
            initial.append([ticker.upper(),int(balance),first_buy.upper()])
            if flag.lower() == 'y' : continue
            else : break



    elif sys.argv[1]=="-p": 
        with open(sys.argv[2],"r") as f :
            preset = json.load(f)
            for c in preset['coins'] : 
                if c['ticker'].isalpha() :
                    ticker = c['ticker'] 
                else :
                    exit("잘못된 형식의 티커입니다 -> %s\n올바른 형태로 바꿔주세요 Ex) BTC"%c)

                if c['balance'].isdigit() :
                    balance = c['balance']
                    if int(balance) < 400000 : exit("초기자본은 400,000\보다 많아야합니다.")
                else :
                    exit("잘못된 형식의 초기자본입니다 -> %s\n올바른 형태로 바꿔주세요 Ex>\"400000\""%c)

                if c['first_buy'].lower() in ('y','n') : 
                    first_buy = c['first_buy'] 
                else :
                    exit("잘못된 형식의 최초매수입니다 -> %s\n올바른 형태로 바꿔주세요 Ex>\"y\" or \"n\""%c)

                initial.append([ticker.upper(),int(balance),first_buy.upper()])

    print("\n[주문내용]\n")
    print("{:<6s}{:<14s}{:<10s}".format("티커","초기자본","최초매수"))
    print("-------------------------------------------")
    for x in initial : 
        print("{:<8s}{:<18s}{:<14s}".format(x[0],format(x[1], ',')+'\\',x[2]))
    print("-------------------------------------------")

    #if sum([x for x in initial[1]]) > upbit.get_balance(self.ticker) : 
    if True : 
        print("[경고] 업비트 잔고보다 초기자본의 합이 더 많습니다!!! 40일 이전에 매수가 종료될 수 있습니다.")

    while True : 
        flag = input("진행하시겠습니까?[Y/N] : ")
        if flag.lower() not in ('y','n') : 
            print("y 혹은 n중에 적어주세요")
        else : 
            if flag=='y' : break
            else : 
                exit("프로그램을 다시 실행시켜주세요.")
    return initial
    
if __name__ == "__main__":
    initial = main()
    with open('secret.json','r') as f : 
        secrets = json.load(f)
        access_key = secrets["access_key"]
        secret_key = secrets["secret_key"]
        token = secrets["token"]
    
    upbit = pu.Upbit(access_key, secret_key)
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