from django.contrib.admin import SimpleListFilter, FieldListFilter
from django.db.models import Q, NullBooleanField

from marer.models import User


class ManagerListFilter(FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = field_path
        self.lookup_kwarg2 = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.lookup_val2 = request.GET.get(self.lookup_kwarg2)
        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [
            self.lookup_kwarg,
            self.lookup_kwarg2
        ]

    def choices(self, changelist):
        yield dict(
            selected=self.lookup_val is None and not self.lookup_val2,
            query_string=changelist.get_query_string({}, [self.lookup_kwarg]),
            display='Все',
        )
        yield {
            'selected': self.lookup_val2 == 'True',
            'query_string': changelist.get_query_string({
                self.lookup_kwarg2: 'True',
            }, [self.lookup_kwarg]),
            'display': 'Отсутствует',
        }
        managers = User.objects.filter(Q(Q(is_staff=True) | Q(is_superuser=True))).order_by('first_name')
        for manager in managers:
            yield dict(
                selected=(self.lookup_val == str(manager.id) and not self.lookup_val2),
                query_string=changelist.get_query_string({self.lookup_kwarg: manager.id}, [self.lookup_kwarg2]),
                display=manager.get_full_name()
            )
