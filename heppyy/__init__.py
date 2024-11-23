import sys
import os

from yasp import GenericObject

class HeppyySettings(GenericObject):
  def __init__(self, **kwargs):
    super(HeppyySettings, self).__init__(**kwargs)


heppyy_settings = HeppyySettings(path=os.path.dirname(os.path.abspath(__file__)))

import importlib
from yasp.cppyyhelper import YaspCppyyHelper

# make sure numpy is present in the include path
import numpy as np
# Find the NumPy include directory
numpy_include_dir = np.get_include()
import cppyy
# Add the NumPy include directory to cppyy
cppyy.add_include_path(numpy_include_dir)

def load_cppyy(name='heppyy', verbose=False, force=False):
  _split = name.split('.')
  if len(_split) == 1:
    sname = _split[0]
    snamespace = _split[0]
  if len(_split) == 2:
    sname = _split[0]
    snamespace = _split[1]
  if len(_split) > 2:
    sname = _split[0:-1]
    snamespace = _split[-1]  
  if snamespace is None:
    snamespace = sname
  symbol = YaspCppyyHelper().get(snamespace, verbose=verbose)
  if symbol is not None:
    if verbose:
      print('[i] Found symbol:', symbol)
    if force is True:
      print('[i] Reloading symbol:', symbol)
    else:
      return symbol
  # otherwise try to load the module / helper
  _loaded = False
  _errors = []
  try:
    mname = f'heppyy.util.{sname}_cppyy'
    # check if already loaded
    if mname in sys.modules:
      if verbose:
        print(f"[i] {mname} already loaded")
      pass
    else:
      importlib.import_module(mname)
      if verbose:
        print(f"[i] {mname} loaded with importlib")
      _loaded = True
  except ImportError as e:
    _errors.append(f"[e] util load try - {e}")
    _loaded = False
  if not _loaded:
    try:
      mname = f'{sname}'
      # check if already loaded
      if force is False and mname in sys.modules:
        if verbose:
          print(f"[i] {mname} already loaded")
        pass
      else:
        if verbose:
          print(f"[i] trying to load {mname} with importlib")
        importlib.import_module(mname)
        if verbose:
          print(f"[i] {mname} loaded with importlib")
        _loaded = True
    except ImportError as e:
      _errors.append(f"[e] direct load try - {e}")
      _loaded = False
  if not _loaded:
    if verbose:
      print('\n'.join(_errors))
  return YaspCppyyHelper().get(snamespace, verbose=verbose)
