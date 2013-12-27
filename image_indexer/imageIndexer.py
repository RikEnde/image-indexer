#!/usr/bin/env python
from abc import abstractmethod
import hashlib

import string
import imghdr
from fractions import Fraction
from decimal import Decimal
from datetime import datetime, date
import Image

import pyexiv2
from pyexiv2.utils import NotifyingList

from image_indexer.fileIndexer import FileIndexer


class ImageIndexer(FileIndexer):
    """
    Subclass of FileIndexer that handles image files
    Find given image file, extract file stat and exif info, and persist it as a document
    """

    def get_file_type(self, name, path):
        """
        Make an attempt at identifying image type. If the file is not identified as an image file,
        return None, which causes the file not to be indexed
        """
        return imghdr.what(path)

    def make_data(self, name, path, stat):
        """
        Get generic part of file metadata and add exif info for
        """
        data = FileIndexer.make_data(self, name, path, stat)
        # Return none if the file isn't identified as an image
        if data:
            data['exif'] = self.get_exif(path)
            return data
        else:
            return None

    def get_exif(self, path):
        """
        Extract exif info from file and preprocess it
        The preprocessing is necessary because pymongo can't convert some types to mongo's json
        """
        exif = None

        metadata = pyexiv2.ImageMetadata(path)
        try:
            metadata.read()

            exif = {}
            for key in metadata.exif_keys:
                value = metadata[key].value
                if type(value) == Fraction or type(value) == Decimal:
                    value = float(value)
                elif type(value) == str:
                    value = filter(lambda x: x in string.printable, value)
                elif type(value) == date:
                    value = datetime.combine(value, datetime.min.time())
                elif type(value) == NotifyingList:
                    value = map(float, value)

                if self.debug:
                    print key, value, type(value)
                exif[key.replace('.', '')] = value
        except Exception as e:
            print "Error while reading exif info", e, path

        return exif    

    @abstractmethod
    def get_bytes(self, path):
        """
        First read the entire image as a file
        """
        return Image.open(path).tostring()

