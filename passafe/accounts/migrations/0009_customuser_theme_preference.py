# Generated by Django 5.1.2 on 2025-01-11 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_customuser_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='theme_preference',
            field=models.CharField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light', max_length=10),
        ),
    ]
