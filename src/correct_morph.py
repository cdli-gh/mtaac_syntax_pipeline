import codecs
import os

def is_int(string):
  '''
  '''
  try:
    int(string)
    return True
  except:
    return False

def open_file(path):
  '''
  '''
  with codecs.open(path, 'r', 'utf-8') as f:
    headers = None
    for line in f.readlines():
      line = line.strip().split('\t')
      if len(line)>3:
        if not headers:
          headers = line
        else:
          line_dict = dict(zip(headers, line))
          if is_int(line_dict['FORM'].strip('[]')[0]) and line_dict['XPOSTAG'][:2]!='NU':
            print(line_dict)

_path = os.path.dirname(os.path.abspath(__file__))
f_path = os.path.join(_path, 'data', 'cdli-conll-all')

for f in os.listdir(f_path):
  open_file(os.path.join(f_path, f))
