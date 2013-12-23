#!/usr/bin/env python

from image_indexer.imageDAO import ImageDAO
from settings import *


def find_duplicates(dao):
    """
    Group by hash. The result contains image file hashes that occur more than once
    """
    document = dao.aggregate([
        {'$group': {'_id': '$hash', 'count': {'$sum': 1}}},
        {'$match': {'count': {'$gt': 1}}},
        {'$project': {'hash': '$_id', '_id': 0, 'count': 1}},
        {'$sort': {'count': 1}}
    ])
    for i, doc in enumerate(document['result']):
        print i, doc['hash'], doc['count'], dao.find_by_hash(doc['hash'])

def count_cameras(dao):
    """
    Group by Exif.Image.Model and count
    """
    #> db.images.aggregate({$group:{_id:"$exif.ExifImageModel", count:{$sum : 1}}})
    document = dao.aggregate([
        {'$group': {'_id': '$exif.ExifImageModel', 'count': {'$sum': 1}}}, 
        {'$project': {'camera': '$_id', 'count': True, '_id': False}}, 
        {'$sort': {'count': 1}}
    ])
    for doc in document['result']:
        print doc['count'], doc['camera']


if __name__ == '__main__':
    image_dao = ImageDAO(connection_string=connect_string, database=database, collection=collection)
    find_duplicates(image_dao)
    count_cameras(image_dao)
