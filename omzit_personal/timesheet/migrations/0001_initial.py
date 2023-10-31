# Generated by Django 4.2.6 on 2023-10-31 08:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DayStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=2, verbose_name='Статус')),
                ('name', models.CharField(max_length=255, verbose_name='Расшифровка статуса')),
            ],
            options={
                'verbose_name': 'Статус',
                'verbose_name_plural': 'Статусы',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fio', models.CharField(max_length=255, verbose_name='ФИО')),
                ('employment_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата приема на работу')),
                ('fired_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата увольнения')),
                ('job_title', models.CharField(max_length=255, verbose_name='Должность')),
                ('rank_title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Разряд')),
                ('tariff_rate', models.PositiveSmallIntegerField(verbose_name='Тарифная ставка')),
                ('id_1C', models.PositiveBigIntegerField(blank=True, null=True, unique=True, verbose_name='id записи 1C')),
                ('division', models.CharField(max_length=255, verbose_name='Отдел')),
                ('status', models.CharField(max_length=50, verbose_name='Статус')),
                ('schedule', models.CharField(max_length=50, verbose_name='График работы')),
                ('shift_hours', models.PositiveSmallIntegerField(verbose_name='Продолжительность смены')),
                ('skud_access', models.CharField(default='Турникет', max_length=255, verbose_name='Точка доступа СКУД')),
                ('day_start', models.DateTimeField(verbose_name='Плановое время начала рабочего дня')),
                ('boss', models.CharField(max_length=255, verbose_name='ФИО руководителя')),
                ('KTR_category', models.CharField(max_length=50, verbose_name='Категория тарифной ставки')),
                ('KTR', models.DecimalField(decimal_places=2, max_digits=3, verbose_name='Коэффициент тарифной ставки')),
                ('has_NAX', models.BooleanField(verbose_name='Наличие НАКС')),
                ('KNAX', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='Коэффициент НАКС')),
            ],
            options={
                'verbose_name': 'Сотрудник',
                'verbose_name_plural': 'Сотрудники',
            },
        ),
        migrations.CreateModel(
            name='Timesheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Дата')),
                ('skud_day_start', models.DateTimeField(blank=True, null=True, verbose_name='Начало работы по СКУД')),
                ('skud_day_end', models.DateTimeField(blank=True, null=True, verbose_name='Окончание  работы по СКУД')),
                ('skud_day_duration', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Длительность работы по СКУД')),
                ('boss_day_duration', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Длительность работы по данным руководителя')),
                ('skud_night_start', models.DateTimeField(blank=True, null=True, verbose_name='Начало работы в ночь по СКУД')),
                ('skud_night_end', models.DateTimeField(blank=True, null=True, verbose_name='Окончание  работы в ночь по СКУД')),
                ('skud_night_duration', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Длительность работы в ночь по СКУД')),
                ('boss_night_duration', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Длительность работы в ночь по данным руководителя')),
                ('is_day_corrected', models.BooleanField(default=False, verbose_name='Корректировка день')),
                ('is_night_corrected', models.BooleanField(default=False, verbose_name='Корректировка ночь')),
                ('day_status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='timesheet', to='timesheet.daystatus', verbose_name='Статус на день')),
                ('fio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='timesheet', to='timesheet.employee', verbose_name='ФИО сотрудника')),
            ],
            options={
                'verbose_name': 'Табель',
                'verbose_name_plural': 'Табели',
                'ordering': ['-date'],
            },
        ),
    ]
