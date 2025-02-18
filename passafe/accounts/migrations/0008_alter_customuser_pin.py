# Generated by Django 5.1.2 on 2024-11-15 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_customuser_pin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='pin',
            field=models.CharField(help_text='8-digit PIN for multi-factor authentication', max_length=128),
        ),
    ]
