# Generated migration for tenants app
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='tenants/logos/')),
                ('primary_color', models.CharField(default='#4F46E5', max_length=7)),
                ('secondary_color', models.CharField(default='#10B981', max_length=7)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('contact_phone', models.CharField(blank=True, max_length=20)),
                ('address', models.TextField(blank=True)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=10.0, help_text='Tax rate in percentage', max_digits=5)),
                ('service_charge_rate', models.DecimalField(decimal_places=2, default=5.0, help_text='Service charge rate in percentage', max_digits=5)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'tenants',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Outlet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('province', models.CharField(max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=10)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('operating_hours', models.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tenant', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='outlets', to='tenants.tenant')),
            ],
            options={
                'db_table': 'outlets',
                'ordering': ['name'],
            },
        ),
        migrations.AddConstraint(
            model_name='outlet',
            constraint=models.UniqueConstraint(fields=('tenant', 'slug'), name='unique_tenant_outlet_slug'),
        ),
    ]
