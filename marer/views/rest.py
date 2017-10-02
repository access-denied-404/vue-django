from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from marer.forms import RestTenderForm
from marer.serializers import TenderSerializer, TenderPublisherSerializer
from marer.stub import get_serialized_tender


class TenderDataView(APIView):
    def get(self, request, format=None):
        # TODO make errors on errors if occurs
        rtform = RestTenderForm(request.GET)
        if not rtform.is_valid():
            tender = TenderSerializer()

        else:
            tender = get_serialized_tender()

        return Response(tender.data)
