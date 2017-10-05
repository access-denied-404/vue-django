from django.contrib.admin import ModelAdmin, register, StackedInline, TabularInline
from django.utils.translation import ugettext_lazy as _
from marer import models
from marer.models.finance_org import FinanceOrganization
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


class IssueFinanceOrgProposeInlineAdmin(StackedInline):
    extra = 1
    model = models.IssueFinanceOrgPropose


class IssueDocumentInlineAdmin(TabularInline):
    # todo add humanized documents types
    # todo add nested file field
    extra = 1
    model = models.IssueDocument


@register(models.Issue)
class IssueAdmin(ModelAdmin):
    list_display = (
        'id',
        'user',
        'product',
        'issuer_short_name',
        'humanized_sum',
    )
    inlines = (
        IssueFinanceOrgProposeInlineAdmin,
        IssueDocumentInlineAdmin,
    )

    def get_fieldsets(self, request, obj=None):
        result_fieldset = [
            (None, dict(fields=(
                'product',
                'status',
                'user',
                'comment',
            ))),
        ]

        product_fieldset_part = obj.get_product().get_admin_issue_fieldset()
        result_fieldset.extend(product_fieldset_part)
        return result_fieldset


class IFOPClarificationInlineAdmin(TabularInline):
    extra = 1
    model = models.IssueFinanceOrgProposeClarification
    show_change_link = True
    fields = ('id', 'initiator',)


@register(models.IssueFinanceOrgPropose)
class IssueFinanceOrgProposeAdmin(ModelAdmin):
    list_display = (
        'id',
        'issue_id',
        'issuer_full_name',
        'finance_org',
    )

    inlines = (
        IFOPClarificationInlineAdmin,
    )

    def issue_id(self, obj):
        return obj.issue.id
    issue_id.short_description = 'Номер заявки'

    def issuer_full_name(self, obj):
        issuer_full_name = obj.issue.issuer_full_name
        if issuer_full_name and issuer_full_name != '':
            return obj.issue.issuer_full_name
        else:
            return '—'
    issuer_full_name.short_description = 'Заявитель'


@register(FinanceOrganization)
class FinanceOrganizationAdmin(ModelAdmin):
    pass


@register(models.IssueFinanceOrgProposeClarification)
class IssueFinanceOrgProposeClarificationAdmin(ModelAdmin):
    pass
