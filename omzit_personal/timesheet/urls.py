from django.urls import path, include

from timesheet.views import TimesheetListView

urlpatterns = [
    path('', TimesheetListView.as_view(), name="timesheets")
]
