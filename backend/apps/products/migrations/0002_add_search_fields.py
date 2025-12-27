# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_popular',
            field=models.BooleanField(default=False, help_text='Popular/Bestseller item'),
        ),
        migrations.AddField(
            model_name='product',
            name='has_promo',
            field=models.BooleanField(default=False, help_text='Item has active promotion'),
        ),
        migrations.AddField(
            model_name='product',
            name='promo_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Promotional price', max_digits=10, null=True),
        ),
    ]
