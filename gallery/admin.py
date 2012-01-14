#!/usr/bin/python
# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from gallery.models import Album, Image
from imagekit.admin import AdminThumbnail

from mptt.forms import TreeNodeChoiceField

class AlbumAdmin(MPTTModelAdmin):
    list_display = ('title', 'is_public')
    list_filter = ['is_public']
    mptt_level_indent = 40

class ImageAdmin(admin.ModelAdmin):
    list_display = ('admin_thumbnail', 'title', 'album', 'date_added', 'is_public')
    list_display_links = ['title']
    list_filter = ['date_added', 'album', 'is_public']
    search_fields = ['title', 'title_slug', 'text']
    list_per_page = 20
    admin_thumbnail = AdminThumbnail(image_field='thumbnail_image', template="gallery/admin/thumbnail.html")

admin.site.register(Album, AlbumAdmin)
admin.site.register(Image, ImageAdmin)
