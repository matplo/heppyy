import sys
import os

from yasp import GenericObject

class HeppyySettings(GenericObject):
	def __init__(self, **kwargs):
		super(HeppyySettings, self).__init__(**kwargs)


heppyy_settings = HeppyySettings(path=os.path.dirname(os.path.abspath(__file__)))
