""" Build the subject hierarchy as a dict with each subject mapped to its
ancestors. """


import json
from os import listdir


def correct(doc_folder, subjects_file, dump_folder):
  """ Correct the hierarchy violations of the files in the given folder. """
  subjects = json.load(open(subjects_file))
  for file in listdir(doc_folder):
    docs = json.load(open(f'{doc_folder}/{file}'))
    correct_docs = {}
    for subject in docs:
      correct_docs[subject] = []
      for doc in docs[subject]:
        correct_docs[subject].append({
          'data': doc['data'],
          'subjects': complete(doc['subjects'], subjects)
        })
    json.dump(correct_docs, open(f'{dump_folder}/{file}', 'w'))


def correct_vecs(doc_folder, subjects_file, dump_folder):
  """ Correct the hierarchy violations of the files in the given folder, where
  vectors are stored. The difference with the function above is that there
  are no subjects in the files. """
  subjects = json.load(open(subjects_file))
  for file in listdir(doc_folder):
    docs = json.load(open(f'{doc_folder}/{file}'))
    correct_docs = []
    for doc in docs:
      correct_docs.append({
        'data': doc['data'],
        'subjects': complete(doc['subjects'], subjects)
      })
    json.dump(correct_docs, open(f'{dump_folder}/{file}', 'w'))


def complete(doc_subjects, all_subjects):
  """ Given the assigned subjects of a document, append the ancestors of each
  subject to the list. """
  complete_subjects = {}
  for subject, score in doc_subjects.items():
    complete_subjects[subject] = score
    for ancestor in all_subjects[subject]['ancestors']:
      if ancestor['id'] not in doc_subjects:
        if ancestor['id'] not in complete_subjects:
          complete_subjects[ancestor['id']] = score
  return complete_subjects


if __name__ == '__main__':
  subjects_file = 'data/openalex/subjects.json'
  hierarchy_file = 'data/openalex/hierarchy.json'
  dump_folder = 'data/openalex/docs_hierarchy'
  doc_folder = 'data/openalex/docs'
  vecs_folder = 'data/openalex/vecs'
  correct_vecs(vecs_folder, subjects_file, vecs_folder)