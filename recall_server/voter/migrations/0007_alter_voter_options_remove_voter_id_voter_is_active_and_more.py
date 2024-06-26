# Generated by Django 5.0.6 on 2024-06-26 16:33

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("voter", "0006_alter_voter_password"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="voter",
            options={"ordering": ("-updated_at", "-created_at")},
        ),
        migrations.RemoveField(
            model_name="voter",
            name="id",
        ),
        migrations.AddField(
            model_name="voter",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="voter",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="voter",
            name="password",
            field=models.CharField(
                default="pbkdf2_sha256$720000$w7y9GxBQ37mFmxxz6p05lD$UsQsZhUSgyjwYNE8PlmOLAxUBpZ7SvUyoD8JqumKzIQ=",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="voter",
            name="tokenized_id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
