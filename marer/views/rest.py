import requests
from django.http import HttpResponseNotFound
from django.utils.dateparse import parse_datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib3.exceptions import MaxRetryError

from marer.forms import RestTenderForm, IssueBankCommissionForm
from marer.utils.issue import bank_commission


def _move_date_to_field(obj: dict, src_field: str, dst_field: str, del_src_field=True):
    src_date_raw = obj.get(src_field, None)
    try:
        src_date = parse_datetime(src_date_raw).strftime('%d.%m.%Y')
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
        try:
            req = requests.get('https://tender.marer.ru/rest/tender/' + gos_number)
            if req and req.status_code != 200:
                return HttpResponseNotFound()
            if req.text:
                tdata = req.json()

                _move_date_to_field(tdata, 'publish_datetime', 'publish_date')
                _move_date_to_field(tdata, 'open_datetime', 'collect_start_date')
                _move_date_to_field(tdata, 'close_datetime', 'collect_end_date')
                _move_date_to_field(tdata, 'finish_datetime', 'finish_date')
        except MaxRetryError:
            pass

        return Response(tdata)


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
