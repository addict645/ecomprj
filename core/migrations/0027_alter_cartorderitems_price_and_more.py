# Generated by Django 5.0 on 2024-11-01 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_delete_filterpreference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartorderitems',
            name='price',
            field=models.DecimalField(decimal_places=2, default='0.99', max_digits=15),
        ),
        migrations.AlterField(
            model_name='cartorderitems',
            name='total',
            field=models.DecimalField(decimal_places=2, default='0.99', max_digits=15),
        ),
    ]
