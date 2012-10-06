# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from django.conf.urls import *
from gallery.feeds import GalleryFeed, AlbumFeed

urlpatterns = patterns('',
    url(r'^$', 'gallery.views.recent', name="gallery"),
    url(r'^feed/$', GalleryFeed(), name="gallery-feed"),
    url(r'^feed/album/(?P<album_id>[0-9]+)/$', AlbumFeed(), name="gallery-album-feed"),
    url(r'^image/(?P<id>[0-9]+)/(?P<path>[a-z\-_0-9\/]*)$', 'gallery.views.image', name="gallery-image"),
    url(r'^album/(?P<id>[0-9]+)/(?P<path>[a-z\-_0-9\/]*)$', 'gallery.views.album', name="gallery-album"),
    url(r'^tags/(?P<slug>[a-z\-_0-9\/]*)/$', 'gallery.views.tag', name="gallery-tag"),
)

