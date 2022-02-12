from urllib.request import Request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserInfo,TradePerCoin,TradeHistory,PriceLog,AccountState
from django.contrib.auth import get_user
from django.core import serializers


def index(request) : 
    if request.user.is_authenticated : 
        user = UserInfo.objects.get(id=get_user(request))
        account_state = AccountState.objects.get(userid=user)
        trade_per_coin = TradePerCoin.objects.filter(userid=user)
        context = {'account_state' : account_state, 'trade_per_coin':trade_per_coin}
        return render(request, 'polls/manage.html', context)
    else : 
        return redirect('common/login')
    
def googlechart(request) : 
    ticker = request.GET['ticker']
    logs = PriceLog.objects.filter(log_ticker=ticker).order_by('log_date')
    log_list = serializers.serialize('json', logs)
    return HttpResponse(log_list, content_type="text/json")


# Create your views here.
