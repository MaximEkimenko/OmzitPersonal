from django.urls import path

from timesheet.views import TimesheetListView

urlpatterns = [
    path('', TimesheetListView.as_view(), name="timesheets")
]
