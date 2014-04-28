
import sys, os
from ast_load import from_string
from rpython.rlib.streamio import open_file_as_stream
from rpython.rlib import rpath

def read_file(filename):
	path = rpath.rabspath(filename)
	try:
		file = open_file_as_stream(path, mode="rb", buffering=0)
		try:
			data = file.readall()
		finally:
			file.close()
	except OSError as e:
		os.write(2, "%s -- %s (LoadError)\n" % (os.strerror(e.errno), path))
		return ("", False)
	return (data, True)

def entry_point(argv):
	if len(argv) < 1:
		print "Need at least 1 parameter: json file to interpret."
		return 1
	json, ok = read_file(argv[1])
	if not ok:
		return 1
	pkg = from_string(json)
	return run_main_package(pkg, argv[2:])

def run_main_package(pkg, args):
	# TODO invoke ast-interpreter
	print "%s" % pkg
	return 0
	
if __name__ == "__main__":
	entry_point(sys.argv)

def target(driver, *args):
	return entry_point, None
