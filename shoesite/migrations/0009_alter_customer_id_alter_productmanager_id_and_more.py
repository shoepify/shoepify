# Generated by Django 4.2.16 on 2024-11-11 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoesite', '0008_customer_is_active_customer_username_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='productmanager',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='salesmanager',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
