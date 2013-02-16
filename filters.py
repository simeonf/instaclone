#!/usr/bin/env python
"""
Started from http://www.mike-griffith.com/blog/2010/01/batch-convert-images-to-sepia-tone-with-python/

Usage:
    python filters.py input.jpg output.jpg

"""

import Image as PIL_Image
import shutil, os
from optparse import OptionParser

registry = {}

def register(f):
    registry[f.func_name] = f
    return f

def open_image(filename):
    """ grab a PIL image from the given location
    """
    image = PIL_Image.open(filename)
    image.load()
    return image

def save_image(image, filename, quality=95):
    """ save the PIL image to disk
    """
    image.save(filename, "JPEG", quality=quality)

def make_linear_ramp(white):
    """ generate a palette in a format acceptable for `putpalette`, which
        expects [r,g,b,r,g,b,...]
    """
    ramp = []
    r, g, b = white
    for i in range(255):
        ramp.extend((r*i/255, g*i/255, b*i/255))
    return ramp

def putpalette(image, palette):
    # convert to grayscale
    orig_mode = image.mode
    if orig_mode != "L":
        image = image.convert("L")

    # optional: apply contrast enhancement here, e.g.
    #image = ImageOps.autocontrast(image)

    # apply palette
    image.putpalette(palette)

    # convert back to its original mode
    if orig_mode != "L":
        image = image.convert(orig_mode)
    return image
    
@register
def sepia(image):
    """ Apply a sepia-tone filter to the given PIL Image
        Based on code at: http://effbot.org/zone/pil-sepia.htm
    """
    # make sepia ramp (tweak color as necessary)
    palette = make_linear_ramp((255, 240, 192))
    return putpalette(image, palette)

@register
def red(image):
    """ Apply a sepia-tone filter to the given PIL Image
        Based on code at: http://effbot.org/zone/pil-sepia.htm
    """
    # make sepia ramp (tweak color as necessary)
    palette = make_linear_ramp((200, 40, 40))
    return putpalette(image, palette)

@register
def blue(image):
    """ Apply a sepia-tone filter to the given PIL Image
        Based on code at: http://effbot.org/zone/pil-sepia.htm
    """
    # make sepia ramp (tweak color as necessary)
    palette = make_linear_ramp((0, 0, 255))
    return putpalette(image, palette)

@register
def purple(image):
    """ Apply a sepia-tone filter to the given PIL Image
        Based on code at: http://effbot.org/zone/pil-sepia.htm
    """
    # make sepia ramp (tweak color as necessary)
    palette = make_linear_ramp((100, 100, 255))
    return putpalette(image, palette)

@register
def gray(image):
    return image.convert('L')

def convert_image(filename, output_filename, filter_name='sepia'):
    if not os.path.exists(filename):
        return
    f = registry[filter_name]
    save_image(f(open_image(filename)), output_filename)

if __name__ == '__main__':
    parser = OptionParser(usage="Usage filters.py input.jpg output.jpg")
    parser.add_option('-f', '--filter',
                      type="choice",
                      choices=registry.keys(),
                      help='Specify a filter name eg "sepia" or "gray".')
    parser.set_defaults(filter="sepia")
    (options, files) = parser.parse_args()
    if len(files) != 2:
        raise Exception("Please specify input and output file.")
    print options.filter
    convert_image(*files, filter_name=options.filter)
