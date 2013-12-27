#!/usr/bin/env python

"""
Generate a document containing exif and file stat info of image files and persist this document

Usage:
    image_indexer.py --path=/root [-v | --verbose=true] [-u | --upsert=true] [-d | --debug=true] [-h | --hashing=true]
        -v, --verbose   if true, print to stdout what file the indexer is currently working on
        -u, --upsert    if true, update files that have already been indexed. If false, skip.
        -d, --debug     print extremely verbose debugging info to stdout
        -h, --hashing   if true, include an md5 hash in the document that is persisted
"""

import sys
import getopt
from image_indexer.fileIndexer import FileIndexer
from settings import collection, connect_string, database

from image_indexer.imageIndexer import ImageIndexer
from image_indexer.imageDAO import ImageDAO


def parse_bool(opt, name):
    return opt.get('--' + name, str(('-' + name[0]) in options.keys())).lower() == 'true'


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'vudh', ['path=', 'upsert=', 'verbose=', 'debug=', 'hashing='])
    options = dict(opts)

    path = options['--path'] if '--path' in options else '.'
    verbose = parse_bool(options, 'verbose')
    upsert = parse_bool(options, 'upsert')
    debug = parse_bool(options, 'debug')
    hashing = parse_bool(options, 'hashing')

    if debug:
        print "path=%s(%s), verbose=%s(%s), upsert=%s(%s), debug=%s(%s), hashing=%s(%s)" % \
              (path, type(path), verbose, type(verbose), upsert, type(upsert), debug, type(debug), hashing,
               type(hashing))

    dao = ImageDAO(connection_string=connect_string, database=database, collection=collection, upsert=upsert)
    indexer = ImageIndexer(path, dao, verbose=verbose, debug=debug, hashing=hashing)
    try:
        indexer.index()
    except KeyboardInterrupt as e:
        print "Aborted. ", e

