# Generated by Django 4.0.2 on 2022-02-27 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_order_date_time_alter_product_stock'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderdetail',
            old_name='cuantity',
            new_name='quantity',
        ),
    ]
