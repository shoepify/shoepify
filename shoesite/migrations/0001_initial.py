# Generated by Django 5.1.3 on 2024-11-19 18:04

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('tax_id', models.CharField(max_length=50, unique=True)),
                ('email', models.EmailField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('home_address', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('discount_id', models.AutoField(primary_key=True, serialize=False)),
                ('discount_name', models.CharField(max_length=100)),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=4)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('guest_id', models.AutoField(primary_key=True, serialize=False)),
                ('session_id', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductManager',
            fields=[
                ('manager_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SalesManager',
            fields=[
                ('manager_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_date', models.DateField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_applied', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(max_length=50)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('invoice_id', models.AutoField(primary_key=True, serialize=False)),
                ('invoice_date', models.DateField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shoesite.order')),
            ],
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('delivery_id', models.AutoField(primary_key=True, serialize=False)),
                ('delivery_status', models.CharField(max_length=50)),
                ('delivery_address', models.CharField(max_length=255)),
                ('delivery_date', models.DateField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.order')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('model', models.CharField(max_length=100)),
                ('serial_number', models.CharField(max_length=100)),
                ('stock', models.IntegerField()),
                ('inventory_to_stock', models.IntegerField()),
                ('warranty_status', models.CharField(max_length=50)),
                ('distributor_info', models.CharField(max_length=100)),
                ('description', models.TextField(default='No description available')),
                ('category', models.CharField(default='Uncategorized', max_length=100)),
                ('base_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('popularity_score', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('avg_rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('discount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='shoesite.discount')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('order_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('price_per_item', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.product')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.AutoField(primary_key=True, serialize=False)),
                ('comment', models.TextField()),
                ('approval_status', models.CharField(max_length=50)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.product')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('rating_id', models.AutoField(primary_key=True, serialize=False)),
                ('rating_value', models.IntegerField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.product')),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('refund_id', models.AutoField(primary_key=True, serialize=False)),
                ('request_date', models.DateField(default=django.utils.timezone.now)),
                ('approval_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=50)),
                ('refunded_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.orderitem')),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('cart_id', models.AutoField(primary_key=True, serialize=False)),
                ('owner_object_id', models.PositiveIntegerField()),
                ('owner_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('cart_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.product')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.shoppingcart')),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('wishlist_id', models.AutoField(primary_key=True, serialize=False)),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shoesite.customer')),
            ],
        ),
        migrations.CreateModel(
            name='WishlistItem',
            fields=[
                ('wishlist_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.product')),
                ('wishlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoesite.wishlist')),
            ],
        ),
    ]
