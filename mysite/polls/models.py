# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class AccountState(models.Model):
    userid = models.OneToOneField('UserInfo', models.DO_NOTHING, db_column='UserID', primary_key=True)  # Field name made lowercase.
    total_balance = models.IntegerField()
    total_deposit = models.IntegerField()
    total_buy = models.IntegerField()
    total_cash = models.IntegerField()
    sell_count = models.IntegerField()
    total_profit = models.IntegerField()
    total_profit_percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'account_state'

class TradeHistory(models.Model):
    userid = models.ForeignKey('UserInfo', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.        
    histotry_ticker = models.CharField(max_length=40)
    history_buy_or_sell = models.IntegerField()
    history_coin_price = models.DecimalField(max_digits=20, decimal_places=10)
    history_amount = models.IntegerField()
    history_execution_time = models.IntegerField()
    history_date = models.DateTimeField()
    history_done = models.IntegerField()
    history_my_average = models.DecimalField(max_digits=20, decimal_places=10)
    history_profit = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'trade_history'



class UserInfo(models.Model):
    userid = models.IntegerField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    id = models.CharField(max_length=40)
    password = models.CharField(max_length=40)
    upbit_secret_key = models.CharField(max_length=255)
    upbit_access_key = models.CharField(max_length=255)
    slack_token = models.CharField(max_length=255)
    admin = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_info'
        
class PriceLog(models.Model):
    log_seq = models.AutoField(primary_key=True)
    log_ticker = models.CharField(max_length=40)
    log_price = models.DecimalField(max_digits=20, decimal_places=10)
    log_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'price_log'
        
class TradePerCoin(models.Model):
    userid = models.ForeignKey('UserInfo', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.
    ticker = models.CharField(max_length=40)
    principal = models.IntegerField()
    split = models.IntegerField()
    average = models.DecimalField(max_digits=20, decimal_places=10)
    execution_count = models.IntegerField()
    already = models.IntegerField()
    remain = models.IntegerField()
    recent_update = models.DateTimeField()
    ticker_name = models.CharField(max_length=40)
    coin_profit = models.IntegerField()
    coin_profit_percent = models.DecimalField(max_digits=5, decimal_places=3)

    class Meta:
        managed = False
        db_table = 'trade_per_coin'