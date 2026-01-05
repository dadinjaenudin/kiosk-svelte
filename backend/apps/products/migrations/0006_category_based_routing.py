# Generated migration for Category-Based Routing

from django.db import migrations, models


def set_default_routing(apps, schema_editor):
    """Set default routing for existing categories"""
    Category = apps.get_model('products', 'Category')
    
    # Set BEVERAGE for drink categories
    Category.objects.filter(
        models.Q(name__icontains='beverage') |
        models.Q(name__icontains='drink') |
        models.Q(name__icontains='coffee') |
        models.Q(name__icontains='tea') |
        models.Q(name__icontains='juice')
    ).update(kitchen_station_code='BEVERAGE')
    
    # Set DESSERT for dessert categories
    Category.objects.filter(
        models.Q(name__icontains='dessert') |
        models.Q(name__icontains='ice') |
        models.Q(name__icontains='cake') |
        models.Q(name__icontains='sweet')
    ).update(kitchen_station_code='DESSERT')
    
    # Ensure all others are MAIN
    Category.objects.filter(kitchen_station_code='').update(kitchen_station_code='MAIN')


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_product_kitchen_station'),
    ]

    operations = [
        # Step 1: Add kitchen_station_code to categories
        migrations.AddField(
            model_name='category',
            name='kitchen_station_code',
            field=models.CharField(
                default='MAIN',
                help_text='Auto-route products in this category to kitchen station (e.g., MAIN, BEVERAGE, GRILL, DESSERT)',
                max_length=20
            ),
        ),
        
        # Step 3: Add kitchen_station_code_override to products
        migrations.AddField(
            model_name='product',
            name='kitchen_station_code_override',
            field=models.CharField(
                blank=True,
                help_text='Override category default routing (e.g., MAIN, BEVERAGE, GRILL). Leave blank to use category default.',
                max_length=20,
                null=True
            ),
        ),
        
        # Step 4: Remove outlet_id from products (if exists)
        migrations.RemoveField(
            model_name='product',
            name='outlet',
        ),
        
        # Step 4: Remove kitchen_station FK from products
        migrations.RemoveField(
            model_name='product',
            name='kitchen_station',
        ),
        
        # Run data migration to set default routing
        migrations.RunPython(set_default_routing, migrations.RunPython.noop),
    ]
