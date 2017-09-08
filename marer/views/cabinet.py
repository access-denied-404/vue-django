from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from marer import forms
from marer.models import Issue, Issuer
from marer.views import StaticPagesContextMixin


@method_decorator(csrf_exempt, name='dispatch')
class CabinetRequestsView(LoginRequiredMixin, TemplateView, StaticPagesContextMixin):
    template_name = 'marer/cabinet/requests.html'

    def get(self, request, *args, **kwargs):
        filtered_issues_qs = Issue.objects.filter(user=request.user)
        filter_form = forms.CabinetIssueListFilterForm(request.GET)
        if filter_form.is_valid():
            filter_fgrp = filter_form.cleaned_data.get('fpgrp', None)
            filter_status = filter_form.cleaned_data.get('status', None)
            if filter_fgrp is not None and filter_fgrp != '':
                filtered_issues_qs = filtered_issues_qs.filter(type=filter_fgrp)
            if filter_status is not None and filter_status != '':
                filtered_issues_qs = filtered_issues_qs.filter(status=filter_status)
        paged_filtered_issues_qs = filtered_issues_qs  # fixme make pageable
        kwargs.update(dict(
            filter_form=filter_form,
            issues=paged_filtered_issues_qs
        ))
        return super().get(request, *args, **kwargs)


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
        profile_form = forms.ProfileForm(initial=dict(
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            phone=request.user.phone,
        ))
        if 'profile_form' not in kwargs:
            kwargs.update(dict(profile_form=profile_form))
        return super().get(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        profile_form = forms.ProfileForm(request.POST)
        if profile_form.is_valid():
            user = request.user
            user.first_name = profile_form.cleaned_data['first_name']
            user.last_name = profile_form.cleaned_data['last_name']
            user.phone = profile_form.cleaned_data['phone']
            user.save()

            url = reverse('cabinet_profile', args=args, kwargs=kwargs)
            return HttpResponseRedirect(url)
        else:
            kwargs.update(dict(profile_form=profile_form))
            return self.get(request=request, *args, **kwargs)
