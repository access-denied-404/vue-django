from django.conf import settings
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import TemplateView

from marer import consts
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
            dadata_token=settings.DADATA_TOKEN,
        )
        kwargs.update(context_part)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = ''
        if request.user.id:
            quick_request_form = QuickRequestForm(request.POST, user=request.user)
        else:
            quick_request_form = QuickRequestForm(request.POST)
            quick_request_form.full_clean()
            username = quick_request_form.cleaned_data.get('contact_email', None)
            if username is not None:
                username = User.normalize_username(username)
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

            issuer_full_name = quick_request_form.cleaned_data['party_full_name']
            issuer_short_name = quick_request_form.cleaned_data['party_short_name']
            issuer_ogrn = quick_request_form.cleaned_data['party_ogrn']
            issuer_inn = quick_request_form.cleaned_data['party_inn']
            issuer_kpp = quick_request_form.cleaned_data['party_kpp']

            issuer = None
            try:
                issuer = Issuer.objects.get(
                    # Q(Q(full_name__iexact=issuer_name) | Q(short_name__iexact=issuer_name))
                    ogrn=issuer_ogrn,
                    inn=issuer_inn,
                    kpp=issuer_kpp,
                )
            except ObjectDoesNotExist:
                issuer = Issuer()
                issuer.user = request.user
                issuer.full_name = issuer_full_name
                issuer.short_name = issuer_short_name
                issuer.ogrn = issuer_ogrn
                issuer.inn = issuer_inn
                issuer.kpp = issuer_kpp
                issuer.save()

            new_issue = Issue()
            new_issue.issuer = issuer
            new_issue.fill_from_issuer()
            new_issue.status = consts.ISSUE_STATUS_REGISTERING
            new_issue.user = request.user  # fixme it's naive when new user, check it
            new_issue.product = quick_request_form.cleaned_data['product']

            # new_issue.issuer_ogrn = quick_request_form.cleaned_data['party_ogrn']
            # new_issue.issuer_inn = quick_request_form.cleaned_data['party_inn']
            # new_issue.issuer_kpp = quick_request_form.cleaned_data['party_kpp']
            new_issue.issuer_okved = quick_request_form.cleaned_data['party_okved']
            new_issue.issuer_okopf = quick_request_form.cleaned_data['party_okopf']

            # new_issue.issuer_full_name = quick_request_form.cleaned_data['party_full_name']
            # new_issue.issuer_short_name = quick_request_form.cleaned_data['party_short_name']
            new_issue.issuer_foreign_name = quick_request_form.cleaned_data['party_foreign_name']
            new_issue.issuer_legal_address = quick_request_form.cleaned_data['party_legal_address']

            head_fio = quick_request_form.cleaned_data['party_head_fio']
            fio_arr = head_fio.split(' ')
            if len(fio_arr) == 1:
                # only name
                new_issue.issuer_head_first_name = fio_arr[0]
            elif len(fio_arr) == 2:
                # last and first names
                new_issue.issuer_head_last_name = fio_arr[0]
                new_issue.issuer_head_first_name = fio_arr[1]
            elif len(fio_arr) == 3:
                # last, first, middle names
                new_issue.issuer_head_last_name = fio_arr[0]
                new_issue.issuer_head_first_name = fio_arr[1]
                new_issue.issuer_head_middle_name = fio_arr[2]

            new_issue.issuer_head_org_position_and_permissions = quick_request_form.cleaned_data['party_head_position']

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
            dadata_token=settings.DADATA_TOKEN,
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
