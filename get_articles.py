""" Retrieve the first paragraphs of the Wikipedia articles of the subjects. """



import json
import logging
import re
from time import time

from bs4 import BeautifulSoup
import requests as req


class WikiRetriever:
  def __init__(self, subjects_file, dump_file):
    self.subjects = json.load(open(subjects_file))
    self.dump_file = dump_file
    self.articles = {}
    self.enwiki = 'https://en.wikipedia.org/wiki/[^\"]+'
  
  def get_articles(self):
    for subject, data in self.subjects.items():
      wikidata = req.get(data['wikidata']).text
      links = re.findall(self.enwiki, wikidata)
      if len(links) == 0:
        logging.info(f'{subject} has no Wikipedia link')
      elif len(links) > 2:
        logging.info(f'{subject} has multiple Wikipedia links')
      else:
        self.get_paragraph(subject, links[0])
  
  def get_paragraph(self, subject, link):
    """ Return the first paragraph of the Wikipedia page. Only paragraphs
    with more than 50 characters are considered. """
    try:
      soup = BeautifulSoup(req.get(link).text, features="lxml")
      for paragraph in soup.find_all('p'):
        if len(paragraph.text) > 50:
          text = paragraph.text.replace('\n', '')
          text = re.sub('\[[0-9]+\]', '', text)
          text = re.sub('\[[a-z]\]', '', text)
          text = re.sub('\[i+\]', '', text)
          self.articles[subject] = text
          logging.info(f'Article of {subject} added.')
          return
    except Exception as e:
      logging.error(
        f'An exception occurred while getting the paragraph of {subject}: {e}'
      )
  
  def dump(self):
    json.dump(self.articles, open(self.dump_file, 'w'))


if __name__ == '__main__':
  logging.basicConfig(
    level=logging.INFO,
    filename=f'logs/get_articles_{int(time())}.log'
  )
  subjects_file = 'data/openalex/subjects.json'
  dump_file = 'data/openalex/articles.json'
  retriever = WikiRetriever(subjects_file, dump_file)
  retriever.get_articles()
  retriever.dump()