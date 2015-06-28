###############################################################################
# The MIT License (MIT)                                                       #
#                                                                             #
# Copyright (c) 2015 Clyde Stanfield                                          #
#                                                                             #
# Permission is hereby granted, free of charge, to any person obtaining a     #
# copy of this software and associated documentation files (the "Software"),  #
# to deal in the Software without restriction, including without limitation   #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
# and/or sell copies of the Software, and to permit persons to whom the       #
# Software is furnished to do so, subject to the following conditions:        #
#                                                                             #
# The above copyright notice and this permission notice shall be included in  #
# all copies or substantial portions of the Software.                         #
#                                                                             #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
# DEALINGS IN THE SOFTWARE.                                                   #
###############################################################################
"""
Handles CHR ROM into something more usable by modern processors. The CHR
ROM is arranged to be bitwise or'd together to create the images on a per
row basis. We would rather have a usable texture.
"""
import numpy
import os
from PIL import Image
from core.hex import to_hex

PIXEL_SCALE = 86

def extract(chr_rom, tile):
    """
    Extracts a single 8x8 image from CHR ROM as a 8x8 numpy array.

    Args:
        chr_rom (array): The 4096 numpy array representing CHR ROM
        tile (int): The tile number to extract

    Returns:
        array: The 8x8 image from CHR ROM.
    """
    address = tile * 16
    plane1 = numpy.unpackbits(chr_rom[address:address + 8])
    plane2 = numpy.unpackbits(chr_rom[address + 8:address + 16])
    plane2 = numpy.left_shift(plane2, 1)
    return numpy.bitwise_or(plane1, plane2).reshape((8, 8))

def extract_pngs(chr_rom, index=0, directory='.'):
    """
    Extracts all images from CHR ROM and saves them off as individual
    png files. The pixels are scaled to make them visible.

    Args:
        chr_rom (array): The 4096 numpy array representing CHR ROM
        index (int): The index of the CHR ROM. This is used to
            uniquely name the file.
        directory (path): The directory to save each png in. If this does
            not exists, the function will try to create it.
    """
    # Check if the directory exists
    if not os.path.isdir(directory):
        os.makedirs(directory)

    prefix = os.path.join(directory, 'chrrom_')
    lut = numpy.array([0x00, PIXEL_SCALE, PIXEL_SCALE * 2, PIXEL_SCALE * 3])

    for tile in range(0, 256):
        image = lut[extract(chr_rom, tile)].astype('uint8')
        image = Image.fromarray(image)
        image.save(prefix + to_hex(index) + to_hex(tile) + '.png')
