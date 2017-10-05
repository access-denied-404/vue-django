from django.contrib.admin import StackedInline, TabularInline

from marer import models


class IssueFinanceOrgProposeInlineAdmin(StackedInline):
    extra = 1
    model = models.IssueFinanceOrgPropose


class IssueDocumentInlineAdmin(TabularInline):
    # todo add humanized documents types
    # todo add nested file field
    extra = 1
    model = models.IssueDocument


class IFOPClarificationInlineAdmin(TabularInline):
    extra = 1
    model = models.IssueFinanceOrgProposeClarification
    show_change_link = True
    fields = ('id', 'initiator',)


class IFOPClarificationMessageInlineAdmin(StackedInline):
    model = models.IssueFinanceOrgProposeClarificationMessage
    show_change_link = True


class IFOPClarificationMessageDocumentInlineAdmin(TabularInline):
    model = models.IssueFinanceOrgProposeClarificationMessageDocument
    show_change_link = True