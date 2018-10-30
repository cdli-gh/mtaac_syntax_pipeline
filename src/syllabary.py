import re
from lxml import etree

NOT_IN_SYLLABARY = \
'''sagi: SILA3.ŠU.GABA
cucin: MUŠ3.EREN
nanna: ŠEŠ.KI
siskur2: AMAR×ŠE.AMAR×ŠE
ictaran: KA.DI
ukken: URU×BAR
cakkan: GIR3
cunigin: ŠU.GAN2@t
nerah: MUŠ
mudra5: SIK2.BU
kup4: KID
nisaba: ŠE.NAGA
acnan: ŠE.ŠE.NUN&NUN
kikken2: HI×AŠ2.HI×AŠ2
nijir: DUN3@g@g
jectug2: GIŠ.TUG2.PI
isimud4: PAP.IGI@g.NUN.ME
dirig: SI.A
cembizid: ŠIM
jizzal: GIŠ.TUG2.PI.ŠIR.SILA3
jicbun: KI.BI.GAR
eridug: NUN
jissu: GIŠ.MI
cej3: A.AN
jisal: GISAL
mussa: SAL.UŠ.DI
cej14: IM.A.AN
jarza2: PA.LUGAL
enkud: ZAG.HA
isimud: PAP.IGI@g
abula: KA2.GAL
gudug: HI×NUN.ME
nijin3: U.UD.KID
tackarin: TUG2
surungal: UD.NUN
sizkur2: AMAR×ŠE.AMAR×ŠE
cajan: U.GAN
gur21: E.TUM
gibil6: NE.GI
jickim: IGI.DUB
curuppag: SU.KUR.RU
jarza: PA.AN
cubtum6: KASKAL.LAGAB×U&LAGAB×U
enegir: IM
gira2: GIŠ.BAR
jecpu2: ŠU.PAP.PAP
cajar: KA×GAR
pel: NE
gilgamec2: GIŠ.NE@s.GA.ME.U.U.U
cagina: GIR3.ARAD
nergal: PIRIG.AB@g.GAL
dur3: ANŠE.ARAD
nijin: LAGAB.LAGAB
cembi: ŠIM
sajcu: U.SAG
ganba: KI.LAM
nijin6: AB×HA
gilgamec3: GIŠ.NE.GA.MES
karkara: IM
ajrig: IGI.DUB
aratta: LAM×KUR+RU
ulutim: KI.KAL
jectug3: GIŠ.PI.TUG2
anzud2: AN.IM.MI
ji25: DUGUD
kucu4: SAG@g
abgal2: NUN.ME.KA×GAN2@t
si19: KA×UD
cimacki: LU.SU
ligima: IGI.TUR.TUR
mitum: KU.AN
cubtum5: KASKAL.LAGAB×U
marduk: AMAR.UTU
cubtum3: KASKAL.LAGAB
imjaja3: AŠ2.AN
gilgamec: GIŠ.DUN3@g.MAŠ
kadra2: GAR.ŠA3
tidnim: PIRIG.PIRIG
tur8: BU
cembi2: ŠIM
cuba4: MUŠ3
gakkul3: U.DIM
mitum2: KU.IDIM
kas7: ŠID
bibad: ŠE.HU.TUR
imjaja: AŠ2.A.AN
algamec: UD.SAL.HUB2
dagan: KI.URU×MIN
jicbum: KI.BI.GAR
cennux: ME.AD.KU3
cimacgi: LU.SU
cimacki: LU.SU
cimacgi2: LU.SU.A
emedu2: GA2×AN.A.TU
enerux: AN.U
gidlam4: SAL.UŠ
gilgamesx: BIL3.GA.MES
rigx: PA.MUNUS.HUB2.DU
bil4: GIŠ.NE
nijin5: LAL2.LAGAB
zipah2: ŠU.BAD
urub: URU×GAN2@t
mete: TE.ME
curmen: ŠU.ME.EREN
nijar: U.UD.KID
umma2: HI×DIŠ
nindaba: PAD.AN.MUŠ3
sab: PA.IB
cet: ŠID
': ALEPH
durum: EZEN×BAD
adad: IM
geckim: IGI.DUB
zigum: ZIKUM
dimgal: DIMGUL
nirah: MUŠ
enegir3: EN.DIM2.GIG
jizzal2: ŠIR@t.SILA3
rab: RAB
aski: AŠ.HI×DIŠ.GI4
jecbun: KI.BI.GAR
rig8: PA.HUB2
rig9: HUB2.DU
sala4: SILA3
zabar3: KA×UD.BAR
reb: KAL
mara2: AMAR
jir15: EŠ2
unud: AB2.KU'''

###PHONETIC
#ALEPH in ši-te-ʾ-u₂, iš-te-ʾ-u₂)
#ŠID in ep-šet

CORRECT_READING_DICT = {
  'rab3': ['rab', 'RAB'],
  'im4': ['im6', 'DU'],
  'asgi': ['aski', 'AŠ.HI×DIŠ.GI4'] #BORGER 102
  }

###PROBLEMATIC:
#zikum s. MZL no. 757 (indistinguishable from ENGUR in NA).
#for rab3 (Borger: just RAB, not LUGAL - different signs) see MZL no. 262
#dimgal is not is MZL, but there is DIMGUL. It is unclear is that is the same.
#asgi is missing in MZL, cf. aski: MZL no. 102

SPECIAL_SIGNS_DICT = {
  '1(barig)': 'DIŠ',
  '2(barig)': 'NIGIDAMIN',
  '3(barig)': 'NIGIDAEŠ',
  '4(barig)': '4(DIŠ)',

  "1(gec'u)": 'DIŠ', #?
  "2(gec'u)": '2(GEŠU)',
  "3(gec'u)": '3(GEŠU)',
  "4(gec'u)": '4(GEŠU)',
  "5(gec'u)": '5(GEŠU)',

  "1(dic@t)": 'AŠ@z', #?
  "2(dic@t)": '2(AŠ@t)', #?
  "3(dic@t)": '3(AŠ@t)', #?

  "2(dic@v)": '2(AŠ~a)', #? SAME VALUE ALSO FOR 2(AŠ~b)
  "3(dic@v)": '3(AŠ~a)', #? SAME VALUE ALSO FOR 3(AŠ~b)
  "4(dic@v)": '4(AŠ~a)', #? SAME VALUE ALSO FOR 4(AŠ~b)
  "8(dic@v)": '8(AŠ)', #?

  "3(ban2)": '3(BAN2)',

  "1(bur'u)": 'BUR',
  "2(bur'u)": '2(BURU)',
  "3(bur'u)": '3(BURU)',
  }

### Placeholders:

##n
##n(bur3)
##n(esze3)
##n(iku)
##n(ban2)
##n(barig)

#---/ Levinstein Distance /----------------------------------------------------
#
def LD(s, t):
  if s == "":
    return len(t)
  if t == "":
    return len(s)
  if s[-1] == t[-1]:
    cost = 0
  else:
    cost = 1
  res = min([LD(s[:-1], t)+1,
             LD(s, t[:-1])+1,
             LD(s[:-1], t[:-1]) + cost])
  return res

#---/ Syllabary /--------------------------------------------------------------
#
class syllabary:

  re_index = re.compile(r'(?P<value>[^\d]+)(?P<index>\d+)')
  BASIC_XPATH_DICT = {
    'name': 'name/text()',
    'unicode': 'unicode/text()',
    'unicode_empty': 'unicode_empty',
    'unicode_name': 'unicode_name/text()',
    'borger_2004': 'syllabars/borger_2004/text()',
    'borger_1981': 'syllabars/borger_1981/text()'
  }
  UNICODE_ATF_DICT = {
    'ṣ': 's,',
    'ṭ': 't,',
    'š': 'c',
    'ŋ': 'j',
    'ḫ': 'h',
    'ʾ': "'"
  }
  ATF_UNICODE_DICT = dict([[v,k] for k,v \
                           in UNICODE_ATF_DICT.items()])

  def __init__(self):
    self.norm_dict = {}
    #self.replaced_pairs = [] #for checking
    self.signs_lst = []
    self.load_all()

  def check_sequence(self, s_dict_lst, sign_list):
    s_names = '-'.join([s['name'] for s in s_dict_lst])
    seq_new = '-'.join([s['value']+s['index'] \
                           for s in sign_list])
    if s_names not in self.norm_dict.keys():
      self.norm_dict[s_names] = [seq_new]
    else:
      if seq_new not in self.norm_dict[s_names]:
        #print(s_names+':', seq_new, 'vs.', ', '.join(self.norm_dict[s_names]))
        self.norm_dict[s_names]+=[seq_new]
        
##  def standardize(self, s_dict, sign_index_lst, atf=True):
##    '''
##    Function to standardize transliteration conventions.
##    '''
##    [value, index] = sign_index_lst
##    sign = value+self.stringify_index(index)
##    sign_u = self.unicode_atf_converter(value, direction='a>u')\
##             +self.stringify_index(index).lower()
##    #IF ALREADY IN DICT AS KEY
##    if sign_u in self.norm_dict.keys():
##      return sign
##    # IF NOT IN DICT. KEYS
##    else:
##      for k in self.norm_dict.keys():
##        # IF IN VALUES
##        if sign_u in self.norm_dict[k]:
##          if (sign, k) not in self.signs_lst:
##            print('replacing', sign, 'with', k)
##            self.signs_lst+=[(sign, k)]
##          return self.unicode_atf_converter(k, direction='u>a')
##    matches_lst = self.group_entry_by_similar_values(s_dict)
##    self.add_to_norm_dict(sign_u, matches_lst)
##    return sign
##
##  def add_to_norm_dict(self, sign_u, matches_lst):
##    '''
##    Subfunction of ´self.standardize()´.
##    '''
##    m_group = {}
##    for m in matches_lst:
##      for k in m.keys():
##        if sign_u.lower() in m[k] or sign_u.upper() in m[k]:
##          m_group = m
##          break
##    m_group_keys = [k for k in m_group.keys() if k not in ['None']]
##    # Use sign as standard value
##    key = sign_u
####    # Use 'main' as standard value if exists
####    if m_group_keys!=[]:
####      key = m_group_keys[0].lower()
##    self.norm_dict[key] = []
##    for k in m_group.keys():
##      for v in m_group[k]:
##        if v.lower() not in self.norm_dict[key]:
##          self.norm_dict[key].append(v.lower())
##
##    #print(sign_u, m_group, m_group_keys)
##    #CONTINUE FROM HERE!!!!     
##    #self.group_entry_by_similar_values(s_dict)
##    #self.stringify_index(index) ???

  def find_entry_by_name(self, name):
    if name.lower() in SPECIAL_SIGNS_DICT.keys():
      name = SPECIAL_SIGNS_DICT[name]
    for s_dict in self.signs_lst:
      if s_dict['name']==None:
        #print(s_dict)
        pass
      elif name.lower()==s_dict['name'].lower():
        return s_dict
    return None
    
  def find_entry_by_value(self, value, index=1, atf=True):
    '''
    Find sign entry by value and index. Return sign name.
    The atf argument (default True) serves to convert ATF values to unicode.
    '''
    indx_str = self.stringify_index(index)
    if value+indx_str in CORRECT_READING_DICT.keys():
      value_and_index = self.val_and_index(
        CORRECT_READING_DICT[value+indx_str][0])
      index = value_and_index['index']
      value = value_and_index['value']
    x_index_lst = []
    if index=='x':
      index = 'ₓ'
    for s_dict in self.signs_lst:
      if type(s_dict)!=dict:
        print('S_dict issue:', s_dict, value, index)
      for v_dict in s_dict['values']:
        if atf==True:
          sign_value = self.unicode_atf_converter(v_dict['value'],
                                                  'u>a').lower()
        else:
          sign_value = v_dict['value'].lower()
        if sign_value==value.lower() and str(v_dict['index'])==str(index):
          if index in ['ₓ']:
            x_index_lst.append(s_dict['name'])
          else:
            return s_dict
    if x_index_lst!=[]:
      return x_index_lst
    return None

  def unicode_atf_converter(self, value, direction='u>a'):
    '''
    Convert Unicode value to ATF (direction='u>a')
    or ATF values to Unicode (direction='a>u').
    '''
    if direction=='u>a':
      dictionary=self.UNICODE_ATF_DICT
    elif direction=='a>u':
      dictionary=self.ATF_UNICODE_DICT
    value_new = ''
    for c in value.lower():
      if c in dictionary.keys():
        if value_new!='':
          if value_new[-1]!='@':
            c = dictionary[c]
        else:
          c = dictionary[c]
      value_new+=c
    if value.lower()!=value:
      return value_new.upper()
    return value_new

  def load_all(self):
    '''
    Load complete XML to list as dictionaries.
    '''
    for s_tag in etree.parse("syllabary.xml").xpath("//sign"):
      s_dict = {}
      s_dict = self.load_general_info(s_tag, s_dict)
      s_dict = self.load_values(s_tag, s_dict)
      self.signs_lst.append(s_dict)
    self.load_extra()

  def load_general_info(self, s_tag, s_dict):
    '''
    Load general entry info.
    '''
    for k in self.BASIC_XPATH_DICT.keys():
      v = s_tag.xpath(self.BASIC_XPATH_DICT[k])
      if v!=[]:
        s_dict[k] = v[0]
        if k in ['unicode_empty']: #binary values
          s_dict[k] = True
      else:
        s_dict[k] = None
    return s_dict

  def load_values(self, s_tag, s_dict):
    '''
    Load and parse values in entry, return dict.
    '''
    s_dict['values'] = []
    for typ in ['logographic', 'syllabic', 'determinative', 'numeral']:
      for v_tag in s_tag.xpath('values/%s/value' %typ):
        v_dict = {'type': typ}
        for attr in ['main', 'period']:
          attr_val = v_tag.xpath('@%s' %attr)
          if attr_val in [[], ['']]:
            attr_val = None
          v_dict[attr] = attr_val
        if v_tag.xpath('text()') not in [[], [''], ['empty']]:
          for s_str in v_tag.xpath('text()')[0].split(','):
            s_dict['values'].append({**v_dict, **self.val_and_index(s_str)})
    return s_dict

  def load_extra(self):
    '''
    Quick patch to include some missing values.
    '''
    for line in NOT_IN_SYLLABARY.split('\n'):
      [s_str, name] = line.split(': ')
      s_str = self.unicode_atf_converter(s_str, 'a>u')
      s_dict = self.find_entry_by_name(name)
      #NOTE THAT SOME MISSING VALUES ARE ACTUALLY SYLLABIC!
      v_dict = {'type': 'logographic', 'main': None}
      if s_dict!=None:
        s_dict['values']+=[{**v_dict, **self.val_and_index(s_str)}]
      else:
        s_dict = {'name': name,
                  'values': [{**v_dict, **self.val_and_index(s_str)}],
                  }
        self.signs_lst.append(s_dict)

  def val_and_index(self, s_str):
    '''
    Parse value and index in sign, return dict.
    '''
    value = s_str
    index = 1
    if 'ₓ' in s_str:
      return {'value': s_str.strip('ₓ'),
              'index': 'ₓ'}
    elif self.re_index.search(s_str):
      i = 0
      for x in self.re_index.finditer(s_str):
        if i==0:
          value = x.groupdict()['value']
          index = x.groupdict()['index']
        else:
          pass
        i+=1
    return {'index': int(index), 'value': value}

  def stringify_index(self, index):
    '''
    Return value index as int., x or zero.
    '''
    index_str = ''
    if index in ['ₓ']:
      return index
    if int(index) > 1:
      index_str = str(index)
    return index_str

  def group_all_similar(self):
    '''
    Compare LD of all values within one syllabary entry.
    '''
    for s_dict in self.signs_lst:
      self.group_entry_by_similar_values(s_dict)

  def group_entry_by_similar_values(self, s_dict):
    '''
    Function to group values of entry by similarity.
    '''
    done_lst = []
    matches_lst = []
    log_lst = s_dict['values']
    for v1_dict in log_lst:
      val_1 = v1_dict['value']
      v1_ndx = self.stringify_index(v1_dict['index'])
      matches_lst = self.group_match(val_1+v1_ndx, matches_lst)
      for v2_dict in log_lst:
        val_2 = v2_dict['value']
        if val_2 not in done_lst and val_1!=val_2:
          ld = self.levinsteiner(val_1, val_2, 0.15)
          if ld[0]==True:
            v2_ndx = self.stringify_index(v2_dict['index'])
            matches_lst = self.group_match(val_2+v2_ndx, matches_lst,
                                           val_1+v1_ndx)
      done_lst.append(val_1)
    return self.arrange_matches_by_main(matches_lst, s_dict)

  def arrange_matches_by_main(self, matches_lst, s_dict):
    '''
    Function to arrange `matches_lst` as dict. by the `main` parameter.
    This also corrects the original LD arrangment by merging groups
    if there is a valid `main` match between different dictionaries.
    '''
    matches_lst_new = []
    for gr in matches_lst:
      gr_dict = {}
      for s_str in gr:
        VI_dict = self.val_and_index(s_str)
        for v_dict in s_dict['values']:
          if VI_dict['value']==v_dict['value'] and \
             VI_dict['index']==v_dict['index']:
            main = 'None'
            if type(v_dict['main'])==list:
              main = v_dict['main'][0]
            if main not in gr_dict.keys():
              gr_dict[main] = [s_str]
            else:
              gr_dict[main]+=[s_str]
            break
      matches_lst_new.append(gr_dict)
    return self.merge_matches(matches_lst_new)

  def merge_matches(self, matches_lst):
    '''
    Subfunction of `self.arrange_matches_by_main`.
    This corrects the original LD arrangment by merging groups
    if there is a valid `main` match between different dictionaries.
    '''
    i = 0
    while i < len(matches_lst):
      n = 0
      while n < len(matches_lst):
        if n!=i:
          k_match = list(set(matches_lst[i].keys()) &
                         set(matches_lst[n].keys()))
          if [k for k in k_match if k!='None']!=[]:
            for k in matches_lst[n].keys():
              if k in matches_lst[i].keys():
                matches_lst[i][k]+=matches_lst[n][k]
              else:
                matches_lst[i][k] = matches_lst[n][k]
            matches_lst.remove(matches_lst[n])
            n-=1
        n+=1
      i+=1
    return matches_lst    
      
  def group_match(self, new_value, matches_lst, key_value=''):
    '''
    Function to group matches in sub-lists of `matches_lst`.
    '''
    if key_value=='':
      if [gr for gr in matches_lst if new_value in gr]==[]:
        matches_lst.append([new_value])
      return matches_lst
    for gr in matches_lst:
      if key_value in gr and new_value not in gr:
        gr.append(new_value)
      elif key_value not in gr and new_value in gr:
        gr.append(key_value)
    i = 0
    while i+1 < len(matches_lst):
      n = 0
      while n < len(matches_lst):
        if n!=i:
          if list(set(matches_lst[i]) & set(matches_lst[n]))!=[]:
            matches_lst[i] = list(set(matches_lst[i]+matches_lst[n]))
            matches_lst.remove(matches_lst[n])
            n-=1
        n+=1
      i+=1
    return matches_lst

  def levinsteiner(self, val_1, val_2, max_d=0.15):
    '''
    Compare values with Levinstein distance.
    Get two syllabary value strings.
    Preprocessing:
      - Strings converted to lowerscript.
      - Consonants unified.
      - Vowels escaped when both strings consist of two chars
        which are not vowels only.
      - Variants for interchangible elements.
    Similarity is measured in Levinstein Distance divided
    by the lenght of both original strings combined.
    The `max_d` param (default 0.15 for empirical best balance between losses and noise)
    defines the lower grade of similarity to be considered valid.
    The algorithm is optimistic: when dealing with variants, it returns the best score.
    '''
    result_lst = []
    val_1 = val_1.lower()
    val_2 = val_2.lower()
    for v1 in self.produce_variants(val_1):
      for v2 in self.produce_variants(val_2):
        v1 = self.escape_cons(v1)
        v2 = self.escape_cons(v2)
        if (len(v1)==2 and len(v1)==2) or (len(v1)>2 and len(v2)>2):
          v1 = self.escape_vowels(v1)
          v2 = self.escape_vowels(v2)
        ld_divided_by_length = LD(v1, v2) / len(v1+v2)
        result_lst.append([
          ld_divided_by_length < max_d,
          ld_divided_by_length,
          v1,
          v2])
    return sorted(result_lst, key=lambda x: x[1])[0]

  def escape_cons(self, value):
    '''
    Part of string similarity comparison on values.
    1. Replace similar consonants with placeholders.
    2. Escape gemination.
    '''
    escape_lst = [
      ('p', ['b', 'p']),
      ('k', ['k', 'q', 'g']),
      ('t', ['t', 'd', 'ṭ']),
      ('s', ['z', 's', 'š', 'ṣ']),
      ('m', ['m', 'n']),
      ('mk', ['ŋ']),
      ('h', ['ḫ', 'ʾ'])
      ]
    for v in value:
      for e in escape_lst:
        if v in e[1]:
          value = value.replace(v, e[0])
    i = 1
    new_val = value[0]
    while i < len(value):
      if value[i]!=value[i-1]:
        new_val+=value[i]
      i+=1
    return new_val

  def escape_vowels(self, value):
    '''
    Part of string similarity comparison on values.
    Replace all vowels with zero.
    Return escaped string or original one when consists of vowels only.
    '''
    esc_value = value
    vow_lst = ['a', 'e', 'i', 'u']
    for e in vow_lst:
      esc_value = esc_value.replace(e, '')
    if esc_value!='':
      return esc_value
    return value

  def produce_variants(self, value):
    '''
    Part of string similarity comparison on values.
    Produces variants for frequently interchangible elements
    for comprehensive comparison.
    
    Additionally, adds one char shorter variants
    for signs of 3 and more characters.
    '''
    vars_dict = {
      'e': ['a', 'i'],
      'i': ['e'],
      'y': ['w', 'i', ''],
      'w': ['p', 'y', ''],
      'n': ['ŋ'],
      'g': ['ŋ'],
      'r': ['l'],
      'l': ['r'],
      'ʾ': ['']
      }
    vars_lst = ['']
    for char in value:
      vchars_lst = [char]
      if char in vars_dict.keys():
        vchars_lst+=vars_dict[char]
      new_vars = []
      for var in vars_lst:
        new_vars+=[var+v_char for v_char in vchars_lst]
      vars_lst = new_vars
    return self.cut_longer_variants(vars_lst)

  def cut_longer_variants(self, vars_lst):
    '''
    Adds minus one char variants
    for signs of 3 and more characters
    and minus two chars variants
    for signs of 4 and more characters.
    '''
    I_shorter_vars = [v[:-1] for v in vars_lst if len(v)>3]
    II_shorter_vars = [v[:-2] for v in vars_lst if len(v)>4]
    return list(set(vars_lst+I_shorter_vars+II_shorter_vars))
    

#sylb = syllabary()
#print(sylb.levinsteiner('UTU', 'UD'))
#sylb.group_all_similar()
#print(sylb.find_entry_by_value("rab3"))

