use pictures
query = [
    {'$group': {'_id': '$type', 'count': {'$sum': 1}, 'sum': {'$sum': '$size'}}},
    {'$project': {'file_type': '$_id', 'count': true, 'sum': true, '_id': false}},
    {'$sort': {'count': 1}}
]
db.images.aggregate(query)
