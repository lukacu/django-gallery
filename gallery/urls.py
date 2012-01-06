# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from django.conf.urls.defaults import *
from gallery.feeds import GalleryFeed, AlbumFeed

urlpatterns = patterns('',
    url(r'^feed/gallery/$', GalleryFeed(), name="gallery-feed"),
    url(r'^feed/album/(?P<album_id>[0-9]+)/$', AlbumFeed(), name="gallery-album-feed"),
    url(r'^(?P<path>[a-z\-_0-9\/]*)$', 'gallery.views.resolve', name="gallery"),
)

