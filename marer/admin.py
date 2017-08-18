from django.contrib.admin import ModelAdmin, register
from marer import models
from mptt.admin import MPTTModelAdmin


@register(models.FinanceProduct)
class FinanceProductAdmin(MPTTModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
