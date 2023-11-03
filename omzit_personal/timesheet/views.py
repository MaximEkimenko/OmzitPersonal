import datetime
import locale

import django_filters
from django.utils import timezone
from django.views.generic.list import ListView

from timesheet.filters import get_filterset
from timesheet.models import Timesheet

locale.setlocale(locale.LC_ALL, '')
class TimesheetListView(ListView):
    now = datetime.datetime.now()
    now_month = datetime.datetime.now().month
    now_month_word = now.strftime('%B')
    queryset = Timesheet.objects.filter(date__month=now_month).order_by('date')
    template_name = "timesheet/ag_grid_template.html"

    # paginate_by = 100

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = {}
        # filter = get_filterset(
        #     data=self.request.GET,
        #     queryset=self.queryset,
        #     fields=['fio__division', 'date']
        # )
        # filter.filter_fields.append('date__month')
        # filter.filters.update({'date__month': django_filters.DateFilter(field_name='date', lookup_expr='month')})
        # filter.filter_fields.append('date__year')
        # filter.filters.update({'date__year': django_filters.DateFilter(field_name='date', lookup_expr='year')})
        # context["filter"] = filter
        timesheets = dict()
        for timesheet in self.queryset:
            timesheets[timesheet.fio.fio] = timesheets.get(
                timesheet.fio.fio,
                {
                    'employee': timesheet.fio,
                    'days': {},
                    'now_month': [self.now_month, self.now_month_word]
                })
            timesheets[timesheet.fio.fio]['days'].update({
                timesheet.date.day:
                    [timesheet.skud_day_duration if timesheet.skud_day_duration else 0,
                    timesheet.skud_night_duration if timesheet.skud_night_duration else 0]
                    # timesheet

            })

        context["timesheets"] = list(timesheets.values())
        context["range"] = range(1, 32)
        print(context['timesheets'][0])
        print(self.queryset)
        return context
