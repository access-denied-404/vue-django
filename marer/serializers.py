from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.utils import model_meta

from marer import consts
from marer.models import Issue, User, IssueClarificationMessage, IssueFinanceOrgProposeClarificationMessageDocument
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
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = IssueOrgManagementCollegial
        fields = ['id', 'org_name', 'fio']


class IssueOrgManagementDirectorsSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = IssueOrgManagementDirectors
        fields = ['id', 'org_name', 'fio']


class IssueOrgManagementOthersSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = IssueOrgManagementOthers
        fields = ['id', 'org_name', 'fio']


class IssueOrgBeneficiaryOwnerSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = IssueOrgBeneficiaryOwner
        fields = ['id', 'fio', 'legal_address', 'fact_address', 'post_address', 'inn_or_snils']


class IssueOrgBankAccountSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = IssueOrgBankAccount
        fields = ['id', 'name', 'bik']


class IssueBGProdFounderPhysicalSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = IssueBGProdFounderPhysical
        fields = ['id', 'fio', 'add_date', 'additional_business', 'country', 'auth_capital_percentage', 'address', 'passport_data']


class IssueBGProdFounderLegalSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = IssueBGProdFounderLegal
        fields = ['id', 'name', 'add_date', 'additional_business', 'country', 'auth_capital_percentage', 'legal_address']


class DocumentSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Document
        fields = ['id', 'file', 'sign', 'sign_state']


class IssueProposeDocumentSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    document = DocumentSerializer()
    sample = DocumentSerializer()
    visible = serializers.BooleanField(default=True)

    class Meta:
        model = IssueProposeDocument
        fields = ['id', 'name', 'document', 'sample', 'type', 'is_required', 'is_approved_by_manager', 'visible']


class IssueSerializer(ModelSerializer):
    org_management_collegial = IssueOrgManagementCollegialSerializer(many=True)
    org_management_directors = IssueOrgManagementDirectorsSerializer(many=True)
    org_management_others = IssueOrgManagementOthersSerializer(many=True)
    org_beneficiary_owners = IssueOrgBeneficiaryOwnerSerializer(many=True)
    org_bank_accounts = IssueOrgBankAccountSerializer(many=True)
    issuer_founders_legal = IssueBGProdFounderLegalSerializer(many=True)
    issuer_founders_physical = IssueBGProdFounderPhysicalSerializer(many=True)
    application_doc = DocumentSerializer(read_only=True)
    propose_documents = IssueProposeDocumentSerializer(many=True, read_only=True)

    bg_contract_doc = DocumentSerializer()
    bg_doc = DocumentSerializer()
    transfer_acceptance_act = DocumentSerializer()
    payment_of_fee = DocumentSerializer()
    approval_and_change_sheet = DocumentSerializer()
    contract_of_guarantee = ContractOfGuaranteeSerializer()
    bank_commission = serializers.CharField(max_length=512)

    def update(self, instance, validated_data):
        related_fields = [
            'org_management_collegial', 'org_management_directors', 'org_management_others',
            'org_beneficiary_owners', 'org_bank_accounts', 'issuer_founders_legal',
            'issuer_founders_physical'
        ]
        for field in related_fields:
            ids = []
            for data in validated_data[field]:
                id = data.pop('id')
                if id:
                    getattr(instance, field).filter(id=id).update(**data)
                    ids.append(id)
                else:
                    obj = getattr(instance, field).create(**data)
                    ids.append(obj.id)
            getattr(instance, field).exclude(id__in=ids).delete()
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if not (attr in info.relations and info.relations[attr].to_many):
                setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = Issue
        exclude = ('issuer', 'user', 'product')
        read_only_fields = ('created_at', 'updated_at')


class ProfileSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone',)


class IssueMessageDocumentLink(ModelSerializer):
    document = DocumentSerializer()

    class Meta:
        model = IssueFinanceOrgProposeClarificationMessageDocument
        fields = ('id', 'name', 'document')


class IssueClarificationMessagesSerializer(ModelSerializer):
    documents_links = IssueMessageDocumentLink(many=True)
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = IssueClarificationMessage
        fields = ('id', 'message', 'user', 'documents_links', 'created_at')


class IssueMessagesSerializer(ModelSerializer):
    clarification_messages = IssueClarificationMessagesSerializer(many=True)

    class Meta:
        model = Issue
        fields = ('id', 'clarification_messages')


class IssueSecDepSerializer(ModelSerializer):
    sec_dep_conclusion_doc = DocumentSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = (
            'id',
            'is_positive_security_department_conclusion',
            'sec_dep_conclusion_doc',
        )


class IssueDocOpsSerializer(ModelSerializer):
    doc_ops_mgmt_conclusion_doc = DocumentSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = (
            'id',
            'bg_sum',
            'is_issuer_all_bank_liabilities_less_than_max',
            'is_issuer_executed_contracts_on_44_or_223_or_185_fz',
            'is_issuer_executed_goverment_contract_for_last_3_years',
            'is_contract_has_prepayment',
            'is_issuer_executed_contracts_with_comparable_advances',
            'is_issuer_executed_gte_5_contracts_on_44_or_223_or_185_fz',
            'is_issuer_last_year_revenue_higher_in_5_times_than_all_bank_bgs',
            'is_issuer_has_garantor_for_advance_related_requirements',
            'is_contract_price_reduction_lower_than_50_pct_on_supply_contract',
            'is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets',
            'is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets',
            'is_need_to_check_real_of_issuer_activity',
            'is_real_of_issuer_activity_confirms',
            'is_contract_corresponds_issuer_activity',
            'contract_advance_requirements_fails',
            'is_issuer_has_bad_credit_history',
            'is_issuer_has_blocked_bank_account',
            'total_bank_liabilities_vol',
            'doc_ops_mgmt_conclusion_doc'
        )


class IssueLawyersDepSerializer(ModelSerializer):
    lawyers_dep_conclusion_doc = DocumentSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = (
            'id',
            'persons_can_acts_as_issuer_and_perms_term_info',
            'lawyers_dep_recommendations',
            'is_positive_lawyers_department_conclusion',
            'lawyers_dep_conclusion_doc',
        )
