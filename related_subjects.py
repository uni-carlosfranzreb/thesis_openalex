""" Extract relationships between the picked subjects. """


import json
import requests as req
from time import sleep


def get_relationships(subjects_file, dump_file):
  subjects = json.load(open(subjects_file))
  rel_dict = {}
  for subject in subjects:
    rel_dict[subject] = {}
    related_subjects = get_related(subject)
    for related in related_subjects:
      if related['id'] in subjects:
        rel_dict[subject][related['id']] = related['score']
  json.dump(rel_dict, open(dump_file, 'w'))
  ensure_symmetry(rel_dict)


def get_related(subject_id, try_nr=0):
  """ Retrieve subject information from the OpenAlex API. If an error occurs,
  try again after waiting five seconds, as the error comes from the server. If
  it is not resolved after three tries, return an empty dict. """
  res = req.get(f'https://api.openalex.org/concepts/{subject_id}')
  try:
    return res.json()['related_concepts']
  except json.decoder.JSONDecodeError as e:
    print(subject_id, e)
    sleep(5)
    if try_nr == 3:
      return {}
    else:
      return get_related(subject_id, try_nr=try_nr+1)

def ensure_symmetry(rel_dict):
  """ Ensure that the resulting dictionary is symmetric, i.e. if a subject
  B appears in the list of related subjects of A, A should appear in the 
  list of B with the same score. """
  for subject in rel_dict:
    for related in rel_dict[subject]:
      if related not in rel_dict:
        print(f'Related subject does not have its own list: {related}')
      elif subject not in rel_dict[related]:
        print(f'Subject is not in the list of the related subject: {related}')
      elif rel_dict[subject][related] == rel_dict[related][subject]:
        print(f'Scores do not match: {subject}, {related}')


if __name__ == '__main__':
  subjects_file = 'data/openalex/subjects.json'
  dump_file = 'data/openalex/related.json'
  get_relationships(subjects_file, dump_file)