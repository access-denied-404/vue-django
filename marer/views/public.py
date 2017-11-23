from django.conf import settings
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView

from marer import consts
from marer.forms import QuickRequestForm
from marer.models import User, Issuer, Issue
from marer.utils.notify import notify_user_manager_about_user_created_issue


class QuickRequestFormContextMixin(TemplateView):

    def get_context_data(self, **kwargs):

        if 'quick_request_form' not in kwargs:
            qrf_kwargs = dict()

            if self.request.user.id:
                qrf_kwargs['user'] = self.request.user

            product_page = kwargs.get('product', None)
            if product_page:
                product_obj = product_page.get_finance_product()
                if product_obj:
                    qrf_kwargs['initial'] = dict(product=product_obj.name)

            kwargs['quick_request_form'] = QuickRequestForm(**qrf_kwargs)

        if 'dadata_token' not in kwargs:
            kwargs['dadata_token'] = settings.DADATA_TOKEN

        return super().get_context_data(**kwargs)

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
                new_password = new_user.generate_new_password()
                new_user.save()
                new_user.email_user(
                    subject='Новый пользователь',
                    html_template_filename='mail/new_user_by_quick_form.html',
                    context=dict(
                        username=new_user.username,
                        password=new_password,
                    ),
                )
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

            new_issue.issuer_okved = quick_request_form.cleaned_data['party_okved']
            new_issue.issuer_okopf = quick_request_form.cleaned_data['party_okopf']

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
            notify_user_manager_about_user_created_issue(new_issue)
            url = reverse('cabinet_request', args=[new_issue.id])
            return HttpResponseRedirect(url)
        else:
            kwargs.update(dict(quick_request_form=quick_request_form))
            return self.get(request, *args, **kwargs)
