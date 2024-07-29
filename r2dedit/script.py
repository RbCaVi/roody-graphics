# script

import re
import typing

class TreeNode:
	parent: typing.Self | None
	children: list[typing.Self]
	data: typing.Any

	def __init__(self, parent: typing.Self | None, children: list[typing.Self], data: typing.Any):
		self.parent = parent
		self.children = children
		self.data = data

	def __repr__(self):
		s = str(self.data)
		s = '\n\t'.join([s] + [line for child in self.children for line in repr(child).split('\n')])
		return s

def parseexpr(expr: str) -> typing.Any:
	# fancy new algorithm

	s = expr

	tree = TreeNode(None, [], ['op', '_', 1])
	bottom = tree

	nexttype = 'val'

	while True:
		if s.strip() == '':
			break
		s,token,nexttype = parsetoken(nexttype, s)
		tokentype = token.data[0]
		if tokentype == 'val':
			addvaltotree(bottom, token)
			bottom = token
		if tokentype == 'op':
			addoptotree(bottom, token)
			bottom = token
	return tree

def parsetoken(typ, s: str):
	s = s.strip()
	if typ == 'val':
		opmatch = re.match('[+-]', s)
		if opmatch is not None:
			op = opmatch[0]
			return s[len(op):], TreeNode(None, [], ['op', op, 1]), 'val'
		symbolmatch = re.match('[a-zA-Z_][a-zA-Z_0-9]*', s)
		if symbolmatch is not None:
			symbol = symbolmatch[0]
			return s[len(symbol):], TreeNode(None, [], ('val', symbol)), 'op'
		raise ValueError('no match')
	if typ == 'op':
		opmatch = re.match('[+\\-*/]', s)
		if opmatch is not None:
			op = opmatch[0]
			return s[len(op):], TreeNode(None, [], ['op', op, 2]), 'val'
		raise ValueError('no match')
	raise ValueError('no match')

# high number = bind loose
precedence = {
	('_', 1): 200,
	('+', 2): 20,
	('-', 2): 20,
	('*', 2): 10,
	('/', 2): 10,
	('+', 1): 5,
	('-', 1): 5,
}

prefixness = {
	('+', 1): True,
	('-', 1): True,
	('+', 2): False,
	('-', 2): False,
	('*', 2): False,
	('/', 2): False,
}

def addvaltotree(bottom, val) -> None:
	assert len(bottom.children) < bottom.data[2]
	bottom.children.append(val)
	val.parent = bottom

def goesabove(op, highop) -> bool:
	if highop.data[0] == 'val':
		return True
	_,opname,arity = op.data
	opkey = opname, arity
	_,highopname,higharity = highop.data
	highopkey = highopname, higharity
	if precedence[opkey] > precedence[highopkey]:
		return True
	return False

def isprefix(op) -> bool:
	_,opname,arity = op.data
	opkey = opname, arity
	return prefixness[opkey]

def addoptotree(bottom, op) -> None:
	other = bottom
	while goesabove(op, other):
		other = other.parent
	op.parent = other
	if not isprefix(op):
		lastchild = other.children[-1]
		lastchild.parent = op
		other.children[-1] = op
		op.children.append(lastchild)
	else:
		other.children.append(op)