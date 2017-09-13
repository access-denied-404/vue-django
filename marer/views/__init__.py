from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import TemplateView

from marer.forms import QuickRequestForm
from marer.models import FinanceProductPage, StaticPage
from marer.models.finance_org import FinanceOrgProductConditions
from marer.models.issue import Issue
from marer.models.issuer import Issuer
from marer.models.user import User
from marer.views.mixins import StaticPagesContextMixin


class IndexView(TemplateView, StaticPagesContextMixin):
    template_name = 'marer/index.html'

    def get(self, request, *args, **kwargs):
        if 'quick_request_form' in kwargs:
            quick_request_form = kwargs.get('quick_request_form')
        elif request.user.id:
            quick_request_form = QuickRequestForm(user=request.user)
        else:
            quick_request_form = QuickRequestForm()
        finance_product_roots = FinanceProductPage.objects.root_nodes()

        best_finance_products = FinanceProductPage.objects.filter(
            product_icon__isnull=False
        ).exclude(
            product_icon=''
        ).order_by('?')[:8]

        bg_rated_foc_list = FinanceOrgProductConditions.objects.filter(
            bg_44_contract_exec_interest_rate__isnull=False,
            bg_review_term_days__gt=0,
        ).order_by('bg_44_contract_exec_interest_rate')[:5]

        # distinctize by finance org
        bg_rated_foc_list = [x for x in bg_rated_foc_list]
        fo_ids_used = []
        distinctized_bg_rated_foc_list = []
        for foc in bg_rated_foc_list:
            if foc.finance_org_id not in fo_ids_used:
                distinctized_bg_rated_foc_list.append(foc)
                fo_ids_used.append(foc.finance_org_id)

        context_part = dict(
            finance_product_roots=finance_product_roots,
            best_finance_products=best_finance_products,
            quick_request_form=quick_request_form,
            bg_rated_foc_list=distinctized_bg_rated_foc_list,
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
            issuer_name = quick_request_form.cleaned_data['issuer']

            issuer = None
            try:
                issuer = Issuer.objects.get(Q(Q(full_name__iexact=issuer_name) | Q(short_name__iexact=issuer_name)))
            except ObjectDoesNotExist:
                issuer = Issuer(
                    full_name=issuer_name,
                    short_name=issuer_name,
                    inn='0000000000',
                    kpp='000000000',
                    ogrn='0000000000000',
                    user=request.user,
                )
                issuer.save()

            new_issue = Issue()
            new_issue.issuer = issuer
            new_issue.fill_from_issuer()
            new_issue.status = Issue.STATUS_REGISTERING
            new_issue.user = request.user  # fixme it's naive when new user, check it
            new_issue.product = quick_request_form.cleaned_data['product']
            new_issue.save()
            url = reverse('cabinet_request', args=[new_issue.id])
            return HttpResponseRedirect(url)
        else:
            kwargs.update(dict(quick_request_form=quick_request_form))
            return self.get(request, *args, **kwargs)


class FinanceProductView(TemplateView, StaticPagesContextMixin):
    template_name = 'marer/product.html'

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(FinanceProductPage, id=kwargs.get('pid', 0))
        finance_product = product.get_finance_product()
        if finance_product is not None:
            finance_product_name = finance_product.name
        else:
            finance_product_name = None
        if request.user.id:
            quick_request_form = QuickRequestForm(initial=dict(
                product=finance_product_name,
                contact_person_name=request.user.get_full_name(),
                contact_email=request.user.email,
                contact_phone=request.user.phone,
            ))
            quick_request_form.fields['contact_person_name'].disabled = True
            quick_request_form.fields['contact_email'].disabled = True
            quick_request_form.fields['contact_phone'].disabled = True
        else:
            quick_request_form = QuickRequestForm(initial=dict(
                product=finance_product_name,
            ))
        finance_product_roots = FinanceProductPage.objects.root_nodes()
        context_part = dict(
            finance_product_roots=finance_product_roots,
            product=product,
            quick_request_form=quick_request_form,
        )
        kwargs.update(context_part)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class StaticPageView(TemplateView, StaticPagesContextMixin):
    template_name = 'marer/static_page.html'

    def get(self, request, *args, **kwargs):
        static_page_id = kwargs.get('spid', 0)
        static_page = get_object_or_404(StaticPage, id=static_page_id)

        if 'quick_request_form' in kwargs:
            quick_request_form = kwargs.get('quick_request_form')
        elif request.user.id:
            quick_request_form = QuickRequestForm(user=request.user)
        else:
            quick_request_form = QuickRequestForm()
        finance_product_roots = FinanceProductPage.objects.root_nodes()

        context_part = dict(
            finance_product_roots=finance_product_roots,
            quick_request_form=quick_request_form,
            static_page=static_page,
        )
        kwargs.update(context_part)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
