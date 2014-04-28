
from rpython.tool.pairtype import extendabletype

# ====== Basic nodes ======

class A_Node(object):
	__metaclass__ = extendabletype

class A_Package(A_Node):
	def __init__(self):
		self.scope = None
		self.name = uninitialized_string
		self.importPath = uninitialized_string
		self.imports = {}
	
	def __repr__(self):
		return "<Package %s [%s]\nImporting: %r\nScope: %r>" % (self.name, self.importPath, self.imports, self.scope)

class A_Scope(A_Node):
	def __init__(self):
		self.funcs = {}
		self.types = {}
		self.vars = {}
	
	def __repr__(self):
		return "<Scope Funcs: %r\nTypes: %r\n Vars: %r>" % (self.funcs, self.types, self.vars)

# ====== Expression nodes ======

class A_Expr(A_Node):
	pass

illegal_expr = A_Expr()

class A_Block(A_Node):
	def __init__(self):
		self.scope = None
		self.stmts = []

illegal_block = A_Block()

class A_Func(A_Expr):
	def __init__(self):
		self.type = illegal_type
		self.body = illegal_block
	
class A_ConstIntExpr(A_Expr):
	def __init__(self):
		self.value = 0

class A_ConstUintExpr(A_Expr):
	def __init__(self):
		self.value = 0
	
class A_ConstFloatExpr(A_Expr):
	def __init__(self):
		self.value = 0.0
	
class A_ConstStringExpr(A_Expr):
	def __init__(self):
		self.value = ""
	
class A_ConstBoolExpr(A_Expr):
	def __init__(self):
		self.value = False
	
# These constants are shadowed from go-ast/ast-expr.go
Scope_Current = 1
Scope_Invalid = 0
Scope_Builtin = -1
Scope_ImportedPackage = -2
Scope_OwnPackage = -3
	
class A_IdentExpr(A_Expr):
	def __init__(self):
		self.homeScope = Scope_Invalid
		self.identifier = uninitialized_string
	
class A_UnaryExpr(A_Expr):
	def __init__(self):
		self.op = uninitialized_string
		self.expr = illegal_expr
	
class A_BinaryExpr(A_Expr):
	def __init__(self):
		self.op = uninitialized_string
		self.left = illegal_expr
		self.right = illegal_expr
	
class A_TypeAssertExpr(A_Expr):
	def __init__(self):
		self.type = illegal_type
		self.expr = illegal_expr
	
class A_IndexExpr(A_Expr):
	def __init__(self):
		self.index = illegal_expr
		self.expr = illegal_expr
	
class A_SelectorExpr(A_Expr):
	def __init__(self):
		self.selector = uninitialized_string
		self.expr = illegal_expr
	
class A_StarExpr(A_Expr):
	def __init__(self):
		self.expr = illegal_expr
	
class A_KeyValueExpr(A_Expr):
	def __init__(self):
		self.constKey = None
		self.identKey = None
		self.value = illegal_expr
	
class A_EllipsisExpr(A_Expr):
	def __init__(self):
		self.expr = illegal_expr
	
class A_CallExpr(A_Expr):
	def __init__(self):
		self.func = illegal_expr
		self.args = []
	
class A_SliceExpr(A_Expr):
	def __init__(self):
		self.sliced = illegal_expr
		self.isSlice3 = False
		self.low = None
		self.high = None
		self.max = None
	
class A_CompositeLiteralExpr(A_Expr):
	def __init__(self):
		self.type = illegal_type
		self.elements = []
	
class A_BlankIdentExpr(A_Expr):
	def __init__(self):
		pass

# ====== Type nodes ======

class A_Type(A_Expr):
	pass

illegal_type = A_Type()
uninitialized_string = "<not initialized>"

class A_BasicType(A_Type):
	def __init__(self):
		self.basic = uninitialized_string
		
class A_PointerType(A_Type):
	def __init__(self):
		self.underlying = illegal_type
	
class A_NamedType(A_Type):
	def __init__(self):
		self.underlying = illegal_type
	
class A_ImportedType(A_Type):
	def __init__(self):
		self.name = uninitialized_string
		self.package = uninitialized_string
	
class A_SliceType(A_Type):
	def __init__(self):
		self.underlying = illegal_type
	
class A_ArrayType(A_Type):
	def __init__(self):
		self.underlying = illegal_type
		self.size = 0
	
class A_MapType(A_Type):
	def __init__(self):
		self.key = illegal_type
		self.value = illegal_type
	
class A_ChannelType(A_Type):
	def __init__(self):
		self.element = illegal_type
		self.isSend = False
		self.isReceive = False
		
class A_TypeAndName(A_Node):
	# This is just a helper class to hold data
	def __init__(self):
		self.name = uninitialized_string
		self.type = illegal_type

class A_StructTypeField(A_TypeAndName):
	# This is just a helper class to hold data
	def __init__(self):
		A_TypeAndName.__init__(self)
		self.tag = uninitialized_string

class A_StructType(A_Type):
	def __init__(self):
		self.fields = []

class A_FuncType(A_Type):
	def __init__(self):
		self.args = []
		self.ret = []
		self.recv = illegal_type
		self.isVariadic = False
	
class A_InterfaceType(A_Type):
	def __init__(self):
		self.fields = []

# ====== Statement nodes ======

class A_Stmt(A_Node):
	pass

illegal_stmt = A_Stmt()

class A_EmptyStmt(A_Stmt):
	def __init__(self):
		pass

class A_AssignmentStmt(A_Stmt):
	def __init__(self):
		self.rhs = illegal_expr
		self.lhs = [illegal_expr]

class A_MultipleStmt(A_Stmt):
	def __init__(self):
		self.stmts = []

class A_BranchStmt(A_Stmt):
	def __init__(self):
		self.type = uninitialized_string
		self.label = None

class A_LabeledStmt(A_Stmt):
	def __init__(self):
		self.label = uninitialized_string
		self.stmt = illegal_stmt

class A_BlockStmt(A_Stmt):
	def __init__(self):
		self.block = illegal_block

class A_CaseStmt(A_Stmt):
	def __init__(self):
		self.body = illegal_block
		self.cases = [illegal_expr]

class A_ExprStmt(A_Stmt):
	def __init__(self):
		self.expr = illegal_expr
		
class A_ReturnStmt(A_Stmt):
	def __init__(self):
		self.values = []
		
class A_DecStmt(A_Stmt):
	def __init__(self):
		self.expr = illegal_expr
		
class A_IncStmt(A_Stmt):
	def __init__(self):
		self.expr = illegal_expr
		
class A_IfStmt(A_Stmt):
	def __init__(self):
		self.init = None
		self.els = None
		self.cond = illegal_expr
		self.body = illegal_block
		
class A_ForStmt(A_Stmt):
	def __init__(self):
		self.init = None
		self.cond = None
		self.post = None
		self.body = illegal_block
		
class A_ForRangeStmt(A_Stmt):
	def __init__(self):
		self.body = illegal_block
		self.expr = illegal_expr
		self.key = None
		self.value = None
		
class A_DeferStmt(A_Stmt):
	def __init__(self):
		# This is not optional, but we want to only have CallExprs or None here.
		self.expr = None
		
class A_SwitchStmt(A_Stmt):
	def __init__(self):
		self.init = None
		self.cases = []
		self.tag = illegal_expr
		
class A_TypeSwitchStmt(A_Stmt):
	def __init__(self):
		self.init = None
		self.assignedTo = None
		self.expr = illegal_expr
		self.cases = []
		
class A_GoStmt(A_Stmt):
	def __init__(self):
		# This is not optional, but we want to only have CallExprs or None here.
		self.expr = None
		
class A_SendStmt(A_Stmt):
	def __init__(self):
		self.chan = illegal_expr
		self.value = illegal_expr
		
class A_SelectStmt(A_Stmt):
	def __init__(self):
		self.cases = []
		
class A_SelectCaseStmt(A_Stmt):
	def __init__(self):
		self.comm = illegal_stmt
		self.body = illegal_block
