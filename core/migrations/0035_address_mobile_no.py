# Generated by Django 5.0 on 2024-11-03 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_alter_cartorder_product_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='mobile_no',
            field=models.CharField(default='+254 712 345 678', max_length=20),
        ),
    ]