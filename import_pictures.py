#!/usr/bin/env python

"""
Generate a document containing exif and file stat info of image files and persist this document

Usage:
    media_indexer.py --path=/root [-v | --verbose=true] [-u | --upsert=true] [-d | --debug=true] [-h | --hashing=true]
        -v, --verbose   if true, print to stdout what file the indexer is currently working on
        -u, --upsert    if true, update files that have already been indexed. If false, skip.
        -d, --debug     print extremely verbose debugging info to stdout
        -h, --hashing   if true, include an md5 hash in the document that is persisted
"""

import sys

from options import get_options
from settings import collection, connect_string, database

from image_indexer.imageIndexer import ImageIndexer
from image_indexer.imageDAO import ImageDAO


if __name__ == '__main__':
    opt = get_options(sys.argv[1:])

    if opt.debug:
        print "path=%s(%s), verbose=%s(%s), upsert=%s(%s), debug=%s(%s), hashing=%s(%s)" % \
              (opt.path, type(opt.path), opt.verbose, type(opt.verbose),
               opt.upsert, type(opt.upsert), opt.debug, type(opt.debug), opt.hashing,
               type(opt.hashing))

    dao = ImageDAO(connection_string=connect_string, database=database, collection=collection, upsert=opt.upsert)
    indexer = ImageIndexer(opt.path, dao, verbose=opt.verbose, debug=opt.debug, hashing=opt.hashing)
    try:
        indexer.index()
    except KeyboardInterrupt as e:
        print "Aborted. ", e

