use pictures
query = [
	{'$group': {'_id': '$magic', 'count': {'$sum': 1}, 'sum': {'$sum': '$size'}}},
	{'$project': {'magic': '$_id', 'count': true, 'sum': true, '_id': false}},
	{'$sort': {'count': 1}}
]
db.images.aggregate(query)
