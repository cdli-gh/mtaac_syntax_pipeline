import subprocess
import os
import codecs
import json
import re
import math
from pathlib import Path
#from multiprocessing import Pool
from ATF_translit_parser import transliteration, sylb
from random import sample

#---/ POS and named entities /-------------------------------------------------
#
class tags:
  '''
  Class for managing tags order in dict. lists:
  ORACC, ETCSL, UD.
  '''
  
  order_dict = {'ORACC': 0, 'ETCSL': 1, 'UD': 2}
  POS_dict = {
    'adjective': ['AJ', 'AJ', 'ADJ'],
    'adverb': ['AV', 'AV', 'ADV'],
    'number': ['NU', 'NU', 'NUM'],
    'conjunction': ['CNJ', 'C', 'CONJ'],
    'determinative pronoun': ['DET', 'PD', 'DET'],
    'interjection': ['J', 'I', 'INTJ'],
    'noun': ['N', 'N', 'NOUN'],
    'verb': ['V', 'V', 'VERB'],
    'independent/anaphoric pronoun': ['IP', '', ''],
    'possessive pronoun': ['PP', '', ''],
    'demonstrative pronoun': ['DP', '', ''],
    'modal/negative/conditional particle': ['MOD', '', ''],
    'preposition/adposition': ['PRP', '', 'ADP'],
    'interrogative pronoun': ['QP', '', ''],
    'relative pronoun': ['REL', '', ''],
    'reflexive/reciprocal pronoun': ['RP', '', ''],
    'subjunction': ['SBJ', '', ''],      
    'indefinite pronoun': ['XP', '', ''],
    'negator': ['', 'NEG', ''],
    }
  named_entities_dict = {
    'Divine Name': ['DN', 'DN', 'PROPN'],
    'Ethnos Name': ['EN', 'EN', 'PROPN'],
    'Geographical Name': ['GN', 'GN', 'PROPN'],
    'Month Name': ['MN', 'MN', 'PROPN'],
    'Personal Name': ['PN', 'PN', 'PROPN'],
    'Royal Name': ['RN', 'RN', 'PROPN'],
    'Settlement Name': ['SN', 'SN', 'PROPN'],
    'Temple Name': ['TN', 'TN', 'PROPN'],
    'Watercourse Name': ['WN', 'WN', 'PROPN'],
    'Agricultural (locus) Name': ['AN', '', 'PROPN'],
    'Celestial Name': ['CN', '', 'PROPN'],
    'Field Name': ['FN', 'PROPN', ''],
    'Line Name (ancestral clan)': ['LN', '', 'PROPN'],
    'Object Name': ['ON', '', 'PROPN'],
    'Quarter Name (city area)': ['QN', '', 'PROPN'],
    'Year Name': ['YN', '', 'PROPN'],
    'Other Name': ['', 'ON', 'PROPN']
    }

  def __init__(self):
    '''
    Create a list of all possible values.
    '''
    self.all = ['_']
    for dct in [self.POS_dict, self.named_entities_dict]:
      for k in dct.keys():
        for el in dct[k]:
          if el not in self.all:
            self.all.append(el)
    #ToDo: Ensure this line is everywhere elsewhere:
    self.all = sorted(self.all, key=lambda k: -len(k))

  def convert(self, tag, source, target):
    '''
    Recieve tag in one convention and return it in another, if exists.
    Allowed `source` and `target` values: 'ORACC', 'ETCSL', and 'UD'.
    '''
    if source==target or tag=='_':
      return tag
    src = self.order_dict[source]
    trg = self.order_dict[target]
    for dct in [self.POS_dict, self.named_entities_dict]:
      for k in dct.keys():
        if dct[k][src]==tag and dct[k][trg]!='':
          return dct[k][trg]
    #print('No %s value found for %s tag: %s' %(target, source, tag))
    return tag

  def adjust_POS(self, tag, src_convention, trg_convention='ORACC'):
    #ToDo: Ensure the following function is so elsewhere:
    '''
    Strip and unify POS tag.
    '''
    # NOTE 'X', 'U', 'L', and 'MA' as POS tags (clarify!)
    tag = tag.upper()
    if ' ' in tag:
      tag = tag.split(' ')[0]
    for t in self.all:
      for p in ['.', '/', ':']:
        if '%s%s' %(t,p) in tag:
          #print([t, self.convert(t, src_convention, trg_convention)])
          return self.convert(t, src_convention, trg_convention)
    if tag not in self.all:
      #print('Undefined %s tag escaped: %s' %(src_convention, tag))
      return '_'
    c_tag = self.convert(tag, src_convention, trg_convention)
    if c_tag!='':
      return c_tag
    return tag

#---/ CoNLL file /-------------------------------------------------------------
#
class conll_file:
  '''
  The class parses the .conll data.
  '''
  corpus_conventions = {'cdli': 'ORACC',
                        'etcsl': 'ETCSL',
                        'etcsri': 'ORACC'}
  
  def __init__(self, path):
    self.tags = tags()
    self.tokens_lst = []
    self.info_dict = {}
    self.info_lst = []
    for c in self.corpus_conventions.keys():
      if c in str(path):
        self.corpus = c
        self.convention = self.corpus_conventions[c]
    with codecs.open(path, 'r', 'utf-8') as f:
      self.data = f.read()
    self.parse()

  def parse(self):
    token_ID = ''
    for l in self.data.splitlines():
      if l:
        if l[0] not in ['#', ' ']:
          self.add_token(l.split('\t'), token_ID)
        elif l[0]=='#':
          self.info_lst.append(l)
          if ': ' in l:
            info_lst = l.strip('# ').split(': ')
            key = info_lst[0].strip(' ')
            value = ': '.join(info_lst[1:]).strip(' ')
            self.info_dict[key] = value
          elif '.' in l:
            token_ID = l.strip('# ')
          else:
            l = l.strip('# ')
            if l:
              if ('WORD' in l or 'FORM' in l) and 'ID' in l:
                l = l.replace("XPOSTAG", "POS")
                l = l.replace("FORM", "WORD")
                self.info_dict['legend'] = l.split('\t')
              else:
                self.info_dict['title'] = l
                
  def add_token(self, token_lst, token_ID):
    token_dict = self.make_token_dict(token_lst, token_ID)
    if 'SEGM' in token_dict.keys() and 'BASE' not in token_dict.keys():
      [token_dict['BASE'], token_dict['SENSE']] = \
                           self.segm_to_base_and_sense(token_dict['SEGM'])
    if 'WORD' in token_dict.keys():
      tw = transliteration(token_dict['WORD'])
      if tw.defective==False:
        token_dict['WORD'] = [tw.normalization,
                              tw.normalization_u,
                              tw.sign_and_det_normalization]
      token_dict['WORD_RAW'] = tw.raw_translit
    if 'BASE' in token_dict.keys():
      tb = transliteration(token_dict['BASE'], base=True)
      if tb.defective==False:
        token_dict['BASE'] = [tb.normalization,
                              tb.normalization_u,
                              tb.sign_and_det_normalization]
    if self.filter_token(token_dict)!=False:
      self.tokens_lst.append(token_dict)
    else:
      # DO NOT OMIT LINES!
      # ToDo:
      # 1. Ensure this is in the others versions of this class elsewhere.
      # 2. Check cases:
      #     - might be caused by [] in BASE / SEGM!
      print('WARNING! Defective token:', token_dict)
      self.tokens_lst.append(token_dict)

  def make_token_dict(self, token_lst, token_ID):
    token_dict = {'ID': token_ID}
    if 'legend' not in self.info_dict.keys():
      if token_lst[-1] not in ['_', 'proper', 'emesal', 'glossakk']:
        print('-1', token_lst[-1])
      legend = ['ID', 'WORD', 'BASE', 'POS', 'SENSE'] # ETCSL
    else:
      legend = self.info_dict['legend']
    i = 0
    while i < len(legend):
      try:
        if legend[i]=='POS':
          token_dict['MORPH2'] = token_lst[i]         
          token_dict['POS'] = self.tags.adjust_POS(
            token_lst[i], self.convention)
        else:
          token_dict[legend[i]] = token_lst[i]
      except IndexError:
        token_dict[legend[i]] = '_'
      i+=1
    return token_dict

  def segm_to_base_and_sense(self, segm):
    '''
    Recieve segmentation, return lemma.
    '''
    for s in segm.split('-'):
      if '[' in s and ']' in s:
        base = s.split('[')[0]
        sense = s.split('[')[1][:-1]
        return [base, sense]
    return ['_', '_']

  def filter_token(self, t):
    if 'LANG' in t.keys():
      if 'akk' in t['LANG']:
        return False
    try:
      for tag in ['WORD', 'BASE', 'POS']:
        tt = t[tag]
        if type(tt)==list:
          tt = ''.join(tt)
        if '_' in tt or tt=='':
          return False
    except KeyError:
      return False
    if type(t['WORD'])!=list or type(t['BASE'])!=list:
      return False
    return True    

  def __str__(self):
    '''
    Return CoNLL string.
    '''
    conll_fields = ['ID', 'WORD_RAW', 'BASE', 'SENSE', 'MORPH2', 'POS', 'SEGM']
    conll_str = '\n'.join([i for i in self.info_lst if ' ID\t' not in i])+'\n'
    conll_str+='# %s\n' %'\t'.join(conll_fields)
    for t in self.tokens_lst:
      row_vals = []
      for cf in conll_fields:
        v = t[cf]
        if cf=='MORPH2':
          v = self.add_fake_position_placeholders(t[cf], t['POS'])
        if type(v)==list:
          row_vals.append(v[0])
        else:
          row_vals.append(v)
      conll_str+='\t'.join(row_vals)+'\n'
    print(conll_str)
    return conll_str

  def add_fake_position_placeholders(self, morph_str, POS):
    '''
    Add fake ETCSRI-style position placeholders
    to MTAAC-style morph. annotation. 
    '''
    morph_lst = []
    tags_lst = morph_str.split('.')
    if tags_lst[0]=='NF':
      POS = tags_lst[0] = 'NV'
    if len(tags_lst)>1 and tags_lst[0]==POS or POS in ['NU']:
      #tags_lst = tags_lst[1:]
      for m in tags_lst:
        placeholder = POS
        for case_abbr in ['GEN', 'ABS', 'L1', 'L2',
                          'ERG', 'TERM', 'DEM1', 'DEM2']:
          if case_abbr in m:
            placeholder = 'N'
        morph_lst.append('%s5=%s' %(placeholder, m))
    else:
      morph_lst = tags_lst
      #morph_lst = ['%s1=STEM' %POS]
    return '.'.join(morph_lst)

  
