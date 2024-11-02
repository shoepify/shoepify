# Generated by Django 4.2.16 on 2024-11-02 18:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "customer_id",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=100)),
                ("tax_id", models.CharField(max_length=20, unique=True)),
                ("email", models.EmailField(max_length=100)),
                ("password", models.CharField(max_length=100)),
                ("home_address", models.CharField(max_length=255)),
                ("billing_address", models.CharField(max_length=255)),
                ("phone_number", models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("order_id", models.AutoField(primary_key=True, serialize=False)),
                ("order_date", models.DateField()),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "discount_applied",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("payment_status", models.CharField(max_length=50)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.customer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("product_id", models.AutoField(primary_key=True, serialize=False)),
                ("model", models.CharField(max_length=100)),
                ("serial_number", models.CharField(max_length=100)),
                ("stock", models.IntegerField()),
                ("inventory_to_stock", models.IntegerField()),
                ("warranty_status", models.CharField(max_length=50)),
                ("distributor_info", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="ProductManager",
            fields=[
                ("manager_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=100)),
                ("phone_number", models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name="SalesManager",
            fields=[
                ("manager_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=100)),
                ("phone_number", models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name="Wishlist",
            fields=[
                ("wishlist_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.customer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                ("cart_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.customer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Rating",
            fields=[
                ("rating_id", models.AutoField(primary_key=True, serialize=False)),
                ("rating_value", models.IntegerField()),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.customer",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("order_item_id", models.AutoField(primary_key=True, serialize=False)),
                ("quantity", models.IntegerField()),
                (
                    "price_per_item",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shoesite.order"
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("invoice_id", models.AutoField(primary_key=True, serialize=False)),
                ("invoice_date", models.DateField()),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shoesite.order"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Discount",
            fields=[
                ("discount_id", models.AutoField(primary_key=True, serialize=False)),
                ("discount_name", models.CharField(max_length=100)),
                (
                    "discount_amount",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Delivery",
            fields=[
                ("delivery_id", models.AutoField(primary_key=True, serialize=False)),
                ("delivery_status", models.CharField(max_length=50)),
                ("delivery_address", models.CharField(max_length=255)),
                ("delivery_date", models.DateField()),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shoesite.order"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("comment_id", models.AutoField(primary_key=True, serialize=False)),
                ("comment", models.TextField()),
                ("approval_status", models.CharField(max_length=50)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.customer",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("cart_item_id", models.AutoField(primary_key=True, serialize=False)),
                ("quantity", models.IntegerField()),
                (
                    "cart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.shoppingcart",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shoesite.product",
                    ),
                ),
            ],
        ),
    ]
