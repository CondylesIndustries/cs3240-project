# Generated by Django 5.0.2 on 2024-04-11 05:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bgmaintenance', '0009_alter_report_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 11, 1, 13, 12, 295086, tzinfo=datetime.timezone.utc)),
        ),
    ]
