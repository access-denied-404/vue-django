from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView

from marer import consts
from marer.forms import IssueRegisteringForm, IFOPCMessageForm
from marer.models import Issue, Document
from marer.models.issue import IssueClarificationMessage, \
    IssueFinanceOrgProposeClarificationMessageDocument, IssueClarification, \
    IssueProposeDocument
from marer.products import get_finance_products
from marer.stub import create_stub_issuer
from marer.utils.notify import notify_user_manager_about_user_created_issue, \
    notify_user_manager_about_user_updated_issue, notify_about_user_created_clarification, \
    notify_about_user_adds_message, notify_fo_managers_about_issue_proposed_to_banks, \
    notify_user_manager_about_issue_proposed_to_banks


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


class IssueRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get(self, request, *args, **kwargs):
        iid = kwargs.get('iid', None)
        issue = None
        if iid is not None:
            # fixme maybe make error 403?
            issue = get_object_or_404(Issue, id=iid, user_id=request.user.id)

        if issue.status == consts.ISSUE_STATUS_REGISTERING:
            self.pattern_name = 'issue_registering'
        elif issue.status == consts.ISSUE_STATUS_REVIEW:
            self.pattern_name = 'issue_additional_documents_requests'
        elif issue.status == consts.ISSUE_STATUS_FINISHED:
            self.pattern_name = 'issue_finished'
        elif issue.status == consts.ISSUE_STATUS_CANCELLED:
            self.pattern_name = 'issue_cancelled'

        return super().get(request, *args, **kwargs)


class IssueRegisteringView(IssueView):
    template_name = 'marer/issue/registering.html'

    def get(self, request, *args, **kwargs):
        if 'base_form' not in kwargs:
            if self.get_issue():
                initial = dict(
                    product=self.get_issue().product,
                    org_search_name=self.get_issue().get_issuer_name(),
                    comment=self.get_issue().comment,
                )
            else:
                initial = dict()
            kwargs['base_form'] = IssueRegisteringForm(initial=initial)
        kwargs['issue'] = self.get_issue()
        kwargs['products'] = get_finance_products()
        kwargs['dadata_token'] = settings.DADATA_TOKEN
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        if self.get_issue() and 'issue_registering' not in self.get_issue().editable_dashboard_views():
            return self.get(request, *args, **kwargs)

        base_form = IssueRegisteringForm(request.POST)
        if base_form.is_valid():
            # todo go to next stage if we can
            need_to_notify_for_issue_create = False
            if not self.get_issue():
                issuer = create_stub_issuer(
                    user_owner=request.user,
                    issuer_name=base_form.cleaned_data['org_search_name'],
                )

                new_issue = Issue(
                    issuer=issuer,
                    product=base_form.cleaned_data['product'],
                    status=consts.ISSUE_STATUS_REGISTERING,
                    user=request.user,
                )  # todo set values
                new_issue.fill_from_issuer()
                need_to_notify_for_issue_create = True
                self._issue = new_issue
            issue = self.get_issue()
            issue.comment = base_form.cleaned_data['comment']
            issue.product = base_form.cleaned_data['product']
            issue.save()
            if need_to_notify_for_issue_create:
                notify_user_manager_about_user_created_issue(issue)
            else:
                notify_user_manager_about_user_updated_issue(issue)

            # todo issue process registering form
            product = issue.get_product()
            product.set_issue(issue)
            processed_valid = product.process_registering_form(request)

            if processed_valid:
                url = reverse('issue_survey', args=[issue.id])
                return HttpResponseRedirect(url)

        kwargs.update(dict(base_form=base_form))
        return self.get(request, *args, **kwargs)


class IssueSurveyView(IssueView):
    template_name = 'marer/issue/survey.html'

    def get(self, request, *args, **kwargs):
        kwargs['survey_template'] = self.get_issue().get_product().survey_template_name
        kwargs.update(self.get_issue().get_product().get_survey_context_part())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        if self.get_issue() and 'issue_survey' not in self.get_issue().editable_dashboard_views():
            return self.get(request, *args, **kwargs)

        all_ok = self.get_issue().get_product().process_survey_post_data(request)
        if all_ok:
            notify_user_manager_about_user_updated_issue(self.get_issue())
            url = reverse('issue_additional_documents_requests', args=[self.get_issue().id])
            return HttpResponseRedirect(url)
        else:
            return self.get(request, *args, **kwargs)


class IssueAdditionalDocumentsRequestsView(IssueView):
    template_name = 'marer/issue/additional_documents_requests.html'

    def post(self, request, *args, **kwargs):

        proposes_docs = IssueProposeDocument.objects.filter(
            issue=self.get_issue())
        for pdoc in proposes_docs:
            pdoc_files_key = 'propose_doc_%s' % pdoc.id
            pdoc_files_del_key = 'propose_doc_%s_del' % pdoc.id
            pdoc_file = request.FILES.get(pdoc_files_key, None)
            pdoc_del_mark = request.POST.get(pdoc_files_del_key, None)
            if pdoc_file:
                if pdoc.document:
                    pdoc.document.file = pdoc_file
                    pdoc.document.save()
                else:
                    new_doc = Document()
                    new_doc.file = pdoc_file
                    new_doc.save()
                    pdoc.document = new_doc
                pdoc.save()

            if pdoc_del_mark:
                pdoc.document = None
                pdoc.save(chain_docs_update=False)

        return self.get(request, *args, **kwargs)


class IssueAdditionalDocumentsRequestView(IssueView):
    template_name = 'marer/issue/additional_documents_request.html'

    def _get_clarification(self):
        clarif_id = self.kwargs.get('adrid', None)
        if clarif_id:
            clarification = get_object_or_404(IssueClarification, id=clarif_id)
            return clarification
        return None

    def get(self, request, *args, **kwargs):
        clarification = self._get_clarification()
        if clarification:
            kwargs['clarification'] = clarification
        kwargs['consts'] = consts
        if 'comment_form' not in kwargs:
            kwargs['comment_form'] = IFOPCMessageForm()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        comment_form = IFOPCMessageForm(request.POST, request.FILES)

        if comment_form.is_valid():

            if self.get_issue() and 'issue_additional_documents_requests' not in self.get_issue().editable_dashboard_views():
                return self.get(request, *args, **kwargs)

            clarification = self._get_clarification()
            clarification_change = True
            if not clarification:
                propose_id = request.GET.get('pid', 0)

                clarification = IssueClarification()
                clarification.initiator = consts.IFOPC_INITIATOR_ISSUER
                clarification.issue = self.get_issue()
                clarification.save()
                clarification_change = False

            new_msg = IssueClarificationMessage()
            new_msg.clarification = clarification
            new_msg.message = comment_form.cleaned_data['message']
            new_msg.user = request.user
            new_msg.save()

            for ffield in ['doc%s' % dnum for dnum in range(1, 9)]:
                ffile = comment_form.cleaned_data[ffield]
                if ffile:
                    new_doc = Document()
                    new_doc.file = ffile
                    new_doc.save()

                    new_clarif_doc_link = IssueFinanceOrgProposeClarificationMessageDocument()
                    new_clarif_doc_link.clarification_message = new_msg
                    new_clarif_doc_link.name = ffile.name
                    new_clarif_doc_link.document = new_doc
                    new_clarif_doc_link.save()

            if clarification_change:
                notify_about_user_adds_message(new_msg)
            else:
                notify_about_user_created_clarification(clarification)

            url = reverse(
                'issue_additional_documents_request',
                args=[self.get_issue().id, clarification.id]
            )
            return HttpResponseRedirect(url)
        else:
            kwargs['comment_form'] = comment_form
        return self.get(request, *args, **kwargs)


class IssuePaymentsView(IssueView):
    template_name = 'marer/issue/payments.html'


class IssueFinishedView(IssueView):
    template_name = 'marer/issue/finished.html'


class IssueCancelledView(IssueView):
    template_name = 'marer/issue/cancelled.html'
