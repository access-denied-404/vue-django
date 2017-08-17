from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView

from marer import forms


class IndexView(TemplateView):
    template_name = 'marer/index.html'


class CabinetRequestsView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet/requests.html'


class CabinetOrganizationsView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet/organizations.html'


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


