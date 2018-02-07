import requests
from django.http import HttpResponseNotFound
from django.utils.dateparse import parse_datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib3.exceptions import MaxRetryError

from marer.models import Issue
from marer.serializers import ProfileSerializer, IssueListSerializer, IssueSerializer
from marer import consts
from marer.forms import RestTenderForm, IssueBankCommissionForm
from marer.utils.issue import bank_commission


def _parse_date(src_date_raw):
    return parse_datetime(src_date_raw).strftime('%d.%m.%Y')


def _move_date_to_field(obj: dict, src_field: str, dst_field: str, del_src_field=True):
    src_date_raw = obj.get(src_field, None)
    try:
        src_date = _parse_date(src_date_raw)
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
        tdata = {}
        tender_data = {}

        if gos_number.startswith('http://zakupki.gov.ru/'):
            gos_number = gos_number.split('=', 1)[1]

        try:
            if len(gos_number) == 19:
                req = requests.get('http://tender.marer.ru:8090/tender44?gosNumber=' + gos_number)
                if req and req.status_code != 200:
                    return HttpResponseNotFound()
                if req.text:
                    tdata = req.json()

                lot_data = tdata.get('lot', None)
                if not lot_data:
                    lots = lot_data.get('lots', [])
                    if len(lots) > 0:
                        lot_data = lots[0]

                requirements = lot_data.get('customerRequirements', [])
                cust_req_data = {}
                if len(requirements) > 0:
                    cust_req_data = requirements[0]

                collecting_data = tdata.get('procedureInfo', {}).get('collecting', {})
                if len(collecting_data) == 0:
                    collecting_data = None

                if tdata.get('purchaseResponsible', {}).get('responsibleRole', '') == 'CU':
                    publisher = dict(
                        full_name=tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('fullName'),
                        legal_address=tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('factAddress'),
                        inn=tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('inn'),
                        kpp=tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('kpp'),
                    )
                    beneficiary_reg_number = tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('regNum')
                else:
                    publisher = dict()
                    beneficiary_reg_number = cust_req_data.get('customer', {}).get('regNum')

                req = requests.get('http://tender.marer.ru:8090/tender44org?regNumber=' + beneficiary_reg_number)
                if req and req.status_code != 200:
                    pass
                if req.text:
                    bdata = req.json()

                    publisher_additional = dict(
                        full_name=bdata.get('fullName'),
                        legal_address=bdata.get('postalAddress'),
                        ogrn=bdata.get('ogrn'),
                        inn=bdata.get('inn'),
                        kpp=bdata.get('kpp'),
                    )
                    publisher.update(publisher_additional)

                tender_data = dict(
                    gos_number=tdata.get('gosNumber'),
                    law=consts.TENDER_EXEC_LAW_44_FZ,
                    description=tdata.get('purchaseObjectInfo'),
                    placement_type=tdata.get('placingWay', {}).get('name'),
                    publish_date=_parse_date(tdata.get('publishDate')),
                    collect_start_date=_parse_date(collecting_data.get('startDate')) if collecting_data else None,
                    collect_end_date=_parse_date(collecting_data.get('endDate')) if collecting_data else None,
                    finish_date=None,
                    start_cost=lot_data.get('maxPrice'),
                    application_ensure_cost=cust_req_data.get('applicationGuarantee', {}).get('amount', None) if cust_req_data.get('applicationGuarantee', None) else None,
                    contract_execution_ensure_cost=cust_req_data.get('contractGuarantee', {}).get('amount', None) if cust_req_data.get('contractGuarantee', None) else None,
                    currency_code=consts.CURRENCY_RUR,
                    publisher=publisher,
                )

            elif len(gos_number) == 11:
                req = requests.get('http://tender.marer.ru:8090/tender223?gosNumber=' + gos_number)
                if req and req.status_code != 200:
                    return HttpResponseNotFound()
                if req.text:
                    tdata = req.json()

                publisher = dict(
                    full_name=tdata.get('customer', {}).get('mainInfo', {}).get('fullName', ''),
                    legal_address=tdata.get('customer', {}).get('mainInfo', {}).get('fullName', ''),
                    ogrn=tdata.get('customer', {}).get('mainInfo', {}).get('ogrn', ''),
                    inn=tdata.get('customer', {}).get('mainInfo', {}).get('inn', ''),
                    kpp=tdata.get('customer', {}).get('mainInfo', {}).get('kpp', ''),
                )

                tender_data = dict(
                    gos_number=tdata.get('purchaseNumber'),
                    law=consts.TENDER_EXEC_LAW_223_FZ,
                    description=tdata.get('purchaseObjectInfo'),
                    placement_type=tdata.get('placingWayName'),
                    publish_date=_parse_date(tdata.get('publishDate')),
                    collect_start_date=None,
                    collect_end_date=None,
                    finish_date=None,
                    start_cost=tdata.get('lots', [])[0].get('lotData', {}).get('initialSum'),
                    application_ensure_cost=None,
                    contract_execution_ensure_cost=None,
                    currency_code=consts.CURRENCY_RUR,
                    publisher=publisher,
                )

        except MaxRetryError:
            pass

        return Response(tender_data)


class IssueBankCommissionView(APIView):
    def get(self, request, format=None):
        form = IssueBankCommissionForm(request.GET)
        if form.is_valid():
            commission = bank_commission(
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
        issues_qs = Issue.objects.filter(user_id=request.user.id)
        ilist_ser = IssueListSerializer(issues_qs, many=True)
        return Response(ilist_ser.data)


class IssueView(APIView):
    def get(self, request, iid, format=None):
        issue = Issue.objects.get(id=iid)
        ser = IssueSerializer(issue)
        return Response(ser.data)


class ProfileView(APIView):
    def get(self, request, format=None):
        user_ser = ProfileSerializer(request.user)
        return Response(user_ser.data)
