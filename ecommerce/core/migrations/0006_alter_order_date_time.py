# Generated by Django 4.0.2 on 2022-03-01 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_orderdetail_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_time',
            field=models.DateTimeField(),
        ),
    ]
