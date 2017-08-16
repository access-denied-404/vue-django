from django.conf.urls import url

from marer import views
from marer.views import auth

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^login$', auth.LoginView.as_view(), name='login'),
    url(r'^logout$', auth.LogoutView.as_view(), name='logout'),
    url(r'^register$', auth.RegisterView.as_view(), name='register'),
    url(r'^password_reset/request$', auth.PasswordResetRequestView.as_view(), name='password_reset_request'),
    url(r'^password_reset/reset$', auth.PasswordResetResetView.as_view(), name='password_reset_reset'),

    url(r'^cabinet/requests$', views.CabinetRequestsView.as_view(), name='cabinet_requests'),
    url(r'^cabinet/requests/new$', views.CabinetRequestsNewView.as_view(), name='cabinet_requests_new'),
    url(r'^cabinet/requests/(?P<rid>\d+)$', views.CabinetRequestView.as_view(), name='cabinet_request'),
    url(r'^cabinet/requests/(?P<rid>\d+)/banks$', views.CabinetRequestBanksView.as_view(), name='cabinet_request_banks'),
    url(r'^cabinet/organizations$', views.CabinetOrganizationsView.as_view(), name='cabinet_organizations'),
    url(r'^cabinet/profile$', views.CabinetProfileView.as_view(), name='cabinet_profile'),
]
