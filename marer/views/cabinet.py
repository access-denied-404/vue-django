from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from marer import forms
from marer.forms import ChangePasswordForm
from marer.models import Issue, Issuer


@method_decorator(csrf_exempt, name='dispatch')
class CabinetRequestsView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet/requests.html'

    def get(self, request, *args, **kwargs):
        filtered_issues_qs = Issue.objects.filter(user=request.user)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by', '')
            filtered_issues_qs = filtered_issues_qs.order_by(order_by)
        filter_form = forms.CabinetIssueListFilterForm(request.GET)
        if filter_form.is_valid():
            filter_fgrp = filter_form.cleaned_data.get('fpgrp', None)
            filter_status = filter_form.cleaned_data.get('status', None)
            if filter_fgrp is not None and filter_fgrp != '':
                filtered_issues_qs = filtered_issues_qs.filter(type=filter_fgrp)
            if filter_status is not None and filter_status != '':
                filtered_issues_qs = filtered_issues_qs.filter(status=filter_status)
        paged_filtered_issues_qs = Paginator(filtered_issues_qs, 20)
        page = request.GET.get('page', 1)
        try:
            paged_filtered_issues_qs = paged_filtered_issues_qs.page(page)
        except PageNotAnInteger:
            paged_filtered_issues_qs = paged_filtered_issues_qs.page(1)
        except EmptyPage:
            paged_filtered_issues_qs = paged_filtered_issues_qs.page(1)
        get_params = request.GET.copy()
        for key in request.GET:
            if get_params.get(key, '') == '' or get_params.get(key, None) is None or key == 'page':
                del get_params[key]
        get_params_as_new = ''
        get_params_as_addition = ''
        if len(get_params):
            get_params = get_params.urlencode()
            get_params_as_new = '?' + get_params
            get_params_as_addition = '&' + get_params
        kwargs.update(dict(
            filter_form=filter_form,
            issues=paged_filtered_issues_qs,
            get_params_as_new=get_params_as_new,
            get_params_as_addition=get_params_as_addition,
        ))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('issue_del', False):
            del_issue_id = request.POST.get('id', None)
            # if del_issue_id:
            #     Issue.objects.filter(id=del_issue_id, user=request.user).delete()

        url = reverse(request.resolver_match.url_name, args=request.resolver_match.args)
        if len(request.GET):
            url += '?' + request.GET.urlencode()
        return HttpResponseRedirect(url)


class CabinetOrganizationsView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet/organizations.html'

    def get(self, request, *args, **kwargs):
        issuers = Issuer.objects.filter(user_id=request.user.id)
        kwargs.update(dict(issuers=issuers))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            iid = request.POST.get('iid', 0)
            issuer = Issuer.objects.get(id=iid, user_id=request.user.id)
            issuer.delete()
        except ObjectDoesNotExist:
            pass  # todo make a warning
        url = reverse('cabinet_organizations', args=args, kwargs=kwargs)
        return HttpResponseRedirect(url)


class CabinetProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet/profile.html'

    def get(self, request, *args, **kwargs):
        profile_form = forms.ProfileForm(prefix='profile', initial=dict(
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            phone=request.user.phone,
        ))
        password_form = ChangePasswordForm(prefix='password', user=request.user)
        if 'profile_form' not in kwargs:
            kwargs.update(dict(profile_form=profile_form))
        if 'password_form' not in kwargs:
            kwargs.update(dict(password_form=password_form))
        return super().get(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        profile_form = forms.ProfileForm(request.POST, prefix='profile')
        password_form = ChangePasswordForm(data=request.POST, prefix='password', user=request.user)

        if profile_form.is_valid():
            user = request.user
            user.first_name = profile_form.cleaned_data['first_name']
            user.last_name = profile_form.cleaned_data['last_name']
            user.phone = profile_form.cleaned_data['phone']
            user.save()

            url = reverse('cabinet_profile', args=args, kwargs=kwargs)
            return HttpResponseRedirect(url)

        if password_form.is_valid():
            request.user.set_password(password_form.cleaned_data['password'])
            request.user.save()

            url = reverse('cabinet_profile', args=args, kwargs=kwargs)
            return HttpResponseRedirect(url)

        else:
            kwargs.update(dict(
                profile_form=profile_form,
                password_form=password_form,
            ))
            return self.get(request=request, *args, **kwargs)


class CabinetManagerView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet/manager.html'
