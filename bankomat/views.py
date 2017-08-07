from django.views.generic.base import TemplateView, RedirectView


class IndexView(TemplateView):
    template_name = 'bankomat/index.html'


class LoginView(TemplateView):
    template_name = 'bankomat/login.html'


class RegisterView(TemplateView):
    template_name = 'bankomat/register.html'


class PasswordResetRequestView(TemplateView):
    template_name = 'bankomat/password_reset_request.html'


class PasswordResetResetView(TemplateView):
    template_name = 'bankomat/password_reset_reset.html'


class CabinetView(TemplateView):
    template_name = 'bankomat/cabinet.html'


class CabinetRequestsView(TemplateView):
    template_name = 'bankomat/cabinet_requests.html'


class CabinetRequestsNewView(TemplateView):
    template_name = 'bankomat/cabinet_requests_new.html'


class CabinetRequestView(TemplateView):
    template_name = 'bankomat/cabinet_request.html'


class CabinetRequestBanksView(TemplateView):
    template_name = 'bankomat/cabinet_request_banks.html'


class CabinetSettingsView(TemplateView):
    template_name = 'bankomat/cabinet_settings.html'


class LogoutView(RedirectView):
    pattern_name = 'index'
