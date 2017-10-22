import datetime

from django.core.serializers.json import DjangoJSONEncoder


class CustomJSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%d.%m.%Y')
        return super().default(o)
