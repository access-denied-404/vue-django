import requests
from django.http import HttpResponseNotFound
from django.utils.dateparse import parse_datetime
from rest_framework.response import Response
from rest_framework.views import APIView

from marer.forms import RestTenderForm


class TenderDataView(APIView):
    def get(self, request, format=None):
        # TODO make errors on errors if occurs
        rtform = RestTenderForm(request.GET)
        if not rtform.is_valid():
            return HttpResponseNotFound()

        # tender = get_serialized_tender()
        gos_number = rtform.cleaned_data['gos_number']
        req = requests.get('https://inspectrum.su/rest/tender/' + gos_number)

        if req.status_code != 200:
            return HttpResponseNotFound()

        tdata = req.json()

        tdata['publish_datetime'] = parse_datetime(tdata['publish_datetime'])

        # return Response(tender.data)
        return Response(tdata)
