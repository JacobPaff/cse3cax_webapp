# Generated by Django 5.0.7 on 2024-08-13 02:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("admin_user_input", "0002_remove_role_role_name_alter_role_role_id"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="userprofile",
            table="user_profile",
        ),
    ]