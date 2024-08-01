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

	nexttypes = ('val',)

	while True:
		#print(s)
		#print(nexttypes)
		#print(tree)
		if s.strip() == '':
			break
		#print()
		snext,token,nexttypes = parsetoken(nexttypes, s)
		if token is None:
			break
		tokentype = token.data[0]
		if tokentype == 'val':
			addvaltotree(bottom, token)
			bottom = token
		if tokentype == 'op':
			addoptotree(bottom, token)
			bottom = token
		if tokentype == 'paren':
			try:
				addparentotree(bottom, token)
			except:
				break
			bottom = token
		if tokentype == 'comma':
			addoptotree(bottom, token)
			bottom = token
		s = snext
	return tree, s

def parsetoken(types, s: str):
	sorig = s
	s = s.strip()
	if 'val' in types:
		opmatch = re.match('[([+-]', s)
		if opmatch is not None:
			op = opmatch[0]
			return s[len(op):], TreeNode(None, [], ['op', op, 1]), ('val',)
		symbolmatch = re.match('[a-zA-Z_][a-zA-Z_0-9]*', s)
		if symbolmatch is not None:
			symbol = symbolmatch[0]
			return s[len(symbol):], TreeNode(None, [], ('val', symbol)), ('op', 'cparen')
	if 'op' in types:
		opmatch = re.match('[+\\-*/]', s)
		if opmatch is not None:
			op = opmatch[0]
			return s[len(op):], TreeNode(None, [], ['op', op, 2]), ('val',)
		commamatch = re.match('[,]', s)
		if commamatch is not None:
			comma = commamatch[0]
			return s[len(comma):], TreeNode(None, [], ['comma', comma, 2]), ('val', 'cparen')
		opparenmatch = re.match('[([]', s)
		if opparenmatch is not None:
			opparen = opparenmatch[0]
			return s[len(opparen):], TreeNode(None, [], ['op', '_' + opparen, 2]), ('val',)
	if 'cparen' in types:
		cparenmatch = re.match('[])]', s)
		if cparenmatch is not None:
			cparen = cparenmatch[0]
			return s[len(cparen):], TreeNode(None, [], ('paren', cparen)), ('op', 'cparen')
	return sorig, None, None
	raise ValueError('no match')

# high number = bind loose
precedence = {
	('_', 1): 200,
	('[', 1): 100,
	('(', 1): 100,
	('_(', 2): 100,
	('_[', 2): 100,
	(',', 2): 90,
	('+', 2): 20,
	('-', 2): 20,
	('*', 2): 10,
	('/', 2): 10,
	('+', 1): 5,
	('-', 1): 5,
}

insertprecedence = {
	**precedence,
	('(', 1): 5,
	('[', 1): 5,
	('_(', 2): 5,
	('_[', 2): 5,
}

prefixness = {
	('+', 1): True,
	('-', 1): True,
	('(', 1): True,
	('[', 1): True,
	('_(', 2): False,
	('_[', 2): False,
	(',', 2): False,
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
	if highopkey not in precedence:
		return True
	if insertprecedence[opkey] > precedence[highopkey]:
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

def addcommatotree(bottom, comma) -> None:
	other = bottom
	while goesabove(comma, other):
		other = other.parent
	comma.parent = other
	lastchild = other.children[-1]
	lastchild.parent = comma
	other.children[-1] = comma
	comma.children.append(lastchild)

parens = {
	('(', 1): ')',
	('[', 1): ']',
	('_(', 2): ')',
	('_[', 2): ']',
}

def unmatched(paren, match):
	if match.data[0] == 'val':
		return True
	_,parenname = paren.data
	parenkey = parenname
	_,matchname,matcharity = match.data
	matchkey = matchname, matcharity
	if matchkey not in parens:
		return True
	if parens[matchkey] == parenkey:
		return False
	return True

parenmatches = {
	(('(', 1), ')'): ('op', '()', 1),
	(('[', 1), ']'): ('op', '[]', 1),
	(('_(', 2), ')'): ('op', '_()', 2),
	(('_[', 2), ']'): ('op', '_[]', 2),
}

def closeparen(paren, match):
	_,parenname = paren.data
	parenkey = parenname
	_,matchname,matcharity = match.data
	matchkey = matchname, matcharity
	return parenmatches[(matchkey, parenkey)]

def addparentotree(bottom, paren) -> None:
	other = bottom
	while unmatched(paren, other):
		other = other.parent
	paren.parent = other.parent
	i = paren.parent.children.index(other)
	paren.parent.children[i] = paren
	paren.children = other.children
	paren.data = closeparen(paren, other)

def parseidx(s):
	t,s = chain(
		string('['),
		parseexpr,
		string(']'),
	)(s)
	if t is None:
		return None, s
	_lbr,e,_rbr = t
	return e, s

def parseset(line):
	t,s = chain(
		parsesym,
		many(parseidx),
		string('='),
		parseexpr,
	)(line)
	if t is None:
		return None, s
	var,idxs,_eq,e = t
	return ('set', var, idxs, e), s

def chain(*ps):
	def parsechain(s):
		sp = s
		out = []
		for p in ps:
			t,sp = p(sp)
			if t is None:
				return None, s
			out.append(t)
		return out, sp
	return parsechain

def many(p):
	def parsemany(s):
		sp = s
		out = []
		while True:
			t,sp = p(sp)
			if t is None:
				return out, sp
			out.append(t)
	return parsemany

def string(pat):
	def parsestring(s):
		sp = s.strip()
		if sp.startswith(pat):
			return pat, sp[len(pat):]
		return None, s
	return parsestring

def regex(reg):
	def parseregex(s):
		sp = s.strip()
		match = re.match(reg, sp)
		if match is not None:
			return match[0], sp[len(match[0]):]
		return None, s
	return parseregex

def parsesym(s):
	return regex('[a-zA-Z_][a-zA-Z_0-9]*')(s)

def parsecode(code):
	t,s = many(choose(
		parseset,
	))(code)
	if t is None:
		return None, s
	return t, s

def choose(*ps):
	def parsechoose(s):
		for p in ps:
			t,sp = p(s)
			if t is not None:
				return t, sp
		return None, s
	return parsechoose