import os
import sys
import subprocess
import codecs
import re
from ansi2html import Ansi2HTMLConverter
from mtaac_conll import conll_file


##import rdflib
##from SPARQLWrapper import SPARQLWrapper, JSON

#---/ GENERAL COMMENTS /-------------------------------------------------------
#
'''
WORKFLOW:

+ 1. CDLI-CoNLL (already there)
+ 2. CoNLL2RDF <https://github.com/acoli-repo/conll-rdf>
+ 3. RDF
+ 4. Syntactic Pre-annotator
+ 5. RDF2CoNLL
>? 6. CDLI-CoNLL2CoNLL-U <https://github.com/cdli-gh/CDLI-CoNLL-to-CoNLLU-Converter)>
> 7. CoNLLU > Brat
8. Brat (push file to brat server)
(9. Editor corrects syntax)
10. Brat 2 CDLI-Conll <https://github.com/cdli-gh/brat_to_cdli_CONLLconverter>
'''
##
##1. CDLI-CoNLL / ETCSRI > CoNLL-RDF
##2. CoNLL-C > 

# Pip dependencies:
# ansi2html
# rdflib // not used
# SPARQLWrapper // not used

# Dependencies (Windows):
# http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html
#

#---/ CHECKS /-----------------------------------------------------------------
#
def is_int(char):
  try:
    int(char)
    return True
  except ValueError:
    return False

#---/ COMMON FUNCTIONS /-------------------------------------------------------
#
class common_functions:

  def load_json(self, path):
    with codecs.open(path, 'r', 'utf-8') as f:
      json_data = json.load(f)
    return json_data
  
  def dump(self, data, filename, encoding='utf-8'):
    if not os.path.exists(os.path.dirname(filename)):
      os.makedirs(os.path.dirname(filename))
    with codecs.open(filename, 'w', encoding) as dump:
      dump.write(data)

  def get_html(self, url="", path="", repeated=False):
    html = None
    if url:
      try:
        with urlopen(url) as response:
          html = lxml_html.parse(response).getroot()
      except (TimeoutError, URLError) as e:
        if repeated==False:
          print('TimeoutError: %s\nTrying again...' %(url))
          return self.get_html(url=url, repeated=True)
        else:
          print('TimeoutError: %s\nFailed' %(url))
          self.errors.append('TimeoutError: %s' %(url))
          return None
    elif path:
      html = lxml_html.parse(path).getroot()
    return html
#
#---/ ANSI 2 HTML /------------------------------------------------------------
#
a2h_conv = Ansi2HTMLConverter()
#
#---/ SUBPROCESS /-------------------------------------------------------------
#
class subprocesses(common_functions):

  def __init__(self):
    self.subprocesses_list = []
    self.pending_lst = []
    self.max = 4
    self.env = os.environ.copy()
    
  def run(self, cmd, cwd='', stdin=None, print_stdout=False,
          return_stdout=True, decode_stdout=True, log_stdout=False):
    print('\n')
    print(r'run: %s' %(' '.join(cmd)))
    if not cwd:
      cwd = os.getcwd()
##    print(r'cwd: %s' %(cwd))
    p = subprocess.run(cmd,
                       cwd=r'%s' %(cwd),
                       input=stdin,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       env=self.env,
                       shell=True,
                       )
    output = self.trace_console(p, decode_stdout)
    if output==None:
      return None
##    if print_stdout==True and type(output)!=bytes:
##      print(output)
    if log_stdout==True and type(output)!=bytes:
      self.dump(output, 'syntax_pipeline.log')
    if return_stdout==True:
      return output
      
  def trace_console(self, p, decode_stdout):
    if decode_stdout:
      return p.stdout.decode('utf-8')
    return p.stdout

_path = os.path.dirname(os.path.abspath(__file__))
sp = subprocesses()

#---/ CDLI-CoNLL > CONLL-U /---------------------------------------------------
#
class CC2CU(common_functions):
  '''
  Wrapper around CDLI-CoNLL-to-CoNLLU-Converter:
  https://github.com/cdli-gh/CDLI-CoNLL-to-CoNLLU-Converter
  
  '''
  GIT_CC2CU = 'https://github.com/cdli-gh/CDLI-CoNLL-to-CoNLLU-' \
              'Converter.git'
  
  def __init__(self):
    self.install_or_upgrade_CC2CU()
    from cdliconll2conllu.converter import CdliCoNLLtoCoNLLUConverter as conv
    ## TESTING ONLY:
    for f_name in ['P100149.conll', 'P100159.conll', 'P100188.conll']:
      f_path = os.path.join(_path, 'data', 'cdli-conll', f_name)
      self.convert_CC2CU(f_path)

  def install_or_upgrade_CC2CU(self):
    '''
    Install CC2CU if missing or upgrade it.
    '''
    sp.run(['pip', 'install', 'git+'+self.GIT_CC2CU, '--upgrade'])

  def convert_CC2CU(self, filename):
    '''
    Convert CDLI-CoNLL to CoNLL-U.
    '''
    sp.run(['cdliconll2conllu', '-i', filename, '-v'], print_stdout=False)

#---/ CONLL-U <> CONLL-RDF /---------------------------------------------------
#
class CoNLL2RDF(common_functions):
  '''
  Wrapper around CoNLL-RDF:
  https://github.com/acoli-repo/conll-rdf
  
  '''
  GIT_CONLLRDF = 'https://github.com/acoli-repo/conll-rdf.git'
  CONLLRDF_PATH = os.path.join(_path, 'conll-rdf')

  COLUMNS_CONLLU = [
    'ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL',
    'DEPS', 'MISC']


  #ORIGINAL CDLI: 'ID', 'FORM', 'SEGM', 'XPOSTAG', 'HEAD', 'DEPREL', 'MISC']
  #CDLI AFTER PARSING: 'ID', 'WORD', 'BASE', 'SENSE', 'SEGM', 'POS'
  
  COLUMNS_CDLI_IN = ['OLD_ID', 'WORD', 'BASE', 'GW', 'MORPH2', 'POS']
  COLUMNS_CDLI_CONVERT = [
    'ID', 'OLD_ID', 'WORD', 'BASE', 'GW', 'MORPH2', 'POS', 'HEAD', 'EDGE']
  COLUMNS_CDLI_DROP = [
    'ID', 'IGNORE', 'WORD', 'BASE', 'GW', 'MORPH2', 'POS', 'HEAD', 'EDGE']
  COLUMNS_CDLI_OUT = [
    'ID', 'WORD', 'BASE', 'GW', 'MORPH2', 'HEAD', 'EDGE']

##ETCSRI WORD = MTAAC FORM
##
##ETCSRI POS = MTAAC XPOSTAG (!)
##ETCSRI MORPH2 = MTAAC XPOSTAG (!)
##
##ETCSRI STEM = MTAAC POS tags
##ETCSRI NAME = (MTAAC Names entities tags)
  
  #OLD_ID WORD BASE CF EPOS FORM GW LANG MORPH MORPH2 NORM POS SENSE
  COLUMNS_ETCSRI_IN = [
    'OLD_ID', 'WORD', 'BASE', 'CF', 'EPOS', 'FORM', 'GW', 'LANG', 'MORPH',
    'MORPH2', 'NORM', 'POS', 'SENSE']
  COLUMNS_ETCSRI_CONVERT = [
    'ID', 'OLD_ID', 'WORD', 'BASE', 'CF', 'EPOS', 'FORM', 'GW', 'LANG',
    'MORPH','MORPH2', 'NORM', 'POS', 'SENSE', '_HEAD', 'HEAD', 'EDGE']
  COLUMNS_ETCSRI_DROP = [
    'ID', 'IGNORE', 'WORD', 'BASE', 'IGNORE', 'IGNORE', 'IGNORE', 'GW',
    'IGNORE', 'IGNORE', 'MORPH2', 'IGNORE', 'POS', 'IGNORE', '_HEAD',
    'HEAD', 'EDGE']
  COLUMNS_ETCSRI_OUT = [
    'ID', 'WORD', 'BASE', 'GW', 'MORPH2', 'POS', '_HEAD', 'HEAD', 'EDGE']
##  COLUMNS_ETCSRI_DROP = [
##    'ID', 'OLD_ID', 'WORD', 'BASE', 'CF', 'EPOS', 'FORM', 'GW', 'LANG',
##    'MORPH','MORPH2', 'NORM', 'POS', 'SENSE', 'HEAD', 'EDGE']
##  COLUMNS_ETCSRI_OUT = [
##    'ID', 'OLD_ID', 'WORD', 'BASE', 'CF', 'EPOS', 'FORM', 'GW', 'LANG',
##    'MORPH','MORPH2', 'NORM', 'POS', 'SENSE', 'HEAD', 'EDGE']

  def __init__(self):
    self.add_java_path()
    if not os.path.exists(self.CONLLRDF_PATH):
      self.install_CONLLRDF()
    self.active_col_len = None
      
##    self.conll2rdf(f_path='data/cdli-conll/P100188.conll')

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
    self.define_columns(columns_typ)
    command = self.CoNLLStreamExtractor_command() + ['../data/'] \
              + self.columns
    self.dump_rdf(rdf_str, f_path)

  def rdf2conll(self, columns_type, f_path=None, stdin_str=None,
                decode_stdout=False, target_path=None):
    '''
    Run Java CoNNL2RDF script to convert CoNLL file to RDF.
    '''
##    print('!!!!!!!!!!!!!!!!!!!!!!!!!!', stdin_str.decode('utf-8'))
    self.define_columns(columns_type)
    if f_path==None and stdin_str==None:
      print('rdf2conll wrapper: specify path OR string.')
      return None
    command = self.CoNLLRDFFormatter_command() + ['-conll'] \
              + self.columns
    (CONLLstr, errors) = self.run(
      command,
      cwd_path=f_path,
      stdin_str=stdin_str,
      decode_stdout=True)
    CONLLstr = CONLLstr.replace(' #', ' \n#') \
               .replace('\t#', '\n#').replace('\n\n', '\n')
    if target_path:
      self.dump_conll(CONLLstr, target_path)
    return CONLLstr

  def get_stdin(self, stdin_path=None, stdin_str=None, escape_unicode=False):
    '''
    Get stdin from path or string to use with run.
    '''
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
    if escape_unicode==True:
      stdin = self.standardize_translit(stdin)
    return stdin

  def convert_ETCSRI(self, f_str):
    '''
    Special function to properly format ETCSRI CoNLL files.
    Extends the line ID with a text ID prefix.
    '''
    prefix = ''
    lines_lst = []
    for line in f_str.splitlines():
      if line!='':
        if '# Q' in line:
          prefix = line.split(' ')[1].strip('\n')
        elif is_int(line[0])==True and prefix!='':
          t_lst = line.split('\t')
          t_lst[0] = '%s.%s' %(prefix, t_lst[0])
          line = '\t'.join(t_lst)
        if '# Q' not in line:
          lines_lst+=[line]
    return '\n'.join(lines_lst)
    
  def run(self, command, cwd_path=None, stdin_path=None, stdin_str=None,
          decode_stdout=True, escape_unicode=False):
    '''
    Open file, load it to stdin, run command, return stdout.
    '''
    stdin = self.get_stdin(
      stdin_path, stdin_str, escape_unicode=escape_unicode)
    if not cwd_path:
      cwd_path=self.CONLLRDF_PATH
    stdout = sp.run(
      command,
      cwd=cwd_path,
      stdin=stdin,
      print_stdout=True,
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
      print(stdout.decode('utf-8'))
      print(errors.decode('utf-8'))
    elif typ==str:
      errors = b'\n'.join(shell_lst).decode('utf-8')
      stdout = b'\n'.join(stdout_lst).decode('utf-8')
      print(stdout)
      print(errors)
    #input()
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
    return ['java',
            '-cp', cp]

  def define_columns(self, typ):
    '''
    Define ´self.columns´ to match CoNLL format. 
    '''
    self.columns = getattr(self, 'COLUMNS_%s' %typ.upper())
##    columns_dict = {
##      'cdli_in': self.COLUMNS_CDLI,
##      'etcsri_in': self.COLUMNS_ETCSRI_IN,
##      'etcsri_convert': self.COLUMNS_ETCSRI_CONVERT,
##      'etcsri_drop': self.COLUMNS_ETCSRI_DROP,
##      'etcsri_out': self.COLUMNS_ETCSRI_OUT}
##    self.columns = columns_dict[typ]
##    if self.active_col_len:
##      self.columns = self.columns[:self.active_col_len]

  def standardize_translit(self, translit):
    '''
    Standardize transliteration and escape unicode chars.
    Necessery due to conll-rdf unicode issues.
    Accepts both utf-8 and bytes str.
    '''
    std_dict = {'š':'c', 'ŋ':'j', '₀':'0', '₁':'1', '₂':'2',
                '₃':'3', '₄':'4', '₅':'5', '₆':'6', '₇':'7',
                '₈':'8', '₉':'9', '+':'-', 'Š':'C', 'Ŋ':'J',
                '·':'', '°':'', 'sz': 'c', 'SZ': 'C',
                'ʾ': "'"}
    typ = type(translit)
    if typ==bytes:
      translit = translit.decode('utf-8')
    for key in std_dict.keys():
      translit = translit.replace(key, std_dict[key])
    if typ==bytes:
      return translit.encode('utf-8')
    return translit
      
  def dump_rdf(self, rdf_str, f_path):
    '''
    Recieve original path and rdf string, dump to file.
    '''
    rdf_str = "#new_text" + rdf_str.split("#new_text")[1]
    filename = f_path.split('/')[-1].split('.')[0]+'.ttl'
    dump_path = os.path.join(_path, 'data', 'conll-rdf', filename)
    self.dump(rdf_str, dump_path)

  def dump_conll(self, conll_str, target_path):
    '''
    Recieve original path and rdf string, dump to file.
    '''
    if type(conll_str)==bytes:
      conll_str = conll_str.decode('utf-8')
    self.dump(conll_str, target_path)

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
    ('REDUCE-compound-verbs', 1),
    ('REDUCE-adjective', 3),
    ('REDUCE-adnominal', 3),
    ('REDUCE-appos', 1),
    ('REDUCE-absolutive', 1),
    ('REDUCE-appos', 1),
    ('REDUCE-adjective', 1),
    ('REDUCE-appos', 4),
    ('REDUCE-preposed-genitive', 1),
    ('REDUCE-arguments', 5),
    ('REDUCE-adjective', 1),
    ('REDUCE-arguments', 5),
    ('REDUCE-to-HEAD', 1),
    ('remove-feats', 1),
    ('create-ID-and-DEP', 1),
    ('create-_HEAD', 1)
    ]
  REQUEST_REMOVE_IGNORE = [
    ('remove-IGNORE', 1)
    ]
  SPARQL_PATH = os.path.join(_path, 'syntax-preannotation', 'sparql')
  OUTPUT_PATH = os.path.join(_path, 'data', 'conll-preannotated')
  
  def __init__(self):
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
    corpus = 'cdli'
    self.active_col_len = None
    if 'etcsri' in f_path:
      corpus = 'etcsri'
      with codecs.open(f_path, 'r', 'utf-8') as f:
        t = f.read()
      columns = [s for s in t.split('\n') if '# ID\t' in s][0]\
                .strip('# ').split('\t')
      self.active_col_len = len(columns)
##      print(columns)
##      input(self.active_col_len)
    rdf_str = self.convert_to_conll_and_preannotate(
      f_path, columns_type='%s_in' %corpus)
    rdf_str = self.change_formatting(rdf_str, columns_type='%s_convert' %corpus)
    rdf_str = self.drop_columns(rdf_str, columns_type='%s_drop' %corpus)
    filename = os.path.basename(f_path)
    target_path = os.path.join(self.OUTPUT_PATH, filename)
    target_path_tree = os.path.join(
      self.OUTPUT_PATH, '%s_tree.html' %filename.split('.')[0])
    self.tree_output(rdf_str, target_path_tree)
    
    self.rdf2conll(stdin_str=rdf_str, columns_type='%s_out' %corpus,
                   decode_stdout=False,
                   target_path=target_path)

  def convert_to_conll_and_preannotate(self, f_path, columns_type):
    '''
    Convert CoNLL to RDF and preannotate with SPARQL.
    '''
    self.define_columns(columns_type)
    # !TODO!
    # REPLACE ['http://oracc.museum.upenn.edu/etcsri/'] by context!
    command = self.CoNLLStreamExtractor_command() \
              + ['http://oracc.museum.upenn.edu/etcsri/'] \
              + self.columns + ['-u'] \
              + self.load_requests()
    run_dict={
      'command': command, 'stdin_path': f_path,
      'decode_stdout': False, 'escape_unicode': True}
    if 'cdli' in f_path:
      run_dict['stdin_str'] = str(conll_file(f_path))
      del run_dict['stdin_path']
    (rdf_str, errors) = self.run(**run_dict)
    return rdf_str
    
  def change_formatting(self, rdf_str, columns_type):
    '''
    RDF2CoNLL function.
    Replace Old_ID with ID (plain numeration), add DEP and EDGE.
    '''
    self.define_columns(columns_type)
    command = self.CoNLLRDFFormatter_command() \
          + ['-conll'] \
          + self.columns
    (rdf_str, errors) = \
              self.run(command, stdin_str=rdf_str,
                       decode_stdout=False)
    return rdf_str

  def drop_columns(self, rdf_str, columns_type):
    '''
    CoNLL2RDF function plus drop extra columns.
    '''
    #print(rdf_str.decode('utf-8'))
    self.define_columns(columns_type)
    # !TODO!
    # REPLACE ['http://oracc.museum.upenn.edu/etcsri/'] by context!
    command = self.CoNLLStreamExtractor_command() \
              + ['http://oracc.museum.upenn.edu/etcsri/'] \
              + self.columns + ['-u'] \
              + self.load_requests(self.REQUEST_REMOVE_IGNORE)
    (rdf_str, errors) = \
              self.run(command, stdin_str=rdf_str, 
                       decode_stdout=False)
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

#---/ ROOT COMMANDS /----------------------------------------------------------
#

f_path = os.path.join(_path, 'data', 'etcsri-conll-all') #'cdli-conll'
sx = syntax_preannotation()
for f in os.listdir(f_path):
  try: 
    sx.preannotate(os.path.join(f_path, f))
  except Exception as e:
    #raise e
    pass

#CC2CU()
#CoNLL2RDF()
#syntax_preannotation()

##c = CoNLL2RDF()
##c.rdf2conll("data\conll-rdf\P100188.ttl")

    ## ***** TO DO *****
    ##  - check .sh scripts for missed steps
    ##  - columns should be adjusted for CDLI-CoNLL:
    ##    ID WORD MORPH2 POS IGNORE IGNORE IGNORE
    ##  - make sure columns are correctly designated for both formats
    ##  - make sure abbreviations are unified:
    ##    - either different rules for different abbreviations
    ##      OR
    ##    - better:
    ##      - apply your own abbr. unifier (lemmatization data scripts)
    ##        to make the data unified.
    ##      - then insure that the abbr. in SPARQL match
    ##  - Find a solution for rendering words in SPARQL.
    ##    Perhaps, FLASK templates would be the best solution also to corpus-specific
    ##    placeholders' rendering.

## FROM SYNTAX PREANNOTATION __INIT__

##    ### THE FOLLOWING LINES IN FUNCTION ARE TESTING ONLY:
##    #f_path = os.path.join(_path, 'data', 'cdli-conll', 'P100188.conll')
##    f_path = os.path.join(_path, 'data', 'cdli-conll', 'P100149.conll')
##    #f_path = os.path.join(_path, 'data', 'etcsri-conll', 'Q000937.conll')
##
##    etcsri = 'etcsri' in f_path
##    self.preannotate(f_path, ETCSRI=etcsri)

    #f_path = 'data/cdli-conll/P100188.conll' #os.path.join(_path, 'data', 'conll-rdf', 'P100188.ttl')
    #self.preannotate(f_path, ETCSRI=True)
    
##    self.graph = rdflib.Graph()
##
##  def preannotate(self, path):
##    self.graph.parse(path, format='n3')

## FROM SYNTAX PREANNOTATION preannotate()
 
    #self.dump(rdf_str, dump_path)
    #print(rdf_str)

##    command = self.CoNLLRDFFormatter_command() + ['-conll', 'ID'] \
##              + ['../data/'] + columns + ['DEP', 'EDGE']
##    conll_str = self.run(command, stdin_str=rdf_str, ETCSRI=ETCSRI)
##    print(conll_str)
##    self.dump_rdf(conll_str, f_path)

##  def conll2rdf(self, f_path):
##    '''
##    Run Java CoNNL2RDF script to convert CoNLL file to RDF.
##    '''
##    command = self.CoNLLStreamExtractor_command() + ['../data/'] \
##              + self.COLUMNS_CDLI_CONLL
##    rdf_str = "#new_text" + self.run(command, f_path).split("#new_text")[1]
##    self.dump_rdf(rdf_str, f_path)

## FROM ROOT

  ### THE FOLLOWING LINES IN FUNCTION ARE TESTING ONLY:

#CoNLL2RDF()

#f_path = os.path.join(_path, 'data', 'cdli-conll', 'P100188.conll')
#f_path = os.path.join(_path, 'data', 'cdli-conll', 'P100149.conll')
#f_path = os.path.join(_path, 'data', 'etcsri-conll', 'Q000937.conll')
#f_path = os.path.join(_path, 'data', 'cdli-conll', 'test.conll')

##    # test for unicode errors
##    for b in rdf_str.split(b'\n'):
##      try:
##        b.decode('utf-8')
##      except UnicodeDecodeError as e:
##        print('!!!!!!!', e, b)










