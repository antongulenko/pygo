import ast
from json import loads

def from_string(str):
	json = loads(str)
	return from_json(json)

def from_json(json):
	return visit(ast.A_Package, json)

def visit(astClass, json):
	astObj = astClass()
	try:
		astObj.initialize_from(json)
	except KeyError, k:
		if json.is_object:
			raise ValueError("Missing slot %s, available slots: %s" % (k, json.value_object().keys()))
		raise
	return astObj

def visit_block(json):
	return visit(ast.A_Block, json)

expression_nodes = {
	# Types / type expressions
	"BasicType": ast.A_BasicType,
	"PointerType": ast.A_PointerType,
	"NamedType": ast.A_NamedType,
	"ImportedType": ast.A_ImportedType,
	"SliceType": ast.A_SliceType,
	"ArrayType": ast.A_ArrayType,
	"MapType": ast.A_MapType,
	"ChannelType": ast.A_ChannelType,
	"StructType": ast.A_StructType,
	"FuncType": ast.A_FuncType,
	"InterfaceType": ast.A_InterfaceType,
	
	# Regular expressions
	"ConstInt": ast.A_ConstIntExpr,
	"ConstUint": ast.A_ConstUintExpr,
	"ConstFloat": ast.A_ConstFloatExpr,
	"ConstString": ast.A_ConstStringExpr,
	"ConstBool": ast.A_ConstBoolExpr,
	"HomeScope": ast.A_IdentExpr,
	"BlankIdentifier": ast.A_BlankIdentExpr,
	"UnaryOp": ast.A_UnaryExpr,
	"BinaryOp": ast.A_BinaryExpr,
	"TypeAssert": ast.A_TypeAssertExpr,
	"Index": ast.A_IndexExpr,
	"Selector": ast.A_SelectorExpr,
	"SlicedExpr": ast.A_SliceExpr,
	"StarExpr": ast.A_StarExpr,
	"ConstKey": ast.A_KeyValueExpr, # KeyValueExpr has two possible indicator slots.
	"IdentKey": ast.A_KeyValueExpr, # 
	"Ellipsis": ast.A_EllipsisExpr,
	"CalledFunc": ast.A_CallExpr,
	"CompositeLiteral": ast.A_CompositeLiteralExpr,
	
	# Func expressions / func declarations
	"FuncBody": ast.A_Func
}

def visit_expr(json):
	obj = json.value_object()
	for key, astClass in expression_nodes.items():
		if key in obj:
			return visit(astClass, json)
	raise ValueError("Could not handle expr node with following keys: %s" % obj.keys())

def visit_type(json):
	# Types are just special expressions
	expr = visit_expr(json)
	assert isinstance(expr, ast.A_Type)
	return expr

stmt_nodes = {
	"Assignment": ast.A_AssignmentStmt,
	"Multiple": ast.A_MultipleStmt,
	"Branch": ast.A_BranchStmt,
	"Labeled": ast.A_LabeledStmt,
	"Block": ast.A_BlockStmt,
	"Case": ast.A_CaseStmt,
	"Expr": ast.A_ExprStmt,
	"Return": ast.A_ReturnStmt,
	"Dec": ast.A_DecStmt,
	"Inc": ast.A_IncStmt,
	"If": ast.A_IfStmt,
	"For": ast.A_ForStmt,
	"ForRange": ast.A_ForRangeStmt,
	"Defer": ast.A_DeferStmt,
	"Switch": ast.A_SwitchStmt,
	"TypeSwitch": ast.A_TypeSwitchStmt,
	"Go": ast.A_GoStmt,
	"Send": ast.A_SendStmt,
	"Select": ast.A_SelectStmt,
	"SelectCase": ast.A_SelectCaseStmt,
}

def visit_stmt(json):
	obj = json.value_object()
	if len(obj.keys()) == 0:
		return ast.A_EmptyStmt()
	elif len(obj.keys()) != 1:
		raise ValueError("Stmt nodes are supposed to have exactly one slot. Have: %s" % obj.keys())
	key = obj.keys()[0]
	if key in stmt_nodes:
		return visit(stmt_nodes[key], obj[key])
	else:
		raise ValueError("Could not handle stmt node with following keys: %s" % obj.keys())

# ====== Basic nodes ======

class __extend__(ast.A_Node):
	def initialize_from(self, json):
		raise NotImplementedError("Abstract, called on: %s" % self)

class __extend__(ast.A_Package):
	def initialize_from(self, json):
		jsonPackage = json.value_object()
		self.name = jsonPackage["PackageName"].value_string()
		self.importPath = jsonPackage["ImportPath"].value_string()
		self.imports = jsonPackage["Imports"].value_object() # Reuse the dict.
		self.scope = visit(ast.A_Scope, jsonPackage["Scope"])
	
class __extend__(ast.A_Scope):
	def initialize_from(self, json):
		jsonScope = json.value_object()
		if "Types" in jsonScope:
			for typeName, jsonType in jsonScope["Types"].value_object().items():
				self.types[typeName] = visit_type(jsonType)
		if "Funcs" in jsonScope:
			for funcName, jsonFunc in jsonScope["Funcs"].value_object().items():
				astFunc = visit_expr(jsonFunc)
				assert isinstance(astFunc, ast.A_Func)
				self.funcs[funcName] = astFunc
		if "Vars" in jsonScope:
			for jsonValue in jsonScope["Vars"].value_array():
				jsonVar = jsonValue.value_object()
				varName = jsonVar["Name"].value_string()
				if "Type" in jsonVar:
					type = visit_type(jsonVar["Type"])
				else:
					# This happens only for the target variable in type switch statements.
					type = None
				self.vars[varName] = type

class __extend__(ast.A_Block):
	def initialize_from(self, json):
		jsonBlock = json.value_object()
		self.scope = visit(ast.A_Scope, jsonBlock["Scope"])
		if "Stmts" in jsonBlock:
			for jsonStmt in jsonBlock["Stmts"].value_array():
				self.stmts.append(visit_stmt(jsonStmt))

# ====== Expression nodes ======

class __extend__(ast.A_Expr):
	def initialize_from(self, json):
		# All Expr nodes are based on json objects.
		self.initialize_from_obj(json.value_object())
	
	def initialize_from_obj(self, dict):
		raise NotImplementedError("Abstract, called on: %s" % self)

class __extend__(ast.A_Func):
	def initialize_from_obj(self, json):
		self.type = visit_type(json["Type"])
		self.body = visit_block(json["FuncBody"])

class __extend__(ast.A_ConstIntExpr):
	def initialize_from_obj(self, json):
		self.value = int(json["ConstInt"].value_int())

class __extend__(ast.A_ConstUintExpr):
	def initialize_from_obj(self, json):
		self.value = int(json["ConstUint"].value_int())
	
class __extend__(ast.A_ConstFloatExpr):
	def initialize_from_obj(self, json):
		self.value = json["ConstFloat"].value_float()
	
class __extend__(ast.A_ConstStringExpr):
	def initialize_from_obj(self, json):
		self.value = json["ConstString"].value_string()
	
class __extend__(ast.A_ConstBoolExpr):
	def initialize_from_obj(self, json):
		self.value = json["ConstBool"].value_bool()
	
class __extend__(ast.A_IdentExpr):
	def initialize_from_obj(self, json):
		self.identifier = json["Identifier"].value_string()
		self.homeScope = int(json["HomeScope"].value_int())
		
class __extend__(ast.A_UnaryExpr):
	def initialize_from_obj(self, json):
		self.op = json["UnaryOp"].value_string()
		self.expr = visit_expr(json["Expr"])
	
class __extend__(ast.A_BinaryExpr):
	def initialize_from_obj(self, json):
		self.op = json["BinaryOp"].value_string()
		self.left = visit_expr(json["Left"])
		self.right = visit_expr(json["Right"])
	
class __extend__(ast.A_TypeAssertExpr):
	def initialize_from_obj(self, json):
		self.type = visit_type(json["TypeAssert"])
		self.expr = visit_expr(json["Expr"])
	
class __extend__(ast.A_IndexExpr):
	def initialize_from_obj(self, json):
		self.index = visit_expr(json["Index"])
		self.expr = visit_expr(json["Expr"])
	
class __extend__(ast.A_SelectorExpr):
	def initialize_from_obj(self, json):
		self.selector = json["Selector"].value_string()
		self.expr = visit_expr(json["Expr"])
	
class __extend__(ast.A_StarExpr):
	def initialize_from_obj(self, json):
		self.expr = visit_expr(json["StarExpr"])
	
class __extend__(ast.A_KeyValueExpr):
	def initialize_from_obj(self, json):
		if "ConstKey" in json:
			self.constKey = visit_expr(json["ConstKey"])
		if "IdentKey" in json:
			self.identKey = json["IdentKey"].value_string()
		self.value = visit_expr(json["Value"])
		
class __extend__(ast.A_EllipsisExpr):
	def initialize_from_obj(self, json):
		self.expr = visit_expr(json["Expr"])
	
class __extend__(ast.A_CallExpr):
	def initialize_from_obj(self, json):
		self.func = visit_expr(json["CalledFunc"])
		if "Args" in json:
			for jsonArg in json["Args"].value_array():
				self.args.append(visit_expr(jsonArg))
	
class __extend__(ast.A_SliceExpr):
	def initialize_from_obj(self, json):
		self.sliced = visit_expr(json["SlicedExpr"])
		self.isSlice3 = json["Slice3"].value_bool()
		if "Low" in json:
			self.low = visit_expr(json["Low"])
		if "High" in json:
			self.high = visit_expr(json["High"])
		if "Max" in json:
			self.max = visit_expr(json["Max"])
	
class __extend__(ast.A_CompositeLiteralExpr):
	def initialize_from_obj(self, json):
		for elem in json["CompositeElements"].value_array():
			self.elements.append(visit_expr(elem))
		self.type = visit_type(json["Type"])
	
class __extend__(ast.A_BlankIdentExpr):
	def initialize_from_obj(self, json):
		pass

# ====== Type expressions ======

class __extend__(ast.A_BasicType):
	def initialize_from_obj(self, json):
		self.basic = json["BasicType"].value_string()
	
class __extend__(ast.A_PointerType):
	def initialize_from_obj(self, json):
		self.underlying = visit_type(json["PointerType"])
	
class __extend__(ast.A_NamedType):
	def initialize_from_obj(self, json):
		self.underlying = visit_expr(json["NamedType"])
		assert isinstance(self.underlying, ast.A_IdentExpr)
	
class __extend__(ast.A_ImportedType):
	def initialize_from_obj(self, json):
		jsonImportedType = json["ImportedType"].value_object()
		self.name = jsonImportedType["Name"].value_string()
		self.package = jsonImportedType["PackagePath"].value_string()
	
class __extend__(ast.A_SliceType):
	def initialize_from_obj(self, json):
		self.underlying = visit_type(json["SliceType"])
	
class __extend__(ast.A_ArrayType):
	def initialize_from_obj(self, json):
		jsonArrayType = json["ArrayType"].value_object()
		self.underlying = visit_type(jsonArrayType["Type"])
		self.size = int(jsonArrayType["Size"].value_int())
	
class __extend__(ast.A_MapType):
	def initialize_from_obj(self, json):
		jsonMapType = json["MapType"].value_object()
		self.key = visit_type(jsonMapType["Key"])
		self.value = visit_type(jsonMapType["Value"])
	
class __extend__(ast.A_ChannelType):
	def initialize_from_obj(self, json):
		jsonChannelType = json["ChannelType"].value_object()
		self.element = visit_type(jsonChannelType["ElementType"])
		self.isSend = jsonChannelType["IsSend"].value_bool()
		self.isReceive = jsonChannelType["IsReceive"].value_bool()

class __extend__(ast.A_TypeAndName):
	def initialize_from(self, json):
		self.name = json.value_object()["Name"].value_string()
		self.type = visit_type(json.value_object()["Type"])
	
class __extend__(ast.A_StructTypeField):
	def initialize_from(self, json):
		ast.A_TypeAndName.initialize_from(self, json)
		if "Tag" in json.value_object():
			self.tag = json.value_object()["Tag"].value_string()
	
class __extend__(ast.A_StructType):
	def initialize_from_obj(self, json):
		jsonStructType = json["StructType"].value_object()
		for jsonField in jsonStructType["Fields"].value_array():
			field = visit(ast.A_StructTypeField, jsonField)
			self.fields.append(field)
	
class __extend__(ast.A_FuncType):
	def initialize_from_obj(self, json):
		jsonFuncType = json["FuncType"].value_object()
		self.isVariadic = jsonFuncType["IsVariadic"].value_bool()
		if "Recv" in jsonFuncType:
			self.recv = visit(ast.A_TypeAndName, jsonFuncType["Recv"])
		if "Args" in jsonFuncType:
			for jsonArg in jsonFuncType["Args"].value_array():
				arg = visit(ast.A_TypeAndName, jsonArg)
				self.args.append(arg)
		if "Ret" in jsonFuncType:
			for jsonRet in jsonFuncType["Ret"].value_array():
				ret = visit(ast.A_TypeAndName, jsonRet)
				self.ret.append(ret)
	
class __extend__(ast.A_InterfaceType):
	def initialize_from_obj(self, json):
		jsonInterfaceType = json["InterfaceType"].value_object()
		if "Fields" in jsonInterfaceType:
			for jsonField in jsonInterfaceType["Fields"].value_array():
				field = visit(ast.A_TypeAndName, jsonField)
				self.fields.append(field)

# ====== Statement nodes ======

class __extend__(ast.A_AssignmentStmt):
	def initialize_from(self, json):
		jsonAssignStmt = json.value_object()
		self.rhs = visit_expr(jsonAssignStmt["Rhs"])
		for jsonLhs in jsonAssignStmt["Lhs"].value_array():
			self.lhs.append(visit_expr(jsonLhs))

class __extend__(ast.A_MultipleStmt):
	def initialize_from(self, json):
		for jsonStmt in json.value_array():
			self.stmts.append(visit_stmt(jsonStmt))

class __extend__(ast.A_BranchStmt):
	def initialize_from(self, json):
		jsonBranch = json.value_object()
		self.type = jsonBranch["Branch"].value_string()
		if "Label" in jsonBranch:
			self.label = jsonBranch["Label"].value_string()

class __extend__(ast.A_LabeledStmt):
	def initialize_from(self, json):
		jsonLabeled = json.value_object()
		self.label = jsonLabeled["Label"].value_string()
		self.stmt = visit_stmt(jsonLabeled["Stmt"])

class __extend__(ast.A_BlockStmt):
	def initialize_from(self, json):
		self.block = visit_block(json)

class __extend__(ast.A_CaseStmt):
	def initialize_from(self, json):
		jsonCase = json.value_object()
		self.body = visit_block(jsonCase["Body"])
		if "Cases" in jsonCase:
			for jsonCaseExpr in jsonCase["Cases"].value_array():
				self.cases.append(visit_expr(jsonCaseExpr))

class __extend__(ast.A_ExprStmt):
	def initialize_from(self, json):
		self.expr = visit_expr(json)
		
class __extend__(ast.A_ReturnStmt):
	def initialize_from(self, json):
		if "Value" in json.value_object():
			for jsonValue in json.value_object()["Value"].value_array():
				self.values.append(visit_expr(jsonValue))
		
class __extend__(ast.A_DecStmt):
	def initialize_from(self, json):
		self.expr = visit_expr(json)
		
class __extend__(ast.A_IncStmt):
	def initialize_from(self, json):
		self.expr = visit_expr(json)
		
class __extend__(ast.A_IfStmt):
	def initialize_from(self, json):
		jsonIf = json.value_object()
		if "Init" in jsonIf:
			self.init = visit_stmt(jsonIf["Init"])
		if "Else" in jsonIf:
			self.els = visit_stmt(jsonIf["Else"])
		self.cond = visit_expr(jsonIf["Cond"])
		self.body = visit_block(jsonIf["Body"])
		
class __extend__(ast.A_ForStmt):
	def initialize_from(self, json):
		jsonFor = json.value_object()
		if "Init" in jsonFor:
			self.init = visit_stmt(jsonFor["Init"])
		if "Cond" in jsonFor:
			self.cond = visit_expr(jsonFor["Cond"])
		if "Post" in jsonFor:
			self.post = visit_stmt(jsonFor["Post"])
		self.body = visit_block(jsonFor["Body"])
		
class __extend__(ast.A_ForRangeStmt):
	def initialize_from(self, json):
		jsonForRange = json.value_object()
		self.body = visit_block(jsonForRange["Body"])
		self.expr = visit_expr(jsonForRange["Expr"])
		if "Key" in jsonForRange:
			self.key = visit_expr(jsonForRange["Key"])
		if "Value" in jsonForRange:
			self.value = visit_expr(jsonForRange["Value"])
		
class __extend__(ast.A_DeferStmt):
	def initialize_from(self, json):
		self.expr = visit_expr(json)
		assert isinstance(self.expr, ast.A_CallExpr)

def visit_switch_cases(json, list):
	for jsonCase in json.value_array():
		list.append(visit(ast.A_CaseStmt, jsonCase))

class __extend__(ast.A_SwitchStmt):
	def initialize_from(self, json):
		jsonSwitch = json.value_object()
		visit_switch_cases(jsonSwitch["Body"], self.cases)
		if "Init" in jsonSwitch:
			self.init = visit_stmt(jsonSwitch["Init"])
		self.tag = visit_expr(jsonSwitch["Tag"])
		
class __extend__(ast.A_TypeSwitchStmt):
	def initialize_from(self, json):
		jsonTypeSwitch = json.value_object()
		self.expr = visit_expr(jsonTypeSwitch["Expr"])
		if "Init" in jsonTypeSwitch:
			self.Init = visit_stmt(jsonTypeSwitch["Init"])
		if "AssignedTo" in jsonTypeSwitch:
			self.assignedTo = jsonTypeSwitch["AssignedTo"].value_string()
		visit_switch_cases(jsonTypeSwitch["Body"], self.cases)
		
class __extend__(ast.A_GoStmt):
	def initialize_from(self, json):
		self.expr = visit_expr(json)
		assert isinstance(self.expr, ast.A_CallExpr)
	
class __extend__(ast.A_SendStmt):
	def initialize_from(self, json):
		jsonSend = json.value_object()
		self.chan = visit_expr(jsonSend["Chan"])
		self.value = visit_expr(jsonSend["Value"])
	
class __extend__(ast.A_SelectStmt):
	def initialize_from(self, json):
		jsonSelect = json.value_object()
		if "Body" in jsonSelect:
			for jsonCase in jsonSelect["Body"].value_array():
				self.cases.append(visit_stmt(jsonCase))
	
class __extend__(ast.A_SelectCaseStmt):
	def initialize_from(self, json):
		jsonCase = json.value_object()
		self.comm = visit_stmt(jsonCase["Comm"])
		self.body = visit_block(jsonCase["Body"])
	