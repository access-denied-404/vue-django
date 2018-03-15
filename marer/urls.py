from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from marer.views import auth
from marer.views import cabinet
from marer.views import issue
from marer.views import rest
from marer.views import process_docs

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
    url(r'^manager$', cabinet.CabinetManagerView.as_view(), name='cabinet_manager'),

    url(r'^cabinet/requests/new$', issue.IssueRegisteringView.as_view(), name='issue_new'),
    url(r'^cabinet/requests/(?P<iid>\d+)$', issue.IssueRedirectView.as_view(), name='cabinet_request'),

    url(r'^cabinet/requests/(?P<iid>\d+)/reg$', issue.IssueRegisteringView.as_view(), name='issue_registering'),
    url(r'^cabinet/requests/(?P<iid>\d+)/srv$', issue.IssueSurveyView.as_view(), name='issue_survey'),
    url(r'^cabinet/requests/(?P<iid>\d+)/scr$', issue.IssueScoringView.as_view(), name='issue_scoring'),
    url(r'^cabinet/requests/(?P<iid>\d+)/rsr$', issue.IssueRemoteSurveyView.as_view(), name='issue_remote_survey'),
    url(r'^cabinet/requests/(?P<iid>\d+)/radr$', issue.IssueRemoteAdditionalDocumentsRequests.as_view(), name='issue_remote_add_docs_requests'),
    url(r'^cabinet/requests/(?P<iid>\d+)/rsd$', issue.IssueRemoteSignView.as_view(), name='issue_remote_for_sign'),
    url(r'^cabinet/requests/(?P<iid>\d+)/rsd/sign-file$', issue.IssueRemoteDocumentSignView.as_view(), name='issue_remote_file_sign'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr/clr$', issue.IssueAdditionalDocumentsRequestView.as_view(), name='issue_additional_documents_request_new'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr/(?P<adrid>\d+)$', issue.IssueAdditionalDocumentsRequestView.as_view(), name='issue_additional_documents_request'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr$', issue.IssueAdditionalDocumentsRequestsView.as_view(), name='issue_additional_documents_requests'),
    url(r'^cabinet/requests/(?P<iid>\d+)/adr/sign-file$', issue.IssueAdditionalDocumentSignView.as_view(), name='issue_adr_file_sign'),
    url(r'^cabinet/requests/(?P<iid>\d+)/finished$', issue.IssueFinishedView.as_view(), name='issue_finished'),
    url(r'^cabinet/requests/(?P<iid>\d+)/cancelled$', issue.IssueCancelledView.as_view(), name='issue_cancelled'),
    url(r'^cabinet/requests/(?P<iid>\d+)/chat', issue.IssueChatView.as_view(), name='issue_chat'),

    url(r'^rest/tender$', rest.TenderDataView.as_view(), name='rest_tender'),
    url(r'^rest/bank_commission$', csrf_exempt(rest.IssueBankCommissionView.as_view()), name='rest_bank_commission'),

    url(r'^rest/issues$', rest.IssuesView.as_view(), name='rest_issues'),
    url(r'^rest/issue/(?P<iid>\d+)$', rest.IssueView.as_view(), name='rest_issue'),
    url(r'^rest/issue/(?P<iid>\d+)/sec-dep-mgmt$', rest.IssueSecDepView.as_view(), name='rest_issue_sec_dep_mgmt'),
    url(r'^rest/issue/(?P<iid>\d+)/doc-ops-mgmt$', rest.IssueDocOpsView.as_view(), name='rest_issue_doc_ops_mgmt'),
    url(r'^rest/issue/(?P<iid>\d+)/lawyers-dep-mgmt$', rest.IssueLawyersDepView.as_view(), name='rest_issue_lawyers_dep_mgmt'),
    url(r'^rest/issue/(?P<iid>\d+)/generate_doc_ops_mgmt_conclusion_doc$', rest.IssueGenerateDocOpsView.as_view(), name='rest_generate_doc_ops_mgmt_conclusion_doc'),
    url(r'^rest/issue/(?P<iid>\d+)/generate_lawyers_dep_conclusion_doc$', rest.IssueGenerateLawyersDepConclusionDocView.as_view(), name='rest_generate_lawyers_dep_conclusion_doc'),
    url(r'^rest/issue/(?P<iid>\d+)/generate_sec-dep-mgmt$', rest.IssueGenerateSecDepMgmtView.as_view(), name='rest_generate_sec-dep-mgmt'),
    url(r'^rest/issue/(?P<iid>\d+)/messages$', rest.IssueMessagesView.as_view(), name='rest_issue_messages'),
    url(r'^rest/profile$', rest.ProfileView.as_view(), name='rest_profile'),

    url(r'^issue/(?P<iid>\d+)/docs-zip/$', rest.DocsZipView.as_view(), name='docs_zip'),
    url(r'^delete-docs/issue/(?P<iid>\d+)$', process_docs.IssueDeleteDocument.as_view(), name='delete_document'),
    url(r'^replace-docs/issue/(?P<iid>\d+)$', process_docs.IssueReplaceDocument.as_view(), name='replace_document'),
    url(r'^reform-docs/issue/(?P<iid>\d+)$', process_docs.IssueReformDocument.as_view(), name='reform_document'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
