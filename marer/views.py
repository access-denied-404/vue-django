from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView, RedirectView

from marer import forms
from marer.models import User


class IndexView(TemplateView):
    template_name = 'marer/index.html'


class LoginView(TemplateView):
    template_name = 'marer/login.html'

    def post(self, request, *args, **kwargs):
        url = reverse('cabinet_requests', args=args, kwargs=kwargs)
        return HttpResponseRedirect(url)


class RegisterView(TemplateView):
    template_name = 'marer/register.html'

    def get(self, request, *args, **kwargs):
        reg_form = forms.RegisterForm()
        if 'reg_form' not in kwargs:
            kwargs.update(dict(reg_form=reg_form))
        return super().get(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        reg_form = forms.RegisterForm(request.POST)
        reg_form.full_clean()
        username = User.normalize_username(reg_form.cleaned_data['email'])
        user_exists = User.objects.filter(username=username).exists()
        if user_exists:
            reg_form.add_error('email', 'Пользователь с таким email уже существует ')
        if reg_form.is_valid():
            new_user = User()
            new_user.first_name = reg_form.cleaned_data['first_name']
            new_user.last_name = reg_form.cleaned_data['last_name']
            new_user.email = reg_form.cleaned_data['email']
            new_user.username = username
            new_user.phone = reg_form.cleaned_data['phone']
            new_user.set_password(reg_form.cleaned_data['password'])
            new_user.save()

            login(request, new_user)
            url = reverse('cabinet_requests', args=args, kwargs=kwargs)
            return HttpResponseRedirect(url)
        else:
            kwargs.update(dict(reg_form=reg_form))
            return self.get(request=request, *args, **kwargs)


class PasswordResetRequestView(TemplateView):
    template_name = 'marer/password_reset_request.html'


class PasswordResetResetView(TemplateView):
    template_name = 'marer/password_reset_reset.html'


class CabinetRequestsView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet/requests.html'


class CabinetRequestsNewView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet_requests_new.html'


class CabinetRequestView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet_request.html'


class CabinetRequestBanksView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet_request_banks.html'


class CabinetOrganizationsView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet/organizations.html'


class CabinetProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet/profile.html'


class LogoutView(RedirectView):
    pattern_name = 'index'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)
