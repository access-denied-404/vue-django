from django import forms
from django.contrib.admin import StackedInline, TabularInline
from django.db.models import TextField
from django.forms import BaseInlineFormSet

from marer import models
from marer.admin.forms import FinanceOrgProductProposeDocumentInlineAdminForm, IFOPFinalDocumentInlineAdminForm, \
    IFOPFormalizeDocumentInlineAdminForm, IssueDocumentInlineAdminForm, IssueProposeDocumentInlineAdminForm
from marer.models.finance_org import FinanceOrgProductProposeDocument, FinanceOrgProductConditions
from marer.models.issue import IssueFinanceOrgProposeFormalizeDocument, IssueFinanceOrgProposeFinalDocument, \
    IssueBGProdAffiliate, IssueBGProdFounderLegal, IssueBGProdFounderPhysical, IssueCreditPledge, \
    IssueFinanceOrgProposeDocument


class IssueFinanceOrgProposeFormSet(BaseInlineFormSet):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('-updated_at')[:3]


class IssueFinanceOrgProposeInlineAdmin(TabularInline):
    extra = 1
    model = models.IssueFinanceOrgPropose
    verbose_name_plural = 'Предложения заявки в банки (последние 3)'
    fields = (
        'id',
        'finance_org',
        'final_decision',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'id',
        'finance_org',
        'final_decision',
        'created_at',
        'updated_at',
    )
    formset = IssueFinanceOrgProposeFormSet

    show_change_link = True
    can_delete = False

    def __init__(self, parent_model, admin_site):
        super().__init__(parent_model, admin_site)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            if obj is None:
                return True
            elif obj.user.manager_id == request.user.id:
                return True
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            return True
        return super().has_change_permission(request, obj)

    show_view_all_link = True
    has_alter_add_url = True

    def get_alter_add_url(self, parent_obj):
        return '/admin/{app_label}/{model_name}/?issue_id={parent_obj_id}'.format(
            app_label=self.model._meta.app_label,
            model_name=FinanceOrgProductConditions._meta.model_name,
            parent_obj_id=parent_obj.id,
        )


class IssueDocumentInlineAdmin(TabularInline):
    extra = 0
    fields = (
        'code',
        'file',
    )
    model = models.IssueDocument
    form = IssueDocumentInlineAdminForm

    def get_formset(self, request, obj=None, **kwargs):
        if obj is not None:
            choices = [(ch.code, ch.name) for ch in obj.get_product().get_documents_list()]
            self.form.declared_fields['code'].widget.choices = choices

        formset = super().get_formset(request, obj, **kwargs)
        if request.user.has_perm('marer.change_issue'):
            pass
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            for field_name in formset.form.base_fields:
                field = formset.form.base_fields[field_name]
                field.disabled = True

        return formset

    def has_add_permission(self, request):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            if obj is None:
                return True
            elif obj.user.manager_id == request.user.id:
                return True
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_delete_permission(request, obj)


class IFOPClarificationInlineAdmin(TabularInline):
    model = models.IssueFinanceOrgProposeClarification
    show_change_link = True
    fields = (
        'humanized_id',
        'issue_str',
        'propose_finance_org',
        'initiator',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'humanized_id',
        'issue_str',
        'propose_finance_org',
        'initiator',
        'created_at',
        'updated_at',
    )
    classes = ('collapse',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('marer.change_issuefinanceorgproposeclarification'):
            pass
        elif request.user.has_perm('marer.can_change_managed_users_issues'):
            if obj is None:
                return True
            elif obj.issue.user.manager_id == request.user.id:
                return True
        elif request.user.has_perm('marer.can_change_managed_finance_org_proposes'):
            if obj is None:
                return True
            elif obj.finance_org.manager_id == request.user.id:
                return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def propose_finance_org(self, obj):
        return obj.propose.finance_org.name
    propose_finance_org.short_description = 'finance org'

    def issue_str(self, obj):
        return obj.propose.issue
    issue_str.short_description = 'заявка'

    def humanized_id(self, obj):
        return obj.id
    humanized_id.short_description = 'номер дозапроса'


class IFOPFormalizeDocumentInlineAdmin(TabularInline):
    extra = 1
    model = IssueFinanceOrgProposeFormalizeDocument
    show_change_link = True
    form = IFOPFormalizeDocumentInlineAdminForm
    fields = (
        'name',
        'file',
    )
    classes = ('collapse',)

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('marer.change_issuefinanceorgproposeformalizedocument'):
            pass
        elif request.user.has_perm('marer.can_change_managed_users_issues'):
            # todo make it read only
            if obj is None:
                return True
            elif obj.issue.user.manager_id == request.user.id:
                return True
        elif request.user.has_perm('marer.can_change_managed_finance_org_proposes'):
            if obj is None:
                return True
            elif obj.finance_org.manager_id == request.user.id:
                return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.has_perm('marer.change_issuefinanceorgproposeformalizedocument'):
            pass
        elif request.user.has_perm('marer.can_change_managed_finance_org_proposes'):
            return True
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('marer.change_issuefinanceorgproposeformalizedocument'):
            pass
        elif request.user.has_perm('marer.can_change_managed_finance_org_proposes'):
            if obj is None:
                return True
            elif obj.finance_org.manager_id == request.user.id:
                return True
        return super().has_delete_permission(request, obj)


class IFOPFinalDocumentInlineAdmin(TabularInline):
    extra = 1
    model = IssueFinanceOrgProposeFinalDocument
    show_change_link = True
    form = IFOPFinalDocumentInlineAdminForm
    fields = (
        'name',
        'file',
    )
    classes = ('collapse',)

    # todo check add permission
    # todo check del permission

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('marer.change_issuefinanceorgproposefinaldocument'):
            pass
        elif request.user.has_perm('marer.can_change_managed_users_issues'):
            # todo make it read only
            if obj is None:
                return True
            elif obj.issue.user.manager_id == request.user.id:
                return True
        elif request.user.has_perm('marer.can_change_managed_finance_org_proposes'):
            if obj is None:
                return True
            elif obj.finance_org.manager_id == request.user.id:
                return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.has_perm('marer.change_issuefinanceorgproposeformalizedocument'):
            pass
        elif request.user.has_perm('marer.can_change_managed_finance_org_proposes'):
            return True
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('marer.change_issuefinanceorgproposeformalizedocument'):
            pass
        elif request.user.has_perm('marer.can_change_managed_finance_org_proposes'):
            if obj is None:
                return True
            elif obj.finance_org.manager_id == request.user.id:
                return True
        return super().has_delete_permission(request, obj)


class FinanceOrgProductProposeDocumentInlineAdmin(TabularInline):
    extra = 1
    model = FinanceOrgProductProposeDocument
    show_change_link = True
    form = FinanceOrgProductProposeDocumentInlineAdminForm
    fields = (
        'name',
        'finance_product',
        'code',
        'file',
    )
    classes = ('collapse',)

    # todo check add permission
    # todo check change permission
    # todo check del permission


class IssueProposeDocumentInlineAdmin(TabularInline):
    extra = 1
    model = IssueFinanceOrgProposeDocument
    show_change_link = True
    form = IssueProposeDocumentInlineAdminForm
    fields = (
        'name',
        'code',
        'file_sample',
        'file',
    )
    classes = ('collapse',)

    # todo check add permission
    # todo check change permission
    # todo check del permission


class IFOPClarificationMessageInlineAdmin(StackedInline):
    extra = 1
    model = models.IssueFinanceOrgProposeClarificationMessage
    show_change_link = True
    formfield_overrides = {
        TextField: dict(widget=forms.Textarea(dict(rows=4)))
    }


class IssueBGProdAffiliateInlineAdmin(TabularInline):
    extra = 0
    model = IssueBGProdAffiliate
    classes = ('collapse',)

    def has_add_permission(self, request):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            if obj is None:
                return True
            elif obj.user.manager_id == request.user.id:
                return True
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_delete_permission(request, obj)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if request.user.has_perm('marer.change_issue'):
            pass
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            for field_name in formset.form.base_fields:
                field = formset.form.base_fields[field_name]
                field.disabled = True

        return formset


class IssueBGProdFounderLegalInlineAdmin(TabularInline):
    extra = 0
    model = IssueBGProdFounderLegal
    classes = ('collapse',)

    def has_add_permission(self, request):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            if obj is None:
                return True
            elif obj.user.manager_id == request.user.id:
                return True
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_delete_permission(request, obj)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if request.user.has_perm('marer.change_issue'):
            pass
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            for field_name in formset.form.base_fields:
                field = formset.form.base_fields[field_name]
                field.disabled = True

        return formset


class IssueBGProdFounderPhysicalInlineAdmin(TabularInline):
    extra = 0
    model = IssueBGProdFounderPhysical
    classes = ('collapse',)

    def has_add_permission(self, request):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            if obj is None:
                return True
            elif obj.user.manager_id == request.user.id:
                return True
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_delete_permission(request, obj)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if request.user.has_perm('marer.change_issue'):
            pass
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            for field_name in formset.form.base_fields:
                field = formset.form.base_fields[field_name]
                field.disabled = True

        return formset


class IssueCreditPledgeInlineAdmin(TabularInline):
    extra = 0
    model = IssueCreditPledge
    classes = ('collapse',)

    def has_add_permission(self, request):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            if obj is None:
                return True
            elif obj.user.manager_id == request.user.id:
                return True
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            return True
        return super().has_delete_permission(request, obj)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if request.user.has_perm('marer.change_issue'):
            pass
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            for field_name in formset.form.base_fields:
                field = formset.form.base_fields[field_name]
                field.disabled = True

        return formset
