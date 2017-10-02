"""
All functions and classes described here are stubs.
All of it must be re-declared and re-implemented somewhere else.
"""
from django.utils import timezone

from marer import consts
from marer.models import Issuer
from marer.serializers import TenderPublisherSerializer, TenderSerializer


def create_stub_issuer(user_owner, issuer_name):
    issuer = Issuer(
        full_name=issuer_name,
        short_name=issuer_name,
        inn='0000000000',
        kpp='000000000',
        ogrn='0000000000000',
        user=user_owner,
    )
    issuer.save()
    return issuer


def get_serialized_tender():
    publisher = TenderPublisherSerializer(dict(
        full_name='ООО Тестовая организация',
        legal_address='Не дом и не улица',
        inn='0000000000',
        ogrn='000000000000',
        kpp='00000000',
    ))

    tender = TenderSerializer(dict(
        gos_number='0000000000000000',
        law=consts.TENDER_EXEC_LAW_44_FZ,
        placement_type='Открытый аукцион',
        publish_datetime=timezone.localtime(timezone.now()),
        start_cost=100500.00,
        application_ensure_cost=100.50,
        contract_execution_ensure_cost=10050.00,
        currency_code=consts.CURRENCY_RUR,
        publisher=publisher.data,
    ))
    return tender
