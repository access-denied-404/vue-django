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
        if doc_id:
            propose_doc = IssueProposeDocument.objects.get(id=doc_id)
            propose_doc.document.delete()
            propose_doc.document_id = None
            propose_doc.document.save()
            propose_doc.save()
        else:
            if request.data.get('docList', []):
                doc_list = request.data.get('docList', [])
                if doc_list[0].get('type', 0) == 4:
                    for request_doc in doc_list:
                        for doc in issue.propose_documents_app:
                            if request_doc.get('name', '') == doc.name and not request_doc.get('document'):
                                    doc.document.delete()
                                    doc.document_id = None
                                    doc.document.save()
                                    doc.save()
                else:
                    return Response(issue)
        issue.save()
        return Response(issue)


class IssueReplaceDocument(APIView):
    def post(self, request, iid):
        issue = Issue.objects.get(id=iid)
        file = request.FILES.get('file')
        file_storage = FileSystemStorage()
        filename = file_storage.save('documents/{}/{}/{}/{}/{}'.format(
            year(), month(), day(), uuid.uuid4(), file.name), file)

        if request.data.get('id'):
            doc_id = request.data.get('id', None)
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
                issue.save()
        return Response(issue)

    def fill_document(self, document, filename):
        document.file = filename
        document.sign = None
        document.sign_state = consts.DOCUMENT_SIGN_NONE
        return document
