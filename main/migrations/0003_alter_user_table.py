# Generated by Django 4.2.6 on 2023-11-30 09:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_remove_user_name_alter_user_username'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='user',
            table='Users_Table',
        ),
    ]
