from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from marer import consts
from marer.models import Issue, User, Document
from marer.models.base import Document
from marer.models.issue import IssueOrgManagementCollegial, IssueOrgManagementDirectors, IssueOrgManagementOthers, \
    IssueOrgBeneficiaryOwner, IssueOrgBankAccount, IssueBGProdFounderPhysical, IssueBGProdFounderLegal, \
    IssueProposeDocument


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
        fields = ('id', 'product', 'bg_sum', 'issuer_short_name', 'issuer_inn', 'status')


class IssueBankCommission(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['bank_commission']


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


class IssueOrgBeneficiaryOwnerSerializer(ModelSerializer):

    class Meta:
        model = IssueOrgBeneficiaryOwner
        fields = ['id', 'fio', 'legal_address', 'fact_address', 'post_address', 'inn_or_snils', 'on_belong_to_pub_persons_info']


class IssueOrgBankAccountSerializer(ModelSerializer):

    class Meta:
        model = IssueOrgBankAccount
        fields = ['id', 'name', 'bik']


class IssueBGProdFounderPhysicalSerializer(ModelSerializer):

    class Meta:
        model = IssueBGProdFounderPhysical
        fields = ['id', 'fio', 'add_date', 'additional_business', 'country', 'auth_capital_percentage', 'address', 'passport_data']


class IssueBGProdFounderLegalSerializer(ModelSerializer):

    class Meta:
        model = IssueBGProdFounderLegal
        fields = ['id', 'name', 'add_date', 'additional_business', 'country', 'auth_capital_percentage', 'legal_address']


class DocumentSerializer(ModelSerializer):

    class Meta:
        model = Document
        fields = ['id', 'file', 'sign', 'sign_state']


class IssueProposeDocumentSerializer(ModelSerializer):
    document = DocumentSerializer()
    sample = DocumentSerializer()

    class Meta:
        model = IssueProposeDocument
        fields = ['id', 'name', 'document', 'sample', 'type', 'is_required', 'is_approved_by_manager']


class IssueSerializer(ModelSerializer):
    org_management_collegial = IssueOrgManagementCollegialSerializer(many=True)
    org_management_directors = IssueOrgManagementDirectorsSerializer(many=True)
    org_management_others = IssueOrgManagementOthersSerializer(many=True)
    org_beneficiary_owners = IssueOrgBeneficiaryOwnerSerializer(many=True)
    org_bank_accounts = IssueOrgBankAccountSerializer(many=True)
    issuer_founders_legal = IssueBGProdFounderLegalSerializer(many=True)
    issuer_founders_physical = IssueBGProdFounderPhysicalSerializer(many=True)
    application_doc = DocumentSerializer()
    propose_documents = IssueProposeDocumentSerializer(many=True)

    bg_contract_doc = DocumentSerializer()
    bg_doc = DocumentSerializer()
    transfer_acceptance_act = DocumentSerializer()
    payment_of_fee = DocumentSerializer()
    contract_of_guarantee = ContractOfGuaranteeSerializer()

    class Meta:
        model = Issue
        # exclude = ('issuer', 'user',)
        fields = ['org_management_collegial', 'org_management_directors',
                  'org_management_others', 'org_beneficiary_owners', 'org_bank_accounts',
                  'issuer_founders_legal', 'issuer_founders_physical', 'application_doc',
                  'propose_documents', 'bg_contract_doc', 'bg_doc', 'transfer_acceptance_act',
                  'payment_of_fee', 'contract_of_guarantee', 'bank_commission']


class IssueSecDepSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            'id',
            'is_positive_security_department_conclusion',
        )


class IssueLawyersDepSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            'id',
            'persons_can_acts_as_issuer_and_perms_term_info',
            'lawyers_dep_recommendations',
            'is_positive_lawyers_department_conclusion',
        )


class ProfileSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone',)
