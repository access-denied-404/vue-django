from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from marer import consts
from marer.models import Issue, User
from marer.models.base import Document
from marer.models.issue import IssueOrgManagementCollegial, IssueOrgManagementDirectors, IssueOrgManagementOthers


class ReadOnlySerializer(serializers.Serializer):

    def create(self, validated_data):
        self.validated_data = validated_data
        # raise NotImplementedError('Not available for info requests')

    def update(self, instance, validated_data):
        raise NotImplementedError('Not available for info requests')


class TenderPublisherSerializer(ReadOnlySerializer):
    full_name = serializers.CharField(max_length=512)
    legal_address = serializers.CharField(max_length=512)
    inn = serializers.CharField()
    ogrn = serializers.CharField()
    kpp = serializers.CharField()


class TenderSerializer(ReadOnlySerializer):
    gos_number = serializers.CharField(max_length=32)
    law = serializers.ChoiceField(choices=[consts.TENDER_EXEC_LAW_44_FZ, consts.TENDER_EXEC_LAW_223_FZ])
    placement_type = serializers.CharField(max_length=512)
    publish_datetime = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    start_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    application_ensure_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    contract_execution_ensure_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency_code = serializers.ChoiceField(choices=[consts.CURRENCY_RUR, consts.CURRENCY_USD, consts.CURRENCY_EUR])
    publisher = TenderPublisherSerializer(many=False)


class IssueListSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ('id', 'product', 'bg_sum', 'issuer_short_name', 'issuer_inn', 'bg_doc',
                  'transfer_acceptance_act', 'contract_of_guarantee', 'status')


class ContractOfGuaranteeSerializer(ModelSerializer):

    class Meta:
        model = Document
        fields = ['file', 'sign', 'sign_state']


class TransferAcceptanceActSerializer(ModelSerializer):

    class Meta:
        model = Document
        fields = ['file', 'sign', 'sign_state']


class BGDocumentSerializer(ModelSerializer):

    class Meta:
        model = Document
        fields = ['file', 'sign', 'sign_state']


class IssueOrgManagementCollegialSerializer(ModelSerializer):

    class Meta:
        model = IssueOrgManagementCollegial
        fields = ['id', 'org_name', 'fio']


class IssueOrgManagementDirectorsSerializer(ModelSerializer):

    class Meta:
        model = IssueOrgManagementDirectors
        fields = ['id', 'org_name', 'fio']


class IssueOrgManagementOthersSerializer(ModelSerializer):

    class Meta:
        model = IssueOrgManagementOthers
        fields = ['id', 'org_name', 'fio']


class IssueSerializer(ModelSerializer):
    org_management_collegial = IssueOrgManagementCollegialSerializer(many=True)
    org_management_directors = IssueOrgManagementDirectorsSerializer(many=True)
    org_management_others = IssueOrgManagementOthersSerializer(many=True)
    bg_doc = BGDocumentSerializer()
    transfer_acceptance_act = TransferAcceptanceActSerializer()
    contract_of_guarantee = ContractOfGuaranteeSerializer()

    class Meta:
        model = Issue
        exclude = ('issuer', 'user',)


class ProfileSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone',)
