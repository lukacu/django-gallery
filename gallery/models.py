#!/usr/bin/python
# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

import django
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from gallery.fields import ThumbnailParametersField
from gallery.watermark import Watermark

from imagekit.models.fields import ImageSpecField
from imagekit.processors import *

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from tagging.fields import TagField

from gallery import EXIF

DISPLAY_IMAGE_PROCESSORS = [Transpose(Transpose.AUTO), ResizeToFill(width=600, height=600)]
THUMBNAIL_IMAGE_PROCESSORS = [Transpose(Transpose.AUTO), Crop(width=128, height=128, anchor=Anchor.CENTER)]
COVER_IMAGE_PROCESSORS = [Transpose(Transpose.AUTO), Crop(width=128, height=128, anchor=Anchor.CENTER)]

ORDER_CHOICES = (
    ("-a", 'Descending by addition date'),
    ("+a", 'Ascending by addition date'),
    ("-t", 'Descending by date taken'),
    ("+t", 'Ascending by date taken'),
    ("-m", 'Descending by modification date'),
    ("+m", 'Ascending by modification date'),
  )

ORDER_MAPPING = {
 "a" : "date_added",
 "t" : "date_taken",
 "m" : "date_modified",
}

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

class Album(MPTTModel):
    title = models.CharField(_('title'), max_length=255)
    title_slug = models.SlugField(_('title slug'), editable = False, max_length=255)
    text = models.TextField(_('text'), blank=True)
    is_public = models.BooleanField(_('is public'), default=True, help_text=_('Public albums will be displayed in the default views.'))
    tags = TagField(help_text=_('Separate tags with spaces, put quotes around multiple-word tags.'), verbose_name=_('tags'))
    order = models.CharField(max_length=2, blank=False, default="", choices=ORDER_CHOICES, help_text=_('The default order of images for this album.'))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    cover = models.ForeignKey('Image', related_name='cover', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
      unique_together = (("title_slug", "parent"),)

    def save(self, *args, **kwargs):
      for i in xrange(0, 1000):
        try:
          if i == 0:
            self.title_slug = slugify(self.title)
          else:
            self.title_slug = "%s-%d" % (slugify(self.title), i)
          if hasattr(self, "_slug"):
            self._slug == None
          super(Album, self).save(*args, **kwargs)
        except django.db.utils.IntegrityError, e:
          continue
        break

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()

    def slug(self):
      if not hasattr(self, "_slug"):
        self._slug = "/".join([ x.title_slug for x in self.get_ancestors()] + [self.title_slug ])
      return self._slug

    def cover_image(self):
      if self.cover == None:
        try:
          if not hasattr(self, '_cover'):
            q = self.get_descendants(include_self=True).filter(is_public=True).values("id")
            order = "%s%s" % ('' if self.get_sorting_order() else '-', self.get_sorting_field())
            self._cover = Image.objects.filter(album__in=q, is_public=True).order_by(order)[0]
          return self._cover
        except IndexError:
          return None
      else:
        return self.cover

    def get_absolute_url(self):
      return reverse('gallery', kwargs={"path" : self.slug()})

    def get_sorting_field(self):
      if len(self.order) < 2:
        return "date_added"
      return ORDER_MAPPING.get(self.order[1], "date_added")

    def get_sorting_order(self):
      if len(self.order) < 2:
        return False
      return self.order[0] == "+"

class Image(models.Model):
    title = models.CharField(max_length=255)
    title_slug = models.SlugField(_('slug'), editable = False, max_length=255)
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
    album = TreeForeignKey(Album)

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = _("image")
        verbose_name_plural = _("images")
        unique_together = (("title_slug", "album"),)

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
        if self.title_slug is None:
            self.title_slug = slugify(self.title)
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

        for i in xrange(0, 9999):
          try:
            if i == 0:
              self.title_slug = slugify(self.title)
            else:
              self.title_slug = "%s-%d" % (slugify(self.title), i)
            if hasattr(self, "_slug"):
              self._slug == None
            super(Image, self).save(*args, **kwargs)
          except django.db.utils.IntegrityError, e:
            continue
          break

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()

    def slug(self):
      if not hasattr(self, "_slug"):
        self._slug = "%s/%s" % (self.album.slug(), self.title_slug)
      return self._slug

    def get_absolute_url(self):
      return reverse('gallery', kwargs={"path" : self.slug()})



