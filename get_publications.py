""" Retrieve documents from OpenAlex. We want 50 documents per subject in
our set, so all subjects have data. Process the titles and abstracts before
storing them. Keep also the document type and assigned subjects. Use the link
to the works found in subjects.json (works_api_url). Save 2000 documents per
file. """


import requests as req
import json
import logging
from collections import Counter

from flair.data import Sentence
from flair.tokenization import SpacyTokenizer
from flair.models import SequenceTagger

from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams
from nltk.corpus import stopwords, wordnet


class DocRetriever:
  def __init__(self, vocab_file):
    self.vocab = json.load(open(vocab_file))
    self.cnt = 0
    self.tokenizer = SpacyTokenizer('en_core_web_sm')
    self.lemmatizer = WordNetLemmatizer()
    self.tagger = SequenceTagger.load('upos-fast')
    self.tag_dict = {
      'ADJ': wordnet.ADJ,
      'NOUN': wordnet.NOUN,
      'VERB': wordnet.VERB,
      'ADV': wordnet.ADV
    }
  
  def get_docs(self, url, n=50):
    """ Given the URL leading to the documents of a subject, yield documents
    that are either publications. n is the number of docs that will be yielded. """
    yielded, page = 0, 1
    url += ',type:journal-article&page='
    while yielded < n:
      for doc in req.get(f'{url}{page}').json()['results']:
        abstract = doc['abstract_inverted_index']
        if abstract is not None:
          yield {
            'data': self.process_texts(doc['display_name'], abstract),
            'subjects': {s['id']: s['score'] for s in doc['concepts']},
            'type': doc['type']
          }
      page += 1
      yielded += 1

  def process_texts(self, title, abstract_idx):
    """ Lower-case the string, lemmatize the words and remove those that don't
    appear in the vocab. Return the list of remaining words ordered by freq.
    and by order in the text when tied, without duplicates. Merge title and
    abstract after building the abstract from the index. """
    abstract = self.build_abstract(abstract_idx)
    if abstract[-2:] != '. ':
      abstract += '. '
    sentence = Sentence(abstract + title)
    self.tagger.predict(sentence)
    lemmas = []
    for token in sentence:
      if token.labels[0].value in self.tag_dict:
        lemmas.append(self.lemmatizer.lemmatize(
          token.text.lower(), self.tag_dict[token.labels[0].value])
        )
      else:
        lemmas.append(token.text.lower())
    lemmas_cnt = Counter(lemmas)
    vocab_lemmas = Counter()
    for word in lemmas_cnt:
      if word in self.vocab:
        vocab_lemmas[word] = lemmas_cnt[word]
    return [tup[0] for tup in vocab_lemmas.most_common()]
  
  def build_abstract(self, abstract_idx):
    """ Given an abstract as an inverted index, return it as normal text. """
    text = ''
    n_words = sum([len(v) for v in abstract_idx.values()])
    for i in range(n_words):
      for word in abstract_idx:
        if i in abstract_idx[word]:
          text += word + ' '
    return text


if __name__ == '__main__':
  works_api_url = 'https://api.openalex.org/works?filter=concept.id:C518881349'
  vocab_file = 'data/vocab/vocab.json'
  retriever = DocRetriever(vocab_file)
  for doc in retriever.get_docs(works_api_url):
    print(doc)
    break
  # ! Why is "-" in the vocab?