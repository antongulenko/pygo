import .ast
from .json import loads

def from_string(str):
	json = loads(str)
	return from_json(json)

def from_json(json):
	return visit_package(json)

def visit_package(json):
	jsonPackage = json.value_object()
	package = ast.Package()
	package.Name = jsonPackage["PackageName"].value_string()
	package.ImportPath = jsonPackage["ImportPath"].value_string()
	package.Imports = jsonPackage["Imports"].value_object() # Reuse the dict.
	package.Scope = visit_scope(jsonPackage["Scope"])

def visit_scope(json):
	jsonScope = json.value_object()
	scope = ast.Scope()
	for typeName, jsonType = enumerate(jsonScope["Types"].value_object()):
		scope.types[typeName] = visit_type(jsonType)
	for funcName, jsonFunc = enumerate(jsonScope["Funcs"].value_object()):
		scope.funcs[funcName] = visit_func(jsonFunc)
	for jsonValue = enumerate(jsonScope["Vars"].value_array()):
		jsonVar = jsonValue.value_object()
		scope.types[typeName] = visit_type(jsonType)
	return scope

def visit_type(json):
	jsonType = json.value_object()
	if "BasicType" in jsonType:
		return BasicType(jsonType["BasicType"].value_string())
	elif "PointerType" in jsonType:
		return PointerType(visit_type(jsonType["PointerType"]))
	elif "NamedType" in jsonType:
		return NamedType(visit_identifier(jsonType["PointerType"]))
	elif "ImportedType" in jsonType:
		jsonImportedType = jsonType["ImportedType"].value_object()
		name = jsonImportedType["Name"].value_string()
		package = jsonImportedType["PackagePath"].value_string()
		return ImportedType(name, package)
	elif "SliceType" in jsonType:
		return SliceType(visit_type(jsonType["SliceType"]))
	elif "ArrayType" in jsonType:
		jsonArrayType = jsonType["ArrayType"].value_object()
		subtype = visit_type(jsonArrayType["Type"])
		size = int(jsonArrayType["Size"].value_float())
		return ArrayType(subtype, size)
	elif "MapType" in jsonType:
		jsonMapType = jsonType["MapType"].value_object()
		key = visit_type(jsonMapType["Key"])
		value = visit_type(jsonMapType["Value"])
		return MapType(key, value)
	elif "ChannelType" in jsonType:
		jsonChannelType = jsonType["ChannelType"].value_object()
		
		return ChannelType()
	elif "StructType" in jsonType:
	elif "FuncType" in jsonType:
	elif "InterfaceType" in jsonType:
	assert False, "Illegal Type node"

def visit_func(json):
	jsonFunc = json.value_object()
	func = ast.Type()
	# TODO
	return func

def visit_identifier(json):
	# TODO
