# Generated by Django 5.0 on 2024-11-02 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_alter_cartorder_product_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartorder',
            name='product_status',
            field=models.CharField(choices=[('processing', 'Processing'), ('shipped', 'Shipped'), ('Delivered', 'Delivered')], default='processing', max_length=30),
        ),
    ]
