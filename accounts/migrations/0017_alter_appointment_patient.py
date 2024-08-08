# Generated by Django 5.0.7 on 2024-08-08 14:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0016_alter_appointment_patient"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="patient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments_as_patient",
                to="accounts.patient",
            ),
        ),
    ]
