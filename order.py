import pyupbit
import json

def createOrder() : 
    orders = []
    valid_tickers = pyupbit.get_tickers()
    while True : 
        # ticker
        while True : 
            ticker = input("Coin ticker(Ex:BTC) : ").upper()
            if not ticker.isalpha() : 
                print("Please check ticker format.")
            elif 'KRW-'+ticker not in valid_tickers : 
                print("Invalid ticker. Please put correct ticker.")
            elif ticker in [x['ticker'] for x in orders] :
                print("Invalid Input : Given ticker is already enlisted.")
            else : 
                break

        # principal
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

        # first_buy
        while True : 
            first_buy = input("Do you want to execute initial buy? [Y/N] : ")
            if first_buy.lower() not in ('y','n') : 
                print("format : y or n")
            else : 
                break

        # add element of ticker, principal and first buy
        order = dict()
        order['ticker'] = ticker
        order['principal'] = int(principal)
        order['first_buy'] = first_buy.upper()
        orders.append(order)

        while True : 
            print("\n[Order]\n")
            print("{:<4s}{:<8s}{:<18s}{:<14s}".format("","ticker","principal","initial buy"))
            print("-------------------------------------------")
            for i,x in enumerate(orders) : 
                print("{:<4d}{:<8s}{:<18s}{:<14s}".format(i+1,x['ticker'],format(x['principal'], ',')+' Won',x['first_buy']))
            print("-------------------------------------------")
            
            # Ask whether add more or not
            while True : 
                questions = ["[1] Add order","[2] Remove order","[3] Remove all orders","[4] Finish","Select service you want : "]
                more = input('\n'.join(questions))
                if more.lower() not in ('1','2','3','4') : 
                    print("Your input should be in 0,1,2 and 3")
                else : 
                    break
            if more == '2' : 
                selected = input('Select index you want to remove : ')
                if not selected.isdigit() : 
                    print("Invalid input : index should be digit")
                elif int(selected) > len(orders) : 
                    print("Invalid input : index should be exist in order sheet.\n")
                else : 
                    poped = orders.pop(int(selected)-1)
                    continue
            else : 
                break
        
        if more == '1' : continue
        elif more == '3' : 
            print("[WARNING] All of orders are removed.")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            orders = []
            continue
        else : 
            break
        
    return orders
    
def saveOrderJson(orders) :     
    coins = dict()
    coins['coins'] = orders
    with open('order.json', 'w', encoding="utf-8") as make_file:
        json.dump(coins, make_file, ensure_ascii=False, indent="\t")
        
    print("order.json << Successfully created !")

if __name__ == '__main__' : 
    orders = createOrder()
    saveOrderJson(saveOrderJson)