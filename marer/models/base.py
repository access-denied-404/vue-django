import datetime
import os
import uuid

from django.db import models
from django.utils.encoding import force_str, force_text

__all__ = ['Document']


def documents_upload_path(instance, filename):
    filename_arr = str(filename).split('.')
    ext = filename_arr[-1]
    new_filename = 'documents/%Y/%m/%d/{file_name}.{file_ext}'.format(
        file_name=uuid.uuid4(),
        file_ext=ext,
    )
    new_filename = force_str(new_filename)
    new_filename = datetime.datetime.now().strftime(new_filename)
    new_filename = force_text(new_filename)
    new_filename = os.path.normpath(new_filename)
    return new_filename


def finance_products_page_images_upload_path(instance, filename):
    filename_arr = str(filename).split('.')
    ext = filename_arr[-1]
    new_filename = 'images/finance_products_page_images/{file_name}.{file_ext}'.format(
        file_name=uuid.uuid4(),
        file_ext=ext,
    )
    new_filename = force_str(new_filename)
    new_filename = force_text(new_filename)
    new_filename = os.path.normpath(new_filename)
    return new_filename


class Document(models.Model):
    file = models.FileField(upload_to=documents_upload_path)
