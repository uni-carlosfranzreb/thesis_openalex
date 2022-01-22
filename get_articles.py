""" Retrieve the first paragraphs of the Wikipedia articles of the subjects. """



import json
import logging
import re
from time import time

from lxml import etree
import requests as req


class WikiRetriever:
  def __init__(self, subjects_file, dump_file):
    self.subjects = json.load(open(subjects_file))
    self.dump_file = dump_file
    self.articles = {}
    self.enwiki = 'https://en.wikipedia.org/wiki/[^\"]+'
  
  def get_articles(self):
    for subject, data in self.subjects.items():
      link = self.get_link(req.get(data['wikidata']).text)
      if link is None:
        logging.info(f'{subject}: no link found. Description will be used.')
        self.articles[subject] = data['description']
      self.get_paragraph(subject, link)
  
  def get_link(self, wikidata):
    """ Retrieve the English Wikipedia link from the Wikidata page. """
    tree = etree.HTML(wikidata)
    try:
      table = tree.xpath('//table[@class="wikibase-entitytermsforlanguagelistview"]')[0]
      a = table.xpath('//span[contains(@class, "wikibase-sitelinkview-link-enwiki")]//a')[0]
      return a.get('href')
    except IndexError as e:
      return None
  
  def get_paragraph(self, subject, link):
    """ Return the first paragraph of the Wikipedia page. Only paragraphs
    with more than 50 characters are considered. """
    tree = etree.HTML(req.get(link).text)
    self.articles[subject] = ''
    for p in tree.xpath(
        '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]/p'
      ):
      text = prettify(''.join(p.itertext('i','b','a')))
      self.articles[subject] += text
      logging.info(f'{subject}: paragraph added.')
      if len(self.articles[subject]) < 500:
        self.articles[subject] += ' '
      else:
        logging.info(f'{subject} has {len(self.articles[subject])} chars.')
        return
        
  def dump(self):
    json.dump(self.articles, open(self.dump_file, 'w'))
  
def prettify(text):
  """ Remove references and newlines. """
  text = text.replace('\n', '')
  text = re.sub('\[[0-9]+\]', '', text)
  text = re.sub('\[[a-z]\]', '', text)
  return re.sub('\[i+\]', '', text)  


def test():
  logging.basicConfig(
    level=logging.INFO,
    filename=f'logs/test_get_articles_{int(time())}.log'
  )
  subjects_file = 'data/openalex/test/test_subjects.json'
  dump_file = 'data/openalex/test/test_articles.json'
  retriever = WikiRetriever(subjects_file, dump_file)
  retriever.get_articles()
  retriever.dump()


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
  # test()
