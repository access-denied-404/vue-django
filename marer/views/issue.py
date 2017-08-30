from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, RedirectView

from marer.forms import IssueRegisteringForm
from marer.models import Issue


class IssueView(LoginRequiredMixin, TemplateView):
    template_name = ''
    _issue = None

    def get_issue(self):
        if self._issue is not None:
            return self._issue

        iid = self.kwargs.get('iid', None)
        if iid is not None:
            # fixme maybe make error 403?
            issue = get_object_or_404(Issue, id=iid, user_id=self.request.user.id)
            self._issue = issue
            return issue

    def get_context_data(self, **kwargs):
        kwargs.update(dict(issue=self.get_issue()))
        return super().get_context_data(**kwargs)


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

    def get(self, request, *args, **kwargs):
        if 'base_form' not in kwargs:
            base_form = IssueRegisteringForm(
                initial=dict(
                    product=self.get_issue().product,
                    org_search_name=self.get_issue().get_issuer_name(),
                    comment=self.get_issue().comment,
                )
            )
            kwargs.update(dict(base_form=base_form))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        base_form = IssueRegisteringForm(request.POST)
        if base_form.is_valid():
            # todo go to next stage if we can
            issue = self.get_issue()
            issue.comment = base_form.cleaned_data['comment']
            issue.save()
        kwargs.update(dict(base_form=base_form))
        return self.get(request, *args, **kwargs)


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
