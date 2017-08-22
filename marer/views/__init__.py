from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from marer.forms import QuickRequestForm
from marer.models import FinanceProduct


class IndexView(TemplateView):
    template_name = 'marer/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.id:
            quick_request_form = QuickRequestForm(initial=dict(
                contact_person_name=request.user.get_full_name(),
                contact_email=request.user.email,
                contact_phone=request.user.phone,
            ))
            quick_request_form.fields['contact_person_name'].disabled = True
            quick_request_form.fields['contact_email'].disabled = True
            quick_request_form.fields['contact_phone'].disabled = True
        else:
            quick_request_form = QuickRequestForm()
        finance_product_roots = FinanceProduct.objects.root_nodes()
        context_part = dict(
            finance_product_roots=finance_product_roots,
            quick_request_form=quick_request_form,
        )
        kwargs.update(context_part)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class FinanceProductView(TemplateView):
    template_name = 'marer/product.html'

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(FinanceProduct, id=kwargs.get('pid', 0))
        if request.user.id:
            quick_request_form = QuickRequestForm(initial=dict(
                finance_product=product.id,
                contact_person_name=request.user.get_full_name(),
                contact_email=request.user.email,
                contact_phone=request.user.phone,
            ))
            quick_request_form.fields['contact_person_name'].disabled = True
            quick_request_form.fields['contact_email'].disabled = True
            quick_request_form.fields['contact_phone'].disabled = True
        else:
            quick_request_form = QuickRequestForm(initial=dict(
                finance_product=product.id,
            ))
        if product.childrens.exists():
            raise Http404()
        finance_product_roots = FinanceProduct.objects.root_nodes()
        context_part = dict(
            finance_product_roots=finance_product_roots,
            product=product,
            quick_request_form=quick_request_form,
        )
        kwargs.update(context_part)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
