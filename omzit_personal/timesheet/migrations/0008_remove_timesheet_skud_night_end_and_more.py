# Generated by Django 4.2.6 on 2023-11-02 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0007_remove_timesheet_skud_day_end_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timesheet',
            name='skud_night_end',
        ),
        migrations.RemoveField(
            model_name='timesheet',
            name='skud_night_start',
        ),
        migrations.AddField(
            model_name='timesheet',
            name='skud_night_end_1',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Окончание ночной смены по СКУД (интервал 1)'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='skud_night_end_2',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Окончание ночной смены по СКУД (интервал 2)'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='skud_night_start_1',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Начало ночной смены по СКУД (интервал 1)'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='skud_night_start_2',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Начало ночной смены по СКУД (интервал 2)'),
        ),
    ]
