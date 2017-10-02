from rest_framework import serializers


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
    LAW_44_FZ = '44_fz'
    LAW_223_FZ = '223_fz'
    LAW_185_FZ = '185_fz'

    CURRENCY_RUR = 'rur'
    CURRENCY_USD = 'usd'
    CURRENCY_EUR = 'eur'

    gos_number = serializers.CharField(max_length=32)
    law = serializers.ChoiceField(choices=[LAW_44_FZ, LAW_223_FZ, LAW_185_FZ])
    placement_type = serializers.CharField(max_length=512)
    publish_datetime = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    start_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    application_ensure_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    contract_execution_ensure_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency_code = serializers.ChoiceField(choices=[CURRENCY_RUR, CURRENCY_USD, CURRENCY_EUR])
    publisher = TenderPublisherSerializer(many=False)
