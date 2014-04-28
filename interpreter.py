


class Interpreter(object):
	MainFuncName = "main"
	
	def __init__(self, space, mainPkg):
		self.space = space
		self.mainPkg = mainPkg
	
	def interpret_main(self, args):
		funcs = self.mainPkg.scope.funcs
		if self.MainFuncName not in funcs:
			raise InterpreterError("Function %s not found in main package!" % self.MainFuncName)
		mainFunc = funcs[self.MainFuncName]
		w_args = [self.space.wrap_str(str) for str in args]
		return self.call_func(mainFunc, w_args)
	
	def call_func(self, func, args):
		print "Entering func. Args: %s" % args
		# TODO

class InterpreterError(Exception):
	pass
