import pyupbit as pu
from datetime import datetime
import requests
import time

def post_message(token, channel, text) :
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text},
)

class coin() : 
    def __init__(self, upbit, token, ticker, principal, first_buy) : 
        if not all([type(upbit)==pu.exchange_api.Upbit,type(ticker)==str, type(principal)==int, first_buy in ('Y','N')]) : 
            raise(Exception("Please match the form of input(string, int, Y or N)"))
        
        #invariables
        self.upbit = upbit
        self.ticker = 'KRW-'+ticker
        self.principal = principal
        self.split = int(principal)/40
        self.token = token
        
        #variables
        self.avg = 0
        self.remain = self.principal
        self.already = False
        self.debug=False
        
        if self.split < 5000 : raise(Exception("Lower than minimum price.")) #Exception
        if first_buy=='Y' : 
            self.upbit.buy_market_order(self.ticker, self.split) #First buy
            time.sleep(2)
            self.update_state()
            post_message(self.token, "#notice","[RESTART]\nCoin : {}\nPrincipal : {}Won\nFirst Buy Avarage Price : {}Won".format(self.ticker,self.principal,self.avg))
            post_message(self.token, "#notice","[BUY]  {} {} at {} ({})".format('First Buy',self.ticker,self.avg,str(datetime.now())[:-7]))
            post_message(self.token, "#notice","<<Debug>> {} {} {} {} {} {}".format(self.ticker,self.principal,self.split,self.avg,self.remain,self.already))
        else : 
            self.update_state(buy=False)
            post_message(self.token, "#notice","<<Debug>> {} {} {} {} {} {}".format(self.ticker,self.principal,self.split,self.avg,self.remain,self.already))
            
    def restart(self) : 
        self.remain = self.principal
        self.already = False
        self.avg = self.get_current_price()

        # First Buy
        self.upbit.buy_market_order(self.ticker, self.split)
        time.sleep(2)
        self.update_state()
        post_message(self.token, "#notice","[RESTART]\nCoin : {}\nPrincipal : {}Won\nFirst Buy Avarage Price : {}Won".format(self.ticker,self.principal,self.avg))
        post_message(self.token, "#notice","[BUY]  {} {} at {} ({})".format('First Buy',self.ticker,self.avg,str(datetime.now())[:-7]))
        post_message(self.token, "#notice","<<Debug>> {} {} {} {} {} {}".format(self.ticker,self.principal,self.split,self.avg,self.remain,self.already))
        

    #LOC average price buy
    def buy_LOC(self) : 
        
        current_price = self.get_current_price()
        
        #LOC average price buy case
        if current_price < self.avg and self.remain > self.split/2 : 
            self.upbit.buy_market_order(self.ticker, self.split/2)
            time.sleep(2)
            self.update_state(half=True)
            self.already = True
            post_message(self.token, "#notice","[BUY]  {} {} at {} ({})".format('LOC Buy under case',self.ticker,self.avg,str(datetime.now())[:-7]))
            post_message(self.token, "#notice","<<Debug>> {} {} {} {} {} {}".format(self.ticker,self.principal,self.split,self.avg,self.remain,self.already))
        
        #LOC Big average price buy case
        if current_price < self.avg*1.1 and self.remain > self.split/2: 
            self.upbit.buy_market_order(self.ticker, self.split/2)
            time.sleep(2)
            self.update_state(half=True)
            self.already = True
            post_message(self.token, "#notice","[BUY]  {} {} at {} ({})".format('LOC Buy over case',self.ticker,self.avg,str(datetime.now())[:-7]))
            post_message(self.token, "#notice","<<Debug>> {} {} {} {} {} {}".format(self.ticker,self.principal,self.split,self.avg,self.remain,self.already))
        
    
    #When price get 5% lower than my average
    def buy_lower(self) : 
        
        current_price = self.get_current_price()
        
        if current_price < self.avg*0.9 and self.remain > self.split: 
            self.upbit.buy_market_order(self.ticker, self.split)
            time.sleep(2)
            self.update_state()
            self.already=True
            post_message(self.token, "#notice","[BUY]  {} {} at {} ({})".format('Lower Buy',self.ticker,self.avg,str(datetime.now())[:-7]))
            post_message(self.token, "#notice","<<Debug>> {} {} {} {} {} {}".format(self.ticker,self.principal,self.split,self.avg,self.remain,self.already))
            
    #When profit go byond over 10%
    def sell_over(self) : 
        
        current_price = self.get_current_price()
        #selling point
        if current_price > self.avg*1.1 : 
            balance = self.upbit.get_balance(self.ticker)
            amount = self.upbit.get_amount(self.ticker)
            sell = balance * current_price
            profit = round(sell - amount)
            
            self.upbit.sell_market_order(self.ticker, balance)
            post_message(self.token, "#notice","[SELL]  {} {} at {} ({})".format('Over Sell',self.ticker,self.avg,str(datetime.now())[:-7]))
            post_message(self.token, "#notice","<<Debug>> {} {} {} {} {} {}".format(self.ticker,self.principal,self.split,self.avg,self.remain,self.already))
            post_message(self.token, "#notice","[RESULT]\nCoin : {}\nBuy : {}Won\nSell : {}Won\nProfit : {}Won".format(self.ticker,format(round(amount), ','),format(round(sell), ','),format(profit,',')))
            
            self.restart()
    
    #When 40 splits run out
    def sell_end(self) :
    
        current_price = self.get_current_price()
        
        # between +10% ~ -10% 
        if current_price < self.avg*1.1 and current_price > self.avg*0.9 : 
            balance = self.upbit.get_balance(self.ticker)
            amount = self.upbit.get_amount(self.ticker)
            sell = balance * current_price
            profit = round(sell - amount)
            
            self.upbit.sell_market_order(self.ticker, balance)
            post_message(self.token, "#notice","[SELL]  {} {} at {} ({})".format('End Sell',self.ticker,self.avg,str(datetime.now())[:-7]))
            post_message(self.token, "#notice","<<Debug>> {} {} {} {} {} {}".format(self.ticker,self.principal,self.split,self.avg,self.remain,self.already))
            post_message(self.token, "#notice","[RESULT]\nCoin : {}\nBuy : {}Won\nSell : {}Won\nProfit : {}Won".format(self.ticker,format(round(amount), ','),format(round(sell), ','),format(profit,',')))
            self.restart()
            return True
            
        # over -10%
        else : 
            post_message(self.token, "#notice","<<Debug>> {} {} {} {} {} {}".format(self.ticker,self.principal,self.split,self.avg,self.remain,self.already))
            post_message(self.token, "#notice","[RESULT]  Loss is over 10%. Try next one. ( {} )".format(str(datetime.now())[:-7]))
            return False
        
    def get_current_price(self) : 
        for _ in range(20) : 
            try : 
                price = pu.get_current_price(self.ticker)
            except : 
                price = 0
            if price : return price
        raise(Exception("Can't get the price from Upbit API"))
    
    def update_state(self, buy=True, half=False) : 
        self.avg = self.upbit.get_avg_buy_price(self.ticker)
        if buy : 
            self.remain -= self.split/2 if half else self.split
        else : 
            self.remain = self.principal - self.upbit.get_amount(self.ticker)
