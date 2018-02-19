from django.http import HttpResponseNotFound
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from marer.models import Issue
from marer.serializers import ProfileSerializer, IssueListSerializer, IssueSerializer, IssueSecDepSerializer, \
    IssueLawyersDepSerializer
from marer.forms import RestTenderForm, IssueBankCommissionForm
from marer.utils.issue import calculate_bank_commission
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


class IssueBaseAPIView(APIView):
    serializer = IssueSerializer

    def get(self, request, iid, format=None):
        issue = Issue.objects.get(id=iid)
        ser = self.serializer(issue)
        return Response(ser.data)

    def post(self, request, iid):
        issue = Issue.objects.get(id=iid)
        ser = self.serializer(issue, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueView(IssueBaseAPIView):
    serializer = IssueSerializer


class IssueSecDepView(IssueBaseAPIView):
    serializer = IssueSecDepSerializer


class IssueLawyersDepView(IssueBaseAPIView):
    serializer = IssueLawyersDepSerializer


class ProfileView(APIView):
    def get(self, request, format=None):
        user_ser = ProfileSerializer(request.user)
        return Response(user_ser.data)
