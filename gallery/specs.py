#!/usr/bin/python
# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from imagekit.specs import ImageSpec 
from imagekit import processors 
from gallery.watermark import Watermark
from django.conf import settings

# first we define our thumbnail resize processor 
class ResizeThumb(processors.Resize): 
    width = 128
    height = 128 
    crop = True

# now we define a display size resize processor
class ResizeDisplay(processors.Resize):
    width = 600 
    height = 600

# now lets create an adjustment processor to enhance the image at small sizes 
class EnchanceThumb(processors.Adjustment): 
    contrast = 1.2 
    sharpness = 1.1 

# now we can define our thumbnail spec 
class Thumbnail(ImageSpec): 
    access_as = 'thumbnail_image' 
    pre_cache = True 
    processors = [ResizeThumb, EnchanceThumb] 
    quality = 75

# and our display spec
class Display(ImageSpec):
    access_as = 'display_image' 
    increment_count = True
    processors = [ResizeDisplay]
    quality = 95

