import datetime
import os
import uuid
from logging import warning

from django.db import models
from django.utils.encoding import force_str, force_text
from django.utils import timezone
from mptt import models as mptt_models
from mptt.fields import TreeForeignKey

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


def news_pictures_upload_path(instance, filename):
    filename_arr = str(filename).split('.')
    ext = filename_arr[-1]
    new_filename = 'images/news/{file_name}.{file_ext}'.format(
        file_name=uuid.uuid4(),
        file_ext=ext,
    )
    new_filename = force_str(new_filename)
    new_filename = force_text(new_filename)
    new_filename = os.path.normpath(new_filename)
    return new_filename


def showcase_partners_logos_upload_path(instance, filename):
    filename_arr = str(filename).split('.')
    ext = filename_arr[-1]
    new_filename = 'images/showcase/partners/{file_name}.{file_ext}'.format(
        file_name=uuid.uuid4(),
        file_ext=ext,
    )
    new_filename = force_str(new_filename)
    new_filename = force_text(new_filename)
    new_filename = os.path.normpath(new_filename)
    return new_filename


def set_obj_update_time(obj, updated_at_field='updated_at'):
    if obj:
        if hasattr(obj, updated_at_field):
            setattr(obj, updated_at_field, timezone.now())
            obj.save()
        else:
            warning('Object {} got no field called {} for update time there'.format(
                obj, updated_at_field))
    else:
        warning('Got none object for set update time', stacklevel=3)


class Document(models.Model):
    file = models.FileField(upload_to=documents_upload_path)


class OKVED2(mptt_models.MPTTModel):
    name = models.CharField(max_length=512, blank=False, null=False)
    code = models.CharField(max_length=32, blank=False, null=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='childrens')


class Region(mptt_models.MPTTModel):
    name = models.CharField(max_length=512, blank=False, null=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='childrens')

    def __str__(self):
        return self.name
