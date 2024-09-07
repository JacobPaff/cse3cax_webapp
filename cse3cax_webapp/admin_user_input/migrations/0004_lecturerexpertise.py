# Generated by Django 5.0.7 on 2024-09-06 23:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_user_input", "0003_alter_userprofile_table"),
    ]

    operations = [
        migrations.CreateModel(
            name="LecturerExpertise",
            fields=[
                ("expertise_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="admin_user_input.subject",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="admin_user_input.userprofile",
                    ),
                ),
            ],
            options={
                "db_table": "lecturer_expertise",
                "managed": True,
                "unique_together": {("subject", "user")},
            },
        ),
    ]
