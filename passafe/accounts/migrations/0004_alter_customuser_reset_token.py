# Generated by Django 5.1.2 on 2024-10-31 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_customuser_reset_token_customuser_token_expiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='reset_token',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
