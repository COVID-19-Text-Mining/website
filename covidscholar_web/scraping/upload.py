import pymongo
import pickle
import time
import copy
from datetime import datetime
import os

client = pymongo.MongoClient('mongodb+srv://%s:%s@matstract-kve41.mongodb.net/test:27017' %
                             (os.getenv('ATLAS_USER'), os.getenv('ATLAS_USER_PASSWORD')), authSource='admin')
db = client['matstract_db']

abstracts = pickle.load(open('completeEntriesWNER&Doc2Vec.pkl', 'rb'))

entity_types = ["MAT",
                "PRO",
                "APL",
                "SMT",
                "CMT",
                "DSC",
                "SPL"]

entities_all = entity_types + [e + "_summary" for e in entity_types]


for i, abstract in enumerate(abstracts):
    if i % 1000 == 0:
        print(i)
    abstract['top_4'] = [int(i)
                         for i, _ in abstract['top_5'][:4]]
    del(abstract['top_5'])
    abstract['type'] = 'talk'
    abstract['day'] = abstract['date'].split(' ')[0].lower()
    combtime = "{} {}".format(
        abstract['time'], abstract['date'].replace('AM', '').replace('PM', ''))
    abstract['datetime'] = datetime.strptime(
        combtime, "%I:%M %p %A , %B %d, %Y")
    for e in entities_all:
        abstract[e] = [i for i in abstract[e] if not isinstance(i, list)]
    abstract['entities'] = list(
        set([i for e in entities_all for i in abstract[e]]))
    abstract['link'] = "https://www.mrs.org/fall2019/symposium-sessions/symposium-sessions-detail?code={}".format(
        abstract['sessionCode'])
    try:
        abstract['time'] = time.strptime(abstract['time'], "%I:%M %p")
    except TypeError:
        print(abstract['time'])

abstractsNew = []

for i, abstract in enumerate(abstracts):
    if i % 1000 == 0:
        print(i)
    abstractNew = copy.deepcopy(abstract)
    abstractNew['similar_abstracts'] = [
        {k: v for k, v in a.items() if k not in ['top_4', 'top_5']} for a in abstracts if a['enum'] in abstractNew['top_4']]
    abstractsNew.append(abstractNew)

import pprint
pprint.PrettyPrinter().pprint(abstractNew)
db['MRS_abstracts'].drop()
db['MRS_abstracts'].insert_many(abstractsNew, ordered=False)

print(db.MRS_abstracts.index_information())
db.MRS_abstracts.create_index(
    [('title', pymongo.TEXT), ('authors', pymongo.TEXT), ('abstract', pymongo.TEXT), ('entities', pymongo.TEXT)], weights={'entities': 4, 'authors': 4, 'title': 2, 'abstract': 1}, default_language='english')
db.MRS_abstracts.create_index(
    [('enum', pymongo.ASCENDING)], unique=True)
db.MRS_abstracts.create_index(
    [('date', pymongo.ASCENDING)], unique=False)
db.MRS_abstracts.create_index(
    [('day', pymongo.ASCENDING)], unique=False)
for entity_type in entity_types:
    db.MRS_abstracts.create_index([('{}_summary'.format(
        entity_type), pymongo.ASCENDING)], name='{}_summary'.format(entity_type), default_language='english')
    db.MRS_abstracts.create_index([('{}'.format(
        entity_type), pymongo.ASCENDING)], name='{}'.format(entity_type), default_language='english')

print(db.MRS_abstracts.index_information())
print(db['MRS_abstracts'].count())
print(db['MRS_abstracts'].find().__next__().keys())
