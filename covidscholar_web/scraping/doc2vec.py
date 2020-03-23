import logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import os
import gensim
import pickle
import random

abstracts = pickle.load(open('completeEntriesWNER.pkl', 'rb'))
random.shuffle(abstracts)
abstracts_text = []
for i, abstract in enumerate(abstracts):
    print(abstract.keys())
    abstract['enum'] = i
    abstracts_text.append(abstract['abstract'])


def read_corpus(f, tokens_only=False):
    for i, line in enumerate(f):
        tokens = gensim.utils.simple_preprocess(line)
        yield gensim.models.doc2vec.TaggedDocument(tokens, [i])


corpus = list(read_corpus(abstracts_text))

model = gensim.models.doc2vec.Doc2Vec(vector_size=200, min_count=2, epochs=30)
model.build_vocab(corpus)

model.train(corpus, total_examples=model.corpus_count,
            epochs=model.epochs)

ranks = []
for doc_id in range(len(corpus)):
    inferred_vector = model.infer_vector(corpus[doc_id].words)
    sims = model.docvecs.most_similar(
        [inferred_vector], topn=6)
    top_5 = [sims[i] for i in range(6) if sims[i][0] != doc_id]
    abstracts[doc_id]['top_5'] = top_5
    if doc_id % 500 == 0:
        print("Title:")
        print(abstracts[doc_id]['title'])
        print("Most similar titles:")
        for i in range(5):
            print(abstracts[abstracts[doc_id]['top_5'][i][0]]['title'],
                  abstracts[doc_id]['top_5'][i][1])

pickle.dump(abstracts, open('completeEntriesWNER&Doc2Vec.pkl', 'wb'))
