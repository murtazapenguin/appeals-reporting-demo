from pymongo import MongoClient
import os

client = MongoClient(os.getenv('MONGODB_URL'))
db = client[os.getenv('DATABASE_NAME', 'claim_appeals')]

pipeline = [
    {"$group": {"_id": "$claim_number", "ids": {"$push": "$_id"}, "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}}
]

total = 0
for d in db.denials.aggregate(pipeline):
    ids_to_delete = d['ids'][1:]
    result = db.denials.delete_many({'_id': {'$in': ids_to_delete}})
    print(f'Deleted {result.deleted_count} duplicates of {d["_id"]}')
    total += result.deleted_count

print(f'Total deleted: {total}')
print(f'Remaining: {db.denials.count_documents({})}')
