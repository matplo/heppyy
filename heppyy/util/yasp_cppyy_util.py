import yasp
import cppyy

class CPPYYwrapper(yasp.GenericObject):
	def __init__(self, cppyy, **kwargs):
		super(Yasp, self).__init__(**kwargs)
		print('[i] cppyy is', self.cppyy)

	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(SingletonClass, cls).__new__(cls)
		return cls.instance

	def cppyy_add_include_paths_files(files=[], *packages):
		dirs = yasp.yasp_find_files_dirnames_in_packages(files, packages)
		for d in dirs:	
			print(f'[heppyy-i] adding include path {d}')
			self.cppyy.add_include_path(f"{d}")

	def cppyy_add_paths(*packages):
		for pfix in yasp.features('prefix', *packages):
			_include_path = os.path.join(pfix, 'include')
			_lib_path = os.path.join(pfix, 'lib')
			_lib64_path = os.path.join(pfix, 'lib64')
			if os.path.isdir(_include_path):
				print('[heppyy-i] adding include path', _include_path)
				self.cppyy.add_include_path(_include_path)
			if os.path.isdir(_lib_path):
				print('[heppyy-i] adding library path', _lib_path)
				self.cppyy.add_library_path(_lib_path)
			if os.path.isdir(_lib64_path):
				print('[heppyy-i] adding library path', _lib64_path)
				self.cppyy.add_library_path(_lib64_path)
   
gycw = CPPYYWrapper(cppyy)
