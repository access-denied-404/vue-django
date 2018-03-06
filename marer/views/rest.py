import io

from django.core.exceptions import ValidationError
from django.http import HttpResponseNotFound, HttpResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView, View

from marer.models import Issue
from marer.serializers import ProfileSerializer, IssueListSerializer, IssueSerializer, IssueSecDepSerializer, \
    IssueLawyersDepSerializer, IssueMessagesSerializer, IssueDocOpsSerializer, DocumentSerializer
from marer.forms import RestTenderForm, IssueBankCommissionForm
from marer.utils.issue import calculate_bank_commission, zip_docs
from marer.utils.other import parse_date_to_frontend_format, get_tender_info


def _move_date_to_field(obj: dict, src_field: str, dst_field: str, del_src_field=True):
    src_date_raw = obj.get(src_field, None)
    try:
        src_date = parse_date_to_frontend_format(src_date_raw)
    except TypeError:
        src_date = None
    obj[dst_field] = src_date

    if del_src_field:
        del obj[src_field]


class TenderDataView(APIView):
    def get(self, request, format=None):
        rtform = RestTenderForm(request.GET)
        if not rtform.is_valid():
            return HttpResponseNotFound()

        gos_number = rtform.cleaned_data['gos_number']
        tender_data = get_tender_info(gos_number)
        return Response(tender_data)


class IssueBankCommissionView(APIView):
    def get(self, request, format=None):
        form = IssueBankCommissionForm(request.GET)
        if form.is_valid():
            commission = calculate_bank_commission(
                form.cleaned_data['bg_start_date'],
                form.cleaned_data['bg_end_date'],
                form.cleaned_data['bg_sum'],
                form.cleaned_data['bg_is_benefeciary_form'],
                form.cleaned_data['bg_type'],
                form.cleaned_data['tender_exec_law'],
                form.cleaned_data['tender_has_prepayment']
            )
            return Response({
                'status': True,
                "commission": commission
            })
        else:

            return Response({
                'status': False,
                'errors': form.errors,
            })


class IssuesView(APIView):
    def get(self, request, format=None):
        if request.user.is_superuser:
            issues_qs = Issue.objects.all()
        elif request.user.is_staff:
            issues_qs = Issue.objects.filter(manager_id=request.user.id)
        elif request.user.is_authenticated:
            issues_qs = Issue.objects.filter(user_id=request.user.id)
        else:
            issues_qs = Issue.objects.none()
        ilist_ser = IssueListSerializer(issues_qs, many=True)
        return Response(ilist_ser.data)


class DocsZipView(View):

    def get(self, request, iid):
        type = request.GET.get('group', '')
        issue = Issue.objects.get(id=iid)
        if type == '1':
            response = self.calculate_response(issue.propose_documents_leg)
            response['Content-Disposition'] = 'attachment; filename=leg_docs_for_issue_{}.zip'.format(str(issue.id))
        elif type == '2':
            response = self.calculate_response(issue.propose_documents_fin)
            response['Content-Disposition'] = 'attachment; filename=fin_docs_for_issue_{}.zip'.format(str(issue.id))
        elif type == '3':
            response = self.calculate_response(issue.propose_documents_oth)
            response['Content-Disposition'] = 'attachment; filename=oth_docs_for_issue_{}.zip'.format(str(issue.id))
        elif type == '4':
            response = self.calculate_response(issue.propose_documents_app)
            response['Content-Disposition'] = 'attachment; filename=acts_for_issue_{}.zip'.format(str(issue.id))
        else:
            response = HttpResponse('')
        return response

    def calculate_response(self, doc_list):
        file = zip_docs(doc_list)
        resp = HttpResponse(file, content_type='application/zip')
        return resp


class IssueBaseAPIView(APIView):
    serializer = IssueSerializer

    def get(self, request, iid, format=None):
        issue = Issue.objects.get(id=iid)
        ser = self.serializer(issue)
        return Response(ser.data)

    def post(self, request, iid):
        issue = Issue.objects.get(id=iid)
        ser = self.serializer(issue, data=request.data['body'])
        if ser.is_valid():
            ser.save()
            self.issue_post_save(request, issue)
            return Response(ser.data)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def issue_post_save(self, request, issue):
        pass


class IssueView(IssueBaseAPIView):
    serializer = IssueSerializer


class IssueSecDepView(IssueBaseAPIView):
    serializer = IssueSecDepSerializer


class IssueDocOpsView(IssueBaseAPIView):
    serializer = IssueDocOpsSerializer


class IssueGenerateDocOpsView(IssueBaseAPIView):
    serializer = IssueDocOpsSerializer

    def post(self, request, iid):
        issue = Issue.objects.get(id=iid)
        errors = []
        try:
            issue.fill_doc_ops_mgmt_conclusion(user=request.user)
            ser = self.serializer(issue, data=request.data['body'])
            if ser.is_valid():
                return Response(ser.data)
            else:
                errors = ser.errors
        except ValidationError as ve:
            if len(ve.error_list) > 0:
                for err in ve.error_list:
                    errors.append(err)
        except (ValueError, TypeError):
            errors.append('Заключение УРДО заполнить невозможно')

        return Response({
            'errors': errors
        }, status=status.HTTP_400_BAD_REQUEST)


class IssueGenerateLawyersDepConclusionDocView(APIView):
    serializer = IssueLawyersDepSerializer

    def post(self, request, iid):
        issue = Issue.objects.get(id=iid)
        errors = []
        try:
            issue.fill_lawyers_dep_conclusion(user=request.user)
            ser = self.serializer(issue, data=request.data['body'])
            if ser.is_valid():
                return Response(ser.data)
            else:
                errors = ser.errors
        except ValidationError as ve:
            errors = ve.error_list
        except (ValueError, TypeError):
            errors.append('Заключение ПУ заполнить невозможно')
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class IssueSecDepMgmtView(IssueBaseAPIView):
    serializer = IssueSecDepSerializer

    def post(self, request, iid):
        issue = Issue.objects.get(id=iid)
        errors = []
        try:
            issue.fill_sec_dep_conclusion_doc(user=request.user)
            ser = self.serializer(issue, data=request.data['body'])
            if ser.is_valid():
                return Response(ser.data)
            else:
                errors = ser.errors
        except ValidationError as ve:
            errors = ve.error_list
        except (ValueError, TypeError):
            errors.append('Заключение ДБ заполнить невозможно')
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

class IssueLawyersDepView(IssueBaseAPIView):
    serializer = IssueLawyersDepSerializer

    def issue_post_save(self, request, issue):
        if 'generate' in self.request.GET:
            issue.fill_lawyers_dep_conclusion(commit=True)


class IssueMessagesView(IssueBaseAPIView):
    parser_classes = (MultiPartParser,)
    serializer = IssueMessagesSerializer


class ProfileView(APIView):
    def get(self, request, format=None):
        user_ser = ProfileSerializer(request.user)
        return Response(user_ser.data)
