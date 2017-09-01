import uuid

from django.db import models


__all__ = ['Document']


class Document(models.Model):

    @staticmethod
    def documents_upload_path(instance, filename):
        filename_arr = str(filename).split('.')
        ext = filename_arr[:-1]
        return 'documents/%Y/%m/%d/{file_name}.{file_ext}'.format(
            file_name=uuid.uuid4(),
            file_ext=ext,
        )

    file = models.FileField(upload_to=documents_upload_path)
