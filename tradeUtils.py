import pyupbit

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
   - update existing rows where done=0 to done=1;
   
4. Restart
 - same with case 1, except update all value of trade_per_coin's fields as followed input value.

'''

def update_account(db,upbit,account,type) : 
    
    #update account_state
    total_buy = upbit.get_amount('ALL')
    total_cash = upbit.get_balance(ticker='KRW')
    
    if type=="buy" : #buy
        db.query("""
                UPDATE account_state
                SET total_buy="""+str(total_buy)+",total_cash="+str(total_cash)+\
                " WHERE userid="+account.userid)
    else : #sell
        db.query("""
                UPDATE account_state
                SET total_buy="""+str(total_buy)+",total_cash="+str(total_cash)+",sell_count=sell_count+1"+\
                " WHERE userid="+account.userid)
