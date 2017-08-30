import warnings
from abc import abstractmethod


class FinanceProduct(object):
    _humanized_name = ''

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
