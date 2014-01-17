use pictures
query = [
    {'$group': {'_id': '$exif.ExifImageModel', 'count': {'$sum': 1}}},
    {'$project': {'camera': '$_id', 'count': true, '_id': false}},
    {'$sort': {'count': 1}}
]
db.images.aggregate(query)
