from django.utils import timezone
from django.views.generic.list import ListView

from timesheet.models import Timesheet


class ArticleListView(ListView):
    queryset = Timesheet
    # paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context