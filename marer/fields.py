from django.forms import DecimalField


class BalanceCodeDecimalField(DecimalField):
    
    def to_python(self, value):
        if isinstance(value, str) and value.startswith('(') and value.endswith(')'):
            value = '-%s' % (value[1:-1])
        return super(BalanceCodeDecimalField, self).to_python(value)