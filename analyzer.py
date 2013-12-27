#!/usr/bin/env python

from image_indexer.imageDAO import ImageDAO
from settings import *


class Analyzer(object):
    """
    Container for several aggregation queries on the image file exif collection
    """

    def __init__(self, dao):
        self.dao = dao

    def find_duplicates(self):
        """
        Group by hash. The result contains image file hashes that occur more than once
        """
        document = self.dao.aggregate([
            {'$group': {'_id': '$hash', 'count': {'$sum': 1}}},
            {'$match': {'count': {'$gt': 1}}},
            {'$project': {'hash': '$_id', '_id': 0, 'count': 1}},
            {'$sort': {'count': 1}}
        ])
        for i, doc in enumerate(document['result']):
            print "%d %s %s" % (i, doc['count'], ', '.join(dao.find_by_hash(doc['hash'])))

    def count_cameras(self):
        """
        Group by Exif.Image.Model and count
        """
        document = self.dao.aggregate([
            {'$group': {'_id': '$exif.ExifImageModel', 'count': {'$sum': 1}}},
            {'$project': {'camera': '$_id', 'count': True, '_id': False}},
            {'$sort': {'count': 1}}
        ])
        for doc in document['result']:
            print "%-25s: %s pictures" % (doc['camera'], doc['count'])

    def count_file_extension(self):
        """
        Group by file extension
        """
        document = self.dao.aggregate([
            {'$group': {'_id': '$type', 'count': {'$sum': 1}, 'sum': {'$sum': '$size'}}},
            {'$project': {'file_type': '$_id', 'count': True, 'sum': True, '_id': False}},
            {'$sort': {'count': 1}}
        ])
        for doc in document['result']:
            print "%-4s: %7s files, using: %11s bytes" % (doc['file_type'], doc['count'], doc['sum'])

    def count_file_magic(self):
        """
        Group by lib magic identification
        """
        document = self.dao.aggregate([
            {'$group': {'_id': '$magic', 'count': {'$sum': 1}, 'sum': {'$sum': '$size'}}},
            {'$project': {'magic': '$_id', 'count': True, 'sum': True, '_id': False}},
            {'$sort': {'count': 1}}
        ])
        for doc in document['result']:
            print "%7s files, using %11s bytes of type: %s" % (doc['count'], doc['sum'], doc['magic'])


if __name__ == '__main__':
    dao = ImageDAO(connection_string=connect_string, database=database, collection=collection)
    analyzer = Analyzer(dao)

    print "\nFinding files with identical copies"
    analyzer.find_duplicates()

    print "\nCounting the number of pictures per camera model"
    analyzer.count_cameras()

    print "\nCounting the number of pictures and approximate disk usage per file type"
    analyzer.count_file_extension()

    print "\nCounting the number of pictures and approximate disk usage per libmagic identification"
    analyzer.count_file_magic()

