image-indexer
=============

Trying out pymongo. The exif info of holiday snapshots is a nice source of large amounts of unstructured data.
Generate a document containing exif and file stat info of image files and persist this document. 

Usage
=====
    image_indexer.py --path=/root [-v | --verbose=true] [-u | --upsert=true] [-d | --debug=true] [-h | --hashing=true]
        -v, --verbose   if true, print to stdout what file the indexer is currently working on
        -u, --upsert    if true, update files that have already been indexed. If false, skip.
        -d, --debug     print extremely verbose debugging info to stdout
        -h, --hashing   if true, include an md5 hash in the document that is persisted

Known issues
============
- Not very useful
- Leaky abstractions

TODO
====
- Store image file in GridFS
- Generate and store thumbnails
