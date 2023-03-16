#!/usr/bin/env python3

import cppyy
import yasp.cppyyhelper
import yasp
# import json - newer modules can output json with module list -j
import os

# there is a different way of doing this
# process files with cppyy-generator -> json file
# $ cppyy-generator <output_json_file> <header_file>
# find the object vtable in an .so with
# $nm <solib> --demangle --defined-only | grep vtable
#
# of just provide a "dictionary" -> class to lib to load OR header to lib to load

def get_list_of_modules():
	loaded = None
	y = yasp.dry_yasp_from_str()
	out, err, rc = y.exec_cmnd('modulecmd sh list -t', shell=False)
	if rc == 0:
		loaded = [m for m in err.decode('utf-8').split('\n')[1:] if len(m) > 0]
	else:
		print('[e] modulecmd failed - reverting to all known modules')
		y = yasp.dry_yasp_from_str()
		loaded = y.known_recipes
	return loaded

def figure_out_package_from_filename(fname, use_modules=True):
	lmodules = get_list_of_modules()
	print('- potential modules', lmodules)
	packs = None
	for m in lmodules:
		if len(m) < 1:
			continue
		y = yasp.dry_yasp_from_str(f'-r {m}')
		dirs = y.find_dirs_files(fname)
		if len(dirs):
			if packs is None:
				packs = []
			rv = yasp.GenericObject()
			rv.package = m
			rv.found_files = y.find_files(fname)
			rv.yasp = y
			packs.append(rv)
	return packs


def get_dirs_to_path(yaspObj, d2path):
	for l in [os.path.join(yaspObj.prefix, 'lib'), os.path.join(yaspObj.prefix, 'lib64')]:
		if l not in d2path:
			d2path.append(l)


def main():
	# fname = 'LundGenerator.hh'
	fname = 'ClusterSequence.hh'
	gos = figure_out_package_from_filename(fname)
	if gos is None:
		print(f'[e] not found {fname}')
		return
	_dirs_to_include = []
	_dirs_to_path = []
	_libs_to_load = []
	for g in gos:
		print(g.package, g.yasp.prefix, g.found_files)
		get_dirs_to_path(g.yasp, _dirs_to_path)
		for fn in g.found_files:
			_d = fn.replace(fname, '')
			if _d not in _dirs_to_include:
				_dirs_to_include.append(_d)
			_d = os.path.join(g.yasp.prefix, 'include')
			if _d not in _dirs_to_include:
				_dirs_to_include.append(_d)
			_libs = g.yasp.find_files('*.so')
			_libs.extend(g.yasp.find_files('*.dylib'))
			objname = os.path.splitext(os.path.basename(fn))[0]
			print(objname)
			for lib in _libs:
				_cmnd = f'nm {lib} --demangle --defined-only'
				out, err, rc = g.yasp.exec_cmnd(_cmnd, shell=False)
				_filtered = [l for l in out.decode('utf-8').split('\n') if f'{objname}::{objname}' in l if ' T ' in l]
				_filtered2 = [l for l in out.decode('utf-8').split('\n') if f'{objname}::' in l if ' T ' in l]
				if len(_filtered) == 0:
					# print (f'[w] {lib} not finding symbol - loosening the selection')
					if len(_filtered2) > 0:
						_filtered = _filtered2
				if len(_filtered) > 0:
					print('***', lib, _filtered)
					_lib = os.path.basename(os.path.realpath(lib)).split('.')[0].lstrip('lib')
					if _lib not in _libs_to_load:
						_libs_to_load.append(_lib)

	print(_dirs_to_include, _dirs_to_path, _libs_to_load)
	# yc = yasp.cppyyhelper.YaspCppyyHelper()

if __name__ == "__main__":
	main()
