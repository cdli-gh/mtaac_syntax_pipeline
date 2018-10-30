#
#
#---/ Morph data sets /--------------------------------------------------------
#
'''
Source: http://oracc.museum.upenn.edu/etcsri/parsing/index.html
Transliteration convention: MTAAC
Double vowels stand for long vowel
'''
#
# Noun (phrase)
#
N = [
  {'slot': 'N1',
   'name': 'Head',
   'morphemes': [],
   'abbreviations': []
   },
  {'slot': 'N2',
   'name': 'Modifier',
   'morphemes': ['e'],
   'abbreviations': ['DEM']
   },
  {'slot': 'N3',
   'name': 'Possessor',
   'morphemes': ['ju', 'zu', 'ani', 'bi', 'bi', 'me', 'zunenee', 'anenee'],
   'abbreviations': ['1-SG-POSS', '2-SG-POSS', '3-SG-H-POSS',
                     '3-SG-NH-POSS', 'DEM2', '1-PL-POSS', '2-PL-POSS',
                     '3-PL-POSS']
   },
  {'slot': 'N4',
   'name': 'Plural-marker or the ordinal number suffix',
   'morphemes': ['enee', 'kamak', 'kama'],
   'abbreviations': ['PL', 'ORD', 'ORD']
   },
  {'slot': 'N5',
   'name': 'Case-marker',
   'morphemes': ['ø', 'e', 'ra', 'e', 'da', 'ta', 'ce', "'a", 'ra', "'a", 'ra',
                 'e', 'ak', 'gin', 'ne', 'ec'],
   'abbreviations': ['ABS', 'ERG', 'DAT-H', 'DAT-NH', 'COM', 'ABL', 'TERM',
                     'L1', 'L2-H', 'L2-NH', 'L3-H', 'L3-NH', 'GEN', 'EQU',
                     'L4', 'ADV']
   },
  {'slot': 'N6',
   'name': 'Copula',
   'morphemes': ['men', 'men', 'am', 'menden', 'menzen', 'mec', 'nanna'],
   'abbreviations': ['COP-1-SG', 'COP-2-SG', 'COP-3-SG', 'COP-1-PL',
                     'COP-2-PL', 'COP-3-PL', 'EXCEPT']
   }
  ]
#
# Finite verb
#
V = [
  {'slot': 'V1',
   'name': 'The modal prefix ha-, negative prefix nu-, prefix of anteriority',
   'morphemes': ['nu', 'ha', 'u', 'STEM', 'STEM-PL', 'STEM-RDP',
                 'ga', 'nan', 'bara', 'nuc', 'ci', 'na'],
                 #from ga on - V1, but sub V2 in schema
   'abbreviations': ['NEG', 'MOD1', 'ANT', 'STEM', 'STEM-PL', 'STEM-RDP',
                     'MOD2', 'MOD3', 'MOD4', 'MOD5', 'MOD6', 'MOD7']
   },
  {'slot': 'V2',
   'name': 'Modal prefixes other than ha-, the finite-marker prefixes',
   'morphemes': ['i', 'ii', 'ii', 'a', 'aa', 'al'],
   'abbreviations': ['FIN', 'FIN-LI', 'FIN-L2', 'FIN', 'FIN-L2', 'FIN']
   },
  {'slot': 'V3',
   'name': 'Coordinator prefix',
   'morphemes': ['nga'],
   'abbreviations': ['COOR']
   },
  {'slot': 'V4',
   'name': 'Ventive (cislocative) prefix',
   'morphemes': ['m', 'mu'],
   'abbreviations': ['VEN', 'VEN']
   },
  {'slot': 'V5',
   'name': "Middle prefix or 3nh pronominal prefix "
           "(specifying the person, gender and number "
           "of the first in the sequence of dimensional prefixes)",
   'morphemes': ['ba', 'b'],
   'abbreviations': ['MID', '3-NH']
   },
  {'slot': 'V6',
   'name': "Initial Pronominal prefix (specifying the person, "
           "gender and number of the first in the sequence of "
           "dimensional prefixes)",
   'morphemes': ['1', 'r', 'e', 'nn', 'mee', 'nnee'],
   'abbreviations': ['1-SG', '2-SG', '2-SG', '3-SG-H', '1-PL', '3-PL']
   },
  {'slot': 'V7',
   'name': 'Dimensional I: dative prefix',
   'morphemes': ['a'],
   'abbreviations': ['DAT']
   },
  {'slot': 'V8',
   'name': 'Dimensional II: comitative prefix',
   'morphemes': ['da'],
   'abbreviations': ['COM']
   },
  {'slot': 'V9',
   'name': 'Dimensional III: ablative or terminative prefix',
   'morphemes': ['ta', 'ci', 'ce'],
   'abbreviations': ['ABL', 'TERM', 'TERM']
   },
  {'slot': 'V10',
   'name': 'Dimensional IV: locative1, locative2, or locative3 prefix',
   'morphemes': ['ni', 'ni', 'n', 'i', 'e', 'ø', 'i'],
   'abbreviations': ['L1', 'LOC-OB', 'L1-SYN', 'L2', 'L2', 'L2-SYN', 'L3']
   },
  {'slot': 'V11',
   'name': 'Final Pronominal prefix (referring to A or P, '
           'depending on the tense)',
   'morphemes': ['1', 'e', 'n', 'n', 'n', 'n', 'b', 'b', 'b', 'nnee'],
   'abbreviations': ['1-SG-A', '2-SG-A', '3-SG-H-A', '3-SG-H-P', '3-SG-H-L3',
                     '1-SG-A-OB', '3-SG-NH-A', '3-SG-NH-P', '3-SG-NH-L3',
                     '3-PL-H-P']
   },
  {'slot': 'V12',
   'name': 'stem',
   'morphemes': ['STEM', 'STEM-PF', 'STEM-PL', 'STEM-RDP', 'COP'],
   'abbreviations': ['STEM', 'STEM-PF', 'STEM-PL', 'STEM-RDP', 'COP']
   },
  {'slot': 'V13',
   'name': 'present-future marker (in intransitive verbs)',
   'morphemes': ['ed', 'en'],
   'abbreviations': ['PF', 'PLEN']
   },
  {'slot': 'V14',
   'name': 'pronominal suffix (referring A, S, or P depending on the tense)',
   'morphemes': ['en', 'en', 'en', 'en', 'en', 'en', 'ø', 'ø', 'e', 'e',
                 'enden', 'enden', 'enden', 'enzen', 'enzen', 'enzen',
                 'ec', 'ec', 'ec', 'enee'],
   'abbreviations': ['1-SG-A', '1-SG-S', '1-SG-P', '2-SG-A', '2-SG-S',
                     '2-SG-P', '3-SG-S', '3-SG-P', '3-SG-A', '3-SG-S-OB',
                     '1-PL-A', '1-PL-S', '1-PL', '2-PL-A', '2-PL-S', '2-PL',
                     '3-PL-S', '3-PL-P', '3-PL', '3-PL-A']
   },
  {'slot': 'V15',
   'name': 'Subordinator',
   'morphemes': ["'a"],
   'abbreviations': ['SUB']
   },
  ]
#
# Non-finite verb
#
NV = [
  {'slot': 'NV11',
   'name': 'negative prefix',
   'morphemes': ['nu'],
   'abbreviations': ['NEG']
   },
  {'slot': 'NV2',
   'name': 'stem',
   'morphemes': ['STEM', 'STEM-PF', 'STEM-PL', 'STEM-RDP'],
   'abbreviations': ['STEM', 'STEM-PF', 'STEM-PL', 'STEM-RDP']
   },
  {'slot': 'NV3',
   'name': 'present-future marker',
   'morphemes': ['ed'],
   'abbreviations': ['PF']
   },
  {'slot': 'NV4',
   'name': 'subordinator',
   'morphemes': ["'a"],
   'abbreviations': ['SUB']
   },
  ]
NAMED_ENTITIES = ['DN', 'EN', 'GN', 'MN', 'PN', 'RN', 'SN', 'TN', 'WN', 'AN',
                  'CN', 'FN', 'ON', 'YN']
#---/ Converter /--------------------------------------------------------------
#

class morph_converter:
  '''
  Converts different Sumerian annotation styles with dict. given above.
  MTAAC > ORACC: `self.MTAAC2ORACC()` with annotation str as argument.
  '''

  def __init__(self):
    pass

  def MTAAC2ORACC(self, m_str):
    '''
    Convert MTAAC morph. annotation style to ORACC style.
    '''
    return self.add_slot_lables_to_abbr(m_str)

  def add_slot_lables_to_abbr(self, m_str):
    '''
    Add ORACC-style slots (N1=..., V1=..., NV11=...)
    to MTAAC morph. annotation. 
    '''
    default_slot = ''
    m_lst = m_str.replace('’', "'").split('.')
    if 'NF' in m_lst:
      lst = NV+N
      m_lst = m_lst[1:]
      default_slot = 'NV2=STEM'
    elif 'V' not in m_lst:
      lst = N
      default_slot = 'N1=STEM'
      if set(m_lst) & set(NAMED_ENTITIES):
        default_slot = 'N1=NAME' 
    else:
      lst = V
      default_slot = 'V12=STEM'
    m_lst_new = []
    for m in m_lst:
      slot_m = ''
      for d in lst:
        if m in d['abbreviations']:
          slot_m = '%s=%s' %(d['slot'], m)
          break
      if slot_m=='':
        slot_m = default_slot
      m_lst_new.append(slot_m)
    return '.'.join(m_lst_new)

mc = morph_converter()
test_lst = ['FIN.3-SG-H-A.V.3-SG-P', 'MN.L1', 'MID.V.3-SG-S', 'NF.V.ABS', 'SN.GEN', 'NU', 'PN.GEN.ABL',
            'VEN.3-SG-H-A.V.3-SG-P', "NU.GEN.COP-3-SG.GEN.L1"]

#NV2=STEM.N5=GEN.N6=COP-3-SG.N5=GEN.N5=L1
#V4=VEN.V11=3-SG-H-A.V12=STEM.V14=3-SG-P

for t in test_lst:
  t = mc.MTAAC2ORACC(t)
  print(t)

  

