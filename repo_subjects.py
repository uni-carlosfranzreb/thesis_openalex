""" Map OpenAlex subjects to the subjects of the repositories. """


import json


def map_subjects(dump_file):
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
  json.dump(matches, open(dump_file, 'w'))


if __name__ == '__main__':
  mapping_file = 'data/openalex/repo_mapping.json'
  map_subjects(mapping_file)