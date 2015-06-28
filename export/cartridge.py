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
The cartridge deals with the raw .nes file format. It's primary function is
to read and parse the file into a usable dictionary.
"""
import struct
import numpy

PROG_ROM_SIZE = 16384
CHR_ROM_SIZE = 4096

def read_header(raw):
    """
    Reads the nes header and places the relevant data in a dictionary. The
    keys are the following:
        ID (string): This will always be 'NES'
        MAPPER (int): The nes mapper number.
        FOUR_SCREEN (bool): Does the cartridge support four screen?
        TRAINER (bool): Does the cartridge contain a 512 byte trainer?
        BATTER_BACK (bool): Is the cartridge battery backed?
        MIRRORING (string): Is the cartridge HORIZONTAL or VERTICAL mirrored?
        PLAY_CHOICE_10 (bool): Is the cartridge a play choice 10?
        VS_UNISYSTEM (bool): Is the cartridge a VS Unisystem game?
        NES_2.0 (bool): Is the header an iNES 2.0 header?

    Args:
        raw (string): The first 16 raw bytes from the .nes file

    Returns:
        dict: The key value pairs for the header information.
        int: The number of 16384 byte programming rom sections.
        int: The number of 4096 byte character rom sections.

    Raises:
        IOError: If the nes file does not start with NES.
    """
    header = dict()

    header['ID'] = raw[:3]

    if header['ID'] != 'NES':
        raise IOError('Unknown header type: ' + header['ID'])

    flags6 = struct.unpack('B', raw[6])[0]
    flags7 = struct.unpack('B', raw[7])[0]
    header['MAPPER'] = (flags6 >> 4) | (flags7 & 0xF0)
    header['FOUR_SCREEN'] = (flags6 & 0x08) != 0
    header['TRAINER'] = (flags6 & 0x04) != 0
    header['BATTERY_BACK'] = (flags6 & 0x02) != 0
    header['MIRRORING'] = 'HORIZONTAL' if (flags6 & 0x01) == 0 else 'VERTICAL'
    header['PLAY_CHOICE_10'] = (flags7 & 0x02) != 0
    header['VS_UNISYSTEM'] = (flags7 & 0x01) != 0
    header['NES_2.0'] = (flags7 & 0x08) == 0x08

    return header, struct.unpack('B', raw[4])[0], \
            struct.unpack('B', raw[5])[0] * 2

def parse_file(pathname):
    """
    Parses the .nes file into a usable dictionary. In addition to the header
    keys, this adds the following keys:
        PROM_ROM (list): A list of numpy arrays representing the programming
            read only memory
        CHR_ROM (list): A list of numpy arrays representing the character
            read only memory. This is double the number represented in the
            header, because it separates out the left and right sections.

    Args:
        pathname (string): The full pathname to the .nes file.

    Returns:
        dict: Key value pairs for all metadata.
    """
    with open(pathname, 'rb') as nes_file:
        raw = nes_file.read(16)
        header, prog_rom_size, chr_rom_size = read_header(raw)

        # Load programming read only memory
        header['PROG_ROM'] = []
        for _ in range(0, prog_rom_size):
            header['PROG_ROM'].append( \
                    numpy.fromfile(nes_file,
                                   dtype='uint8',
                                   count=PROG_ROM_SIZE))

        header['CHR_ROM'] = []
        for _ in range(0, chr_rom_size):
            header['CHR_ROM'].append( \
                    numpy.fromfile(nes_file,
                                   dtype='uint8',
                                   count=CHR_ROM_SIZE))

        return header

