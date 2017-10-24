from django.views.generic.base import ContextMixin

from marer.models import StaticPage, FinanceProductPage


class StaticPagesContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        static_pages = StaticPage.objects.all()
        kwargs.update(dict(static_pages=static_pages))
        return super().get_context_data(**kwargs)


class FinanceProductsRootsMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        finance_product_roots = FinanceProductPage.objects.root_nodes().filter(show_in_menu=True)
        kwargs.update(dict(finance_product_roots=finance_product_roots))
        return super().get_context_data(**kwargs)
