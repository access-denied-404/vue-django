from django import forms
from django.contrib.admin import StackedInline, TabularInline
from django.contrib.admin.options import InlineModelAdmin
from django.db.models import TextField
from django.forms import BaseInlineFormSet
from django.forms.formsets import ManagementForm, TOTAL_FORM_COUNT, INITIAL_FORM_COUNT, MAX_NUM_FORM_COUNT, \
    MIN_NUM_FORM_COUNT

from marer.consts import DOCUMENT_SIGN_LABELS
from marer import models
from marer.admin.forms import FinanceOrgProductProposeDocumentInlineAdminForm, IFOPFinalDocumentInlineAdminForm, \
    IFOPFormalizeDocumentInlineAdminForm, IssueDocumentInlineAdminForm, IssueProposeDocumentInlineAdminForm
from marer.models.finance_org import FinanceOrgProductProposeDocument, FinanceOrgProductConditions
from marer.models.issue import IssueProposeFormalizeDocument, IssueProposeFinalDocument, \
    IssueBGProdAffiliate, IssueBGProdFounderLegal, IssueBGProdFounderPhysical, IssueCreditPledge, \
    IssueProposeDocument, IssueLeasingProdAsset, IssueLeasingProdSupplier, IssueLeasingProdPayRule, \
    IssueFactoringBuyer, IssuerLicences


class IIFAInlineFormSet(BaseInlineFormSet):

    @property
    def management_form(self):
        """Returns the ManagementForm instance for this FormSet."""
        if self.is_bound:
            form = ManagementForm(self.data, auto_id=self.auto_id, prefix=self.prefix)
            if not form.is_valid():
                form.cleaned_data = {
                    TOTAL_FORM_COUNT: 0,
                    INITIAL_FORM_COUNT: 0,
                    MIN_NUM_FORM_COUNT: 0,
                    MAX_NUM_FORM_COUNT: 0,
                }
        else:
            form = ManagementForm(auto_id=self.auto_id, prefix=self.prefix, initial={
                TOTAL_FORM_COUNT: self.total_form_count(),
                INITIAL_FORM_COUNT: self.initial_form_count(),
                MIN_NUM_FORM_COUNT: self.min_num,
                MAX_NUM_FORM_COUNT: self.max_num
            })
        return form


class IssueInlineFormsetAdmin(InlineModelAdmin):
    formset = IIFAInlineFormSet

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
            for field_name in formset.form.base_fields:
                field = formset.form.base_fields[field_name]
                field.disabled = False
        if request.user.has_perm('marer.can_change_managed_users_issues'):
            for field_name in formset.form.base_fields:
                field = formset.form.base_fields[field_name]
                field.disabled = False
        elif request.user.has_perm('marer.can_view_managed_finance_org_proposes_issues'):
            for field_name in formset.form.base_fields:
                field = formset.form.base_fields[field_name]
                field.disabled = True

        return formset


class RegionKLADRCodeInlineAdmin(StackedInline):
    extra = 1
    model = models.RegionKLADRCode


class IssueFinanceOrgProposeFormSet(BaseInlineFormSet):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('-updated_at')[:3]


class IssueDocumentInlineAdmin(TabularInline, IssueInlineFormsetAdmin):
    extra = 0
    fields = (
        'code',
        'file',
    )
    model = models.IssueDocument
    form = IssueDocumentInlineAdminForm

    def get_formset(self, request, obj=None, **kwargs):
        if obj is not None:
            choices = [(None, '---------')] + [(ch.code, ch.name) for ch in obj.get_product().get_documents_list()]
            self.form.declared_fields['code'].widget.choices = choices

        return super().get_formset(request, obj, **kwargs)


class IFOPClarificationInlineAdmin(TabularInline):
    model = models.IssueClarification
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

    show_view_all_link = True
    show_view_all_filter_field_name = 'propose'
    has_alter_add_url = True

    def get_alter_add_url(self, parent_obj):
        return '/admin/{app_label}/{model_name}/add/?issue={parent_obj_id}'.format(
            app_label=self.model._meta.app_label,
            model_name=self.model._meta.model_name,
            parent_obj_id=parent_obj.id,
        )


class IFOPFormalizeDocumentInlineAdmin(TabularInline):
    extra = 1
    model = IssueProposeFormalizeDocument
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
    model = IssueProposeFinalDocument
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
    model = IssueProposeDocument
    show_change_link = True
    form = IssueProposeDocumentInlineAdminForm
    fields = (
        'name',
        'cert_info',
        'file_sample',
        'file',
        'is_approved_by_manager',
    )
    readonly_fields = ['cert_info']
    classes = ('collapse',)

    def cert_info(self, obj):
        output = []
        if obj.document:
            output = [
                'Статус подписи: <b>%s</b>' % DOCUMENT_SIGN_LABELS.get(obj.document.sign_state, '-'),
                ('Подпись: <a href="%s" >скачать</a>' % obj.document.sign.url) if obj.document.sign else ''
            ]
        return '<br>'.join(output)
    cert_info.short_description = 'Данные сертификата'
    cert_info.allow_tags = True
    # todo check add permission
    # todo check change permission
    # todo check del permission



class IFOPClarificationMessageInlineAdmin(StackedInline):
    extra = 1
    model = models.IssueClarificationMessage
    show_change_link = True
    formfield_overrides = {
        TextField: dict(widget=forms.Textarea(dict(rows=4)))
    }


class IssueBGProdAffiliateInlineAdmin(TabularInline, IssueInlineFormsetAdmin):
    extra = 0
    model = IssueBGProdAffiliate
    classes = ('collapse',)


class IssueBGProdFounderLegalInlineAdmin(TabularInline, IssueInlineFormsetAdmin):
    extra = 0
    model = IssueBGProdFounderLegal
    classes = ('collapse',)


class IssueBGProdFounderPhysicalInlineAdmin(TabularInline, IssueInlineFormsetAdmin):
    extra = 0
    model = IssueBGProdFounderPhysical
    classes = ('collapse',)


class IssueCreditPledgeInlineAdmin(TabularInline, IssueInlineFormsetAdmin):
    extra = 0
    model = IssueCreditPledge
    classes = ('collapse',)


class IssueLeasingProdAssetInlineAdmin(TabularInline, IssueInlineFormsetAdmin):
    extra = 0
    model = IssueLeasingProdAsset
    classes = ('collapse',)


class IssueLeasingProdSupplierInlineAdmin(TabularInline, IssueInlineFormsetAdmin):
    extra = 0
    model = IssueLeasingProdSupplier
    classes = ('collapse',)


class IssueLeasingProdPayRuleInlineAdmin(TabularInline, IssueInlineFormsetAdmin):
    extra = 0
    model = IssueLeasingProdPayRule
    classes = ('collapse',)


class IssueFactoringBuyerInlineAdmin(StackedInline, IssueInlineFormsetAdmin):
    extra = 0
    model = IssueFactoringBuyer
    classes = ('collapse',)


class IssueLicencesInlineAdmin(StackedInline, IssueInlineFormsetAdmin):
    extra = 0
    model = IssuerLicences
    classes = ('collapse',)
