# Generated by Django 4.2.6 on 2023-11-02 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0008_remove_timesheet_skud_night_end_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='fio',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='ФИО'),
        ),
    ]
