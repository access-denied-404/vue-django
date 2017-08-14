from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView, RedirectView


class IndexView(TemplateView):
    template_name = 'marer/index.html'


class LoginView(TemplateView):
    template_name = 'marer/login.html'

    def post(self, request, *args, **kwargs):
        url = reverse('cabinet_requests', args=args, kwargs=kwargs)
        return HttpResponseRedirect(url)


class RegisterView(TemplateView):
    template_name = 'marer/register.html'

    def post(self, request, *args, **kwargs):
        url = reverse('cabinet_requests', args=args, kwargs=kwargs)
        return HttpResponseRedirect(url)


class PasswordResetRequestView(TemplateView):
    template_name = 'marer/password_reset_request.html'


class PasswordResetResetView(TemplateView):
    template_name = 'marer/password_reset_reset.html'


class CabinetRequestsView(TemplateView):
    template_name = 'marer/cabinet/requests.html'


class CabinetRequestsNewView(TemplateView):
    template_name = 'marer/cabinet_requests_new.html'


class CabinetRequestView(TemplateView):
    template_name = 'marer/cabinet_request.html'


class CabinetRequestBanksView(TemplateView):
    template_name = 'marer/cabinet_request_banks.html'


class CabinetOrganizationsView(TemplateView):
    template_name = 'marer/cabinet/organizations.html'


class CabinetProfileView(TemplateView):
    template_name = 'marer/cabinet/profile.html'


class LogoutView(RedirectView):
    pattern_name = 'index'
