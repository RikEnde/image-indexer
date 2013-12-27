from abc import abstractmethod
import os
import hashlib
from datetime import datetime
from stat import *

from PIL import Image


class FileIndexer(object):
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
        Index any files found under directory tree with root self.path
        """
        self.traverse(self.path, self.process_file)

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

    def get_file_type(self, path):
        """
        Try to derive the file type from the filename extension
        This should be a last resort
        """
        chunks = path.split('.')
        if len(chunks) > 1:
            return chunks[-1]
        else:
            return None

    def make_data(self, name, path, stat):
        """
        Fill the generic part of the metadata document based on file stat and name
        If the file type isn't recognized, return None. This gives subclasses a way to skip
        indexing the file
        """
        file_type = self.get_file_type(path)
        if not file_type:
            return None

        data = {
            'filename': name,
            'path': path,
            'indexed': datetime.today(),
            'atime': datetime.fromtimestamp(stat[ST_ATIME]),
            'ctime': datetime.fromtimestamp(stat[ST_CTIME]),
            'mtime': datetime.fromtimestamp(stat[ST_MTIME]),
            'size': stat[ST_SIZE],
            'type': file_type
        }

        if self.hasing:
            try:
                data['hash'] = self.compute_hash(path)
            except IOError as e:
                print "Can't compute hash", e, path
        return data

    def process_file(self, name, path, stat):
        """
        Read image file and combine file stat and exif info into document and persist
        Do not save the file if metadata document is None
        """
        data = self.make_data(name, path, stat)
        if data and self.dao.add_data(data) and self.verbose:
            print "%s indexed." % path

    def compute_hash(self, path):
        """
        This needs to be fast, not secure. The chance that files causing a collision are also
        valid image files can probably be ignored.
        """
        return hashlib.md5(self.get_bytes(path)).hexdigest()

    @abstractmethod
    def get_bytes(self, path):
        """
        A naive eay to compute the hash of a file. Don't use this on large files. Override this
        with something more appropriate for each type of indexer
        """
        with open(path, 'rb') as f:
            return f.read()

