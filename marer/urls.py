from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from marer.views import auth
from marer.views import cabinet
from marer.views import issue
from marer.views import rest

urlpatterns = [
    url(r'^$', auth.LoginView.as_view(), name='index'),
    url(r'^login$', auth.LoginView.as_view(), name='login'),
    url(r'^login_sign$', auth.LoginSignView.as_view(), name='login_sign'),
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
    url(r'^cabinet/requests/(?P<iid>\d+)/srv$', issue.IssueSurveyView.as_view(), name='issue_survey'),
    url(r'^cabinet/requests/(?P<iid>\d+)/scr$', issue.IssueScoringView.as_view(), name='issue_scoring'),
    url(r'^cabinet/requests/(?P<iid>\d+)/rsr$', issue.IssueRemoteSurveyView.as_view(), name='issue_remote_survey'),
    url(r'^cabinet/requests/(?P<iid>\d+)/rsd$', issue.IssueRemoteSignView.as_view(), name='issue_remote_for_sign'),
    url(r'^cabinet/requests/(?P<iid>\d+)/rsd/sign-file$', issue.IssueRemoteDocumentSignView.as_view(), name='issue_remote_file_sign'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr/clr$', issue.IssueAdditionalDocumentsRequestView.as_view(), name='issue_additional_documents_request_new'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr/(?P<adrid>\d+)$', issue.IssueAdditionalDocumentsRequestView.as_view(), name='issue_additional_documents_request'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr$', issue.IssueAdditionalDocumentsRequestsView.as_view(), name='issue_additional_documents_requests'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr/sign-file$', issue.IssueAdditionalDocumentSignView.as_view(), name='issue_adr_file_sign'),
    url(r'^cabinet/requests/(?P<iid>\d+)/finished$', issue.IssueFinishedView.as_view(), name='issue_finished'),
    url(r'^cabinet/requests/(?P<iid>\d+)/cancelled$', issue.IssueCancelledView.as_view(), name='issue_cancelled'),

    url(r'^rest/tender$', rest.TenderDataView.as_view(), name='rest_tender')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
