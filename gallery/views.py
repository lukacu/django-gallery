# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*- 
from django.db.models import Count
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext, loader
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponse
from django.core import serializers
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from gallery.models import Image, Album
from tagging.models import Tag, TaggedItem

def recent(request):
    recent = Image.objects.filter(is_public = True).order_by("-date_added")[0:getattr(settings, 'GALLERY_RECENT', 20)]
    return render_to_response('gallery/gallery.html',
      { "images" : recent },
      context_instance = RequestContext(request)
    )


def album(request, id, path):
    try:

        album = Album.objects.get(id=id, is_public = True)
        images = Image.objects.filter(album=album, is_public = True) #.order_by(order)

        return render_to_response('gallery/album.html',
          {"album" : album,"images" : images},
          context_instance = RequestContext(request)
        )
    except Album.DoesNotExist:
        raise Http404

def tag(request, slug):
    try:

        tag = get_object_or_404(Tag, slug = slug)

        images = TaggedItem.objects.get_by_model(Image.objects.filter(is_public=True).order_by("date_added"), tag)

        return render_to_response('gallery/gallery.html',
            {"images" : images},
            context_instance = RequestContext(request)
        )
    except Tag.DoesNotExist:
        raise Http404


def image(request, id, path):
    try:
        image = Image.objects.get(is_public = True, id=id)

        return render_to_response('gallery/image.html',
                {"image" : image },
            context_instance = RequestContext(request)
        )
    except Image.DoesNotExist:
        raise Http404

def json_get_image(request):
  if request.GET.has_key('image'):
    try:
      image = Image.objects.filter(id=int(request.GET['image']))
    except MultiValueDictKeyError:
      image = None
  elif request.GET.has_key('album'):
    try:
      image = Image.objects.filter(album=int(request.GET['album'])).order_by('?')[:1]
    except MultiValueDictKeyError:
      image = None
  else:
    try:
      image = Image.objects.order_by('?')[:1]
    except MultiValueDictKeyError:
      image = None

  if image is not None:
    return HttpResponse(serializers.serialize('json', image), mimetype='text/plain')
  else:
    return HttpResponse("", mimetype='text/plain')


