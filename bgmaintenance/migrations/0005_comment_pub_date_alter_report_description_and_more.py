# Generated by Django 5.0.2 on 2024-03-26 19:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bgmaintenance', '0004_alter_report_report_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='description',
            field=models.TextField(max_length=200),
        ),
        migrations.AlterField(
            model_name='report',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='report_type',
            field=models.CharField(choices=[('Toilet', 'TOILET'), ('Window', 'WINDOW'), ('Sink', 'SINK'), ('Other', 'OTHER')], max_length=20),
        ),
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(default='New', max_length=20),
        ),
    ]
