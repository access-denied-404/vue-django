from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class IssueRegisteringView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/issue/registering.html'


class IssueCommonDocumentsRequestView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/issue/common_documents_request.html'


class IssueSurveyView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/issue/survey.html'


class IssueScoringView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/issue/scoring.html'


class IssueAdditionalDocumentsRequestView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/issue/additional_documents_request.html'


class IssuePaymentsView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/issue/payments.html'


class IssueFinalDocumentsApprovalView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/issue/final_documents_approval.html'


class IssueFinishedView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/issue/finished.html'


class IssueCancelledView(LoginRequiredMixin, TemplateView):
    template_name = 'marer/issue/cancelled.html'
