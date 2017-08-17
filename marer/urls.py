from django.conf.urls import url

from marer import views
from marer.views import auth
from marer.views import issue

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^login$', auth.LoginView.as_view(), name='login'),
    url(r'^logout$', auth.LogoutView.as_view(), name='logout'),
    url(r'^register$', auth.RegisterView.as_view(), name='register'),
    url(r'^password_reset/request$', auth.PasswordResetRequestView.as_view(), name='password_reset_request'),
    url(r'^password_reset/reset$', auth.PasswordResetResetView.as_view(), name='password_reset_reset'),

    url(r'^cabinet/requests$', views.CabinetRequestsView.as_view(), name='cabinet_requests'),
    url(r'^cabinet/organizations$', views.CabinetOrganizationsView.as_view(), name='cabinet_organizations'),
    url(r'^cabinet/profile$', views.CabinetProfileView.as_view(), name='cabinet_profile'),

    url(r'^cabinet/requests/new$', issue.IssueCancelledView.as_view(), name='cabinet_requests_new'),
    url(r'^cabinet/requests/(?P<rid>\d+)$', issue.IssueRegisteringView.as_view(), name='cabinet_request'),

    url(r'^cabinet/requests/(?P<rid>\d+)/reg$', issue.IssueRegisteringView.as_view(), name='issue_registering'),
    url(r'^cabinet/requests/(?P<rid>\d+)/cdr$', issue.IssueCommonDocumentsRequestView.as_view(), name='issue_common_documents_request'),
    url(r'^cabinet/requests/(?P<rid>\d+)/srv$', issue.IssueSurveyView.as_view(), name='issue_survey'),
    url(r'^cabinet/requests/(?P<rid>\d+)/scr$', issue.IssueScoringView.as_view(), name='issue_scoring'),
    url(r'^cabinet/requests/(?P<rid>\d+)/adr$', issue.IssueAdditionalDocumentsRequestView.as_view(), name='issue_additional_documents_request'),
    url(r'^cabinet/requests/(?P<rid>\d+)/pay$', issue.IssuePaymentsView.as_view(), name='issue_payments'),
    url(r'^cabinet/requests/(?P<rid>\d+)/fda$', issue.IssueFinalDocumentsApprovalView.as_view(), name='issue_final_documents_approval'),
    url(r'^cabinet/requests/(?P<rid>\d+)/finished$', issue.IssueFinishedView.as_view(), name='issue_finished'),
    url(r'^cabinet/requests/(?P<rid>\d+)/cancelled$', issue.IssueCancelledView.as_view(), name='issue_cancelled'),
]
