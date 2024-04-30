# Generated by Django 5.0.2 on 2024-03-26 17:40

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bgmaintenance', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='file',
        ),
        migrations.AddField(
            model_name='report',
            name='status',
            field=models.CharField(choices=[('Resolved', 'RESOLVED'), ('New', 'NEW'), ('In progress', 'IN PROGRESS')], default='New', max_length=20),
        ),
        migrations.AlterField(
            model_name='report',
            name='description',
            field=models.TextField(max_length=200),
        ),
        migrations.AlterField(
            model_name='report',
            name='pub_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='report',
            name='report_type',
            field=models.CharField(choices=[('Toilet', 'TOILET'), ('Window', 'WINDOW'), ('Sink', 'SINK')], max_length=20),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('comment_text', models.CharField(max_length=200)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bgmaintenance.report')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='files/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'txt'])])),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bgmaintenance.report')),
            ],
        ),
    ]