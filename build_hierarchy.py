""" Build the subject hierarchy as a dict with each subject mapped to its
ancestors. """


import json
from os import listdir


def all_fields(doc_folder, subjects_file):
  """ Assert that all OpenAlex documents have at least one field assigned
  to them. """
  subjects = json.load(open(subjects_file))
  fields = []
  no_field, total = 0, 0
  for subject, data in subjects.items():
    if data['level'] == 0:
      fields.append(subject)
  assert len(fields) == 19
  for file in listdir(doc_folder):
    docs = json.load(open(f'{doc_folder}/{file}'))
    for subject in docs:
      for doc in docs[subject]:
        has_field = False
        total += 1
        for subject in doc['subjects']:
          if subject in fields:
            has_field = True
        if not has_field:
          no_field += 1
  print(total, no_field)


def build(subjects_file, dump_file):
  subjects = json.load(open(subjects_file))
  hierarchy = {}
  for subject in subjects:
    hierarchy[subject] = []
    for ancestor in subjects[subject]['ancestors']:
      if ancestor['id'] in subjects:
        hierarchy[subject].append(ancestor['id'])
  json.dump(hierarchy, open(dump_file, 'w'))


def print_stats(subjects_file, hierarchy_file):
  """ Given a hierarchy, count how many ancestors there are
  that are not fields. """
  subjects = json.load(open(subjects_file))
  hierarchy = json.load(open(hierarchy_file))
  cnt = 0
  for subject in hierarchy:
    for ancestor in hierarchy[subject]:
      if subjects[ancestor]['level'] > 0:
        cnt += 1
  ancestors = sum([len(v) for v in hierarchy.values()])
  print(f'{ancestors} ancestors in total')
  print(f'{cnt} ancestors are not fields')


def complete_hierarchy(hierarchy_file):
  """ Assert that the hierarchy is complete, i.e. that the ancestors
  of ancestors are included in the list. """
  hierarchy = json.load(open(hierarchy_file))
  cnt = 0
  for subject in hierarchy:
    for ancestor in hierarchy[subject]:
      for a in hierarchy[ancestor]:
        if a not in hierarchy[subject]:
          cnt += 1
  print(cnt)


if __name__ == '__main__':
  subjects_file = 'data/openalex/subjects.json'
  hierarchy_file = 'data/openalex/hierarchy.json'
  doc_folder = 'data/openalex/docs'
  # complete_hierarchy(hierarchy_file)
  all_fields(doc_folder, subjects_file)