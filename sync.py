from multiprocessing import synchronize
import pyupbit
from MySQLdb import _mysql
import json
import os
import requests
from pyupbit.request_api import _send_get_request, _send_post_request, _send_delete_request
#from mysite.polls.models import AccountState, UserInfo, AccessKey


class accountObj() : 
    def __init__(self,userid,upbit_secret_key,upbit_access_key,slack_token) : 
        self.userid = userid
        self.upbit_secret_key = upbit_secret_key
        self.upbit_access_key = upbit_access_key
        self.slack_token = slack_token
def connectMySQL(password) : 
    print("MySQL Connected!!")
    return _mysql.connect(host="localhost",user="guest",passwd=password,db="muhan_db") # connect with MySQL
def getDepositsHistory(upbit) : 
    url = "https://api.upbit.com/v1/deposits"
    headers = upbit._request_headers() 
    response = requests.request("GET", url, headers=headers)
    return response.json()

def updateDeposits(db,upbit,deposits,account) : 
    db.query("""
            SELECT * FROM account_state
            WHERE userid="""+account.userid)
    r=db.store_result()
    account_state = r.fetch_row()[0]
    last_deposit_uuid = account_state[8]
    
    total=0
    for dep in deposits : 
        if dep['uuid'].replace("-","")==last_deposit_uuid : 
            break
        total+=float(dep['amount'])
    new_last_deposit_uuid = deposits[-1]["uuid"].replace("-","")
    print(total)
    
    # Update last_deposit_uuid, total deposit
    db.query("""
             UPDATE account_state
             SET last_deposit_uuid='"""+new_last_deposit_uuid+"',total_deposit=total_deposit+"+str(total)+\
             " WHERE userid="+account.userid)

    

def getWithdrawsHistory(upbit) : 
    url = "https://api.upbit.com/v1/withdraws"
    headers = upbit._request_headers() 
    response = requests.request("GET", url, headers=headers)
    return response.json()
#def checkWithdrawsUpdate(upbit,withdraws)  :
def getAccounts(db) : 
    db.query("""
            SELECT * FROM access_key
            """)
    r=db.store_result()
    fetched = r.fetch_row()
    
    account_list = []
    for f in fetched : 
        account_list.append(accountObj(*map(lambda x : x.decode('ascii'),f)))
    return account_list

    
def account_sync(db,upbit,account) : 
    
    print(upbit.__dir__())
    # querying needed data
    
    balanaces = upbit.get_balances()
    total_balance = int(float(balanaces[0]['balance']))
    for b in balanaces[1:] : 
        total_balance += int(pyupbit.get_current_price('KRW-'+b['currency'])*float(b['balance']))
    #print('총 자산(total_balance):',total_balance)
    #print('매수자본(total_buy) :',int(upbit.get_amount('ALL')))
    #print('보유현금(total_cash) :',int(upbit.get_balance(ticker='KRW')))
    
    #print('비트코인 평단 :',upbit.get_avg_buy_price('KRW-BTC'))
    #print('비트코인 총 매수금액 :',int(upbit.get_amount('KRW-BTC')))
    #print('현재 비트코인 가격 :',pyupbit.get_current_price('KRW-BTC'))
    print("===================================")
    print(upbit.get_api_key_list())
    print("===================================")
    deposits = getDepositsHistory(upbit)
    updateDeposits(db,upbit,deposits,account)
    
    #withdraws = getWithdrawsHistory(upbit)
    #checkWithdrawsUpdate(db,upbit,withdraws)
    
    #print(deposits)
    #print(withdraws)
    
    
    return 0
    


if __name__ == "__main__" : 
    
    # get secret key from json file
    secrets = json.loads(open('mysite/secret.json').read())
    password = secrets["PASSWORD"]
    
    # connect with MySQL
    db = connectMySQL(password)
    accounts = getAccounts(db)
    
    for account in accounts : 
    
        keys = json.loads(open('secret.json').read())
        
        access_key = account.upbit_access_key
        secret_key = account.upbit_secret_key
        
        # make pyupbit instance
        upbit = pyupbit.Upbit(access_key, secret_key)

        # execute sync with account(upbit) and database(mysql)
        account_sync(db,upbit,account)