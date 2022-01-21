""" Check how many of our picked subjects are present in OpenAlex. """


import requests as req
import json


def check(subjects_file, dump_file):
  """ Retrieve the concept and the number of works it tags for each one of the
  picked subjects, the URL to retrieve those works, its description and the 
  Wikidata URL. """
  subjects = json.load(open(subjects_file))
  url = 'https://api.openalex.org/concepts?filter=display_name.search:'
  openalex = {}
  for subject, data in subjects.items():
    res = req.get(url + data['name'])
    if res.status_code == 200:
      content = res.json()
      for result in content['results']:
        if result['display_name'] == data['name']:
          openalex[data['name']] = {
            'id': result['id'],
            'makg_id': subject,
            'wikidata': result['wikidata'],
            'description': result['description'],
            'works_count': result['works_count'],
            'works_api_url': result['works_api_url']
          }
      json.dump(openalex, open(dump_file, 'w'))


def check_missing(missing_file, makg_file, dump_file):
  """ Pick the most relevant subject for each missing subject. The names
  will not be identical. """
  missing = json.load(open(missing_file))
  makg = json.load(open(makg_file))
  url = 'https://api.openalex.org/concepts?filter=display_name.search:'
  openalex = {}
  for subject in missing:
    res = req.get(url + subject)
    if res.status_code == 200:
      content = res.json()
      if len(content['results']) > 0:
        result = content['results'][0]
        openalex[result['display_name']] = {
          'id': result['id'],
          'makg_id': get_makg_id(makg, subject),
          'makg_name': subject,
          'wikidata': result['wikidata'],
          'description': result['description'],
          'works_count': result['works_count'],
          'works_api_url': result['works_api_url']
        }
        json.dump(openalex, open(dump_file, 'w'))


def get_makg_id(makg, name):
  """ Return the ID of the MAKG subject with the given name. """
  for subject, data in makg.items():
    if data['name'] == name:
      return subject


if __name__ == '__main__':
  makg_subjects = 'data/subjects/subjects.json'
  subjects_file = 'data/openalex/subjects_missing.json'
  dump_file = 'data/openalex/similar_subjects.json'
  check_missing(subjects_file, makg_subjects, dump_file)
