from django.contrib import admin
from .models import UserInfo,TradePerCoin,TradeHistory

admin.site.register(UserInfo)
admin.site.register(TradePerCoin)
admin.site.register(TradeHistory)
# Register your models here.
