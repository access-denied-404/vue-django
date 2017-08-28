from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, RedirectView

from marer.models import Issue


class IssueView(LoginRequiredMixin, TemplateView):
    template_name = ''

    def get(self, request, *args, **kwargs):
        iid = kwargs.get('iid', None)
        if iid is not None:
            # fixme maybe make error 403?
            issue = get_object_or_404(Issue, id=iid, user_id=request.user.id)
            kwargs.update(issue=issue)
        return super().get(request, *args, **kwargs)


class IssueRedirectView(RedirectView):
    permanent = False

    def get(self, request, *args, **kwargs):
        iid = kwargs.get('iid', None)
        issue = None
        if iid is not None:
            # fixme maybe make error 403?
            issue = get_object_or_404(Issue, id=iid, user_id=request.user.id)

        if issue.status == Issue.STATUS_REGISTERING:
            self.pattern_name = 'issue_registering'
        elif issue.status == Issue.STATUS_COMMON_DOCUMENTS_REQUEST:
            self.pattern_name = 'issue_common_documents_request'
        elif issue.status == Issue.STATUS_SURVEY:
            self.pattern_name = 'issue_survey'
        elif issue.status == Issue.STATUS_SCORING:
            self.pattern_name = 'issue_scoring'
        elif issue.status == Issue.STATUS_ADDITIONAL_DOCUMENTS_REQUEST:
            self.pattern_name = 'issue_additional_documents_request'
        elif issue.status == Issue.STATUS_PAYMENTS:
            self.pattern_name = 'issue_payments'
        elif issue.status == Issue.STATUS_FINAL_DOCUMENTS_APPROVAL:
            self.pattern_name = 'issue_final_documents_approval'
        elif issue.status == Issue.STATUS_FINISHED:
            self.pattern_name = 'issue_finished'
        elif issue.status == Issue.STATUS_CANCELLED:
            self.pattern_name = 'issue_cancelled'

        return super().get(request, *args, **kwargs)


class IssueRegisteringView(IssueView):
    template_name = 'marer/issue/registering.html'


class IssueCommonDocumentsRequestView(IssueView):
    template_name = 'marer/issue/common_documents_request.html'


class IssueSurveyView(IssueView):
    template_name = 'marer/issue/survey.html'


class IssueScoringView(IssueView):
    template_name = 'marer/issue/scoring.html'


class IssueAdditionalDocumentsRequestView(IssueView):
    template_name = 'marer/issue/additional_documents_request.html'


class IssuePaymentsView(IssueView):
    template_name = 'marer/issue/payments.html'


class IssueFinalDocumentsApprovalView(IssueView):
    template_name = 'marer/issue/final_documents_approval.html'


class IssueFinishedView(IssueView):
    template_name = 'marer/issue/finished.html'


class IssueCancelledView(IssueView):
    template_name = 'marer/issue/cancelled.html'
