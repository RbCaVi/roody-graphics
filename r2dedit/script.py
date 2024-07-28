# script

def parseexpr(expr):
	# fancy new algorithm

	s = expr

	tree = ['op', '_', 1]

	typ = 'val'

	s,token = parsetoken(typ, s)
	tokentype = token[0]
	if tokentype == 'val':
		addvaltotree(tree, token)
	return tree
