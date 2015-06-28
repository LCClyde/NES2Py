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
Test cartridge parsing
"""
from export.cartridge import read_header, parse_file
from export.cartridge import PROG_ROM_SIZE, CHR_ROM_SIZE
import unittest
import struct
import numpy
import os

class TestHeader(unittest.TestCase):
    """
    Run header specific parsing tests.
    """
    def test_id(self):
        """
        Ensure the header can find the NES keyword, otherwise Raise exception
        """
        raw = 'NES\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        header, prog_rom, chr_rom = read_header(raw)
        self.assertEqual(header['ID'], 'NES')
        self.assertEqual(prog_rom, 0)
        self.assertEqual(chr_rom, 0)
        self.assertEqual(header['MAPPER'], 0)
        self.assertFalse(header['FOUR_SCREEN'])
        self.assertFalse(header['TRAINER'])
        self.assertFalse(header['BATTERY_BACK'])
        self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
        self.assertFalse(header['PLAY_CHOICE_10'])
        self.assertFalse(header['VS_UNISYSTEM'])
        self.assertFalse(header['NES_2.0'])

        raw = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with self.assertRaises(IOError):
            read_header(raw)

    def test_prog_rom(self):
        """
        Ensure all possible prog rom sizes work.
        """
        prefix = 'NES\x1a'
        suffix = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        for i in range(0, 256):
            header, prog_rom, chr_rom = \
                    read_header(prefix + struct.pack('B', i) + suffix)
            self.assertEqual(header['ID'], 'NES')
            self.assertEqual(prog_rom, i)
            self.assertEqual(chr_rom, 0)
            self.assertEqual(header['MAPPER'], 0)
            self.assertFalse(header['FOUR_SCREEN'])
            self.assertFalse(header['TRAINER'])
            self.assertFalse(header['BATTERY_BACK'])
            self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
            self.assertFalse(header['PLAY_CHOICE_10'])
            self.assertFalse(header['VS_UNISYSTEM'])
            self.assertFalse(header['NES_2.0'])

    def test_chr_rom(self):
        """
        Ensure all possible chr rom sizes work.
        """
        prefix = 'NES\x1a\x00'
        suffix = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        for i in range(0, 256):
            header, prog_rom, chr_rom = \
                    read_header(prefix + struct.pack('B', i) + suffix)
            self.assertEqual(header['ID'], 'NES')
            self.assertEqual(prog_rom, 0)
            # chr_rom returns double (one for left and right)
            self.assertEqual(chr_rom, i * 2)
            self.assertEqual(header['MAPPER'], 0)
            self.assertFalse(header['FOUR_SCREEN'])
            self.assertFalse(header['TRAINER'])
            self.assertFalse(header['BATTERY_BACK'])
            self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
            self.assertFalse(header['PLAY_CHOICE_10'])
            self.assertFalse(header['VS_UNISYSTEM'])
            self.assertFalse(header['NES_2.0'])

    def test_mapper(self):
        """
        Ensure all possible mappers work.
        """
        prefix = 'NES\x1a\x00\x00'
        suffix = '\x00\x00\x00\x00\x00\x00\x00'
        for low in range(0, 16):
            for high in range(0, 16):
                mapper = high * 16 + low
                mapper_str = struct.pack( \
                        'B', (low << 4)) + struct.pack('B', (high << 4))
                header, prog_rom, chr_rom = \
                        read_header(prefix + mapper_str + suffix)
                self.assertEqual(header['ID'], 'NES')
                self.assertEqual(prog_rom, 0)
                self.assertEqual(chr_rom, 0)
                self.assertEqual(header['MAPPER'], mapper)
                self.assertFalse(header['FOUR_SCREEN'])
                self.assertFalse(header['TRAINER'])
                self.assertFalse(header['BATTERY_BACK'])
                self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
                self.assertFalse(header['PLAY_CHOICE_10'])
                self.assertFalse(header['VS_UNISYSTEM'])
                self.assertFalse(header['NES_2.0'])

    def test_four_screen(self):
        """
        Ensure four screen can be set
        """
        raw = 'NES\x1a\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        header, prog_rom, chr_rom = read_header(raw)
        self.assertEqual(header['ID'], 'NES')
        self.assertEqual(prog_rom, 0)
        self.assertEqual(chr_rom, 0)
        self.assertEqual(header['MAPPER'], 0)
        self.assertTrue(header['FOUR_SCREEN'])
        self.assertFalse(header['TRAINER'])
        self.assertFalse(header['BATTERY_BACK'])
        self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
        self.assertFalse(header['PLAY_CHOICE_10'])
        self.assertFalse(header['VS_UNISYSTEM'])
        self.assertFalse(header['NES_2.0'])

    def test_trainer(self):
        """
        Ensure trainer can be set
        """
        raw = 'NES\x1a\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        header, prog_rom, chr_rom = read_header(raw)
        self.assertEqual(header['ID'], 'NES')
        self.assertEqual(prog_rom, 0)
        self.assertEqual(chr_rom, 0)
        self.assertEqual(header['MAPPER'], 0)
        self.assertFalse(header['FOUR_SCREEN'])
        self.assertTrue(header['TRAINER'])
        self.assertFalse(header['BATTERY_BACK'])
        self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
        self.assertFalse(header['PLAY_CHOICE_10'])
        self.assertFalse(header['VS_UNISYSTEM'])
        self.assertFalse(header['NES_2.0'])

    def test_battery_back(self):
        """
        Ensure trainer can be set
        """
        raw = 'NES\x1a\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        header, prog_rom, chr_rom = read_header(raw)
        self.assertEqual(header['ID'], 'NES')
        self.assertEqual(prog_rom, 0)
        self.assertEqual(chr_rom, 0)
        self.assertEqual(header['MAPPER'], 0)
        self.assertFalse(header['FOUR_SCREEN'])
        self.assertFalse(header['TRAINER'])
        self.assertTrue(header['BATTERY_BACK'])
        self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
        self.assertFalse(header['PLAY_CHOICE_10'])
        self.assertFalse(header['VS_UNISYSTEM'])
        self.assertFalse(header['NES_2.0'])

    def test_mirroring(self):
        """
        Ensure mirroring can be set to vertical
        """
        raw = 'NES\x1a\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        header, prog_rom, chr_rom = read_header(raw)
        self.assertEqual(header['ID'], 'NES')
        self.assertEqual(prog_rom, 0)
        self.assertEqual(chr_rom, 0)
        self.assertEqual(header['MAPPER'], 0)
        self.assertFalse(header['FOUR_SCREEN'])
        self.assertFalse(header['TRAINER'])
        self.assertFalse(header['BATTERY_BACK'])
        self.assertEqual(header['MIRRORING'], 'VERTICAL')
        self.assertFalse(header['PLAY_CHOICE_10'])
        self.assertFalse(header['VS_UNISYSTEM'])
        self.assertFalse(header['NES_2.0'])

    def test_play_choice_10(self):
        """
        Ensure play choice 10 can be set
        """
        raw = 'NES\x1a\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00'
        header, prog_rom, chr_rom = read_header(raw)
        self.assertEqual(header['ID'], 'NES')
        self.assertEqual(prog_rom, 0)
        self.assertEqual(chr_rom, 0)
        self.assertEqual(header['MAPPER'], 0)
        self.assertFalse(header['FOUR_SCREEN'])
        self.assertFalse(header['TRAINER'])
        self.assertFalse(header['BATTERY_BACK'])
        self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
        self.assertTrue(header['PLAY_CHOICE_10'])
        self.assertFalse(header['VS_UNISYSTEM'])
        self.assertFalse(header['NES_2.0'])

    def test_vs_unisystem(self):
        """
        Ensure vs unisystem can be set
        """
        raw = 'NES\x1a\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00'
        header, prog_rom, chr_rom = read_header(raw)
        self.assertEqual(header['ID'], 'NES')
        self.assertEqual(prog_rom, 0)
        self.assertEqual(chr_rom, 0)
        self.assertEqual(header['MAPPER'], 0)
        self.assertFalse(header['FOUR_SCREEN'])
        self.assertFalse(header['TRAINER'])
        self.assertFalse(header['BATTERY_BACK'])
        self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
        self.assertFalse(header['PLAY_CHOICE_10'])
        self.assertTrue(header['VS_UNISYSTEM'])
        self.assertFalse(header['NES_2.0'])

    def test_nes_2_0(self):
        """
        Ensure nes 2.0 can be set
        """
        raw = 'NES\x1a\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00'
        header, prog_rom, chr_rom = read_header(raw)
        self.assertEqual(header['ID'], 'NES')
        self.assertEqual(prog_rom, 0)
        self.assertEqual(chr_rom, 0)
        self.assertEqual(header['MAPPER'], 0)
        self.assertFalse(header['FOUR_SCREEN'])
        self.assertFalse(header['TRAINER'])
        self.assertFalse(header['BATTERY_BACK'])
        self.assertEqual(header['MIRRORING'], 'HORIZONTAL')
        self.assertFalse(header['PLAY_CHOICE_10'])
        self.assertFalse(header['VS_UNISYSTEM'])
        self.assertTrue(header['NES_2.0'])

class TestROM(unittest.TestCase):
    """
    Test ROM parsing
    """
    def setUp(self):
        raw = 'NES\x1a\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.prog_rom = []
        self.chr_rom = []
        for _ in range(0, 3):
            self.prog_rom.append(numpy.random.randint( \
                    256, size=PROG_ROM_SIZE).astype('uint8'))
            self.chr_rom.append(numpy.random.randint( \
                    256, size=CHR_ROM_SIZE).astype('uint8'))
            self.chr_rom.append(numpy.random.randint( \
                    256, size=CHR_ROM_SIZE).astype('uint8'))

        # Write to a file
        self.filename = 'temp.nes'
        with open(self.filename, 'wb') as nes_file:
            nes_file.write(raw)
            for array in self.prog_rom:
                array.tofile(nes_file)
            for array in self.chr_rom:
                array.tofile(nes_file)

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_rom(self):
        """
        Ensure that ROM values are correct
        """
        self.assertTrue(os.path.isfile(self.filename))
        cart = parse_file(self.filename)
        self.assertEqual(len(cart['PROG_ROM']), len(self.prog_rom))
        self.assertEqual(len(cart['CHR_ROM']), len(self.chr_rom))

        i = 0
        for array in self.prog_rom:
            self.assertTrue(numpy.array_equal(array, cart['PROG_ROM'][i]))
            i += 1

        i = 0
        for array in self.chr_rom:
            self.assertTrue(numpy.array_equal(array, cart['CHR_ROM'][i]))
            i += 1


if __name__ == '__main__':
    unittest.main()
