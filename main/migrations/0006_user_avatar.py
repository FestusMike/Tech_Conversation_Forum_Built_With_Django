# Generated by Django 4.2.6 on 2023-12-03 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_message_id_alter_room_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='avatar.svg', null=True, upload_to=''),
        ),
    ]
