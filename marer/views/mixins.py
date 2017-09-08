from django.views.generic.base import ContextMixin

from marer.models import StaticPage


class StaticPagesContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        static_pages = StaticPage.objects.all()
        kwargs.update(dict(static_pages=static_pages))
        return super().get_context_data(**kwargs)
