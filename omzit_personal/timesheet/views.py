import datetime
import locale
import logging

from django.views.generic.list import ListView

from timesheet.models import Timesheet

locale.setlocale(locale.LC_ALL, '')

logger = logging.getLogger("logger")


class TimesheetListView(ListView):
    now = datetime.datetime.now()
    now_month = datetime.datetime.now().month
    now_month_word = now.strftime('%B')

    queryset = Timesheet.objects.filter(date__month=now_month).order_by('date')
    template_name = "timesheet/ag_grid_template.html"

    def get_context_data(self, **kwargs):
        context = {}
        timesheets = dict()
        for timesheet in self.queryset:
            fio = timesheet.fio.fio
            timesheets[fio] = timesheets.get(
                fio,
                {
                    'employee': timesheet.fio,
                    'days': {},
                    'now_month': [self.now_month, self.now_month_word]
                })
            timesheets[fio]['days'].update({
                timesheet.date.day: [
                    timesheet.skud_day_duration if timesheet.skud_day_duration else 0,
                    timesheet.skud_night_duration if timesheet.skud_night_duration else 0,
                    timesheet
                ]
            })
        context["timesheets"] = list(timesheets.values())
        return context
