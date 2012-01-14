#!/usr/bin/python
# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from gallery.models import Album, Image

from mptt.forms import TreeNodeChoiceField

class AlbumAdmin(MPTTModelAdmin):
    list_display = ('title', 'is_public')
    list_filter = ['is_public']
    mptt_level_indent = 40

class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'is_public', 'tags') #, 'admin_thumbnail')
    list_filter = ['date_added', 'album']
    search_fields = ['title', 'title_slug', 'text']
    list_per_page = 20
#    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        print kwargs
#        if db_field.name == "gallery":
#            kwargs["widget"] = TreeNodeChoiceField
#        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Album, AlbumAdmin)
admin.site.register(Image, ImageAdmin)
