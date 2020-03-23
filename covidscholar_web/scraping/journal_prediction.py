from matscholar import Rester
import bson
import tqdm
import os
import pymongo

client = pymongo.MongoClient('mongodb+srv://%s:%s@matstract-kve41.mongodb.net/test:27017' %
                             (os.getenv('ATLAS_USER_RW'), os.getenv('ATLAS_USER_PASSWORD_RW')), authSource='admin')
db = client['matstract_db']
c = db.MRS_abstracts

LIMIT = 0
rester = Rester()

print(c.count_documents({}, limit=5))

for d in tqdm.tqdm(c.find({}, limit=LIMIT)):
    id = bson.ObjectId(d["_id"])
    suggestions = rester.get_journal_suggestion(abstract=d["abstract"])
    # print(d)
    c.update({"_id": id}, {"$set": {"journal_suggestions": suggestions}})

    # print(d["abstract"])
    # print(suggestions)
    # print("-----------\n\n\n\n")


