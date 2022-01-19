# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TradeHistory(models.Model):
    userid = models.OneToOneField('UserInfo', models.DO_NOTHING, db_column='UserID', primary_key=True)  # Field name made lowercase.
    histotry_ticker = models.CharField(max_length=40)
    history_buy_or_sell = models.IntegerField()
    history_coin_price = models.DecimalField(max_digits=20, decimal_places=10)
    history_amount = models.IntegerField()
    history_my_price_before = models.DecimalField(max_digits=20, decimal_places=10)
    history_my_price_after = models.DecimalField(max_digits=20, decimal_places=10)
    history_execution_time = models.IntegerField()
    history_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'trade_history'


class TradePerCoin(models.Model):
    userid = models.OneToOneField('UserInfo', models.DO_NOTHING, db_column='UserID', primary_key=True)  # Field name made lowercase.
    ticker = models.CharField(max_length=40)
    principal = models.IntegerField()
    split = models.IntegerField()
    average = models.DecimalField(max_digits=20, decimal_places=10)
    execution_count = models.IntegerField()
    already = models.IntegerField()
    remain = models.IntegerField()
    recent_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'trade_per_coin'


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