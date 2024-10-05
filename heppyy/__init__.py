import sys
import os

from yasp import GenericObject

class HeppyySettings(GenericObject):
  def __init__(self, **kwargs):
    super(HeppyySettings, self).__init__(**kwargs)


heppyy_settings = HeppyySettings(path=os.path.dirname(os.path.abspath(__file__)))

import importlib
from yasp.cppyyhelper import YaspCppyyHelper

def load_cppyy(name='heppyy', verbose=False):
  _split = name.split('.')
  sname = _split[0]
  snamespace = _split[1] if len(_split) > 1 else None  
  if snamespace is None:
    snamespace = sname
  symbol = YaspCppyyHelper().get(snamespace, verbose=verbose)
  if symbol is not None:
    return symbol
  # otherwise try to load the module / helper
  try:
    mname = f'heppyy.util.{sname}_cppyy'
    # check if already loaded
    if mname in sys.modules:
      pass
    else:
      importlib.import_module(f'heppyy.util.{sname}_cppyy')
  except ImportError as e:
    print(f"[e] {e}")
    return None
  return YaspCppyyHelper().get(snamespace, verbose=verbose)
