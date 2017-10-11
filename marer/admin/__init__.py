from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin
from django.db.models import TextField
from django import forms
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin

from marer import models
from marer.admin.inline import IssueFinanceOrgProposeInlineAdmin, IssueDocumentInlineAdmin, \
    IFOPClarificationInlineAdmin, IFOPClarificationMessageInlineAdmin, \
    IFOPFormalizeDocumentInlineAdmin, IFOPFinalDocumentInlineAdmin
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
        'humanized_id',
        'user',
        'product',
        'issuer_short_name',
        'humanized_sum',
    )
    inlines = (
        IssueFinanceOrgProposeInlineAdmin,
        IssueDocumentInlineAdmin,
    )
    formfield_overrides = {
        TextField: dict(widget=forms.Textarea(dict(rows=4)))
    }

    def humanized_sum(self, obj):
        return obj.humanized_sum
    humanized_sum.short_description = 'сумма'
    humanized_sum.admin_order_field = 'bg_sum'

    def humanized_id(self, obj):
        return obj.id
    humanized_id.short_description = 'номер заявки'
    humanized_id.admin_order_field = 'id'

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
        'humanized_id',
        'issue_id',
        'issuer_full_name',
        'finance_org',
        'final_decision',
    )
    fields = (
        'issue_change_link',
        'finance_org',
        'formalize_note',
        'final_decision',
        'final_note',
    )
    readonly_fields = (
        'issue_change_link',
        'finance_org',
    )
    formfield_overrides = {
        TextField: dict(widget=forms.Textarea(dict(rows=4)))
    }

    def issue_change_link(self, obj):
        change_url = reverse('admin:marer_issue_change', args=(obj.id,))
        return '<a href="{}">{}</a>'.format(change_url, obj.issue)
    issue_change_link.short_description = 'Заявка'
    issue_change_link.allow_tags = True

    def humanized_id(self, obj):
        return obj.id
    humanized_id.short_description = 'номер предложения'
    humanized_id.admin_order_field = 'id'

    inlines = (
        IFOPClarificationInlineAdmin,
        IFOPFormalizeDocumentInlineAdmin,
        IFOPFinalDocumentInlineAdmin,
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
    list_display = (
        'humanized_id',
        '__str__',
        'created_at',
        'updated_at',
    )
    fields = (
        'propose',
        'initiator',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'propose',
        'initiator',
        'created_at',
        'updated_at',
    )
    inlines = (IFOPClarificationMessageInlineAdmin,)

    def humanized_id(self, obj):
        return obj.id
    humanized_id.short_description = 'номер дозапроса'
    humanized_id.admin_order_field = 'id'


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
