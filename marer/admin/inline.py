from django.contrib.admin import StackedInline, TabularInline
from django import forms

from marer import models
from marer.forms.widgets import ReadOnlyFileInput
from marer.models import Document
from marer.models.issue import IssueFinanceOrgProposeFormalizeDocument, IssueFinanceOrgProposeFinalDocument


class IssueFinanceOrgProposeInlineAdmin(StackedInline):
    extra = 1
    model = models.IssueFinanceOrgPropose


class IssueDocumentInlineAdmin(TabularInline):
    # todo add humanized documents types
    # todo add nested file field
    extra = 1
    model = models.IssueDocument


class IFOPClarificationInlineAdmin(TabularInline):
    model = models.IssueFinanceOrgProposeClarification
    show_change_link = True
    fields = (
        'id',
        'issue_str',
        'propose_finance_org',
        'initiator',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'id',
        'issue_str',
        'propose_finance_org',
        'initiator',
        'created_at',
        'updated_at',
    )
    classes = ('collapse',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def propose_finance_org(self, obj):
        return obj.propose.finance_org.name
    propose_finance_org.short_description = 'finance org'

    def issue_str(self, obj):
        return obj.propose.issue
    issue_str.short_description = 'issue'


class IFOPFormalizeDocumentInlineAdminForm(forms.ModelForm):
    file = forms.FileField(required=True, label='update_doc', widget=ReadOnlyFileInput)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            initial = kwargs.get('initial', dict())
            if instance.document:
                initial['file'] = instance.document.file
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        new_doc = Document()
        new_doc.file = self.cleaned_data['file']
        new_doc.save()
        self.instance.document = new_doc
        return super().save(commit)


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


class IFOPFinalDocumentInlineAdminForm(forms.ModelForm):
    file = forms.FileField(required=True, label='update_doc', widget=ReadOnlyFileInput)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            initial = kwargs.get('initial', dict())
            if instance.document:
                initial['file'] = instance.document.file
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        new_doc = Document()
        new_doc.file = self.cleaned_data['file']
        new_doc.save()
        self.instance.document = new_doc
        return super().save(commit)


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


class IFOPClarificationMessageInlineAdmin(StackedInline):
    extra = 1
    model = models.IssueFinanceOrgProposeClarificationMessage
    show_change_link = True


class IFOPClarificationMessageDocumentInlineAdmin(TabularInline):
    model = models.IssueFinanceOrgProposeClarificationMessageDocument
    show_change_link = True
