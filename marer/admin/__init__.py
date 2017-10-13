from random import randint

from django.contrib.admin import ModelAdmin, register, site
from django.contrib.auth.admin import UserAdmin
from django.db.models import TextField
from django import forms
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin

from marer import models, consts
from marer.admin.inline import IssueFinanceOrgProposeInlineAdmin, IssueDocumentInlineAdmin, \
    IFOPClarificationInlineAdmin, IFOPClarificationMessageInlineAdmin, \
    IFOPFormalizeDocumentInlineAdmin, IFOPFinalDocumentInlineAdmin, IssueBGProdAffiliateInlineAdmin, \
    IssueBGProdFounderLegalInlineAdmin, IssueBGProdFounderPhysicalInlineAdmin
from marer.models import IssueFinanceOrgProposeClarificationMessage, IssueFinanceOrgProposeClarificationMessageDocument, \
    Document
from marer.models.finance_org import FinanceOrganization


site.site_title = 'Управление сайтом МАРЭР'
site.site_header = 'Управление площадкой МАРЭР'
site.index_title = 'Управление площадкой'


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
        'status',
        'get_manager',
        'humanized_sum',
        'created_at',
        'updated_at',
    )
    list_filter = ('product', 'status',)
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
        if obj is None:
            result_fieldset = [
                (None, dict(fields=(
                    'product',
                    'user',
                    'private_comment',
                    'comment',
                ))),
            ]
        else:
            result_fieldset = [
                (None, dict(fields=(
                    'product',
                    'status',
                    'user',
                    'private_comment',
                    'comment',
                ))),
            ]
            product_fieldset_part = obj.get_product().get_admin_issue_fieldset()
            result_fieldset.extend(product_fieldset_part)
        return result_fieldset

    def get_manager(self, obj):
        return obj.user.manager or '—'
    get_manager.short_description = 'Менеджер'
    get_manager.admin_order_field = 'user__manager_id'

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            self.inlines = []
        else:
            self.inlines = [
                IssueFinanceOrgProposeInlineAdmin,
                IssueDocumentInlineAdmin,
                IssueBGProdAffiliateInlineAdmin,
                IssueBGProdFounderLegalInlineAdmin,
                IssueBGProdFounderPhysicalInlineAdmin,
            ]
        return super().get_inline_instances(request, obj)


@register(models.IssueFinanceOrgPropose)
class IssueFinanceOrgProposeAdmin(ModelAdmin):
    list_display = (
        'humanized_id',
        'humanized_issue_id',
        'issuer_short_name',
        'finance_org',
        'get_manager',
        'final_decision',
        'created_at',
        'updated_at',
    )
    list_filter = (
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

    def humanized_issue_id(self, obj):
        return obj.issue_id
    humanized_issue_id.short_description = 'номер заявки'
    humanized_issue_id.admin_order_field = 'issue_id'

    inlines = (
        IFOPClarificationInlineAdmin,
        IFOPFormalizeDocumentInlineAdmin,
        IFOPFinalDocumentInlineAdmin,
    )

    def issue_id(self, obj):
        return obj.issue.id
    issue_id.short_description = 'Номер заявки'

    def issuer_short_name(self, obj):
        issuer_short_name = obj.issue.issuer_short_name
        if issuer_short_name and issuer_short_name != '':
            return issuer_short_name
        elif issuer_short_name == 'НЕТ':
            return obj.issue.issuer_full_name
        else:
            return '—'
    issuer_short_name.short_description = 'Заявитель'

    def get_manager(self, obj):
        return obj.finance_org.manager or '—'
    get_manager.short_description = 'Менеджер'
    get_manager.admin_order_field = 'finance_org__manager_id'


@register(FinanceOrganization)
class FinanceOrganizationAdmin(ModelAdmin):
    list_display = (
        'name',
        'manager',
    )


class IFOPClarificationAddForm(forms.ModelForm):
    user = None
    message = forms.CharField(label='Сообщение', required=True, widget=forms.Textarea(attrs=dict(rows=4)))
    doc1 = forms.FileField(label='Документ', required=False)
    doc2 = forms.FileField(label='Документ', required=False)
    doc3 = forms.FileField(label='Документ', required=False)
    doc4 = forms.FileField(label='Документ', required=False)
    doc5 = forms.FileField(label='Документ', required=False)
    doc6 = forms.FileField(label='Документ', required=False)
    doc7 = forms.FileField(label='Документ', required=False)
    doc8 = forms.FileField(label='Документ', required=False)

    def save(self, commit=True):
        if not self.instance.id:
            self.instance.initiator = consts.IFOPC_INITIATOR_FINANCE_ORG
            self.instance.save()

        new_msg = IssueFinanceOrgProposeClarificationMessage()
        new_msg.user = self.user
        new_msg.message = self.cleaned_data['message']
        new_msg.clarification = self.instance
        new_msg.save()

        for file_field_name in self.files:
            field_file = self.files[file_field_name]

            new_ifopcmd_doc = Document()
            new_ifopcmd_doc.file = field_file
            new_ifopcmd_doc.save()

            new_ifopcmd = IssueFinanceOrgProposeClarificationMessageDocument()
            new_ifopcmd.name = field_file.name
            new_ifopcmd.clarification_message = new_msg
            new_ifopcmd.document = new_ifopcmd_doc
            new_ifopcmd.save()

        return super().save(commit)


@register(models.IssueFinanceOrgProposeClarification)
class IssueFinanceOrgProposeClarificationAdmin(ModelAdmin):
    list_display = (
        'humanized_id',
        '__str__',
        'created_at',
        'updated_at',
    )

    def humanized_id(self, obj):
        return obj.id
    humanized_id.short_description = 'номер дозапроса'
    humanized_id.admin_order_field = 'id'

    form = IFOPClarificationAddForm

    def get_form(self, request, obj=None, **kwargs):
        # self.form = IFOPClarificationAddForm
        if obj is None:
            self.readonly_fields = ()
            self.fields = (
                'propose',
                'message',
                (
                    'doc1',
                    'doc2',
                    'doc3',
                    'doc4',
                    'doc5',
                    'doc6',
                    'doc7',
                    'doc8',
                ),
            )
        else:
            self.fields = (
                'issue_change_link',
                'finance_org_propose_change_link',
                'initiator',
                'get_messages',
                'message',
                (
                    'doc1',
                    'doc2',
                    'doc3',
                    'doc4',
                    'doc5',
                    'doc6',
                    'doc7',
                    'doc8',
                ),
            )
            self.readonly_fields = (
                'issue_change_link',
                'finance_org_propose_change_link',
                'initiator',
                'get_messages',
            )
        return super().get_form(request, obj, **kwargs)

    def get_messages(self, obj):
        messages = obj.clarification_messages.all().order_by('created_at')
        obj_tmpl = '<div>{msg}</div><br/><div>{msg_docs}</div><br/>'
        line_tmpl = '<b>{msg.user}</b><br/>{msg_created}:<br/>{msg.message}'
        line_doc_tmpl = '<div><a href="{doc_url}">{doc_name}</a></div>'
        ret_text = ''
        idx = 1
        msgs_cnt = messages.count()
        for msg in messages:
            msg_text = line_tmpl.format(msg=msg, msg_created=msg.created_at.strftime('%d.%m.%Y %H:%M'))
            docs = ''
            if msg.documents_links.exists():
                docs += '<b>Документы:</b><br/>'
            for msg_doc in msg.documents_links.all():
                doc_name = msg_doc.name
                if msg_doc.document and msg_doc.document.file:
                    doc_url = msg_doc.document.file.url
                else:
                    doc_url = '#'
                docs += line_doc_tmpl.format(
                    doc_name=doc_name,
                    doc_url=doc_url,
                )
            ret_text += obj_tmpl.format(msg=msg_text, msg_docs=docs)
            if idx < msgs_cnt:
                ret_text += '<hr/>'
            idx += 1
        return ret_text
    get_messages.short_description = 'Сообщения'
    get_messages.allow_tags = True

    def save_form(self, request, form, change):
        form.user = request.user
        return super().save_form(request, form, change)

    def issue_change_link(self, obj):
        change_url = reverse('admin:marer_issue_change', args=(obj.id,))
        return '<a href="{}">{}</a>'.format(change_url, obj.propose.issue)
    issue_change_link.short_description = 'Заявка'
    issue_change_link.allow_tags = True

    def finance_org_propose_change_link(self, obj):
        change_url = reverse('admin:marer_issuefinanceorgpropose_change', args=(obj.id,))
        return '<a href="{}">{}</a>'.format(change_url, obj.propose)
    finance_org_propose_change_link.short_description = 'Предложения заявки в финансовую организацию'
    finance_org_propose_change_link.allow_tags = True


@register(models.User)
class MarerUserAdmin(UserAdmin):
    list_display = (
        'first_name_noempty',
        'last_name',
        'email',
        'phone',
    )
    fieldsets = (
        (None, {'fields': ('username', 'password', 'manager',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')

    def first_name_noempty(self, obj):
        if obj.first_name is None or obj.first_name == '':
            max_rndi = 10
            if randint(0, max_rndi) == max_rndi:
                return '¯\_(ツ)_/¯'
            return 'ИМЯ НЕ УКАЗАНО'
        else:
            return obj.first_name
    first_name_noempty.short_description = 'имя'
    first_name_noempty.admin_order_field = 'first_name'

    def save_model(self, request, obj, form, change):
        if obj.id is None and obj.manager is None:
            obj.manager = request.user
        return super().save_model(request, obj, form, change)
