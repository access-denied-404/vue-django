import importlib
import json
from tempfile import NamedTemporaryFile

import os
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, RedirectView
from django.views.generic.base import ContextMixin

from marer import consts
from marer.forms import IssueRegisteringForm, IFOPCMessageForm, LoginSignForm
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
            self.pattern_name = 'issue_finished'

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
            url = reverse('issue_scoring', args=[self.get_issue().id])
            return HttpResponseRedirect(url)
        else:
            return self.get(request, *args, **kwargs)


class IssueRemoteSignView(TemplateView, ContextMixin, View):
    _issue = None

    def get_context_data(self, **kwargs):
        kwargs['cert_hash'] = self.get_cert_thumb()
        kwargs['consts'] = consts
        kwargs['issue'] = self.get_issue()
        return super().get_context_data(**kwargs)

    def get_issue(self):
        if self._issue is not None:
            return self._issue

        iid = self.kwargs.get('iid', None)
        if iid is not None:
            # fixme maybe make error 403?
            issue = get_object_or_404(Issue, id=iid)
            self._issue = issue
            return issue

    def get_cert_thumb(self):
        dta = self.request.COOKIES.get('cert_thumb', None)
        if not dta:
            dta = self.request.session.get('cert_thumb', None)
        return dta

    def get_cert_sign(self):
        dta = self.request.COOKIES.get('cert_sign', None)
        if not dta:
            dta = self.request.session.get('cert_sign', None)
        return dta

    def is_authenticated_by_cert(self):
        thumb = self.get_cert_thumb()
        sign = self.get_cert_sign()
        # todo check INN for cert and issue issuer
        if thumb and sign:
            return True
        else:
            return False

    def get(self, request, *args, **kwargs):
        if not self.is_authenticated_by_cert():
            self.template_name = 'marer/auth/remote_sign_login.html'
            login_form = LoginSignForm()
            if 'login_form' not in kwargs:
                kwargs.update(dict(login_form=login_form))
        else:
            self.template_name = 'marer/issue/remote_sign_docs.html'
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.is_authenticated_by_cert():
            login_form = LoginSignForm(request.POST)
            if login_form.is_valid():
                request.COOKIES['cert_thumb'] = login_form.cleaned_data['cert']
                request.COOKIES['cert_sign'] = login_form.cleaned_data['signature']
                request.session['cert_thumb'] = login_form.cleaned_data['cert']
                request.session['cert_sign'] = login_form.cleaned_data['signature']

                url = reverse('issue_remote_for_sign', args=[self.get_issue().id])
                response = HttpResponseRedirect(url)
                # response.set_cookie('cert_thumb', login_form.cleaned_data['cert'])
                # response.set_cookie('cert_thumb', login_form.cleaned_data['signature'])
                return response
        return self.get(request, args, kwargs)


class IssueScoringView(IssueView):
    template_name = 'marer/issue/scoring.html'

    def post(self, request, *args, **kwargs):

        if self.get_issue() and 'issue_scoring' not in self.get_issue().editable_dashboard_views():
            return self.get(request, *args, **kwargs)

        # todo add issue form signing
        self.get_issue().refresh_from_db()
        if self.get_issue().status == consts.ISSUE_STATUS_REGISTERING:
            self.get_issue().status = consts.ISSUE_STATUS_REVIEW
            self.get_issue().fill_application_doc(commit=False)
            self.get_issue().save()
        notify_user_manager_about_user_updated_issue(self.get_issue())
        url = reverse('issue_additional_documents_requests', args=[self.get_issue().id])
        return HttpResponseRedirect(url)


class IssueAdditionalDocumentsRequestsView(IssueView):
    template_name = 'marer/issue/additional_documents_requests.html'

    def get_context_data(self, **kwargs):
        kwargs['consts'] = consts
        return super().get_context_data(**kwargs)

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


class IssueFinishedView(IssueView):
    template_name = 'marer/issue/finished.html'

    def get_context_data(self, **kwargs):
        kwargs['consts'] = consts
        return super().get_context_data(**kwargs)


class IssueCancelledView(IssueView):
    template_name = 'marer/issue/cancelled.html'


class IssueAdditionalDocumentSignView(LoginRequiredMixin, ContextMixin, View):
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

    def post(self, request, *args, **kwargs):
        doc_id = request.POST.get('document', None)
        doc = None
        sign = request.POST.get('signature', '')
        response_dict = dict(
            document=doc_id,
            sign_state=consts.DOCUMENT_SIGN_NONE,
        )
        if doc_id and self.get_issue().propose_documents.filter(document_id=doc_id).exists():
            pdoc = IssueProposeDocument.objects.filter(document_id=doc_id)[0]
            doc = pdoc.document

        raw_check_sign_class = settings.FILE_SIGN_CHECK_CLASS
        if raw_check_sign_class is not None and raw_check_sign_class != '':
            raw_check_sign_class = str(raw_check_sign_class)
            check_sign_module_name, check_sign_class_name = raw_check_sign_class.rsplit('.', 1)
            check_sign_module = importlib.import_module(check_sign_module_name)
            check_sign_class = getattr(check_sign_module, check_sign_class_name)

            temp_sign_file = NamedTemporaryFile(delete=False)
            sign_bytes = sign.encode('utf-8')
            temp_sign_file.write(sign_bytes)
            try:
                sign_is_correct = check_sign_class.check_file_sign(doc.file.path, temp_sign_file.name)
            except Exception:
                sign_is_correct = False
            if sign_is_correct:
                final_sign_file = ContentFile(sign_bytes)
                final_sign_file.name = os.path.basename(doc.file.name) + '.sig'
                doc.sign = final_sign_file
                doc.save()
                response_dict['sign_state'] = consts.DOCUMENT_SIGN_VERIFIED
            else:
                response_dict['sign_state'] = consts.DOCUMENT_SIGN_CORRUPTED
            temp_sign_file.close()
            os.unlink(temp_sign_file.name)
        return HttpResponse(json.dumps(response_dict), content_type="application/json")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class IssueRemoteDocumentSignView(ContextMixin, View):
    _issue = None

    def get_issue(self):
        if self._issue is not None:
            return self._issue

        iid = self.kwargs.get('iid', None)
        if iid is not None:
            # fixme maybe make error 403?
            issue = get_object_or_404(Issue, id=iid)
            self._issue = issue
            return issue

    def get_context_data(self, **kwargs):
        kwargs.update(dict(issue=self.get_issue()))
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        doc_id = request.POST.get('document', None)
        doc = None
        sign = request.POST.get('signature', '')
        response_dict = dict(
            document=doc_id,
            sign_state=consts.DOCUMENT_SIGN_NONE,
        )
        if doc_id and self.get_issue().propose_documents.filter(document_id=doc_id).exists():
            pdoc = IssueProposeDocument.objects.filter(document_id=doc_id)[0]
            doc = pdoc.document

        raw_check_sign_class = settings.FILE_SIGN_CHECK_CLASS
        if raw_check_sign_class is not None and raw_check_sign_class != '':
            raw_check_sign_class = str(raw_check_sign_class)
            check_sign_module_name, check_sign_class_name = raw_check_sign_class.rsplit('.', 1)
            check_sign_module = importlib.import_module(check_sign_module_name)
            check_sign_class = getattr(check_sign_module, check_sign_class_name)

            temp_sign_file = NamedTemporaryFile(delete=False)
            sign_bytes = sign.encode('utf-8')
            temp_sign_file.write(sign_bytes)
            try:
                sign_is_correct = check_sign_class.check_file_sign(doc.file.path, temp_sign_file.name)
            except Exception:
                sign_is_correct = False
            if sign_is_correct:
                final_sign_file = ContentFile(sign_bytes)
                final_sign_file.name = os.path.basename(doc.file.name) + '.sig'
                doc.sign = final_sign_file
                doc.save()
                response_dict['sign_state'] = consts.DOCUMENT_SIGN_VERIFIED
            else:
                response_dict['sign_state'] = consts.DOCUMENT_SIGN_CORRUPTED
            temp_sign_file.close()
            os.unlink(temp_sign_file.name)
        return HttpResponse(json.dumps(response_dict), content_type="application/json")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
