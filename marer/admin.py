from django.contrib.admin import ModelAdmin, register
from django.utils.translation import ugettext_lazy as _
from marer import models
from mptt.admin import MPTTModelAdmin


@register(models.FinanceProductPage)
class FinanceProductAdmin(MPTTModelAdmin):
    fieldsets = (
        (None, dict(fields=(
            'name',
            'parent',
            '_finance_product',
            'product_icon',
            'page_content',
        ))),
        (_('SEO'), dict(classes='collapse', fields=(
            ('_seo_h1', '_seo_title'),
            ('_seo_description', '_seo_keywords'),
        ))),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@register(models.StaticPage)
class StaticPageAdmin(ModelAdmin):
    fieldsets = (
        (None, dict(fields=(
            ('name', 'order'),
            'page_content',
        ))),
        (_('SEO'), dict(classes='collapse', fields=(
            ('_seo_h1', '_seo_title'),
            ('_seo_description', '_seo_keywords'),
        ))),
    )
