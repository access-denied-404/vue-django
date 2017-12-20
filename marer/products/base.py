import warnings
from abc import abstractmethod


class FinanceProduct(object):
    _humanized_name = ''
    _survey_template_name = ''
    _issue = None

    def set_issue(self, issue):
        self._issue = issue

    @abstractmethod
    def get_registering_form_class(self):
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def get_documents_list(self):
        raise NotImplementedError("Method is not implemented")

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def humanized_name(self):
        return self._humanized_name

    @property
    def survey_template_name(self):
        return self._survey_template_name

    @abstractmethod
    def get_survey_context_part(self):
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def process_survey_post_data(self, request):
        raise NotImplementedError("Method is not implemented")

    def process_registering_form(self, request):
        self._issue.refresh_from_db()
        form_class = self.get_registering_form_class()
        form = form_class(request.POST)
        form.full_clean()
        for field in form.cleaned_data:
            setattr(self._issue, field, form.cleaned_data[field])
        self._issue.save()
        return form.is_valid()

    @abstractmethod
    def get_admin_issue_fieldset(self):
        raise NotImplementedError("Method is not implemented")

    def get_admin_issue_read_only_fields(self):
        return []

    @abstractmethod
    def get_admin_issue_inlnes(self):
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def get_finance_orgs_conditions_list_fields(self):
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def get_finance_orgs_conditions_list(self):
        raise NotImplementedError("Method is not implemented")

    def load_finance_orgs_conditions_from_worksheet(self, ws):
        raise NotImplementedError("Method is not implemented")


class FinanceProductDocumentItem(object):
    _code = ''
    _name = ''
    _description = None
    _document = None

    def __init__(self, code, name, description=None):
        self._code = code
        self._name = name
        self._description = description

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def set_document(self, document):
        self._document = document

    @property
    def document(self):
        return self._document

    @property
    def url(self):
        if self.document and self.document.file:
            return self.document.file.url
        return None
