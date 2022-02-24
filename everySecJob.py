from multiprocessing import synchronize
import pyupbit
from MySQLdb import _mysql
import json
import os
import requests
from datetime import datetime

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
    
def insertCoinPrice(db,account) : 
    db.query("""
            SELECT ticker FROM trade_per_coin
            WHERE userid="""+account.userid)
    r=db.store_result()
    
    for _ in range(r.num_rows()) : 
        ticker = r.fetch_row()[0][0].decode('ascii')
        price = pyupbit.get_current_price("KRW-"+ticker)
        print("INSERT INTO price_log(log_ticker,log_price,log_date) VALUES('"+ticker+"',"+str(price)+",'"+str(datetime.now())+"');")
        db.query("INSERT INTO price_log(log_ticker,log_price,log_date) VALUES('"+ticker+"',"+str(price)+",'"+str(datetime.now())+"');")
    
def updateCoinProfit(db,upbit,account) : 
    db.query("""
            SELECT * FROM trade_per_coin
            WHERE userid="""+account.userid)
    r=db.store_result()       
    
    total_coin = 0.0
    total_my = 0.0
    for _ in range(r.num_rows()) : 
        coin = r.fetch_row()[0]
        ticker = coin[2].decode('ascii')
        
        db.query("""
            SELECT log_price FROM price_log
            WHERE log_ticker='"""+ticker+"' ORDER BY log_date DESC LIMIT 1")
        price = float(db.store_result().fetch_row()[0][0])
        amount = upbit.get_balance('KRW-'+ticker)
        my_average = upbit.get_avg_buy_price('KRW-'+ticker)
        
        profit = (price - my_average)*amount
        profit_percent = price/my_average*100-100
        print(profit_percent)
        db.query("""
            UPDATE trade_per_coin
            SET coin_profit="""+str(profit)+", coin_profit_percent="+str(profit_percent)+\
            " WHERE userid="+account.userid+" and ticker='"+ticker+"'")
        
        total_coin+=price*amount
        total_my+=my_average*amount
    
    db.query("""
            SELECT total_cash FROM account_state
            WHERE userid="""+account.userid)
    r=db.store_result()  
    
    total_cash = float(r.fetch_row()[0][0])
    updateTotalBalance(db,account,total_coin,total_cash)
    updateTotalProfit(db,account,total_coin,total_my)

def updateTotalBalance(db,account,total_coin,total_cash) : 
    total_balance = total_coin+total_cash
    db.query("""
             UPDATE account_state
             SET total_balance="""+str(total_balance)+\
             " WHERE userid="+account.userid)

def updateTotalProfit(db,account,total_coin,total_my) : 
    total_profit = total_coin - total_my
    total_profit_percent = total_coin / total_my * 100 - 100
    db.query("""
            UPDATE account_state
            SET total_profit="""+str(total_profit)+", total_profit_percent="+str(total_profit_percent)+\
            " WHERE userid="+account.userid)
    
def updatePrice(db,upbit,account) : 
    
    #Insert coin price to price_log table
    insertCoinPrice(db,account)
    
    #Update coin profit in trade_per_coin
    updateCoinProfit(db,upbit,account)
    
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
        updatePrice(db,upbit,account)