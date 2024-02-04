# Generated by Django 5.0.1 on 2024-02-04 01:05

import datetime
from django.db import migrations, models


def migrate_interval(apps, schema_editor):
    Config = apps.get_model("posts", "Config")
    for config in Config.objects.all():
        config.interval = datetime.timedelta(
            hours=config.interval_hours, minutes=config.interval_minutes
        )
        config.save()


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0003_alter_config_options_post_error"),
    ]

    operations = [
        migrations.AddField(
            model_name="config",
            name="interval",
            field=models.DurationField(default=datetime.timedelta(days=1)),
        ),
        migrations.RunPython(migrate_interval),
        migrations.RemoveField(
            model_name="config",
            name="interval_hours",
        ),
        migrations.RemoveField(
            model_name="config",
            name="interval_minutes",
        ),
    ]
