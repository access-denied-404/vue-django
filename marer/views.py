from django.contrib.auth import login, logout, authenticate
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

    def get(self, request, *args, **kwargs):
        login_form = forms.LoginForm()
        if 'login_form' not in kwargs:
            kwargs.update(dict(login_form=login_form))
        return super().get(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        login_form = forms.LoginForm(request.POST)

        login_form.full_clean()
        username = User.normalize_username(login_form.cleaned_data['email'])
        user_exists = User.objects.filter(username=username).exists()

        if not user_exists:
            login_form.add_error('email', 'Пользователь не найден')

        user = authenticate(
            request,
            username=username,
            password=login_form.cleaned_data['password']
        )
        if user is None and user_exists:
            login_form.add_error('password', 'Неверный пароль')

        if login_form.is_valid():
            login(request, user)
            url = reverse('cabinet_requests', args=args, kwargs=kwargs)
            return HttpResponseRedirect(url)
        else:
            kwargs.update(dict(login_form=login_form))
            return self.get(request=request, *args, **kwargs)


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
    template_name = 'marer/cabinet/issue/scoring.html'


class CabinetRequestBanksView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/cabinet_request_banks.html'


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


class LogoutView(RedirectView):
    pattern_name = 'index'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)
