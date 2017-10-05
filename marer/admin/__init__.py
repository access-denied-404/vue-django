from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin

from marer import models
from marer.admin.inline import IssueFinanceOrgProposeInlineAdmin, IssueDocumentInlineAdmin, \
    IFOPClarificationInlineAdmin, IFOPClarificationMessageInlineAdmin, IFOPClarificationMessageDocumentInlineAdmin
from marer.models.finance_org import FinanceOrganization


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
    list_display = ('id', '__str__', 'created_at', 'updated_at',)
    inlines = (IFOPClarificationMessageInlineAdmin,)


@register(models.IssueFinanceOrgProposeClarificationMessage)
class IFOPClarificationMessageAdmin(ModelAdmin):
    inlines = (IFOPClarificationMessageDocumentInlineAdmin,)


@register(models.IssueFinanceOrgProposeClarificationMessageDocument)
class IFOPClarificationMessageDocumentAdmin(ModelAdmin):
    readonly_fields = ('document',)


@register(models.User)
class MarerUserAdmin(UserAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'phone',
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
