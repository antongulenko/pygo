
import sys
from ast_load import from_string
from targetpygo import run_main_package

# TODO - pass this as a parameter somehow.
jsonFile = "go-ast.json"
pkg = from_string(open(jsonFile).read())

def entry_point(argv):
	return run_main_package(pkg, argv[1:])

if __name__ == "__main__":
	entry_point(sys.argv)

def target(driver, *args):
	return entry_point, None
