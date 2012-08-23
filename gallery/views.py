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

def resolve(request, path):

  tokens = filter(lambda x: len(x)>0, path.split('/')) 
  tokens.reverse()
  original = tokens

  if hasattr(request, 'breadcrumbs'):
    request.breadcrumbs(_("Gallery"), reverse(resolve, kwargs={"path" : "/"}))

  if tokens == None or len(tokens) == 0:
    recent = Image.objects.filter(is_public = True).order_by("-date_added")[0:getattr(settings, 'GALLERY_RECENT', 5)]
    return render_to_response('gallery/gallery.html',
      {"albums" : Album.tree.root_nodes().filter(is_public = True), "recent" : recent},
      context_instance = RequestContext(request)
    )

  albums = Album.tree.root_nodes().filter(is_public = True)
  current_album = None
  parent = None

  while not len(tokens) == 0:
    token = tokens.pop()
    albums = list(albums.filter(title_slug=token, parent=parent, is_public = True).all())
    if len(albums) == 0:
      tokens.append(token)
      break
    current_album = albums[0]
    parent = current_album.id

    albums = current_album.children.filter(is_public=True)
    if hasattr(request, 'breadcrumbs'):
      request.breadcrumbs(current_album.title, reverse(resolve, kwargs={"path" : current_album.slug()})) 

    #  for o in current_album.get_ancestors():
    #    request.breadcrumbs
    #  breadcrumbs.extend([{'title' : o.title, 'url' : reverse(resolve, kwargs={"path" : o.slug()})} for o in current_album.get_ancestors() ])

  if len(tokens) == 0:
    order = "%s%s" % ('' if current_album.get_sorting_order() else '-', current_album.get_sorting_field())
    images = Image.objects.filter(album=current_album, is_public = True).order_by(order)

    return render_to_response('gallery/album.html',
      {"album" : current_album, "subalbums" : albums ,"images" : images},
      context_instance = RequestContext(request)
    )

  if len(tokens) == 1:
    try:
      image = Image.objects.get(is_public = True, album=current_album, title_slug=tokens[0])
      if hasattr(request, 'breadcrumbs'):
        request.breadcrumbs(image.title, reverse(resolve, kwargs={"path" : image.slug()}))

      # This part gets a bit long because we have to determine field names and directions of sorting
      order_field = current_album.get_sorting_field()
      order = current_album.get_sorting_order()
      previous_cpr = "%s__%s" % (order_field, 'gt' if order else 'lt')
      next_cpr = "%s__%s" % (order_field, 'lt' if order else 'gt')
      previous_order = "%s%s" % ('' if order else '-', order_field)
      next_order = "%s%s" % ('-' if order else '', order_field)
      try:
        previous = Image.objects.filter(is_public = True, album=current_album).filter(**{previous_cpr : getattr(image, order_field) }).order_by(previous_order)[0]
      except IndexError:
        previous = None

      try:
        next = Image.objects.filter(is_public = True, album=current_album).filter(**{next_cpr : getattr(image, order_field) }).order_by(next_order)[0]
      except IndexError:
        next = None

      return render_to_response('gallery/image.html',
        {"image" : image, "next" : next, "previous" : previous },
        context_instance = RequestContext(request)
      )
    except Image.DoesNotExist:
        raise Http404

  #raise Http404

  tokens = original
  tokens.reverse()
  if len(tokens) > 0:
    try:
      album = Album.objects.get(title_slug=tokens[0], is_public = True)
      if len(tokens) == 1:
        return HttpResponsePermanentRecirect(album.get_absolute_url())
      else:
        image = Image.objects.get(album=album, title_slug=tokens[1], is_public = True)
        return HttpResponsePermanentRedirect(image.get_absolute_url())
    except Album.DoesNotExist:
      raise Http404
    except Image.DoesNotExist:
      raise Http404

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


