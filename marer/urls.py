from django.conf.urls import url

from marer import views
from marer.views import auth
from marer.views import cabinet
from marer.views import issue
from marer.views import rest

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^product/(?P<pid>\d+)', views.FinanceProductView.as_view(), name='finance_product'),
    url(r'^page/(?P<spid>\d+)', views.StaticPageView.as_view(), name='static_page'),

    url(r'^login$', auth.LoginView.as_view(), name='login'),
    url(r'^logout$', auth.LogoutView.as_view(), name='logout'),
    url(r'^register$', auth.RegisterView.as_view(), name='register'),
    url(r'^password_reset/request$', auth.PasswordResetRequestView.as_view(), name='password_reset_request'),
    url(r'^password_reset/reset$', auth.PasswordResetResetView.as_view(), name='password_reset_reset'),

    url(r'^cabinet/requests$', cabinet.CabinetRequestsView.as_view(), name='cabinet_requests'),
    url(r'^cabinet/organizations$', cabinet.CabinetOrganizationsView.as_view(), name='cabinet_organizations'),
    url(r'^cabinet/profile$', cabinet.CabinetProfileView.as_view(), name='cabinet_profile'),

    url(r'^cabinet/requests/new$', issue.IssueRegisteringView.as_view(), name='issue_new'),
    url(r'^cabinet/requests/(?P<iid>\d+)$', issue.IssueRedirectView.as_view(), name='cabinet_request'),

    url(r'^cabinet/requests/(?P<iid>\d+)/reg$', issue.IssueRegisteringView.as_view(), name='issue_registering'),
    url(r'^cabinet/requests/(?P<iid>\d+)/cdr$', issue.IssueCommonDocumentsRequestView.as_view(), name='issue_common_documents_request'),
    url(r'^cabinet/requests/(?P<iid>\d+)/srv$', issue.IssueSurveyView.as_view(), name='issue_survey'),
    url(r'^cabinet/requests/(?P<iid>\d+)/scr$', issue.IssueScoringView.as_view(), name='issue_scoring'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr/clr$', issue.IssueAdditionalDocumentsRequestView.as_view(), name='issue_additional_documents_request_new'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr/(?P<adrid>\d+)$', issue.IssueAdditionalDocumentsRequestView.as_view(), name='issue_additional_documents_request'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr$', issue.IssueAdditionalDocumentsRequestsView.as_view(), name='issue_additional_documents_requests'),
    url(r'^cabinet/requests/(?P<iid>\d+)/pay$', issue.IssuePaymentsView.as_view(), name='issue_payments'),
    url(r'^cabinet/requests/(?P<iid>\d+)/finished$', issue.IssueFinishedView.as_view(), name='issue_finished'),
    url(r'^cabinet/requests/(?P<iid>\d+)/cancelled$', issue.IssueCancelledView.as_view(), name='issue_cancelled'),

    url(r'^rest/tender$', rest.TenderDataView.as_view(), name='rest_tender')
]
