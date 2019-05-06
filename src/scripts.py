import os
import sys
import codecs
import re
from ansi2html import Ansi2HTMLConverter
from mtaac_package.CoNLL_file_parser import conll_file
from mtaac_package.common_functions import *
from cdliconll2conllu.converter import CdliCoNLLtoCoNLLUConverter
##from conllu.convert import convert as conllu2brat
from SPARQLTransformer import sparqlTransformer

'''
Not in use:

import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
'''
#
#---/ GENERAL COMMENTS /-------------------------------------------------------
#
'''
PIP DEPENDENCIES:
- mtaac_package (https://github.com/cdli-gh/mtaac-package)
- ansi2html
# - rdflib // not used
# - SPARQLWrapper // not used

OTHER DEPENDENCIES (Windows):
- http://www.oracle.com/technetwork/java/javase/downloads/
  jdk8-downloads-2133151.html

WORKFLOW:
+ 1. CDLI-CoNLL (already there)
+ 2. CoNLL2RDF <https://github.com/acoli-repo/conll-rdf>
+ 3. RDF
+ 4. Syntactic Pre-annotator
+ 5. RDF2CoNLL
>? 6. CDLI-CoNLL2CoNLL-U
    <https://github.com/cdli-gh/CDLI-CoNLL-to-CoNLLU-Converter)>
> 7. CoNLLU > Brat
8. Brat (push file to brat server)
(9. Editor corrects syntax)
10. Brat 2 CDLI-Conll
  <https://github.com/cdli-gh/brat_to_cdli_CONLLconverter>

TODO:
+ check .sh scripts for missed steps
- columns should be adjusted for CDLI-CoNLL:
  ID WORD MORPH2 POS IGNORE IGNORE IGNORE
- make sure columns are correctly designated for both formats
- make sure abbreviations are unified:
  - either different rules for different abbreviations
    OR
  - better:
    - apply your own abbr. unifier (lemmatization data scripts)
      to make the data unified.
    - then insure that the abbr. in SPARQL match
- Find a solution for rendering words in SPARQL.
  Perhaps, FLASK templates would be the best solution also to corpus-specific
  placeholders' rendering.
'''
#
#---/ ANSI 2 HTML /------------------------------------------------------------
#
a2h_conv = Ansi2HTMLConverter()
#
#---/ Variables /--------------------------------------------------------------
#
_path = os.path.dirname(os.path.abspath(__file__))
sp = subprocesses()
#
#---/ CDLI-CoNLL > CONLL-U /---------------------------------------------------
#

class CC2CU(common_functions, CdliCoNLLtoCoNLLUConverter):
  '''
  Wrapper around CDLI-CoNLL-to-CoNLLU-Converter:
  https://github.com/cdli-gh/CDLI-CoNLL-to-CoNLLU-Converter
  
  '''
  GIT_CC2CU = 'https://github.com/cdli-gh/CDLI-CoNLL-to-CoNLLU-' \
              'Converter.git'
  
  def __init__(self):
    self.cdliCoNLLInputFileName = 'CoNLL data'
    ##    self.install_or_upgrade_CC2CU()
    self.__reset__()
    from cdliconll2conllu.mapping import Mapping
    self.cl = Mapping()
    self.header = '#%s' %'\t'.join(self.cl.conllUFields)
##    print(self.cl.cdliConllFields, len(self.cl.cdliConllFields))
##    ## TESTING ONLY:
##    for f_name in ['P100149.conll', 'P100159.conll', 'P100188.conll']:
##      f_path = os.path.join(_path, 'data', 'cdli-conll', f_name)
##      self.convert_CC2CU(f_path)

  def install_or_upgrade_CC2CU(self):
    '''
    Install CC2CU if missing or upgrade it.
    '''
    sp.run(['pip', 'install', 'git+'+self.GIT_CC2CU, '--upgrade'])

  def convert_from_str(self, conll_str):
    '''
    Convert CDLI-CoNLL to CoNLL-U from CoNLL string.
    '''
    #print(conll_str)
    lines_all = [l.strip() for l in conll_str.splitlines()]
    headerLines = [l for l in lines_all if l[0]=='#']
    inputLines = [l.split('\t') for l in lines_all if l not in headerLines+['']]
    if '\t' in headerLines[-1]:
      headerLines = headerLines[:-1]
    headerLines.append(self.header)
    for l in inputLines:
      print([l])
    self.convertCDLICoNLLtoCoNLLU(inputLines)
    #print(self.outputLines, ['\t'.join(l) for l in self.outputLines])
    conll_str = '\n'.join(headerLines+['\t'.join(l) for l in self.outputLines])
    self.__reset__()
    return conll_str

  def convert_from_file(self, filename):
    '''
    Convert CDLI-CoNLL to CoNLL-U from file.
    '''
    sp.run(['cdliconll2conllu', '-i', filename, '-v'], print_stdout=False)

cdli_conll_u = CC2CU()

#---/ CONLL-U <> CONLL-RDF /---------------------------------------------------
#
class CoNLL2RDF(common_functions):
  '''
  Wrapper around CoNLL-RDF:
  https://github.com/acoli-repo/conll-rdf
  
  '''
  GIT_CONLLRDF = 'https://github.com/acoli-repo/conll-rdf.git'
  CONLLRDF_PATH = os.path.join(_path, 'conll-rdf')

  def __init__(self):
    '''
    '''
    self.add_java_path()
    if not os.path.exists(self.CONLLRDF_PATH):
      self.install_CONLLRDF()

  def add_java_path(self):
    '''
    Windows: Find and add Java/JDK/bin path to env.
    '''
    self.JAVA_PATH = None
    for b in ['', ' (x86)']:
      pf = os.environ['ProgramFiles'].replace(b, '')
      basic_java_path = os.path.join(pf, 'Java')
      if os.path.exists(basic_java_path):
        dirs_lst = os.listdir(basic_java_path)
        jdk_lst = [jdk for jdk in dirs_lst if 'jdk' in jdk]
        jre_lst = [jre for jre in dirs_lst if 'jre' in jre]
        if jdk_lst!=[]:
          self.JAVA_JDK_PATH = \
                             os.path.join(basic_java_path, jdk_lst[-1], 'bin')
          self.JAVA_JRE_PATH = \
                   os.path.join(basic_java_path, jre_lst[-1], 'bin')
          break
    if not self.JAVA_JDK_PATH:
      print(
        '''No Java Development Kit installation found! '''
        '''Download and install latest:\n'''
        '''http://www.oracle.com/technetwork/'''
        '''java/javase/downloads/index.html''')
      return False
    elif self.JAVA_JDK_PATH not in sp.env['PATH']:
      sp.env['PATH']+=self.JAVA_JDK_PATH
    elif self.JAVA_JRE_PATH not in sp.env['PATH']:
      sp.env['PATH']+=self.JAVA_JRE_PATH
    self.JAVAC_PATH = os.path.join(self.JAVA_JDK_PATH, 'javac.exe')
    return True
  
  def install_CONLLRDF(self):
    '''
    Install CoNLL-RDF:
    1. Clone Github repo
    2. Build Java libs
    '''
    sp.run(['git', 'clone', self.GIT_CONLLRDF])
    self.compile_CONLLRDF()

  def compile_CONLLRDF(self):
    '''
    Compile CoNLL-RDF Java libraries.
    '''
    dep_dict = {
      'CoNLLStreamExtractor': 'CoNLL2RDF',
      'CoNLLRDFAnnotator': 'CoNLLRDFFormatter',
      'CoNLLRDFUpdater': 'CoNLLRDFViz' 
      }
    src_path = os.path.join(
      self.CONLLRDF_PATH, 'src', 'org', 'acoli', 'conll', 'rdf')
    target_path = os.path.join(self.CONLLRDF_PATH, 'bin')
    if not os.path.exists(target_path):
      os.mkdir(target_path)
    cp_vars = self.java_command(full_path=True, include_bin=True)[-1]
    for f in os.listdir(src_path):
      if '.java' in f and f.replace('.java', '') in dep_dict.keys():
        src_files_path = os.path.join(src_path, f)
        dep_src_file_path = os.path.join(src_path,
                                    dep_dict[f.replace('.java', '')])
        src_files_lst = [src_files_path, dep_src_file_path+'.java']
        cp_path = cp_vars
        self.compile_java(src_files_lst,
                          target_path,
                          cp_path)

  def compile_java(self, src_files_lst, target_path, cp_path, cwd_path=None):
    '''
    Run Java compiler with command.
    '''
    self.run([r'%s' %self.JAVAC_PATH,
              '-d', r'%s' %target_path,
              '-g',
              '-cp', r'%s' %cp_path,
              ]+[r'%s' %f for f in src_files_lst],
             cwd_path=cwd_path)

  def conll2rdf(self, f_path, columns_typ):
    '''
    Run Java CoNNL2RDF script to convert CoNLL file to RDF.
    '''
    #self.define_columns(columns_typ)
    command = self.CoNLLStreamExtractor_command() + ['../data/'] \
              + self.columns
    self.dump_rdf(rdf_str, f_path)

  def rdf2conll(self, columns, f_path=None, stdin_str=None,
                decode_stdout=False, target_path=None):
    '''
    Run Java CoNNL2RDF script to convert CoNLL file to RDF.
    '''
    #self.define_columns(columns_type)
    if f_path==None and stdin_str==None:
      print('rdf2conll wrapper: specify path OR string.')
      return None
    command = self.CoNLLRDFFormatter_command() + ['-conll'] \
              + columns
    (CONLLstr, errors) = self.run(
      command,
      cwd_path=f_path,
      stdin_str=stdin_str,
      decode_stdout=True)
    CONLLstr = CONLLstr.replace(' #', ' \n#') \
               .replace('\t#', '\n#').replace('\n\n', '\n')
    if target_path:
      self.dump(CONLLstr, target_path)
    return CONLLstr

  def get_stdin(self, stdin_path=None, stdin_str=None): #escape_unicode=False
    '''
    Get stdin from path or string to use with run.
    '''
    stdin = ''
    if stdin_path==None and stdin_str==None:
      return b''
    if stdin_path:
      with codecs.open(stdin_path, 'r', 'utf-8') as file:
        stdin = file.read()
        if 'etcsri' in stdin_path and '.conll' in stdin_path:
          stdin = self.convert_ETCSRI(stdin)
    elif stdin_str:
      stdin = stdin_str
    if type(stdin)!=bytes:
      stdin = stdin.encode('utf-8')
##    if escape_unicode==True:
##      stdin = self.standardize_translit(stdin)
    print(stdin_str)
    return stdin
    
  def run(self, command, cwd_path=None, stdin_path=None, stdin_str=None,
          decode_stdout=True):#, escape_unicode=False
    '''
    Open file, load it to stdin, run command, return stdout.
    '''
    stdin = self.get_stdin(
      stdin_path, stdin_str)#, escape_unicode=escape_unicode)
    if not cwd_path:
      cwd_path=self.CONLLRDF_PATH
    stdout = sp.run(
      command,
      cwd=cwd_path,
      stdin=stdin,
      print_stdout=False,
      decode_stdout=decode_stdout
      )
    return self.filter_errors(stdout)

  def filter_errors(self, stdout):
    '''
    Return (real_result, errors_or_warnings).
    '''
    shell_markers = [b'java.', b'log4j', b'org.apache', b'org.acoli']
    typ = type(stdout)
    if typ==str:
      stdout = stdout.encode('utf-8')
    shell_lst = []
    for b in stdout.split(b'\n'):
      for m in shell_markers:
        if m in b:
          shell_lst.append(b)
          break
    stdout_lst = [b for b in stdout.split(b'\n') if b not in shell_lst]
    if typ==bytes:
      errors = b'\n'.join(shell_lst)
      stdout = b'\n'.join(stdout_lst)
##      print(stdout.decode('utf-8'))
##      print(errors.decode('utf-8'))
    elif typ==str:
      errors = b'\n'.join(shell_lst).decode('utf-8')
      stdout = b'\n'.join(stdout_lst).decode('utf-8')
##      print(stdout)
##      print(errors)
    return (stdout, errors)

  def CoNLLStreamExtractor_command(self):
    '''
    Return a list containing basic command to run CoNLLStreamExtractor
    with no additional arguments.
    '''
    # Make command to run CoNLL2RDF with java
    return self.java_command()+['org.acoli.conll.rdf.CoNLLStreamExtractor']

  def CoNLLRDFFormatter_command(self):
    '''
    Return a list containing basic command to run CoNLLRDFFormatter
    with no additional arguments.
    '''
    # Make command to run CoNLL2RDF with java
    return self.java_command()+['org.acoli.conll.rdf.CoNLLRDFFormatter']

  def java_command(self, full_path=False, include_bin=True):
    '''
    Return a list containing basic java command to the library.
    Set path to 'full' to get full path output.
    '''
    # Prepare java vatriables
    dest = 'bin'
    lib_path = os.path.join(self.CONLLRDF_PATH, 'lib')
    if full_path==False:
      libs = ';'.join(
        ['lib/%s' %l for l in os.listdir(lib_path)
         if '.jar' in l])
    elif full_path==True:
      dest = os.path.join(self.CONLLRDF_PATH, dest)
      libs = ';'.join(
        [os.path.join(lib_path, l) for l in os.listdir(lib_path)
         if '.jar' in l])
    # Make command to run CoNLL2RDF with java
    cp = libs
    if include_bin==True: 
      cp = ';'.join([dest, libs])
    return ['java', '-cp', cp]
      
  def dump_rdf(self, rdf_str, f_path):
    '''
    Recieve original path and rdf string, dump to file.
    '''
    rdf_str = "#new_text" + rdf_str.split("#new_text")[1]
    filename = f_path.split('/')[-1].split('.')[0]+'.ttl'
    dump_path = os.path.join(_path, 'data', 'conll-rdf', filename)
    self.dump(rdf_str, dump_path)

#---/ SYNTAX PREANNOTATION /---------------------------------------------------
#
class syntax_preannotation(CoNLL2RDF):
  '''
  Class to preannotate turtle files with SPARQL update queries.
  Extends ´CoNLL2RDF´.
  '''
  REQUEST_SRC = [
    ('remove-IGNORE', 0),
    ('extract-feats', 1),
    ('remove-MORPH2', 0),
    ('init-SHIFT',  1),
    ('REDUCE-adjective', 3),
    ('REDUCE-math-operators', 1), # <- additional rules for admin - 
    ('REDUCE-numerals-chain', 6),
    ('REDUCE-time-num', 1),
    ('REDUCE-measurements', 1), # -->
    ('REDUCE-compound-verbs', 1),
    ('REDUCE-adnominal', 3),
    ('REDUCE-appos', 1),
    ('REDUCE-absolutive', 1),
    ('REDUCE-appos', 1), # again?
    ('REDUCE-adjective', 1), # again?
    ('REDUCE-appos', 4), # again?
    ('REDUCE-preposed-genitive', 1),
    ('REDUCE-arguments', 5), # again?
    ('REDUCE-adjective', 1), # again?
    ('REDUCE-to-HEAD', 1),
    ('remove-feats', 1),
    ('create-ID-and-DEP', 1),
    ('create-_HEAD', 1)
    ]

  #other possible rules:
  # PN <-- N (as in & instead of PN lugal)
  # reduce remaining nouns to first verb as nmod (?)
  # mu <-- V.MID

  #           (NU) 
  #            | 
  #     (ADJ)  NU
  #        \   /
  #         UNIT\      
  #   (...)/     \     (NU) 
  #   ____________BASE__/
  #  /  |     |    |    \
  # u4  ki   giri  iti  (us)
  # |   |     |    |     |
  # NU  PN   PN  (diri)  mu
  #     |     |    |     \
  #   (...) (...)  MN     V.MID--...
  #                   
  #                  
  
  REQUEST_REMOVE_IGNORE = [
    ('remove-IGNORE', 1)
    ]
  SPARQL_PATH = os.path.join(_path, 'syntax-preannotation', 'sparql')
  OUTPUT_PATH = os.path.join(_path, 'data', 'conll-preannotated')
  
  def __init__(self):
    '''
    '''
    CoNLL2RDF.__init__(self)

  def load_requests(self, requests=[]):
    '''
    Load SPARQL requests to ´self.requests_full_lst´.
    Specify repeats from int in ´r[1]´ when it is not ´None´.
    '''
    requests_lst = []
    if requests==[]:
      requests = self.REQUEST_SRC
    for r in requests:
      addit = ''
      if r[1]!=None:
        repeat = '{%s}' %r[1]
      requests_lst.append(
        r'%s\%s.sparql%s' %(self.SPARQL_PATH, r[0], repeat))
    return requests_lst
    
  def preannotate(self, f_path):
    '''
    Run SPARQL with ´self.requests_full_lst´ from requests.
    First command converts CoNLL to RDF and applies preannotation
    rules to it. The second converts the file back to CoNLL.
    '''
    columns = [
      'ID_NUM', 'FORM', 'BASE', 'MORPH2',
      'POS', 'EPOS', 'HEAD', 'DEP', 'EDGE']
    corpus = 'cdli'
    override = {}
    if 'etcsri' in f_path:
      corpus = 'etcsri'
      columns = [
        'ID_NUM', 'FORM_ATF', 'BASE', 'MORPH2',
        'POS', 'EPOS', 'HEAD', 'DEP', 'EDGE']
      override = {
        'FORM_ATF': 'FORM'}
    c = conll_file(path=f_path, corpus=corpus)
    c.configure_str_output(columns, override=override)
    rdf_str = self.convert_to_conll_and_preannotate(c)
    print('zzzzzzzzzzzzzzzzz', rdf_str) #<-- PROBLEM HERE !!!! returns b''
    filename, target_path, target_path_tree = self.get_path_data(f_path)
    self.tree_output(rdf_str, target_path_tree)
    conll_str = self.rdf2conll(columns=c.override_columns,
                               stdin_str=rdf_str, decode_stdout=False)
    c.merge_columns_from_conll_str(conll_str, ['HEAD', ('EDGE', 'DEPREL')])
    c.configure_str_output(['ID_NUM']+c.COLUMNS_CDLI[1:], override=override)
    conll_u = cdli_conll_u.convert_from_str(str(c))+'\n' #<--convert to CoNLL-U
    self.dump(conll_u, target_path)

  def get_path_data(self, f_path):
    '''
    '''
    filename = os.path.basename(f_path)
    target_path = os.path.join(self.OUTPUT_PATH, filename) 
    target_path_tree = os.path.join(
      self.OUTPUT_PATH, '%s_tree.html' %filename.split('.')[0])
    return filename, target_path, target_path_tree
    
  def convert_to_conll_and_preannotate(self, conll_obj):
    '''
    Convert CoNLL to RDF and preannotate with SPARQL.
    '''
    # !TODO!
    # REPLACE ['http://oracc.museum.upenn.edu/etcsri/'] by context!
    command = self.CoNLLStreamExtractor_command() \
              + ['http://oracc.museum.upenn.edu/etcsri/'] \
              + conll_obj.override_columns + ['-u'] \
              + self.load_requests()
    run_dict={
      'command': command, 'stdin_str': str(conll_obj),
      'decode_stdout': False}
      #, 'escape_unicode': True}
    #print(run_dict) #<-- ALL GOOD
    (rdf_str, errors) = self.run(**run_dict) #<-- PROBLEM SOMEWHERE HERE !!!! returns b''
    print(errors) #Error in Parsing Data: Incorrect XPOSTAG at line:
    #'1	{d}en-lil₂	_	NAME	_	_	_' in file CoNLL data.
    print('!!!!!!!!!!!!!!!!!!!!', str(conll_obj))
    return rdf_str

  def tree_output(self, rdf_str, target_path=''):
    '''
    Return string with parsed RDF tree representation.
    Dump to target_path when it is given.
    '''
    command = self.CoNLLRDFFormatter_command() + ['-grammar']
    (tree_str, errors) = \
               self.run(command, stdin_str=rdf_str, decode_stdout=True)
    tree_html = a2h_conv.convert(tree_str)
    tree_html = tree_html.replace('pre-wrap', 'pre')
    if target_path!='':
      self.dump(tree_html, target_path)
    return tree_str

#---/ COMMANDS /---------------------------------------------------------------
#
'''
Preannotate all files in data/etsri-conll-all, except all errors:
'''
##f_path = os.path.join(_path, 'data', 'etcsri-conll-all')
##sx = syntax_preannotation()
##for f in os.listdir(f_path):
##  try: 
##    sx.preannotate(os.path.join(f_path, f))
##  except Exception as e:
##    raise e
##    pass

'''
Preannotate all files in data/cdli-conll-all, except all errors:
'''
f_path = os.path.join(_path, 'data', 'cdli-jinyan-non-admin') #'etcsri-conll-all')
##f_path = os.path.join(_path, 'data', 'cdli-conll-all')
sx = syntax_preannotation()
for f in os.listdir(f_path):
  try:
    sx.preannotate(os.path.join(f_path, f))
  except Exception as e:
    raise e
    pass

#CC2CU()
#CoNLL2RDF()
#syntax_preannotation()

##c = CoNLL2RDF()
##c.rdf2conll("data\conll-rdf\P100188.ttl")

