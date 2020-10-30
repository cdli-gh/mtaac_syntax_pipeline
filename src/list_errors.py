import codecs
import os

'''
Script to list CoNLL-RDF errors that hindered a proper HTML tree output.
Use for CoNLL-RDF debugging.
'''

_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(_path, 'data')
path_preann = os.path.join(path, 'conll-preannotated')

def list_files_with_errors():
  '''
  '''
  files_list = []
  for f in os.listdir(path_preann):
    if '_tree.html' in f:
      f_size = os.stat( os.path.join(path_preann, f)).st_size
      if f_size==752:
        conll_name = f.replace('_tree.html', '.conll')
        files_list.append(conll_name)
  return files_list
