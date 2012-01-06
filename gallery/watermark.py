# -*- Mode: python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from imagekit.processors import ImageProcessor
from imagekit.lib import *

class Watermark(ImageProcessor):
    image_path = None
    style = 'poss'
    opacity = 1
    offset = '15x15'
    looks_best = '300x300'
    
    @classmethod
    def process(cls, image, fmt, obj=None):
        try:
            mark = Image.open(cls.image_path)
        except IOError, e:
            print e
#            raise IOError('Unable to open watermark source image %s: %s' % \
#                          (cls.image_path, e))
            return image, fmt
        return apply_watermark(image, mark, cls.style, cls.opacity, cls.offset, cls.looks_best), fmt


def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def apply_watermark(im, mark, style, opacity, offset, looks_best):
    """Adds a watermark to an image."""
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    if mark.mode != 'RGBA':
        mark = mark.convert('RGBA')
    
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    if style == 'tile':
        for y in range(0, im.size[1], mark.size[1]):
            for x in range(0, im.size[0], mark.size[0]):
                layer.paste(mark, (x, y))
    elif style == 'scale':
        # scale, but preserve the aspect ratio
        ratio = min(
            float(im.size[0]) / mark.size[0], float(im.size[1]) / mark.size[1])
        w = int(mark.size[0] * ratio)
        h = int(mark.size[1] * ratio)
        mark = mark.resize((w, h))
        layer.paste(mark, ((im.size[0] - w) / 2, (im.size[1] - h) / 2))
    elif style == 'poss':
        lbw,lbh = looks_best.split('x')
        offw,offh = offset.split('x')

        mark_width = mark.size[0] 
        mark_height = mark.size[1] 

     
        mark = mark.resize((mark_width, mark_height), Image.ANTIALIAS)
        
        mark_poss_w = im.size[0] - mark.size[0] - int(offw)
        mark_poss_h = im.size[1] - mark.size[1] - int(offh)
        
        layer.paste(mark,(mark_poss_w,mark_poss_h))
    else:
        layer.paste(mark, style)
    # composite the watermark with the layer
    return Image.composite(layer, im, layer)
