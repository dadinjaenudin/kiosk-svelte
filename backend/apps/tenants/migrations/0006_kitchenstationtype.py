# Generated migration for KitchenStationType

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0005_kitchenstation'),
    ]

    operations = [
        # Create KitchenStationType table
        migrations.CreateModel(
            name='KitchenStationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Display name (e.g., "Main Kitchen", "Grill Station")', max_length=100)),
                ('code', models.CharField(db_index=True, help_text='Unique code (e.g., "MAIN", "GRILL", "BEVERAGE")', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text='Icon name or emoji (e.g., "🍳", "☕", "🍔")', max_length=50)),
                ('color', models.CharField(default='#FF6B35', help_text='Hex color code for UI display', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('is_global', models.BooleanField(default=False, help_text='Global types are available to all tenants')),
                ('sort_order', models.IntegerField(default=0, help_text='Display order (lower number = first)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tenant', models.ForeignKey(blank=True, help_text='Leave empty for global types available to all tenants', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kitchen_station_types', to='tenants.tenant')),
            ],
            options={
                'db_table': 'kitchen_station_types',
                'ordering': ['sort_order', 'name'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='kitchenstationtype',
            index=models.Index(fields=['code', 'is_active'], name='kitchen_sta_code_idx'),
        ),
        migrations.AddIndex(
            model_name='kitchenstationtype',
            index=models.Index(fields=['tenant', 'is_active'], name='kitchen_sta_tenant_idx'),
        ),
        
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='kitchenstationtype',
            unique_together={('tenant', 'code')},
        ),
    ]
