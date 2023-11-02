import datetime

from django.utils import timezone
from django.views.generic.list import ListView

from timesheet.models import Timesheet


class TimesheetListView(ListView):
    queryset = Timesheet.objects.filter(
        date__year=2023,
        date__month=11
    )
    template_name = "timesheet/timesheet.html"

    # paginate_by = 100

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = {}
        timesheets = dict()
        for timesheet in self.queryset:
            timesheets[timesheet.fio.fio] = timesheets.get(
                timesheet.fio.fio,
                {
                    'employee': timesheet.fio,
                    'days': {}
                })
            timesheets[timesheet.fio.fio]['days'].update({
                timesheet.date.day: [
                    timesheet.skud_day_duration,
                    timesheet.skud_night_duration,
                ]
            })
        context["timesheets"] = list(timesheets.values())
        context["range"] = range(1, 32)
        print(context)
        return context
