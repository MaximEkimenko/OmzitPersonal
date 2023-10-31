import os
from datetime import datetime

from django.core.management.base import BaseCommand
import openpyxl

from timesheet.models import Employee


class Command(BaseCommand):
    help = "Создать базу сотрудников из файла Excel"

    def handle(self, *args, **options):
        ex_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "База ФИО(OmzitZP).xlsx")
        ex_wb = openpyxl.load_workbook(ex_file_path, data_only=True)
        excel_list = 'База ФИО'
        ex_sh = ex_wb[excel_list.strip()]

        employees = []
        for i, row in enumerate(ex_sh.iter_rows(
                min_row=2,
                min_col=1,
                values_only=True
        )):
            # print(
            #     f"fio={row[0].strip()}"
            #     f"job_title={row[1][:(row[1].find('Ц'))].strip()}"
            #     f"division={row[1][(row[1].find('Ц')):].strip()}"
            #     f"rank_title={row[2]}"
            #     f"tariff_rate={int(row[3])}"
            #     f"employment_date={row[4]}"
            #     f"shift_hours=10"
            #     f"day_start='08:00:00'"
            #     f"KTR_category={row[5] if row[5] != '' else None}"
            #     f"KTR={row[6] if row[6] != 0 else None}"
            #     f"has_NAX={False if row[7] == 0 else True}"
            #     f"KNAX={row[7] if row[7] != 0 else None}"
            # )
            date = row[4]
            if isinstance(date, str):
                date = datetime.strptime(date, "%d.%m.%Y")
            employee = Employee(
                fio=row[0].strip(),
                job_title=row[1][:(row[1].find('Ц'))].strip(),
                division=row[1][(row[1].find('Ц')):].strip(),
                rank_title=row[2],
                tariff_rate=int(row[3]),
                employment_date=date,
                shift_hours=10,
                day_start='08:00:00',
                KTR_category=row[5] if row[5] != '' else None,
                KTR=row[6] if row[6] != 0 else 0,
                has_NAX=False if row[7] == 0 else True,
                KNAX=row[7] if row[7] != 0 else None,
            )
            employees.append(employee)
        Employee.objects.bulk_create(employees)


