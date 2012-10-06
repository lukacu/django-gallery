#!/usr/bin/python
# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

import django
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.fields.related import ForeignKey
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from gallery.fields import ThumbnailParametersField
from gallery.watermark import Watermark

from imagekit.models.fields import ImageSpecField
from imagekit.processors import *

from tagging.fields import TagField

from gallery import EXIF

def _get_image_processor(instance, file):
    width = getattr(settings, "GALLERY_IMAGE_WIDTH", 600)
    height = getattr(settings, "GALLERY_IMAGE_HEIGHT", 600)
    processor = [Transpose(Transpose.AUTO), ResizeToFill(width=width, height=height)]
    watermark = getattr(settings, "GALLERY_WATERMARK", None)

    if watermark:
        if type(watermark) == dict:
            processor.append(Watermark(image_path = watermark["image"],
                opacity = watermark.get("opacity", 1),
                offset = '%d,%d' % (watermark.get("offsetX", 0), watermark.get("offsetY", 0))))

    return processor

def _get_thumbnail_processor(instance, file):
    width = getattr(settings, "GALLERY_THUMBNAIL_WIDTH", 100)
    height = getattr(settings, "GALLERY_THUMBNAIL_HEIGHT", 100)
    parameters = instance.thumbnail_parameters

    if len(parameters) < 3:
        return [Transpose(Transpose.AUTO), ResizeToFill(width=width, height=height, anchor=Anchor.CENTER)]
    else:
        return [Transpose(Transpose.AUTO), ResizeCanvas(width=width, height=height, anchor=(parameters.get("x", 0.5), parameters.get("y", 0.5)))]

class Album(models.Model):
    title = models.CharField(_('title'), max_length=255)
    text = models.TextField(_('text'), blank=True)
    is_public = models.BooleanField(_('is public'), default=True, help_text=_('Public albums will be displayed in the default views.'))

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()

    def get_absolute_url(self):
      return reverse('gallery-album', kwargs={"id" : self.pk, "path" : slugify(self.title)})

class Image(models.Model):
    title = models.CharField(max_length=255)
    date_added = models.DateTimeField(_('date added'), default=datetime.now, editable = False, auto_now_add = True)
    date_taken = models.DateTimeField(_('date taken'), null=True, blank=True, editable=False)
    date_modified = models.DateTimeField(_('date modified'), editable = False, auto_now = True, default=datetime.now)
    original_image = models.ImageField(upload_to=getattr(settings, 'GALLERY_STORAGE_PATH', 'gallery'))
    display_image = ImageSpecField(processors=_get_image_processor, image_field='original_image', options={'quality': 90})
    thumbnail_image = ImageSpecField(processors=_get_thumbnail_processor, image_field='original_image', format='JPEG', options={'quality': 75})
    thumbnail_parameters = ThumbnailParametersField(editable=False, blank=True)
    text = models.TextField(_('text'), blank=True)
    is_public = models.BooleanField(_('is public'), default=True, help_text=_('Public images will be displayed in the default views.'))
    tags = TagField(help_text=_('Separate tags with spaces, put quotes around multiple-word tags.'), verbose_name=_('tags'))
    enable_comments = models.BooleanField(_('can comment'), default=True)
    album = ForeignKey(Album)

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = _("image")
        verbose_name_plural = _("images")

    @property
    def EXIF(self):
        try:
            return EXIF.process_file(open(self.original_image.path, 'rb'))
        except:
            try:
                return EXIF.process_file(open(self.original_image.path, 'rb'), details=False)
            except:
                return {}

    def save(self, *args, **kwargs):
        if self.date_taken is None:
            try:
                exif_date = self.EXIF.get('EXIF DateTimeOriginal', None)
                if exif_date is not None:
                    d, t = str.split(exif_date.values)
                    year, month, day = d.split(':')
                    hour, minute, second = t.split(':')
                    self.date_taken = datetime(int(year), int(month), int(day),
                                               int(hour), int(minute), int(second))
            except:
                pass
        if self.date_taken is None:
            self.date_taken = datetime.now()

        super(Image, self).save(*args, **kwargs)


    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()

    def get_absolute_url(self):
      return reverse('gallery-image', kwargs={"id" : self.pk, "path" : slugify(self.title)})



