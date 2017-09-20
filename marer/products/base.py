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
        warnings.warn("Method is not implemented", NotImplementedError)

    @abstractmethod
    def get_documents_list(self):
        warnings.warn("Method is not implemented", NotImplementedError)

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
        warnings.warn("Method is not implemented", NotImplementedError)

    @abstractmethod
    def process_survey_post_data(self, request):
        warnings.warn("Method is not implemented", NotImplementedError)


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
