from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView

from marer.forms import IssueRegisteringForm
from marer.models import Issue, Issuer
from marer.models.finance_org import FinanceOrgProductConditions
from marer.models.issue import IssueFinanceOrgPropose
from marer.products import get_finance_products
from marer.views import StaticPagesContextMixin


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
            if self.get_issue():
                initial = dict(
                    product=self.get_issue().product,
                    org_search_name=self.get_issue().get_issuer_name(),
                    comment=self.get_issue().comment,
                )
            else:
                initial = dict()
            base_form = IssueRegisteringForm(initial=initial)
            kwargs.update(dict(
                base_form=base_form,
                issue=self.get_issue(),
                products=get_finance_products()
            ))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        base_form = IssueRegisteringForm(request.POST)
        if base_form.is_valid():
            # todo go to next stage if we can
            if not self.get_issue():
                issuer_name = base_form.cleaned_data['org_search_name']
                issuer = Issuer(
                    full_name=issuer_name,
                    short_name=issuer_name,
                    inn='0000000000',
                    kpp='000000000',
                    ogrn='0000000000000',
                    user=request.user,
                )
                issuer.save()

                new_issue = Issue(
                    issuer=issuer,
                    product=base_form.cleaned_data['product'],
                    status=Issue.STATUS_REGISTERING,
                    user=request.user,
                )  # todo set values
                new_issue.fill_from_issuer()
                self._issue = new_issue
            issue = self.get_issue()
            issue.comment = base_form.cleaned_data['comment']
            issue.save()
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
        fp_documents = self.get_issue().get_product().get_documents_list()
        for fpdoc in fp_documents:
            post_file = request.FILES.get(fpdoc.code, None)
            if post_file is not None:
                self.get_issue().update_common_issue_doc(fpdoc.code, post_file)
        return self.get(request, *args, **kwargs)


class IssueSurveyView(IssueView):
    template_name = 'marer/issue/survey.html'


class IssueScoringView(IssueView):
    template_name = 'marer/issue/scoring.html'

    def get(self, request, *args, **kwargs):
        foc_list = FinanceOrgProductConditions.objects.filter(
            bg_44_contract_exec_interest_rate__isnull=False,
            bg_review_term_days__gt=0,
        ).order_by('bg_44_contract_exec_interest_rate')

        # distinctize by finance org
        foc_list = [x for x in foc_list]
        fo_ids_used = []
        distinctized_foc_list = []
        for foc in foc_list:
            if foc.finance_org_id not in fo_ids_used:
                distinctized_foc_list.append(foc)
                fo_ids_used.append(foc.finance_org_id)

        kwargs['foc_list'] = distinctized_foc_list
        kwargs['proposed_fo_ids'] = IssueFinanceOrgPropose.objects.filter(
            issue=self.get_issue()).values_list('finance_org_id', flat=True)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

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


class IssueAdditionalDocumentsRequestView(IssueView):
    template_name = 'marer/issue/additional_documents_request.html'


class IssuePaymentsView(IssueView):
    template_name = 'marer/issue/payments.html'


class IssueFinishedView(IssueView):
    template_name = 'marer/issue/finished.html'


class IssueCancelledView(IssueView):
    template_name = 'marer/issue/cancelled.html'
