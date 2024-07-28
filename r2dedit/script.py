# script

import re
import typing

class TreeNode:
	parent: typing.Self | None
	children: list[typing.Self]
	data: Any

	def __init__(self, parent: typing.Self | None, children: list[typing.Self], data: Any):
		self.parent = parent
		self.children = children

def parseexpr(expr):
	# fancy new algorithm

	s = expr

	tree = TreeNode(None, [], ['op', '_', 1])
	bottom = tree

	nexttype = 'val'

	while True:
		if s.strip() == '':
			break
		s,token,nexttype = parsetoken(nexttype, s)
		tokentype = token[0]
		if tokentype == 'val':
			addvaltotree(bottom, token)
		if tokentype == 'op':
			addoptotree(bottom, token)
	return tree

def parsetoken(typ, s):
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
		opmatch = re.match('[+-]', s)
		if opmatch is not None:
			op = opmatch[0]
			return s[len(op):], TreeNode(None, [], ['op', op, 2]), 'val'
		raise ValueError('no match')
	raise ValueError('no match')

precedence = {
	('_', 1): 200,
	('+', 1): 10,
	('-', 1): 10,
}

def addvaltotree(bottom, val):
	assert len(bottom.children) < bottom.data[2]
	bottom.children.append(val)

def addoptotree(bottom, op):
	other = bottom.parent
	while goesabove(op, other):
		other = other.parent
	other.children.append(val)