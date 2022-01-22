""" 7 of the retrieved subjects were ambiguous. Instead of running everything
again, we:
1. run get_subjects.py again with the new rule (no ambiguous subjects),
2. separate new subjects from old ones and keep articles and their processed
versions safe,
3. extract articles and process them for new subjects,
4. merge all subjects.
Steps 2, 3 and 4 happen here. """


import json
import logging

from get_articles import WikiRetriever


def separate_articles():
  """ Separate articles which already have a description from those that
  don't. """
  subjects = json.load(open('data/openalex/subjects.json'))
  articles = json.load(open('data/openalex/articles.json'))
  need_article = {}
  for subject, data in subjects.items():
    if subject not in articles:
      need_article[subject] = data
  json.dump(need_article, open('data/openalex/new_subjects.json', 'w'))


def get_new_articles():
  """ Retrieve articles for new subjects. """
  logging.basicConfig(
    level=logging.INFO,
    filename=f'logs/get_new_articles.log'
  )
  subjects_file = 'data/openalex/new_subjects.json'
  dump_file = 'data/openalex/new_articles.json'
  retriever = WikiRetriever(subjects_file, dump_file)
  retriever.get_articles()
  retriever.dump()


def merge_files():
  """ Merge files with old and new articles, raw and processed. """
  subjects = json.load(open('data/openalex/subjects.json'))
  articles = json.load(open('data/openalex/articles.json'))
  new_articles = json.load(open('data/openalex/new_articles.json'))
  processed = json.load(open('data/openalex/articles_processed.json'))
  new_processed = json.load(open('data/openalex/new_articles_processed.json'))
  all_articles = merge(subjects, articles, new_articles)
  all_processed = merge(subjects, processed, new_processed)
  json.dump(all_articles, open('data/openalex/articles.json', 'w'))
  json.dump(all_processed, open('data/openalex/articles_processed.json', 'w'))


def merge(subjects, old, new):
  all_articles = {}
  for subject in subjects:
    if subject in old:
      all_articles[subject] = old[subject]
    elif subject in new:
      all_articles[subject] = new[subject]
    else:
      raise ValueError(f'Subject {subject} not found!')
  return all_articles
    

if __name__ == '__main__':
  # separate_articles()
  # get_new_articles()
  # process new articles in the subject_indexing repo.
  merge_files()