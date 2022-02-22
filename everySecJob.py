from multiprocessing import synchronize
import pyupbit
from MySQLdb import _mysql
import json
import os
import requests
from datetime import datetime
from pyupbit.request_api import _send_get_request, _send_post_request, _send_delete_request

'''
This everySecJob.py file is for update of coin's state for every second.
There are several things that should be updated..
- price_log
- trade_per_coin.coin_profit : coin's value - trade_per_coin.average
- trade_per_coin.coin_profit_percent : coin's value / trade_per_coin.average * 100 - 100
- total_balance : total_cash + every coin's current value
- total_profit : every coin's current value - amount of buy
- total_profit_percent : every coin's current value / amount of buy * 100 - 100
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

def updateTotalBalance(db,upbit,account) : 
    balances = upbit.get_balances()
    cash = float(balances[0]['balance'])
    
    total = 0.0
    for coin in balances[1:] : 
        total += float(coin['balance']) * pyupbit.get_current_price('KRW-'+coin['currency'])
    total += cash
    
    #print("total_balance total : {}".format(total))
    db.query("""
             UPDATE account_state
             SET total_balance="""+str(total)+\
             " WHERE userid="+account.userid)
    
    
def updateTotalProfit(db,upbit,account) : 
    db.query("""
            SELECT total_balance,total_deposit FROM account_state
            WHERE userid="""+account.userid)
    r=db.store_result()
    total_balance,total_deposit = map(lambda x : int(x), r.fetch_row()[0])
    total_profit = total_balance-total_deposit
    total_profit_percent = "%.2f" %(total_balance/total_deposit*100-100)
    
    #print("total_profit : {}".format(total_profit))
    #print("total_profit_percent : {}".format(total_profit_percent))
    
    db.query("""
            UPDATE account_state
            SET total_profit="""+str(total_profit)+", total_profit_percent="+str(total_profit_percent)+\
            " WHERE userid="+account.userid)
    
def insertCoinPrice(db,upbit,account) : 
    db.query("""
            SELECT ticker FROM trade_per_coin
            WHERE userid="""+account.userid)
    r=db.store_result()
    
    tickers = list(map(lambda x : x[0].decode('ascii'), r.fetch_row()))
    for ticker in tickers : 
        price = pyupbit.get_current_price("KRW-"+ticker)
        print("INSERT INTO price_log(log_ticker,log_price,log_date) VALUES('"+ticker+"',"+str(price)+",'"+str(datetime.now())+"');")
        db.query("INSERT INTO price_log(log_ticker,log_price,log_date) VALUES('"+ticker+"',"+str(price)+",'"+str(datetime.now())+"');")
    
    
    
def account_sync(db,upbit,account) : 
    #Update total_balance
    updateTotalBalance(db,upbit,account)
    
    #Update total_profit and total_profit_percent
    updateTotalProfit(db,upbit,account)
    
    #Insert coin price to price_log table
    insertCoinPrice(db,upbit,account)
    
    
    
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