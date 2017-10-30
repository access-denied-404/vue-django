from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView

from marer import consts
from marer.forms import IssueRegisteringForm, IFOPCMessageForm
from marer.models import Issue, Issuer, Document
from marer.models.finance_org import FinanceOrgProductConditions, FinanceOrganization
from marer.models.issue import IssueFinanceOrgPropose, IssueFinanceOrgProposeClarificationMessage, \
    IssueFinanceOrgProposeClarificationMessageDocument, IssueFinanceOrgProposeClarification, \
    IssueFinanceOrgProposeDocument
from marer.products import get_finance_products
from marer.stub import create_stub_issuer
from marer.views.mixins import StaticPagesContextMixin


class IssueView(LoginRequiredMixin, TemplateView, StaticPagesContextMixin):
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

        if issue.status == consts.ISSUE_STATUS_REGISTERING:
            self.pattern_name = 'issue_registering'
        elif issue.status == consts.ISSUE_STATUS_REVIEW:
            if IssueFinanceOrgProposeClarification.objects.filter(propose__issue=issue).exists():
                self.pattern_name = 'issue_additional_documents_requests'
            else:
                self.pattern_name = 'issue_scoring'
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
                self._issue = new_issue
            issue = self.get_issue()
            issue.comment = base_form.cleaned_data['comment']
            issue.product = base_form.cleaned_data['product']
            issue.save()

            # todo issue process registering form
            product = issue.get_product()
            product.set_issue(issue)
            product.process_registering_form(request)

            url = reverse('issue_registering', args=[issue.id])
            return HttpResponseRedirect(url)

        else:
            kwargs.update(dict(base_form=base_form))
            return self.get(request, *args, **kwargs)


class IssueCommonDocumentsRequestView(IssueView):
    template_name = 'marer/issue/common_documents_request.html'

    def get(self, request, *args, **kwargs):
        fp_documents = self.get_issue().get_product().get_documents_list()
        fp_docs_codes = [fpd.code for fpd in fp_documents]
        issue_documents = self.get_issue().common_documents.filter(code__in=fp_docs_codes)
        for idoc in issue_documents:
            for fp in fp_documents:
                if idoc.code == fp.code:
                    fp.set_document(idoc.document)
        kwargs.update(dict(documents=fp_documents))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        if self.get_issue() and 'issue_common_documents_request' not in self.get_issue().editable_dashboard_views():
            return self.get(request, *args, **kwargs)

        fp_documents = self.get_issue().get_product().get_documents_list()
        for fpdoc in fp_documents:
            post_file = request.FILES.get(fpdoc.code, None)
            if post_file is not None:
                self.get_issue().update_common_issue_doc(fpdoc.code, post_file)
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

        self.get_issue().get_product().process_survey_post_data(request)
        return self.get(request, *args, **kwargs)


class IssueScoringView(IssueView):
    template_name = 'marer/issue/scoring.html'

    def get(self, request, *args, **kwargs):

        foc_fields = self.get_issue().get_product().get_finance_orgs_conditions_list_fields()

        foc_list = self.get_issue().get_product().get_finance_orgs_conditions_list()
        first_fld, _ = foc_fields[0]
        foc_list = foc_list.order_by(first_fld)

        # distinctize by finance org
        foc_list = [x for x in foc_list]
        fo_ids_used = []
        distinctized_foc_list = []
        for foc in foc_list:
            if foc.finance_org_id not in fo_ids_used:
                distinctized_foc_list.append(foc)
                fo_ids_used.append(foc.finance_org_id)

        foc_list_list = []
        for foc in distinctized_foc_list:
            ffields_val = []
            for ffield, _ in foc_fields:
                ffields_val.append(getattr(foc, ffield))
            foc_list_list.append(dict(
                finance_org=foc.finance_org,
                values=ffields_val,
            ))

        # kwargs['foc_list'] = distinctized_foc_list
        kwargs['foc_list'] = foc_list_list
        kwargs['foc_fields'] = foc_fields
        kwargs['proposed_fo_ids'] = IssueFinanceOrgPropose.objects.filter(
            issue=self.get_issue()).values_list('finance_org_id', flat=True)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        if self.get_issue() and 'issue_scoring' not in self.get_issue().editable_dashboard_views():
            return self.get(request, *args, **kwargs)

        send_to_all = request.POST.get('send_to_all', None)
        foid = request.POST.get('foid', None)
        if send_to_all:
            foc_list = FinanceOrgProductConditions.objects.filter(
                bg_44_contract_exec_interest_rate__isnull=False,
                bg_review_term_days__gt=0,
            )

            # distinctize by finance org
            foc_list = [x for x in foc_list]
            fo_ids_used = []
            distinctized_foc_list = []
            for foc in foc_list:
                if foc.finance_org_id not in fo_ids_used:
                    distinctized_foc_list.append(foc)
                    fo_ids_used.append(foc.finance_org_id)

            for foc in distinctized_foc_list:
                propose_qs = IssueFinanceOrgPropose.objects.filter(
                    finance_org_id=foc.finance_org_id, issue=self.get_issue())
                if not propose_qs.exists():
                    new_propose = IssueFinanceOrgPropose()
                    new_propose.finance_org = foc.finance_org
                    new_propose.issue = self.get_issue()
                    new_propose.save()

        elif foid:
            propose_qs = IssueFinanceOrgPropose.objects.filter(
                finance_org_id=foid, issue=self.get_issue())
            if not propose_qs.exists():
                new_propose = IssueFinanceOrgPropose()
                new_propose.finance_org_id = foid
                new_propose.issue = self.get_issue()
                new_propose.save()

        url = reverse('issue_scoring', args=args, kwargs=kwargs)
        get_params = request.GET.urlencode()
        if get_params:
            response = HttpResponseRedirect(url + '?' + get_params)
        else:
            response = HttpResponseRedirect(url)
        return response


class IssueAdditionalDocumentsRequestsView(IssueView):
    template_name = 'marer/issue/additional_documents_requests.html'

    def get(self, request, *args, **kwargs):
        proposes = IssueFinanceOrgPropose.objects.filter(issue=self.get_issue())
        kwargs['proposes'] = proposes
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        proposes_docs = IssueFinanceOrgProposeDocument.objects.filter(
            propose__issue=self.get_issue())
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
                break

            if pdoc_del_mark:
                pdoc.document = None
                pdoc.save(chain_docs_update=False)

        return self.get(request, *args, **kwargs)


class IssueAdditionalDocumentsRequestView(IssueView):
    template_name = 'marer/issue/additional_documents_request.html'

    def _get_clarification(self):
        clarif_id = self.kwargs.get('adrid', None)
        if clarif_id:
            clarification = get_object_or_404(IssueFinanceOrgProposeClarification, id=clarif_id)
            return clarification
        return None

    def get(self, request, *args, **kwargs):
        clarification = self._get_clarification()
        if clarification:
            kwargs['clarification'] = clarification
        else:
            propose_id = request.GET.get('pid', 0)
            kwargs['propose'] = get_object_or_404(IssueFinanceOrgPropose, id=propose_id)
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
            if not clarification:
                propose_id = request.GET.get('pid', 0)
                propose = get_object_or_404(IssueFinanceOrgPropose, id=propose_id)

                clarification = IssueFinanceOrgProposeClarification()
                clarification.initiator = consts.IFOPC_INITIATOR_ISSUER
                clarification.propose = propose
                clarification.save()

            new_msg = IssueFinanceOrgProposeClarificationMessage()
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

    def get(self, request, *args, **kwargs):
        formalizing_proposes = IssueFinanceOrgPropose.objects.filter(
            issue=self.get_issue(),
        ).exclude(
            formalize_note=''
        ).exclude(
            formalize_note__isnull=True
        )
        kwargs['formalizing_proposes'] = formalizing_proposes
        return super().get(request, *args, **kwargs)


class IssueFinishedView(IssueView):
    template_name = 'marer/issue/finished.html'

    def get(self, request, *args, **kwargs):
        final_proposes = IssueFinanceOrgPropose.objects.filter(
            issue=self.get_issue(),
            final_decision__isnull=False,
        ).order_by('-final_decision')
        kwargs['final_proposes'] = final_proposes
        return super().get(request, *args, **kwargs)


class IssueCancelledView(IssueView):
    template_name = 'marer/issue/cancelled.html'
