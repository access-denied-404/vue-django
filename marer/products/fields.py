from decimal import Decimal, DecimalException

from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import DecimalField
from django.utils import formats
from django.utils.encoding import force_text


class DecimalForcedThousandsGroupedField(DecimalField):

    def to_python(self, value):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values. Ensures that there are no more
        than max_digits in the number, and no more than decimal_places digits
        after the decimal point.
        """
        if value in self.empty_values:
            return None
        if self.localize:
            used_thousand_separator = settings.USE_THOUSAND_SEPARATOR
            settings.USE_THOUSAND_SEPARATOR = True
            value = formats.sanitize_separators(value)
            settings.USE_THOUSAND_SEPARATOR = used_thousand_separator
        value = force_text(value).strip()
        try:
            value = Decimal(value)
        except DecimalException:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value
