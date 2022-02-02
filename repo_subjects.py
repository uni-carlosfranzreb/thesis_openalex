""" Map OpenAlex subjects to the subjects of the repositories. """


import json
from copy import deepcopy


def map_subjects():
  """ Return a list of dictionaries with the OpenAlex subject ID, the name of
  the subject (valid both in OpenAlex and in the repositories) and the list of
  documents that are indexed with that subject. """
  openalex_data = json.load(open('data/openalex/subjects.json'))
  openalex = {d['name'].lower(): id for id, d in openalex_data.items()}
  matches = {}
  for folder in ['depositonce', 'edoc', 'refubium']:
    repo = json.load(open(
      f'data/json/dim/{folder}/relevant_subjects_reversed.json'
    ))
    for subject in repo:
      if subject['subject'] is None:
        continue
      name = subject['subject'].lower()
      if name in openalex:
        if name in matches:
          matches[name]['docs'] += subject['values']
        else:
          matches[name] = {
            'openalex_id': openalex[name], 'docs': subject['values']
          }
  json.dump(matches, open('data/openalex/repo_mapping.json', 'w'))


def get_ddc():
  """ Dump the numbers and doc counts of the DDC subjects. Sort them by the
  number of documents they are assigned to. """
  # dict of subjects (keys) and the list of publications they appear in (values).
  folder = 'data/json/dim'
  file = 'relevant_subjects_reversed.json'
  depositonce = json.load(open(f'{folder}/depositonce/{file}'))
  edoc = json.load(open(f'{folder}/edoc/{file}'))
  refubium = json.load(open(f'{folder}/refubium/{file}'))
  all = {(s['subject'], s['type']): deepcopy(s['values']) for s in depositonce}
  for repo in (edoc, refubium):
    for s in repo:
      if (s['subject'], s['type']) in all:
        all[(s['subject'], s['type'])] += s['values']
      else:
        all[(s['subject'], s['type'])] = s['values']
  ddc = {k[0]: len(v) for k, v in all.items() if k[1] == 'ddc'}
  sorted_ddc = {
    k: v for k, v in sorted(ddc.items(), key=lambda t: t[1], reverse=True)
  }
  json.dump(sorted_ddc, open('data/json/dim/all/ddc_subjects.json', 'w'))


def ddc_docs():
  """ Once we have manually assigned DDC numbers to the OpenAlex fields, we now
  retrieve the documents for each DDC number and store them by field. """
  ddc = json.load(open('data/openalex/ddc_mapping.json'))
  numbers = []
  docs = {f: {} for f in ddc.keys()}
  for field in ddc:
    numbers += list(ddc[field])
  folder = 'data/json/dim'
  file = 'relevant_subjects_reversed.json'
  for repo in ['depositonce', 'edoc', 'refubium']:
    data = json.load(open(f'{folder}/{repo}/{file}'))
    for subject in data:
      number = subject['subject']
      if subject['type'] == 'ddc' and number[:2] in numbers:
        for field in ddc:
          if number[:2] in ddc[field]:
            if number in docs[field]:
              docs[field][number] += subject['values']
            else:
              docs[field][number] = subject['values']
  json.dump(docs, open('data/openalex/ddc_docs.json', 'w'))


if __name__ == '__main__':
  ddc_docs()