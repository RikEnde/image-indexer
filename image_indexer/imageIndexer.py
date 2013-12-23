#!/usr/bin/env python

import string
import pyexiv2
import os
import imghdr
import hashlib

from PIL import Image
from pyexiv2.utils import NotifyingList
from fractions import Fraction
from decimal import Decimal
from datetime import datetime, date
from stat import *


class ImageIndexer(object):
    """
    Find given image file, extract file stat and exif info, and persist it as a document
    """
    def __init__(self, path, dao, verbose=False, debug=False, hashing=False):
        self.dao = dao
        self.path = path
        self.verbose = verbose
        self.debug = debug
        self.hasing = hashing

    def index(self):
        """
        Index any image files found under directory tree with root self.path
        """
        self.traverse(self.path, self.parse_file)

    def traverse(self, directory, callback):
        """
        Start walking directory tree with root self.path and indexing any image files found
        """
        try:
            for name in os.listdir(directory):
                pathname = os.path.join(directory, name)
                stat = os.lstat(pathname)

                if S_ISDIR(stat[ST_MODE]):
                    self.traverse(pathname, callback)
                else:
                    callback(name, pathname, stat)
        except OSError as e:
            print 'File not found or access denied: ', directory, e

    def parse_file(self, name, path, stat):
        """
        Read image file and combine file stat and exif info into document and persist
        """
        if not imghdr.what(path):
            return

        data = {
            'exif': self.get_exif(path),
            'filename': name,
            'path': path,
            'indexed': datetime.today(),
            'atime': datetime.fromtimestamp(stat[ST_ATIME]),
            'ctime': datetime.fromtimestamp(stat[ST_CTIME]),
            'mtime': datetime.fromtimestamp(stat[ST_MTIME]),
            'size': stat[ST_SIZE]
        }

        if self.hasing:
            try:
                data['hash'] = ImageIndexer.compute_hash(path)
            except IOError as e:
                print "Can't compute hash", e, path

        if self.dao.add_image(data) and self.verbose:
            print "%s indexed." % path

    @staticmethod
    def compute_hash(path):
        """
        This needs to be fast, not secure. The chance that files causing a collision are also
        valid image files can probably be ignored.
        """
        return hashlib.md5(Image.open(path).tostring()).hexdigest()

    def get_exif(self, path):
        """
        Extract exif info from file and preprocess it
        The preprocessing is necessary because pymongo can't convert some types to mongo's json
        """
        exif = {}

        metadata = pyexiv2.ImageMetadata(path)
        try:
            metadata.read()

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

