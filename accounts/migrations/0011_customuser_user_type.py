# Generated by Django 5.0.7 on 2024-08-01 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_remove_customuser_user_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="user_type",
            field=models.CharField(
                choices=[("patient", "Patient"), ("doctor", "Doctor")],
                default="doctor",
                max_length=10,
            ),
        ),
    ]
