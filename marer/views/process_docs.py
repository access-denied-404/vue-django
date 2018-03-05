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
        doc_list = request.data.get('body', [])
        server_doc_list_by_type = get_documents_by_type(issue, doc_list[0].get('type', 0))
        if server_doc_list_by_type:
            for doc in doc_list:
                if not doc.get('document', []):
                    for propose_doc in server_doc_list_by_type:
                        if propose_doc.document and propose_doc.id is doc.get('id', 0):
                            propose_doc.document.delete()
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
                propose_doc.document.file = filename
                propose_doc.document.sign_state = consts.DOCUMENT_SIGN_NONE
                propose_doc.document.sign = None
                propose_doc.document.save()
                issue.save()
        return Response(issue)


def get_documents_by_type(issue, type):
    document_list_by_type = []
    if type == 1:
        document_list_by_type = issue.propose_documents_leg
    elif type == 2:
        document_list_by_type = issue.propose_documents_fin
    elif type == 3:
        document_list_by_type = issue.propose_documents_oth
    elif type == 4:
        document_list_by_type = issue.propose_documents_app
    return document_list_by_type
