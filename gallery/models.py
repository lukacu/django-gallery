#!/usr/bin/python
# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from inspect import isclass

import django
from django.db import models
from django.db.models.signals import post_init
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str, force_unicode
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _

from imagekit.models import ImageModel

from mptt.models import MPTTModel

from tagging.fields import TagField

from gallery import EXIF

class Album(MPTTModel):
    title = models.CharField(_('title'), max_length=255)
    title_slug = models.SlugField(_('title slug'), editable = False, max_length=255)
    weight = models.IntegerField(_('weight'), default=0, blank=True)
    text = models.TextField(_('text'), blank=True)
    is_public = models.BooleanField(_('is public'), default=True, help_text=_('Public albums will be displayed in the default views.'))
    tags = TagField(help_text=_('Separate tags with spaces, put quotes around multiple-word tags.'), verbose_name=_('tags'))

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    cover = models.ForeignKey('Image', related_name='cover', null=True, on_delete=models.SET_NULL)

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
            self._cover = Image.objects.filter(album__in=q, is_public=True).order_by("-date_added")[0]
          return self._cover
        except IndexError:
          return None
      else:
        return self.cover

    def get_absolute_url(self):
      return reverse('gallery', kwargs={"path" : self.slug()})

class Image(ImageModel):
    title = models.CharField(max_length=255)
    title_slug = models.SlugField(_('slug'), editable = False, max_length=255)
    date_added = models.DateTimeField(_('date added'), default=datetime.now, editable = False, auto_now_add = True)
    date_taken = models.DateTimeField(_('date taken'), null=True, blank=True, editable=False)
    date_modified = models.DateTimeField(_('date modified'), editable = False, auto_now = True, default=datetime.now)
    original_image = models.ImageField(upload_to='gallery')
    num_views = models.PositiveIntegerField(editable=False, default=0)

    text = models.TextField(_('text'), blank=True)
    is_public = models.BooleanField(_('is public'), default=True, help_text=_('Public images will be displayed in the default views.'))
    tags = TagField(help_text=_('Separate tags with spaces, put quotes around multiple-word tags.'), verbose_name=_('tags'))

    enable_comments = models.BooleanField(_('can comment'), default=True)

    album = models.ForeignKey(Album)


    class IKOptions:
        # This inner class is where we define the ImageKit options for the model
        spec_module = getattr(settings, 'GALLERY_SPECS', 'gallery.specs')
        cache_dir = 'cache'
        image_field = 'original_image'
        save_count_as = 'num_views'

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



