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
Tests CHR ROM Extraction
"""
from export.chr_extract import extract, extract_pngs
from export.cartridge import CHR_ROM_SIZE
import unittest
import numpy
import os
import shutil

class TestCHRExtract(unittest.TestCase):
    """
    Test CHR ROM Extraction
    """
    def test_extract(self):
        """
        Ensure the correct values are collected when extracting
        an individual tile
        """
        inarray = numpy.array( \
                [0x00, 0xFF, 0x00, 0xFF, 0x55, 0xAA, 0x33, 0xCC, \
                 0x00, 0x00, 0xFF, 0xFF, 0x33, 0xCC, 0x0F, 0xF0], \
                             dtype='uint8')
        expected = numpy.array([[0, 0, 0, 0, 0, 0, 0, 0], \
                                [1, 1, 1, 1, 1, 1, 1, 1], \
                                [2, 2, 2, 2, 2, 2, 2, 2], \
                                [3, 3, 3, 3, 3, 3, 3, 3], \
                                [0, 1, 2, 3, 0, 1, 2, 3], \
                                [3, 2, 1, 0, 3, 2, 1, 0], \
                                [0, 0, 1, 1, 2, 2, 3, 3], \
                                [3, 3, 2, 2, 1, 1, 0, 0]], dtype='uint8')
        array = extract(inarray, 0)
        self.assertTrue(numpy.array_equal(array, expected))

    def test_extract_pngs(self):
        """
        Ensure a 4096 buffer can write out 256 PNG files
        """
        directory = './test_extract_pngs_dir'

        # Ensure this directory does not exist
        if os.path.isdir(directory):
            shutil.rmtree(directory)

        inarray = numpy.empty([CHR_ROM_SIZE], dtype='uint8')

        # Write the pngs
        extract_pngs(inarray, directory=directory)

        # Make sure we created 256 files
        self.assertTrue(os.path.isdir(directory))
        self.assertEqual(len(os.listdir(directory)), 256)

        # Delete the directory
        shutil.rmtree(directory)

if __name__ == '__main__':
    unittest.main()
