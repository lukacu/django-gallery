# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed
from django.contrib.sites.models import Site
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.http import urlquote
from django.shortcuts import get_object_or_404
from django.contrib.markup.templatetags.markup import markdown
from django.utils.translation import ugettext_lazy as _
from django.contrib.markup.templatetags.markup import markdown

from tagging.models import Tag

from gallery.models import Album, Image

class MediaRSSFeed(Rss201rev2Feed):
    """Basic implementation of Yahoo Media RSS (mrss)
    http://video.search.yahoo.com/mrss

    Includes these elements in the Item feed:
    media:content
        url, width, height
    media:thumbnail
        url, width, height
    media:description
    media:title
    media:keywords
    """
    def rss_attributes(self):
        attrs = super(MediaRSSFeed, self).rss_attributes()
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        attrs['xmlns:atom'] = 'http://www.w3.org/2005/Atom'
        return attrs

    def add_item_elements(self, handler, item):
        """Callback to add elements to each item (item/entry) element."""
        super(MediaRSSFeed, self).add_item_elements(handler, item)

        if 'media:title' in item:
            handler.addQuickElement(u"media:title", item['title'])
        if 'media:description' in item:
            handler.addQuickElement(u"media:description", item['description'])

        if 'content_url' in item:
            content = dict(url=item['content_url'])
            if 'content_width' in item:
                content['width'] = str(item['content_width'])
            if 'content_height' in item:
                content['height'] = str(item['content_height'])
            handler.addQuickElement(u"media:content", '', content)
        
        if 'thumbnail_url' in item:
            thumbnail = dict(url=item['thumbnail_url'])
            if 'thumbnail_width' in item:
                thumbnail['width'] = str(item['thumbnail_width'])
            if 'thumbnail_height' in item:
                thumbnail['height'] = str(item['thumbnail_height'])
            handler.addQuickElement(u"media:thumbnail", '', thumbnail)

        if 'keywords' in item:
            handler.addQuickElement(u"media:keywords", item['keywords'])
                                

class GalleryFeed(Feed):
    feed_type = MediaRSSFeed
    item_limit = 20

    def title(self):
        return _("Gallery feed")

    def link(self):
        return reverse('gallery', kwargs={"path" : "" })

    def items(self):
        return Image.objects.filter(is_public=True).order_by("-date_added")[0:20]

    def item_pubdate(self, obj):
        return obj.date_added

    def item_extra_kwargs(self, obj):
        root = "http://" + Site.objects.get_current().domain

        item = {'media:title': obj.title,
                'media:description': obj.text,
                'content_url': root + obj.display_image.url,
                'content_width': obj.display_image.width,
                'content_height': obj.display_image.height,
                'thumbnail_url': root + obj.thumbnail_image.url,
                'thumbnail_width': obj.thumbnail_image.width,
                'thumbnail_height': obj.thumbnail_image.height,
               }

#        if len(obj.tags) > 0:
#           keywords = [tag.name for tag in Tag.objects.get_for_object(obj)]
#           item['keywords'] = keywords

        return item

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown(item.text)

    def item_categories(self, item):
      return [tag.name for tag in Tag.objects.get_for_object(item)]

    def item_guid(self, item):
      return "gallery_item_%d" % item.id

class AlbumFeed(Feed):
    feed_type = MediaRSSFeed
    item_limit = 20

    def get_object(self, request, album_id):
        return get_object_or_404(Album, pk=album_id)

    def title(self, album):
        return album.title

    def description(self, album):
        return album.text

    def link(self, album):
        return reverse('gallery', kwargs={"path" : album.slug() })

    def items(self, album):
        q = album.get_descendants(include_self=True).filter(is_public=True).values("id")
        return Image.objects.filter(album__in=q, is_public=True).order_by("-date_added")[0:20]

    def item_title(self, item):
      return item.title

    def item_description(self, item):
      return markdown(item.text)

    def item_pubdate(self, obj):
        return obj.date_added

    def item_extra_kwargs(self, obj):
        root = "http://" + Site.objects.get_current().domain

        item = {'media:title': obj.title,
                'media:description': obj.text,
                'content_url': root + obj.display_image.url,
                'content_width': obj.display_image.width,
                'content_height': obj.display_image.height,
                'thumbnail_url': root + obj.thumbnail_image.url,
                'thumbnail_width': obj.thumbnail_image.width,
                'thumbnail_height': obj.thumbnail_image.height,
               }

#        if len(obj.tags) > 0:
#           keywords = [tag.name for tag in Tag.objects.get_for_object(obj)]
#           item['keywords'] = keywords

        return item

    def item_categories(self, item):
      return [tag.name for tag in Tag.objects.get_for_object(item)]

    def item_guid(self, item):
      return "gallery_item_%d" % item.id
