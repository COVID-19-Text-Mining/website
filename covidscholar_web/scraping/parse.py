from bs4 import BeautifulSoup
import requests
import json
import re
import pickle
from matscholar_core.nlp import ner
from collections import defaultdict

timeRE = re.compile('[0-9]{1,2}:[0-9]{1,2} [A,P]M')
sessionRE = re.compile('[A-Z]{2}[0-9]{1,2}\.[0-9]{1,2}')
dowlist = ["Monday", "Tuesday", "Wednesday",
           "Thursday", "Friday", "Saturday", "Sunday"]
dateRE = re.compile(
    '(?:%s) [A,P]M, December [0-9]{2}, 2019' % ('|'.join(dowlist)))
sessionDict = dict()
with open('sessionStrings.xt', 'r') as f:
    for l in f:
        relString = re.split(timeRE, l.strip())[0]
        if len(relString) > 1:

            for sessionCode in sessionRE.findall(relString):
                try:
                    title = relString.split('Session Chairs')[0][9:]
                    relString = relString.split('Session Chairs')[1]

                    date = dateRE.findall(relString)[0]
                    room = relString.split('2019')[1]
                    sessionDict[sessionCode] = {
                        "title": title, 'date': date, 'room': room}

                except:
                    pass

abstracts = pickle.load(open('abstractdict.pkl', 'rb'))
missing = set()
for abstract in abstracts:
    session = abstract['session'][:7]
    try:
        sessEnt = sessionDict[session]
    except:
        thisSessionNum = int(session[-2:])
        for i in reversed(["%02d" % i for i in range(thisSessionNum)]):
            try:
                sessionDict[session] = sessionDict[session[:-2] + i]
                sessEnt = sessionDict[session]
                break
            except:
                missing.add(session)
    abstract['sessionName'] = sessEnt['title']
    abstract['date'] = sessEnt['date']
    abstract['room'] = sessEnt['room']
pickle.dump(abstracts, open('completeEntries.pkl', 'wb'))
ner_classifier = ner.NERClassifier()


def tag_and_tidy(doc):
    """

    Args:
        doc (dict): A matscholar entry.

    Returns:
        (dict): A dictionary of entities


    """

    entity_types = ["MAT",
                    "PRO",
                    "APL",
                    "SMT",
                    "CMT",
                    "DSC",
                    "SPL"]

    abstract = doc["abstract"]
    tagged = ner_classifier.tag_doc(abstract)
    normalized = ner_classifier.normalize_entities(
        abstract, tagged)
    entity = defaultdict(list)

    for c in tagged[0]:
        # Tagged contains tuples of word, tag
        # O is default tag, i.e. not an entity
        if c[1] != 'O':
            # Last three characters of the tag are the entity type
            entity_type = c[1][-3:]
            entity[entity_type] += [c[0]]
    # Now normalized too
    # Note that normalized and unnormalized tags may have a different number of tokens - tokens can be combined by normalized
    # So we can't do these both at once :'(
    for c in normalized[0]:
        if c[1] != 'O':
            entity_type = c[1][-3:]
            entity["{}_summary".format(entity_type)] += [c[0]]

    # Make sure to add empty list fields
    for entity_type in entity_types:
        if len(entity[entity_type]) == 0:
            entity[entity_type] = []
        # Sometimes there are MATs but they get normalized to nothing
        if len(entity["{}_summary".format(entity_type)]) == 0:
            entity["{}_summary".format(entity_type)] = []

    return entity


tagged_stracts = []
for i, abstract in enumerate(abstracts):
    if i % 100 == 0:
        print(i)
    try:
        tagged_stracts.append({**abstract, **tag_and_tidy(abstract)})
    except:
        print(abstract)

pickle.dump(tagged_stracts, open('completeEntriesWNER.pkl', 'wb'))
