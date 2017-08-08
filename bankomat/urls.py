from django.conf.urls import url
from bankomat import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    url(r'^register$', views.RegisterView.as_view(), name='register'),
    url(r'^password_reset/request$', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    url(r'^password_reset/reset$', views.PasswordResetResetView.as_view(), name='password_reset_reset'),

    url(r'^cabinet/requests$', views.CabinetRequestsView.as_view(), name='cabinet_requests'),
    url(r'^cabinet/requests/new$', views.CabinetRequestsNewView.as_view(), name='cabinet_requests_new'),
    url(r'^cabinet/requests/(?P<rid>\d+)$', views.CabinetRequestView.as_view(), name='cabinet_request'),
    url(r'^cabinet/requests/(?P<rid>\d+)/banks$', views.CabinetRequestBanksView.as_view(), name='cabinet_request_banks'),
    url(r'^cabinet/organizations$', views.CabinetOrganizationsView.as_view(), name='cabinet_organizations'),
    url(r'^cabinet/profile$', views.CabinetProfileView.as_view(), name='cabinet_profile'),
]
