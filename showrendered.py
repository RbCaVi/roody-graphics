import os
import sys

d=sys.argv[1]
dots={}
for fname in os.listdir(d):
	try:
		x,y=map(int,fname.split('.')[0].split('_'))
		dots[(x,y)]=True
	except ValueError as e:
		print(e)
		pass

minx=min(x for x,y in dots.keys())
maxx=max(x for x,y in dots.keys())
miny=min(y for x,y in dots.keys())
maxy=max(y for x,y in dots.keys())

grid=' '*-minx+' 0\n'
for yi in range(maxy-miny+1):
	line='0' if miny+yi==0 else ' '
	for xi in range(maxx-minx+1):
		x=minx+xi
		y=miny+yi
		line+='#' if dots.get((x,y)) else ' '
	grid+=line+'\n'

print(grid)