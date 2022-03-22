from multiprocessing import synchronize
import pyupbit
from MySQLdb import _mysql
import json
import os
import requests
from datetime import datetime
from tradeUtils import buy_sell_job
import time

'''
This secJob.py file is for update of coin's state for every second.
There are several things that should be updated..
- price_log
- trade_per_coin.coin_profit : coin's value - trade_per_coin.average
- trade_per_coin.coin_profit_percent : coin's value / trade_per_coin.average * 100 - 100
- total_balance : total_cash + every coin's current value
- total_profit : every coin's current value - amount of buy
- total_profit_percent : every coin's current value / amount of buy * 100 - 100

Also there are buy and sell cases..
- Buy lower : when the price of coin drops under -10%, execute 1 buy (1 split)
- Sell over : when the price of coin exceeds over +10%, execute sell all splits (coin)

[TODO]
Secjob executes every second, so even a few amount of API call can be critical.
Upbit API Call like get_current_price(), get_balance(), and get_avg_buy_price() must be minized.
- insert average price(float[20,10], not null) field in trade_per_coin table.
- change name of average field in trade_per_coin table to buy_amount
    - because it confuses the meaning of field's value - actually it is amount of buy (5000, 10000, ...)
- replace all of upbit API calls into queries.
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
    
def buySellConditionJob(db,upbit,account) : 
    
    db.query("""
            SELECT * FROM trade_per_coin
            WHERE userid="""+account.userid)
    r=db.store_result()       
    
    for _ in range(r.num_rows()) : 
        coin = r.fetch_row()[0]
        ticker = coin[2].decode('ascii')
        
        db.query("""
            SELECT log_price FROM price_log
            WHERE log_ticker='"""+ticker+"' ORDER BY log_date DESC LIMIT 1")
        price = float(db.store_result().fetch_row()[0][0])
        my_average = upbit.get_avg_buy_price('KRW-'+ticker)
        
        
        #buy lower
        split,execution_count,already_buy,remain = int(coin[4]), int(coin[6]), bool(int(coin[7])), float(coin[8])
        if price < my_average*0.9 and execution_count<40 and remain>=split and not already_buy :  
            upbit.buy_market_order('KRW-'+ticker, split)
            buy = {
                'coin_parameters'  : split,
                'history_parameters' : [0, split]
            }
            buy_sell_job(db,upbit,account,"buy_lower",ticker,buy)
        
        #sell over
        if price >= my_average*1.1 :
            balance = upbit.get_balance(ticker)
            
            # sell
            sell = {
                'coin_parameters'  : balance,
                'history_parameters' : [1, balance]
            }
            buy_sell_job(db,upbit,account,"sell",ticker,sell)
            upbit.sell_market_order('KRW-'+ticker, balance)
            
            time.sleep(3)
            
            # restart
            # [TODO] principal should be able to input on the admin page
            principal = 400000
            split = principal//40
            restart = {
                'coin_parameters'  : principal, # principal
                'history_parameters' : [0, split] # buy, split
            }
            upbit.buy_market_order('KRW-'+ticker, split)
            buy_sell_job(db,upbit,account,"restart",ticker,restart)
        
    
def updatePrice(db,upbit,account) : 
    
    #Insert coin price to price_log table
    insertCoinPrice(db,account)
    
    #Check buy under case and sell over case
    buySellConditionJob(db,upbit,account)
    
    #Update coin profit in trade_per_coin
    updateCoinProfit(db,upbit,account)
    
    
    return 0

if __name__ == "__main__" : 
    start = datetime.now()
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
        
    end = datetime.now()
    print((end-start).seconds)