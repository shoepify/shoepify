# Generated by Django 4.2.16 on 2024-11-11 18:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoesite', '0011_alter_customer_id_alter_productmanager_id_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
