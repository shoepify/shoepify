# Generated by Django 5.1.3 on 2024-11-25 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoesite', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('Processing', 'Processing'), ('In-Transit', 'In-Transit'), ('Delivered', 'Delivered')], default=None, max_length=20, null=True),
        ),
    ]
