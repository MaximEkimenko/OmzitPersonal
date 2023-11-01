import os
from datetime import datetime

from django.core.management.base import BaseCommand
import openpyxl

from timesheet.models import Employee


class Command(BaseCommand):
    help = "Создать базу табелей"

    def handle(self, *args, **options):
        pass


