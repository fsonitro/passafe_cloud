# Generated by Django 5.1.2 on 2024-11-04 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_customuser_mfa_enabled_customuser_mfa_secret'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='encryption_key',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='salt',
            field=models.TextField(blank=True, null=True),
        ),
    ]
