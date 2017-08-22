import copy
from django.forms.widgets import Select, ChoiceWidget


class CallableChoicesSelect(Select):
    choices_maybe_callable = None

    def __init__(self, attrs=None, choices=()):
        super(ChoiceWidget, self).__init__(attrs)
        self.choices_maybe_callable = choices

    @property
    def choices(self):
        if callable(self.choices_maybe_callable):
            return self.choices_maybe_callable()
        else:
            return self.choices_maybe_callable

    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.attrs = self.attrs.copy()
        obj.choices_maybe_callable = copy.copy(self.choices_maybe_callable)
        memo[id(self)] = obj
        return obj
