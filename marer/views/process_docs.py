import uuid

from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import FileSystemStorage
from marer import consts

from marer.models.issue import Issue, IssueProposeDocument
from marer.models.base import Document
from marer.utils.datetime_utils import year, day, month


class IssueDeleteDocument(APIView):
    def post(self, request, iid):
        issue = Issue.objects.get(id=iid)
        doc_id = request.data.get('id', None)
        index = request.data.get('index', None)
        if doc_id:
            propose_doc = IssueProposeDocument.objects.get(id=doc_id)
            propose_doc.document.delete()
            propose_doc.document_id = None
            propose_doc.document.save()
            propose_doc.save()
        elif index or index == 0:
            ind = int(index)
            if ind == 0:
                issue.application_doc.delete()
                issue.application_doc_id = None
            elif ind == 1:
                issue.bg_doc.delete()
                issue.bg_doc = None
            elif ind == 2:
                issue.payment_of_fee.delete()
                issue.payment_of_fee = None
            elif ind == 3:
                issue.transfer_acceptance_act.delete()
                issue.transfer_acceptance_act = None
            elif ind == 4:
                issue.contract_of_guarantee.delete()
                issue.contract_of_guarantee = None
            elif ind == 5:
                issue.approval_and_change_sheet.delete()
                issue.approval_and_change_sheet = None
            else:
                return Response('document index out of range')
        issue.save()
        return Response('issue {} saved'.format(issue.id))


class IssueReplaceDocument(APIView):
    def post(self, request, iid):
        issue = Issue.objects.get(id=iid)
        file = request.FILES.get('file')
        file_storage = FileSystemStorage()
        filename = file_storage.save('documents/{}/{}/{}/{}/{}'.format(
            year(), month(), day(), uuid.uuid4(), file.name), file)
        doc_id = request.data.get('id', None)
        type = request.data.get('type', None)
        if doc_id and doc_id != 'null' and type != '4':
            if doc_id and filename:
                propose_doc = IssueProposeDocument.objects.get(id=doc_id)
                if propose_doc.document:
                    self.fill_document(propose_doc.document, filename)
                    propose_doc.document.save()
                    propose_doc.save()
                else:
                    propose_doc.document = Document()
                    self.fill_document(propose_doc.document, filename)
                    propose_doc.document.save()
                    propose_doc.document_id = propose_doc.document.id
                    propose_doc.save()
        elif type == '4':
            index = request.data.get('index', None)
            ind = int(index)
            if index and file:
                if ind == 0:
                    if not issue.application_doc:
                        issue.application_doc = Document()
                    self.fill_document(issue.application_doc, filename)
                    issue.application_doc.save()
                    issue.application_doc_id = issue.application_doc.id
                elif ind == 1:
                    if not issue.bg_doc:
                        issue.bg_doc = Document()
                    self.fill_document(issue.bg_doc, filename)
                    issue.bg_doc.save()
                    issue.bg_doc_id = issue.bg_doc.id
                elif ind == 2:
                    if not issue.payment_of_fee:
                        issue.payment_of_fee = Document()
                    self.fill_document(issue.payment_of_fee, filename)
                    issue.payment_of_fee.save()
                    issue.payment_of_fee_id = issue.payment_of_fee.id
                elif ind == 3:
                    if not issue.transfer_acceptance_act:
                        issue.transfer_acceptance_act = Document()
                    self.fill_document(issue.transfer_acceptance_act, filename)
                    issue.transfer_acceptance_act.save()
                    issue.transfer_acceptance_act_id = issue.transfer_acceptance_act.id
                elif ind == 4:
                    if not issue.contract_of_guarantee:
                        issue.contract_of_guarantee = Document()
                    self.fill_document(issue.contract_of_guarantee, filename)
                    issue.contract_of_guarantee.save()
                    issue.contract_of_guarantee_id = issue.contract_of_guarantee.id
                elif ind == 5:
                    if not issue.approval_and_change_sheet:
                        issue.approval_and_change_sheet = Document()
                    self.fill_document(issue.approval_and_change_sheet, filename)
                    issue.approval_and_change_sheet.save()
                    issue.approval_and_change_sheet_id = issue.approval_and_change_sheet.id
                else:
                    return Response('document index out of range')
        issue.save()
        return Response('issue {} saved'.format(issue.id))

    def fill_document(self, document, filename):
        document.file = filename
        document.sign = None
        document.sign_state = consts.DOCUMENT_SIGN_NONE

