
import sys
from ast_load import from_string

def main():
	file = open(sys.argv[1])
	a = from_string(file.read())
	file.close()
	print "%r" % a

if __name__ == "__main__":
	main()
