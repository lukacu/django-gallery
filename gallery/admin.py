#!/usr/bin/python
# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from django.conf import settings
from django.contrib.admin.util import unquote
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import admin
from django.forms import ModelForm
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


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_public')
    list_filter = ['is_public']
    form = AlbumAdminForm

class ImageAdmin(admin.ModelAdmin):
    list_display = ('admin_thumbnail', 'title', 'album', 'date_added', 'is_public')
    list_display_links = ['title']
    list_filter = ['date_added', 'album', 'is_public']
    search_fields = ['title', 'text']
    list_per_page = 20
    admin_thumbnail = AdminThumbnail(image_field='thumbnail_image', template="gallery/admin/thumbnail.html")

admin.site.register(Album, AlbumAdmin)
admin.site.register(Image, ImageAdmin)
