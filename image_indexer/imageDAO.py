#!/usr/bin/env python
import bson
import pymongo


class ImageDAO(object):
    """
    Wraps inserts and queries to the images collection
    As well as some aggregations
    """
    def __init__(self, connection_string='mongodb://localhost', database='pictures', collection='images', upsert=False):
        connection = pymongo.MongoClient(connection_string)
        self.db = connection[database]
        self.images = self.db[collection]
        self.upsert = upsert
        self.images.create_index([('path', 1)], unique=True)
        self.images.create_index([('hash', 1)], unique=False)

    def aggregate(self, query):
        """
        Return one aggregated document
        """
        return self.images.aggregate(query)

    def find_by_path(self, path):
        """
        Return one document by (unique) path
        """
        return self.images.find_one({'path': path})

    def find_by_id(self, _id):
        """
        Return one document by _id
        """
        return self.images.find_one({'_id': _id})

    def find_by_hash(self, hashcode):
        """
        Return list of image file paths with the given hash code
        """
        cursor = self.images.find({'hash': hashcode}, {'path': 1})
        ret = []
        for doc in cursor:
            ret.append(doc['path'])
        return ret

    def add_image(self, data):
        """
        Attempt to insert document called data into the images collection
        In case of a duplicate key exception do an update if the upsert argument
        has been selected
        """
        try:
            try:
                self.images.insert(data)
            except pymongo.errors.DuplicateKeyError as e:
                if self.upsert:
                    _id = data.pop('_id', None)
                    try:
                        self.images.update({'_id': _id}, data)
                    except Exception as e:
                        print data
                        raise e
                else:
                    print "File is already indexed", data['path']
                    return False
        except pymongo.errors.OperationFailure as e:
            print "Mongo error", e
            raise
        except bson.errors.InvalidDocument as e:
            print "Can't convert your datatype", e, data['path']
            raise

        return True

