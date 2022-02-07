from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserInfo,TradePerCoin,TradeHistory,PriceLog,AccountState
from django.contrib.auth import get_user

def index(request) : 
    print(request.user)
    if request.user.is_authenticated : 
        print("하이하이", get_user(request))
        user = UserInfo.objects.get(id=get_user(request))
        account_state = AccountState.objects.get(userid=user)
        context = {'account_state' : account_state}
        return render(request, 'polls/manage.html', context)
    else : 
        return redirect('common/login')


# Create your views here.
