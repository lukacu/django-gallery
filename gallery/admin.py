#!/usr/bin/python
# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from django.conf import settings
from django.contrib.admin.util import unquote
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import admin
from django.forms import ModelForm
from mptt.admin import MPTTModelAdmin
from gallery.models import Album, Image
from imagekit.admin import AdminThumbnail

from mptt.forms import TreeNodeChoiceField

class AlbumAdminForm(ModelForm):

    class Meta:
        model = Album

    def __init__(self, *args, **kwargs):
        super(AlbumAdminForm, self).__init__(*args, **kwargs)
        q = self.instance.get_descendants(include_self=True).filter(is_public=True).values("id")
        self.fields['cover'].queryset = Image.objects.filter(album__in=q, is_public=True).order_by("-date_added")


class AlbumAdmin(MPTTModelAdmin):
    list_display = ('title', 'album_cover', 'is_public', 'order', 'move_up_down_links')
    list_filter = ['is_public']
    mptt_level_indent = 40
    form = AlbumAdminForm

    def get_urls(self):
      from django.conf.urls.defaults import patterns, url
      info = self.model._meta.app_label, self.model._meta.module_name
      return patterns('',
        url(r'^(.+)/move-(up)/$', self.admin_site.admin_view(self.move_album), name='%s_%s_move_up' % info),
        url(r'^(.+)/move-(down)/$', self.admin_site.admin_view(self.move_album), name='%s_%s_move_down' % info),
      ) + super(AlbumAdmin, self).get_urls()

    def move_album(self, request, object_id, direction):
      obj = get_object_or_404(self.model, pk=unquote(object_id))
      if direction == 'up':
        relative = obj.get_previous_sibling()
        if relative:
          obj.move_to(relative, 'left')
      else:
        relative = obj.get_next_sibling()
        if relative:
          obj.move_to(relative, 'right')
      return HttpResponseRedirect('../../')

    def move_up_down_links(self, obj):
      var = {'app_label': self.model._meta.app_label, 'module_name': self.model._meta.module_name, 'object_id': obj.id, 'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX }
      if obj.get_previous_sibling():
        up = '<a href="../../%(app_label)s/%(module_name)s/%(object_id)s/move-up/"><img src="%(ADMIN_MEDIA_PREFIX)simg/admin/arrow-up.gif" alt="Move up" /></a>' % var
      else:
        up = ''
      if obj.get_next_sibling():
        down = '<a href="../../%(app_label)s/%(module_name)s/%(object_id)s/move-down/"><img src="%(ADMIN_MEDIA_PREFIX)simg/admin/arrow-down.gif" alt="Move up" /></a>' % var
      else:
        down = ''
      return "%s %s" % (up, down)

    move_up_down_links.allow_tags = True
    move_up_down_links.short_description = 'Move'

    def album_cover(self, obj):
      cover = obj.cover_image()
      if not cover:
        return "<em>Not defined</em>"
      return '<img src="%s" alt="%s" style="width: 42px;" />' % (cover.cover_image.url, cover.title)

    album_cover.allow_tags = True
    album_cover.short_description = 'Cover'

class ImageAdmin(admin.ModelAdmin):
    list_display = ('admin_thumbnail', 'title', 'album', 'date_added', 'is_public')
    list_display_links = ['title']
    list_filter = ['date_added', 'album', 'is_public']
    search_fields = ['title', 'title_slug', 'text']
    list_per_page = 20
    admin_thumbnail = AdminThumbnail(image_field='thumbnail_image', template="gallery/admin/thumbnail.html")

admin.site.register(Album, AlbumAdmin)
admin.site.register(Image, ImageAdmin)
