import datetime

import django_filters
from django.utils import timezone
from django.views.generic.list import ListView

from timesheet.filters import get_filterset
from timesheet.models import Timesheet


class TimesheetListView(ListView):
    queryset = Timesheet.objects.order_by('fio__fio')
    template_name = "timesheet/timesheet.html"

    # paginate_by = 100

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = {}
        filter = get_filterset(
            data=self.request.GET,
            queryset=self.queryset,
            fields=['fio__division', 'date']
        )
        filter.filter_fields.append('date__month')
        filter.filters.update({'date__month': django_filters.DateFilter(field_name='date', lookup_expr='month')})
        filter.filter_fields.append('date__year')
        filter.filters.update({'date__year': django_filters.DateFilter(field_name='date', lookup_expr='year')})
        context["filter"] = filter
        timesheets = dict()
        for timesheet in filter.qs:
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
                    timesheet
                ]
            })
        context["timesheets"] = list(timesheets.values())
        context["range"] = range(1, 32)

        return context
