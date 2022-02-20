from django.contrib import admin
from .models import UserInfo,TradePerCoin,TradeHistory,PriceLog,AccountState,AccessKey

admin.site.register(UserInfo)
admin.site.register(TradePerCoin)
admin.site.register(TradeHistory)
admin.site.register(PriceLog)
admin.site.register(AccountState)
admin.site.register(AccessKey)
# Register your models here.
