from multiprocessing import synchronize
import pyupbit
from MySQLdb import _mysql
import json
import os
import requests
from pyupbit.request_api import _send_get_request, _send_post_request, _send_delete_request

'''
This sync.py file is for update of account's wallet for everyday or twice a day.
There are several things that should be updated..
- total_deposit : Deposits + Withdraws with last_deposit_uuid and last_withdraws_uuid
- total_buy : every coin's amount of buy
- total_cash
'''


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

def updateDeposits(db,deposits,account) : 
    db.query("""
            SELECT * FROM account_state
            WHERE userid="""+account.userid)
    r=db.store_result()
    account_state = r.fetch_row()[0]
    last_deposit_uuid = account_state[8].decode('ascii')
    
    total=0
    for dep in deposits : 
        if dep['uuid'].replace("-","")==last_deposit_uuid : 
            break
        total+=float(dep['amount'])
    new_last_deposit_uuid = deposits[0]["uuid"].replace("-","")
    
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

def updateWithdraws(db,withdraws,account)  :
    db.query("""
            SELECT * FROM account_state
            WHERE userid="""+account.userid)
    r=db.store_result()
    account_state = r.fetch_row()[0]
    last_withdraws_uuid = account_state[9].decode('ascii')
    
    total=0
    for dep in withdraws : 
        if dep['uuid'].replace("-","")==last_withdraws_uuid : 
            break
        total+=float(dep['amount'])
    last_withdraws_uuid = withdraws[0]["uuid"].replace("-","")
    
    # Update last_deposit_uuid, total deposit
    db.query("""
             UPDATE account_state
             SET last_withdraws_uuid='"""+last_withdraws_uuid+"',total_deposit=total_deposit-"+str(total)+\
             " WHERE userid="+account.userid)
    
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
    
def updateTotalBuy(db,upbit,account) : 
    total_amount = upbit.get_amount('ALL')
    
    #print("total_buy total : {}".format(total_amount))
    db.query("""
             UPDATE account_state
             SET total_buy="""+str(total_amount)+\
             " WHERE userid="+account.userid)
    
def updateTotalCash(db,upbit,account) : 
    total_cash = upbit.get_balance(ticker='KRW')
    
    #print("total_cash total : {}".format(total_cash))
    db.query("""
             UPDATE account_state
             SET total_cash="""+str(total_cash)+\
             " WHERE userid="+account.userid)

def account_sync(db,upbit,account) : 

    #Update Deposits
    deposits = getDepositsHistory(upbit)
    updateDeposits(db,deposits,account)
    
    #Update Withdraws
    withdraws = getWithdrawsHistory(upbit)
    updateWithdraws(db,withdraws,account)
    
    #Update total_buy
    updateTotalBuy(db,upbit,account)
    
    #Update total_cash
    updateTotalCash(db,upbit,account)
    
    return 0

def loc_job(db,upbit,account) : 
    

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