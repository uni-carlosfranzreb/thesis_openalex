""" Retrieve documents from OpenAlex. We want 50 documents per subject in
our set, so all subjects have data. Process the titles and abstracts before
storing them. Keep also the document type and assigned subjects. Use the link
to the works found in subjects.json (works_api_url). Save 2000 documents per
file. """


import requests as req
import json
from collections import Counter
from os import listdir
import logging
from time import time

from flair.data import Sentence
from flair.tokenization import SpacyTokenizer
from flair.models import SequenceTagger

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet


class DocRetriever:
  def __init__(self, vocab_file, subjects_file):
    self.vocab = json.load(open(vocab_file))
    self.subjects = json.load(open(subjects_file))
    self.tokenizer = SpacyTokenizer('en_core_web_sm')
    self.lemmatizer = WordNetLemmatizer()
    self.tagger = SequenceTagger.load('upos-fast')
    self.tag_dict = {
      'ADJ': wordnet.ADJ,
      'NOUN': wordnet.NOUN,
      'VERB': wordnet.VERB,
      'ADV': wordnet.ADV
    }
    self.retrieved = []  # IDs of docs that were retrieved
  
  def get_docs(self, url, n=50, process=True):
    """ Given the URL leading to the documents of a subject, yield documents
    that are either publications. n is the number of docs that will be yielded.
    If process=True, the texts will be tokenized, lemmatized and mapped against
    a vocabulary before being yielded. """
    yielded, page = 0, 1
    url += ',type:journal-article&page='
    try:
      while yielded < n:
        res = req.get(f'{url}{page}').json()
        logging.info(f'Fetched page {page}')
        for doc in res['results']:
          if doc['id'] in self.retrieved:
            continue
          abstract_idx = doc['abstract_inverted_index']
          if abstract_idx is not None:
            abstract = self.build_abstract(abstract_idx)
            text = self.append_texts(doc['display_name'], abstract)
            data = self.process_text(text) if process is True else text
            yield {
              'data': data,
              'subjects': {s['id']: s['score'] for s in doc['concepts']
                  if s['id'] in self.subjects}
            }
            yielded += 1
            self.retrieved.append(doc['id'])
            if yielded == n:
              logging.info(f'{yielded} docs were found.')
              return
        page += 1
    except Exception as e:
      logging.error(f'An error occurred: {e}')
      logging.info(f'{yielded} docs were found.')
      return

  def process_text(self, text):
    """ Lower-case the string, lemmatize the words and remove those that don't
    appear in the vocab. Return the list of remaining words ordered by freq.
    and by order in the text when tied, without duplicates. Merge title and
    abstract after building the abstract from the index. """
    sentence = Sentence(text)
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
  
  def append_texts(self, title, abstract):
    """ Append the abstract to the text. If the title ends in a score,
    just add them. If not, add the score first. """
    if title[-1] == '.':
      return title + ' ' + abstract
    elif title[-2:] == '. ':
      return title + abstract
    else:
      return title + '. ' + abstract
  

def main(vocab_file, subjects_file, n_docs=100, n_file=3000):
  """ Retrieve 'n_docs' docs for each subject and dump them in the folder
  'data/openalex/docs', with 'n_file' docs per file. n_docs should be a
  factor of n_file. We only check n_file after each subject is done. It can
  occur that a file has more than n_file docs, but never less. """
  retriever = DocRetriever(vocab_file, subjects_file)
  subjects = json.load(open(subjects_file))
  done = get_done_subjects()
  logging.info(f'{len(done)} subjects have been retrieved already.')
  batch = {}
  cnt, file_nr = 0, 1
  for subject, data in subjects.items():
    if subject in done:
      continue
    logging.info(f'Retrieving docs for {subject}')
    batch[subject] = []
    for doc in retriever.get_docs(data['works_api_url'], n_docs):
      batch[subject].append(doc)
    cnt += len(batch[subject])
    if cnt >= n_file:
      json.dump(batch, open(f'data/openalex/docs/{file_nr}.json', 'w'))
      file_nr += 1
      cnt = 0
      batch = {}
  if len(batch) > 0:
    json.dump(batch, open(f'data/openalex/docs/{file_nr}.json', 'w'))


def get_done_subjects():
  """ Return the subjects for which the documents have already been
  retrieved. They will be removed from the subject dict. """
  done = []
  for file in listdir('data/openalex/docs'):
    done += [s for s in json.load(open(f'data/openalex/docs/{file}'))]
  return done


if __name__ == '__main__':
  logging.basicConfig(
    level=logging.INFO,
    filename=f'logs/get_publications_{int(time())}.log'
  )
  vocab_file = 'data/vocab/vocab.json'
  subjects_file = 'data/openalex/subjects.json'
  main(vocab_file, subjects_file)
  retriever = DocRetriever(vocab_file)
  subjects = json.load(open(subjects_file))