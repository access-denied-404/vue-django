from django.contrib.auth import login
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import TemplateView

from marer.forms import QuickRequestForm
from marer.models import FinanceProduct, User, Issue


class IndexView(TemplateView):
    template_name = 'marer/index.html'

    def get(self, request, *args, **kwargs):
        if 'quick_request_form' in kwargs:
            quick_request_form = kwargs.get('quick_request_form')
        elif request.user.id:
            quick_request_form = QuickRequestForm(user=request.user)
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
        username = ''
        if request.user.id:
            quick_request_form = QuickRequestForm(request.POST, user=request.user)
        else:
            quick_request_form = QuickRequestForm(request.POST)
            username = User.normalize_username(quick_request_form.cleaned_data['contact_email'])
            if User.objects.filter(username=username).exists():
                quick_request_form.add_error('contact_email', 'Пользователь с таким email уже существует')
        if quick_request_form.is_valid():
            if not request.user.id:
                # todo create new user an log in
                new_user = User()
                new_user.username = username
                new_user.email = quick_request_form.cleaned_data['contact_email']
                new_user.phone = quick_request_form.cleaned_data['contact_phone']
                full_name_arr = quick_request_form.cleaned_data['contact_person_name'].split(' ')

                new_user.first_name = ''
                new_user.last_name = ''
                if len(full_name_arr) == 1:
                    new_user.first_name = full_name_arr[0]
                elif len(full_name_arr) >= 2:
                    new_user.last_name = full_name_arr[0]
                    new_user.first_name = full_name_arr[1]

                # todo generate and send password
                new_user.save()
                login(request, new_user)
            # todo create new issue, redirect to issue page
            new_issue = Issue()
            new_issue.status = Issue.STATUS_REGISTERING
            new_issue.user = request.user  # fixme it's naive when new user, check it
            new_issue.type_id = quick_request_form.cleaned_data['finance_product']
            new_issue.save()
            url = reverse('cabinet_request', args=[new_issue.id])
            return HttpResponseRedirect(url)
        else:
            kwargs.update(dict(quick_request_form=quick_request_form))
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
