import os
import json
import codecs
from mtaac_package.CoNLL_file_parser import conll_file

_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(_path, 'data', 'cdli-conll-all')
path_out = os.path.join(_path, 'data', 'cdli-conll-all-json')

conll_lst = []

def dump_corpus_to_json():
  corpus = 'cdli'
  if 'etcsri' in path:
    corpus = 'etcsri'
  for f in list(os.listdir(path)):
    conll_lst.append(conll_file(path=os.path.join(path,f),
                                corpus=corpus))
    d = conll_lst[-1].dict_output()
    out = os.path.join(path_out,f.replace('conll', 'json'))
    with codecs.open(out, 'w', 'utf-8') as ff:
      ff.write(json.dumps(d))

dump_corpus_to_json()

for f in os.listdir(path_out):
  j_path = os.path.join(path_out, f)
  with codecs.open(j_path, 'r', 'utf-8') as ff:
    d = json.loads(ff.read())  
  conll_lst.append(conll_file(data_dict=d))

print('corpus loaded')

comb_dict_EPOS = {
  '0 NU': 46, 'N N': 769, 'N NU': 333,
  'NU NU': 241, 'NU N': 470, 'N V': 238,
  'V N': 168, 'N PN': 266, 'PN PN': 17,
  'PN V': 24, 'N MN': 42, 'MN N': 38,
  'N DN': 27, 'DN V': 16, 'V NU': 87,
  'NU 0': 10, 'PN N': 217, 'NU V': 46,
  'N SN': 72, 'SN V': 44, 'V 0': 42,
  'V MN': 3, 'MN V': 2, 'V V': 26, 'V DN': 10,
  'DN DN': 3, 'DN NU': 11, 'DN N': 9, 'V PN': 52,
  'PN NU': 153, 'SN N': 30, 'N RN': 16, 'RN N': 21,
  'PN 0': 10, '0 N': 33, 'NU SN': 4, 'NU PN': 87,
  'MN 0': 5, 'N WN': 3, 'WN N': 2, 'PN CNJ': 5,
  'CNJ PN': 6, 'N CNJ': 11, 'CNJ N': 14, 'N GN': 2,
  'GN N': 3, 'V SN': 6, 'N 0': 9, 'N FN': 9, 'FN V': 2,
  'SN CNJ': 5, 'SN NU': 5, 'DN SN': 5, 'V RN': 6, 'RN NU': 1,
  'N _': 11, '_ _': 6, '_ NU': 7, 'N PRP': 1, 'PRP PN': 1,
  'PN DN': 4, 'NU _': 4, 'FN N': 6, 'V _': 3, '_ 0': 1,
  'PN GN': 1, 'SN PN': 3, '_ N': 9, 'FN NU': 1, 'WN NU': 1,
  'N ON': 5, 'ON N': 4, 'SN 0': 3, '_ V': 1, 'N AN': 1,
  'AN N': 1, 'CNJ SN': 2, 'PN SN': 1, 'N AJ': 1, 'AJ V': 1,
  'ON V': 1, 'V CNJ': 1, 'SN SN': 2,
  '0 PN': 1, 'PN _': 1, '_ PN': 1
  }

def filter_valid(c, i, filtr):
  field, v1, v2 = filtr
  if i==0:
    if c.tokens_lst[i][field]==v2 and v1 in [0, '0']:
      return True
  elif i==len(c.tokens_lst):
    if c.tokens_lst[i][field]==v1 and int(v2) in [0, '0']:
      return True
  elif i+1 < len(c.tokens_lst):
    if c.tokens_lst[i][field]==v1 and c.tokens_lst[i+1][field]==v2:
      return True
  return False  

def produce_comb(field='EPOS', replace=None, filtr=None):
  comb_dict = {}
  
  def analyze(c):
    i = 0
    while i<len(c.tokens_lst):
      if not filtr or filter_valid(c, i, filtr):
        if i==0:
          pair = [None, c.tokens_lst[i][field]]
        elif i+1<len(c.tokens_lst):
          pair = [c.tokens_lst[i][field], c.tokens_lst[i+1][field]]
        else:
          pair = [c.tokens_lst[i][field], None]
        if replace:
          for n in range(0,2):
            if replace[n]:
              pair[n] = replace[n]
        comb_key = ' '.join(pair)
        if comb_key in comb_dict.keys():
          comb_dict[comb_key]+=1
        else:
          comb_dict[comb_key] = 1
      i+=1
      
  for c in conll_lst:
    try:
      analyze(c)
    except Exception as e:
      raise e
      pass
  return comb_dict

def apply_rules(kk, field):
  try:
    first, second = kk.split()
  except ValueError:
    first = kk
    second = 'None'
  if field=='EPOS':
    if first==second=='NU':
      return False
  if field=='XPOSTAG':
    if 'GEN' in kk:
      return False
  return True

def print_combinations(k, depth=0):

  def print_c(kk, field, c_dict):
    if c_dict[kk]>5 and apply_rules(kk, field): #note that this filters rare cases
      indent_str = ''.join(['\t' for i in range(0,depth)])
      print(indent_str, kk, c_dict[kk])
      return True

  prim_field = 'EPOS'
  secd_field = 'BASE'

  if print_c(k, prim_field, comb_dict_EPOS):
    filtr_EPOS = (prim_field, k.split(' ')[0], k.split(' ')[1])
    comb_dict = produce_comb(field=secd_field,
                             filtr=filtr_EPOS,
                             replace=(None,'Second')) #('First',None)
    depth+=1
    for kk in sorted(list(comb_dict.keys()),
                     key=lambda k: -comb_dict[k]):
      print_c(kk, secd_field, comb_dict)

comb_dict = {}

for k in sorted(
  list(comb_dict_EPOS.keys()),
  key=lambda k: -comb_dict_EPOS[k]):
  print_combinations(k)
