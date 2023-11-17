from django.db import models


class Employee(models.Model):
    """ Сотрудник """
    objects = models.Manager()

    # TODO Убрать unique=True когда будет синхронизация с 1С
    fio = models.CharField(unique=True, max_length=255, verbose_name="ФИО", db_index=True)

    employment_date = models.DateField(null=True, blank=True, verbose_name="Дата приема на работу")
    fired_date = models.DateField(null=True, blank=True, verbose_name="Дата увольнения")
    job_title = models.CharField(max_length=255, verbose_name="Должность")
    rank_title = models.CharField(null=True, blank=True, max_length=50, verbose_name="Разряд")
    tariff_rate = models.PositiveSmallIntegerField(verbose_name="Тарифная ставка")  # 0 to 32767

    # TODO Убрать null=True, blank=True когда будет синхронизация с 1С
    # 0 to 9223372036854775807 PositiveBigIntegerField
    id_1C = models.PositiveBigIntegerField(null=True, blank=True, unique=True, verbose_name="id записи 1C")

    division = models.CharField(max_length=255, verbose_name="Отдел")

    # TODO Вынести в отдельную модель?
    # (уволен, работает, внештатный и т.д.)
    status = models.CharField(null=True, blank=True, max_length=50, verbose_name="Статус")

    # TODO Вынести в отдельную модель?
    # (2/2, 5/7, и т.д)
    schedule = models.CharField(null=True, blank=True, max_length=50, verbose_name="График работы")

    # 0 to 32767 PositiveSmallIntegerField
    shift_hours = models.PositiveSmallIntegerField(verbose_name="Продолжительность смены")

    # TODO Вынести в отдельную модель?
    skud_access = models.CharField(default='Турникет', max_length=255, verbose_name="Точка доступа СКУД")

    day_start = models.TimeField(verbose_name="Плановое время начала рабочего дня")

    # TODO Вынести в отдельную модель?
    boss = models.CharField(null=True, blank=True, max_length=255, verbose_name="ФИО руководителя")

    # TODO Вынести в отдельную модель?
    KTR_category = models.CharField(null=True, blank=True, max_length=50, verbose_name="Категория тарифной ставки")

    KTR = models.DecimalField(default=0, max_digits=3, decimal_places=2, verbose_name="Коэффициент тарифной ставки")
    has_NAX = models.BooleanField(default=False, verbose_name="Наличие НАКС")
    KNAX = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name="Коэффициент НАКС")

    def __str__(self):
        return f"{self.fio}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["fio"]


class Timesheet(models.Model):
    """ Модель табеля сотрудника """
    objects = models.Manager()
    fio = models.ForeignKey(
        "Employee", on_delete=models.PROTECT, related_name="timesheet", verbose_name="ФИО сотрудника",
    )

    # (больничный, отпуск, явка, прогул и т.д. в виде обозначений)
    day_status = models.ForeignKey(
        'DayStatus',
        on_delete=models.PROTECT,
        related_name="timesheet",
        null=True, blank=True,
        verbose_name="Статус на день"
    )
    date = models.DateField(verbose_name="Дата")
    skud_day_start_1 = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Вход"
    )
    skud_day_end_1 = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Выход"
    )

    skud_day_duration = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Длительность дневной смены по СКУД"
    )

    skud_night_duration = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Длительность ночной смены по СКУД"
    )

    boss_day_duration = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Длительность дневной смены по данным руководителя"
    )
    is_day_corrected = models.BooleanField(default=False, verbose_name="Выполнена корректировка дневной смены")

    boss_night_duration = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Длительность ночной смены по данным руководителя"
    )
    is_night_corrected = models.BooleanField(default=False, verbose_name="Выполнена корректировка ночной смены")

    skud_error = models.BooleanField(default=False, verbose_name="Ошибка входа/выхода по данным СКУД")

    skud_error_query = models.TextField(null=True, blank=True, verbose_name="Запрос на детализацию в БД СКУД")

    def __str__(self):
        return f"{self.fio}-{self.date.strftime('%d.%m.%Y')}"

    class Meta:
        verbose_name = "Табель"
        verbose_name_plural = "Табели"
        ordering = ["date"]
        unique_together = ["fio", "date"]

    def save(self, *args, **kwargs):
        self.is_day_corrected = True if self.boss_day_duration else False
        self.is_night_corrected = True if self.boss_night_duration else False
        super().save(*args, **kwargs)


class DayStatus(models.Model):
    """ Модель статуса сотрудника на день """
    objects = models.Manager()
    symbol = models.CharField(unique=True, max_length=2, verbose_name="Статус")
    name = models.CharField(max_length=255, verbose_name="Расшифровка статуса")

    def __str__(self):
        return f"{self.symbol}-{self.name}"

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
