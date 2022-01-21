""" Retrieve subjects from OpenAlex. All fields, and then 200 of each field,
starting by the uppermost level and picking by popularity when needed. """


import logging
import requests as req
import json
from time import time


class SubjectRetriever:
  def __init__(self):
    """ n is the number of subjects per field. """
    self.url = url = 'https://api.openalex.org/concepts'
    self.subjects = {}  # retrieved subjects
    self.counts = {}  # count of subjects per field
  
  def retrieve(self, n=200):
    """ Retrieve subjects. n is the number of subjects per field we want to
    retrieve."""
    self.get_fields()
    self.get_level(1)
    self.dump_subjects('data/openalex/subjects.json')
    for works_limit in [25000, 10000, 5000, 1000, 50]:
      logging.info(f'Subjects should at least have {works_limit} works.')
      for level in range(2, 6):
        for ancestor in self.counts:
          if self.counts[ancestor] < n:
            self.get_subjects(level, ancestor, n, works_limit)
            self.dump_subjects('data/openalex/subjects.json')

  def get_fields(self):
    res = req.get(self.url + '?filter=level:0')
    for subject in res.json()['results']:
      self.add_subject(subject)
      self.counts[subject['id']] = 0
    logging.info('Fields retrieved')
  
  def get_level(self, level):
    """ Retrieve all subjects from a given level.
    ! Pagination is not implemented yet! """
    res = req.get(self.url + f'?filter=level:{level}')
    for subject in res.json()['results']:
      self.add_subject(subject)
      self.increment_count(subject['ancestors'])
    logging.info(f'Subjects of level {level} retrieved')
  
  def get_subjects(self, level, ancestor_id, n, works_limit):
    """ Retrieve subjects that derive from the given field. n is the number
    of subjects per field we want to retrieve. works_limit is the min. number
    of works a subject should be tagged in to be considered. """
    logging.info(f'Getting subjects of {ancestor_id} in lv {level}')
    url = self.url + f'?filter=level:{level},ancestors.id:{ancestor_id}'
    page=1
    while self.counts[ancestor_id] < n:
      logging.info(f'Retrieving page {page}')
      res = req.get(url + f'&page={page}')
      if len(res.json()['results']) == 0:
        logging.info(f'No more subjects under {ancestor_id} on lv {level}')
        return
      for subject in res.json()['results']:
        if subject['works_count'] > works_limit:
          self.add_subject(subject)
          self.counts[ancestor_id] += 1
          logging.info(f'{subject["id"]} added under {ancestor_id}')
          if self.counts[ancestor_id] == n:
            logging.info(f'All {n} subjects retrieved for {ancestor_id}')
            return
      page += 1
  
  def add_subject(self, subject):
    """ Add the given subject to the list of subjects. """
    self.subjects[subject['id']] = {
      'name': subject['display_name'],
      'description': subject['description'],
      'wikidata': subject['wikidata'],
      'works_count': subject['works_count'],
      'works_api_url': subject['works_api_url'],
      'level': subject['level'],
      'ancestors': subject['ancestors']
    }
  
  def increment_count(self, ancestors):
    for ancestor in ancestors:
      if ancestor['id'] in self.counts.keys():
        self.counts[ancestor['id']] += 1
        break
  
  def dump_subjects(self, dump_file):
    json.dump(self.subjects, open(dump_file, 'w'))


if __name__ == '__main__':
  logging.basicConfig(
    level=logging.INFO,
    filename=f'logs/get_subjects_{int(time())}.log'
  )
  retriever = SubjectRetriever()
  retriever.retrieve()
  retriever.dump_subjects('data/openalex/subjects.json')
  # ! sort:desc ist not a valid parameter