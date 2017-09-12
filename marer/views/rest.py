from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from marer.forms import RestTenderForm
from marer.serializers import TenderSerializer, TenderPublisherSerializer


class TenderDataView(APIView):
    def get(self, request, format=None):
        # TODO make errors on errors if occurs
        rtform = RestTenderForm(request.GET)
        if not rtform.is_valid():
            tdata = TenderSerializer()

        else:
            publisher = TenderPublisherSerializer(dict(
                full_name = 'ООО Тестовая организация',
                legal_address='Не дом и не улица',
                inn='0000000000',
                ogrn='000000000000',
                kpp='00000000',
            ))

            tdata = TenderSerializer(dict(
                gos_number='0000000000000000',
                law=TenderSerializer.LAW_44_FZ,
                placement_type='Открытый аукцион',
                publish_datetime=timezone.localtime(timezone.now()),
                start_cost=100500.00,
                application_ensure_cost=100.50,
                contract_execution_ensure_cost=10050.00,
                currency_code=TenderSerializer.CURRENCY_RUR,
                publisher=publisher.data,
            ))

        return Response(tdata.data)
