# Generated by Django 3.2.18 on 2023-04-13 23:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='DynamicModelField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('field_type', models.CharField(choices=[('string', 'string'), ('number', 'number'), ('boolean', 'boolean')], max_length=10)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.dynamicmodel')),
            ],
        ),
        migrations.DeleteModel(
            name='Card',
        ),
    ]