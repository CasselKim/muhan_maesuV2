# Generated by Django 3.1.2 on 2022-02-07 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceLog',
            fields=[
                ('log_seq', models.AutoField(primary_key=True, serialize=False)),
                ('log_ticker', models.CharField(blank=True, max_length=40, null=True)),
                ('log_price', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
            ],
            options={
                'db_table': 'price_log',
                'managed': False,
            },
        ),
    ]
