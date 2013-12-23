use pictures
query = [
        {'$group': {'_id': '$hash', 'count': {'$sum': 1}}},
        {'$match': {'count': {'$gt': 1}}},
        {'$project': {'hash': '$_id', '_id': 0, 'count': 1}},
        {'$sort': {'count': 1}}
    ]
db.images.aggregate(query)
