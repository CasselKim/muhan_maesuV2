'''
tradeUtils.py
===========
this module provide mothods for updating database after buy or sell event
Attributes:
    updateAccount(db,upbit:Upbit,account:accountObj,type)
    updateTradePerCoin(db,upbit:Upbit,account:accountObj,type,ticker:str,*args)
    insertTradeHistory(db,upbit:Upbit,account:accountObj,type,ticker:str,*args)
    buy_sell_job(db,upbit:Upbit,account:accountObj,type,ticker:str,params)
      
Example:
    
Todo :    
    - update docstring
    - devide every methods into unit methods to follow functional programming.
'''

from tkinter import EXCEPTION
from datetime import datetime
from .dayJob import *

def updateAccount(db,upbit,account:accountObj,type:str) -> None: 
    '''
    updateAccount(db,upbit,account,type)
    ===========
    this method update account's total_buy and total_cash to account_state.total_buy, account_state.total_cash
    if type is sell, count sell_count up for 1
    
    Attributes:
        updateAccount(db,upbit:Upbit,account:accountObj,type)
        updateTradePerCoin(db,upbit:Upbit,account:accountObj,type,ticker:str,*args)
        insertTradeHistory(db,upbit:Upbit,account:accountObj,type,ticker:str,*args)
        buy_sell_job(db,upbit:Upbit,account:accountObj,type,ticker:str,params)
        
    Example:
        
    Todo :    
        - update docstring
        - devide every methods into unit methods to follow functional programming.
    '''
        
    #update account_state
    total_buy = upbit.get_amount('ALL')
    total_cash = upbit.get_balance(ticker='KRW')
    
    if type in ("buy_lower","buy_loc"): #buy
        db.query("""
                UPDATE account_state
                SET total_buy="""+str(total_buy)+",total_cash="+str(total_cash)+\
                " WHERE userid="+account.userid)
    else : #sell
        db.query("""
                UPDATE account_state
                SET total_buy="""+str(total_buy)+",total_cash="+str(total_cash)+",sell_count=sell_count+1"+\
                " WHERE userid="+account.userid)

def updateTradePerCoin(db,upbit,account,type,ticker,*args) : 
    # args is buy amount of this event when type=="buy".
    # Ex) updateTradePerCoin(db,upbit,account,"buy",5000)
    
    if type=="buy_lower" : 
        coin_buy_amount = upbit.get_amount('KRW-'+ticker) #this buy_amount is coin's total buy amount, not only this event.
        db.query("""
        UPDATE trade_per_coin
        SET average="""+str(coin_buy_amount)+", remain=remain-"+str(args[0])+",recent_update = '"+str(datetime.now())+"""',
        execution_count=execution_count+1, already=1 WHERE userid="""+account.userid+" and ticker='"+ticker+"'")
        
    elif type=="buy_loc" : 
        coin_buy_amount = upbit.get_amount('KRW-'+ticker)
        db.query("""
        UPDATE trade_per_coin
        SET average="""+str(coin_buy_amount)+", remain=remain-"+str(args[0])+",recent_update = '"+str(datetime.now())+"""',
        execution_count=execution_count+1, already=0 WHERE userid="""+account.userid+" and ticker='"+ticker+"'")
        
    elif type=="sell" : #sell event
        db.query("""
        DELETE FROM trade_per_coin
        WHERE userid="""+account.userid+" and ticker='"+ticker+"'")
        
    elif type=="restart" : 
        print(args)
        # input value will be trade_per_coin row's new value.
        # args should be like this : [principal(int), ticker_name(string)]
        db.query("""
        INSERT INTO trade_per_coin (UserID,ticker,principal,split,average,execution_count,already,remain,recent_update,ticker_name,coin_profit,coin_profit_percent)
        VALUES ("""+account.userid+",'"+ticker+"',"+str(int(args[0]))+","+str(int(args[0]/40))+",5000,1,1,"+str(int(args[0]-5000))+",'"+str(datetime.now())+"','ticker',0,0)")

    else : 
        raise(EXCEPTION("Wrong type input"))
            
            
def insertTradeHistory(db,upbit,account,type,ticker,*args) : 
    '''
    args input form shoulb be like : [buy(0) or sell(1), amount of buy]
    and the other should be inserted...
    : UserID, coin_price, history_execution_time, history_date, history_done, history_my_average, history_profit
    '''
    if type is not "restart" : 
        buy_or_sell, amount = args[0]
        db.query("""
                SELECT log_price FROM price_log
                WHERE log_ticker='"""+ticker+"' ORDER BY log_date DESC LIMIT 1")
        coin_price = float(db.store_result().fetch_row()[0][0])
        
        db.query("""
                SELECT execution_count,coin_profit FROM trade_per_coin
                WHERE userid="""+account.userid)
        history_execution_time, history_profit = db.store_result().fetch_row()[0]
        history_date = datetime.now()
        history_my_average = upbit.get_avg_buy_price('KRW-'+ticker)
        
        if type=="sell" : 
            db.query("""
                UPDATE trade_history
                SET history_done=1
                WHERE userid="""+account.userid+" and history_ticker='"+ticker+"' and history_done=0")
        
        db.query("""
                INSERT INTO trade_history (UserID, history_ticker, history_buy_or_sell, history_coin_price, history_amount, 
                                            history_execution_time, history_date, history_done, history_my_average, history_profit)
                VALUES ("""+account.userid+",'"+ticker+"',"+str(int(buy_or_sell))+","+str(coin_price)+","+str(amount)+","+\
                        str(int(history_execution_time))+",'"+str(history_date)+"',0,"+str(history_my_average)+","+str(float(history_profit))+')')
    else : 
        buy_or_sell, amount = args[0]
        history_date = datetime.now()
        current_price = pyupbit.get_current_price("KRW-"+ticker)
        db.query("""
                INSERT INTO trade_history (UserID, history_ticker, history_buy_or_sell, history_coin_price, history_amount, 
                                            history_execution_time, history_date, history_done, history_my_average, history_profit)
                VALUES ("""+account.userid+",'"+ticker+"',0,"+str(current_price)+","+str(amount)+","+\
                        "1,'"+str(history_date)+"',0,"+str(current_price)+",0)")
    

def buy_sell_job(db,upbit,account,type,ticker,params) : 
    '''
    kargs format should be like this
    {
        'coin_parameters'  : [
            (if type==buy) amount_of_buy (ex:5000)
            (if type==restart) principal (ex:400000)
        ]
        'history_parameters' : [
            buy_or_sell, amount of buy (ex:1(sell),5000)
        ]
    }
    '''

    updateAccount(db,upbit,account,type)
    insertTradeHistory(db,upbit,account,type,ticker,params['history_parameters'])
    updateTradePerCoin(db,upbit,account,type,ticker,params['coin_parameters'])

    