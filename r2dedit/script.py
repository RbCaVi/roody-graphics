# script

import re
import typing
import itertools
import functools

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
		snext,token,nexttypes = parsetoken(nexttypes, s)
		if token is None:
			break
		#print()
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
	s = strip(s)
	if 'val' in types:
		opmatch = re.match('[+-]', s)
		if opmatch is not None:
			op = opmatch[0]
			return s[len(op):], TreeNode(None, [], ['op', op, 1]), ('val',)
		openparenmatch = re.match('[([]', s)
		if openparenmatch is not None:
			openparen = openparenmatch[0]
			return s[len(openparen):], TreeNode(None, [], ['op', openparen, 1]), ('val', 'cparen')
		symbolmatch = re.match('[a-zA-Z_][a-zA-Z_0-9]*', s)
		if symbolmatch is not None:
			symbol = symbolmatch[0]
			return s[len(symbol):], TreeNode(None, [], ('val', 'var', symbol)), ('op', 'cparen')
		nummatch = re.match('[0-9]+', s)
		if nummatch is not None:
			num = nummatch[0]
			return s[len(num):], TreeNode(None, [], ('val', 'int', int(num))), ('op', 'cparen')
	if 'op' in types:
		opmatch = re.match('><|==|!=|>=|<=|<|>|[+\\-*/]', s)
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
	('>', 2): 2,
	('<', 2): 2,
	('>=', 2): 2,
	('<=', 2): 2,
	('==', 2): 2,
	('!=', 2): 2,
	('<>', 2): 2,
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
	('>', 2): False,
	('<', 2): False,
	('>=', 2): False,
	('<=', 2): False,
	('==', 2): False,
	('!=', 2): False,
	('<>', 2): False,
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
		sp = strip(s)
		if sp.startswith(pat):
			return pat, sp[len(pat):]
		return None, s
	return parsestring

def regex(reg):
	def parseregex(s):
		sp = strip(s)
		match = re.match(reg, sp)
		if match is not None:
			return match[0], sp[len(match[0]):]
		return None, s
	return parseregex

def parsesym(s):
	return regex('[a-zA-Z_][a-zA-Z_0-9]*')(s)

def parsecode(code):
	t,s = many(parsestmt)(code)
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

def strip(s):
	return s.strip()

def geti(x, i):
	return x[i]

def seti(v, xi):
	x,i = xi
	x[i] = v
	return x

def execute(code, scope = None):
	if scope is None:
		scope = {}
	for stmt in code:
		if stmt[0] == 'set':
			_set,var,idxs,e = stmt
			idxs = [evalexpr(idx, scope) for idx in idxs]
			val = evalexpr(e, scope)
			stack = itertools.accumulate(idxs, geti, initial = scope.get(var))
			scope[var] = functools.reduce(seti, reversed(list(zip(stack, idxs))), val)
		if stmt[0] == 'if':
			_if,cond,code = stmt
			if evalexpr(cond, scope):
			  execute(code, scope)
		if stmt[0] == 'for':
			_for,var,start,end,code = stmt
			assert end is not None
			startval = evalexpr(start, scope)
			endval = evalexpr(end, scope)
			for i in range(startval, endval + 1):
				scope[var] = i
				execute(code, scope)
		if stmt[0] == 'expr':
			_expr,e = stmt
			evalexpr(e, scope)
	return scope

def evalexpr(e, scope):
	if e.data[0] == 'op':
		_op,op,arity = e.data
		op = op,arity
		if op == ('_', 1):
			return evalexpr(e.children[0], scope)
		if op == ('()', 1):
			return evalexpr(e.children[0], scope)
		if op == ('-', 1):
			return -evalexpr(e.children[0], scope)
		if op == ('*', 2):
			return evalexpr(e.children[0], scope) * evalexpr(e.children[1], scope)
		if op == ('+', 2):
			return evalexpr(e.children[0], scope) + evalexpr(e.children[1], scope)
		if op == ('<', 2):
			return evalexpr(e.children[0], scope) < evalexpr(e.children[1], scope)
		if op == ('_[]', 2):
			return evalexpr(e.children[0], scope)[evalexpr(e.children[1], scope)]
		if op == ('[]', 1):
			if len(e.children) == 0:
				return []
			return [
				evalexpr(c, scope)
				for c in flattencomma(e.children[0])
			]
		if op == ('_()', 2):
			f,args = e.children
			return evalexpr(f, scope)(*[
				evalexpr(c, scope)
				for c in flattencomma(args)
			])
		print('what is this???', e)
		raise 0
	if e.data[0] == 'val':
		_val,typ,val = e.data
		if typ == 'int':
			return val
		if typ == 'var':
			return scope[val]
	print(e)
	raise 0

def manystopped(p, stop):
	def parsemanystopped(s):
		sp = s
		out = []
		while True:
			st,stp = stop(sp)
			if st is not None:
				return out, stp
			t,sp = p(sp)
			if t is None:
				return None, s
			out.append(t)
	return parsemanystopped

def parseif(s):
	t,s = chain(
		string('if'),
		parseexpr,
		string('then'),
		manystopped(
			parsestmt,
			string('endif')
		)
	)(s)
	if t is None:
		return None, s
	_if,cond,_then,code = t
	return ('if', cond, code), s

def parsestmt(s):
	t,s = choose(
		parseset,
		parseif,
		parsefor,
		parseemptystmt,
		parseparenstmt,
		parseexprstmt,
	)(s)
	if t is None:
		return None, s
	return t, s

def parsefor(s):
	t,s = chain(
		string('for'),
		parsesym,
		string('from'),
		parseexpr,
		optional(chain(
			string('to'),
			parseexpr
		), ('to', None)),
		string('do'),
		manystopped(
			parsestmt,
			string('endfor')
		)
	)(s)
	if t is None:
		return None, s
	_for,var,_from,start,(_to,end),_do,code = t
	return ('for', var, start, end, code), s

def optional(p, default):
	def parseoptional(s):
		t,sp = p(s)
		if t is None:
			return default, s
		return t, sp
	return parseoptional

def parseemptystmt(s):
	t,s = string(';')(s)
	if t is None:
		return None, s
	return ('empty',), s

def parseexprstmt(s):
	t,s = parseexpr(s)
	if t is None:
		return None, s
	if len(t.children) == 0:
		return None, s
	return ('expr', t), s

def parseparenstmt(s):
	t,s = chain(
		string('('),
		parsestmt,
		string(')')
	)(s)
	if t is None:
		return None, s
	_lpar,stmt,_rpar = t
	return stmt, s

def flattencomma(e):
	l = []
	c = e
	while c.data[0] == 'comma':
		l.append(c.children[0])
		if len(c.children) == 2:
			c = c.children[1]
		else:
			c = None
			break
	if c is not None:
		l.append(c)
	return l
