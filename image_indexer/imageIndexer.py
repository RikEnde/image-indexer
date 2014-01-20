#!/usr/bin/env python
from abc import abstractmethod

import string
import imghdr
from PIL import Image, ExifTags

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
            exif = self.get_exif(path)
            if False and exif:
                data['exif'] = exif
            return data
        else:
            return None

    def get_exif(self, path):
        """
        Extract exif info from file and preprocess it
        The preprocessing is necessary because pymongo can't convert some types to mongo's json
        """
        def get_gps(gps_tag):
            gps = {}
            for key in gps_tag.keys():
                decoded = ExifTags.GPSTAGS.get(key)
                gps[decoded] = gps_tag[key]
            return gps    

        def sanitize(key, value):
            if type(value) == str:
                try:
                    value.decode('utf-8')
                except UnicodeDecodeError:
                    return filter(lambda x: x in string.printable, value)
            else:    
                return value

        try:
            img = Image.open(path)
            if 'exif' in img.info.keys():
                return {
                    ExifTags.TAGS[k]: get_gps(v) if ExifTags.TAGS[k] == 'GPSInfo' else sanitize(k,v) 
                    for k, v in img._getexif().items() if k in ExifTags.TAGS
                }
        except IOError as e:
            if self.debug:
                print "Error opening file %s as image" % path

        return None

    @abstractmethod
    def get_bytes(self, path):
        """
        First read the entire image as a file
        """
        return Image.open(path).tostring()

