from tkinter import EXCEPTION
import pyupbit
from datetime import datetime

'''
this tradeUtils.py file gathers methods for updating database after buy or sell event
there are several cases..
1. Buy lower
 - update account_state.total_buy and .total_cash (no needs to update total balance and others because they updates every second)
 - update trade_per_coin.average, .execution_count, .already, .remain and .recent_update
 - insert new row of trade_history;
   - id, UserID, history_ticker, history_buy_or_sell, history_coin_price, history_amount, 
     history_execution_time, history_date, history_done, history_my_average, history_profit
     - history_profit = (history_coin_price-history_my_average)*upbit.get_balance(ticker)
     
2. Buy LOC
 - same with case 1, except update trade_per_coin.already to 0
 
3. Sell over, Sell end
 - same with case 1, except
   - update account_state.sell_count to .sell_count+1
   - update trade_history's existing rows where done=0 to done=1;
   - remove trade_per_coin's row corrensponding with account_id and ticker
   
4. Restart
 - same with case 1, except update all value of trade_per_coin's fields as followed input value.
 * when restart (or start) event, it always buy event immediately (buy amount : 5000, already=1). 
 
overall order : updateAccount -> insertTradeHistory -> updateAccount

'''

def updateAccount(db,upbit,account,type) : 
    
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

    