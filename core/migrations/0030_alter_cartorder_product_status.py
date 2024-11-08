# Generated by Django 5.0 on 2024-11-01 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_alter_cartorder_options_alter_cartorder_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartorder',
            name='product_status',
            field=models.CharField(choices=[('process', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered')], default='process', max_length=30),
        ),
    ]
