# Generated by Django 3.1.2 on 2022-01-19 10:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('userid', models.IntegerField(db_column='UserID', primary_key=True, serialize=False)),
                ('id', models.CharField(max_length=40)),
                ('password', models.CharField(max_length=40)),
                ('upbit_secret_key', models.CharField(max_length=255)),
                ('upbit_access_key', models.CharField(max_length=255)),
                ('slack_token', models.CharField(max_length=255)),
                ('admin', models.IntegerField()),
            ],
            options={
                'db_table': 'user_info',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TradeHistory',
            fields=[
                ('userid', models.OneToOneField(db_column='UserID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='polls.userinfo')),
                ('histotry_ticker', models.CharField(max_length=40)),
                ('history_buy_or_sell', models.IntegerField()),
                ('history_coin_price', models.DecimalField(decimal_places=10, max_digits=20)),
                ('history_amount', models.IntegerField()),
                ('history_my_price_before', models.DecimalField(decimal_places=10, max_digits=20)),
                ('history_my_price_after', models.DecimalField(decimal_places=10, max_digits=20)),
                ('history_execution_time', models.IntegerField()),
                ('history_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'trade_history',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TradePerCoin',
            fields=[
                ('userid', models.OneToOneField(db_column='UserID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='polls.userinfo')),
                ('ticker', models.CharField(max_length=40)),
                ('principal', models.IntegerField()),
                ('split', models.IntegerField()),
                ('average', models.DecimalField(decimal_places=10, max_digits=20)),
                ('execution_count', models.IntegerField()),
                ('already', models.IntegerField()),
                ('remain', models.IntegerField()),
                ('recent_update', models.DateTimeField()),
            ],
            options={
                'db_table': 'trade_per_coin',
                'managed': False,
            },
        ),
    ]
