import os
import PIL
import PIL.Image
import sys

d=os.path.join(sys.argv[1],'images')
dots={}
for fname in os.listdir(d):
	try:
		x,y=map(int,fname.split('.')[0].split('_'))
		print((x,y) in dots)
		dots[(x,y)]=PIL.Image.open(os.path.join(d,fname))#.convert('RGBA')
	except ValueError:
		pass

minx=min(x for x,y in dots.keys())
maxx=max(x for x,y in dots.keys())
miny=min(y for x,y in dots.keys())
maxy=max(y for x,y in dots.keys())

im=PIL.Image.new('RGBA',((maxx-minx)*16*64,(maxy-miny)*16*64),(0,255,0))
for yi in range(maxy-miny+1):
	for xi in range(maxx-minx+1):
		x=minx+xi
		y=miny+yi
		chunk=dots.get((x,y))
		print(x,y)
		if chunk is not None:
			im.paste(chunk,(xi*16*64,yi*16*64))

im.save(os.path.join(d,'rendered.png'))