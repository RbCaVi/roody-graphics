import PIL
import PIL.Image

#welded=top,left,bottom,right
#rotate= 0    1    2      3

class NormalBlock:
	def __init__(self,file,offset=0):
		self.image=PIL.Image.open(f'blocks/{file}.png').crop((offset,0,offset+32,32)).convert('RGBA')

	def draw(self,welded,rotate=0,size=128):
		top,left,bottom,right=rotatewelded(welded,rotate)
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		for x,xside in [(0,left),(8,right)]:
			for y,yside in [(0,top),(8,bottom)]:
				im.alpha_composite(self.image.crop((x+16*xside,y+16*yside,x+16*xside+8,y+16*yside+8)),(x,y))
		im=rotateblock(im,rotate)
		return im.resize((size,size),PIL.Image.NEAREST)

def rotateblock(im,rotate):
	if rotate==0:
		return im
	if rotate==3:
		return im.transpose(PIL.Image.ROTATE_270)
	if rotate==1:
		return im.transpose(PIL.Image.TRANSPOSE)
	if rotate==2:
		return im.transpose(PIL.Image.FLIP_TOP_BOTTOM)

def rotatewelded(welded,rotate):
	if rotate==0:
		return welded
	if rotate==3:
		return [welded[i] for i in [3,0,1,2]]
	if rotate==1:
		return [welded[i] for i in [1,0,3,2]]
	if rotate==2:
		return [welded[i] for i in [2,1,0,3]]

class TwoSideBlock:
	def __init__(self,file,offset=0):
		self.image=PIL.Image.open(f'blocks/{file}.png').crop((offset,0,offset+32,32)).convert('RGBA')

	def draw(self,welded,rotate=0,size=128):
		if rotate==1:
			rotate=3
		if rotate==2:
			rotate=0
		top,left,bottom,right=rotatewelded(welded,rotate)
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		for x,xside in [(0,left),(8,right)]:
			for y,yside in [(0,top),(8,bottom)]:
				im.alpha_composite(self.image.crop((x+16*xside,y+16*yside,x+16*xside+8,y+16*yside+8)),(x,y))
		im=rotateblock(im,rotate)
		return im.resize((size,size),PIL.Image.NEAREST)

class NoWeldBlock:
	def __init__(self,file):
		self.image=PIL.Image.open(f'blocks/noweld/{file}.png').crop((0,0,16,16)).convert('RGBA')

	def draw(self,_,rotate=0,size=128):
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		im.alpha_composite(self.image.crop((0,0,16,16)))
		return im.resize((size,size),PIL.Image.NEAREST)

class WaferBlock:
	def __init__(self,file,base='wafer',offset=0):
		self.wafer=PIL.Image.open(f'blocks/{base}.png').crop((0,0,32,32)).convert('RGBA')
		self.image=PIL.Image.open(f'blocks/{base}/{file}.png').crop((offset,0,offset+32,32)).convert('RGBA')

	def draw(self,welded,rotate=0,size=128,offset=(0,0)):
		top,left,bottom,right=rotatewelded(welded,rotate)
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		for x,xside in [(0,left),(8,right)]:
			for y,yside in [(0,top),(8,bottom)]:
				im.alpha_composite(self.wafer.crop((x+16*xside,y+16*yside,x+16*xside+8,y+16*yside+8)),(x,y))
		im.alpha_composite(self.image.crop((16*offset[0],16*offset[1],16*(offset[0]+1),16*(offset[1]+1))).rotate(90*rotate))
		return im.resize((size,size),PIL.Image.NEAREST)

class PlatformBlock:
	def __init__(self):
		self.image=PIL.Image.open(f'blocks/platform.png').convert('RGBA')
		
	def draw(self,welded,_,size=128,offset=(0,0)):
		_,left,_,right=welded
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		y=0
		if left==0 and right==1 or left==1 and right==0:
			y=16
		for x,xside in [(0,left),(8,right)]:
			print(x,xside,(x+16*xside,0,x+16*xside+8,16))
			im.alpha_composite(self.image.crop((x+16*xside,y,x+16*xside+8,y+16)),(x,0))
		return im.resize((size,size),PIL.Image.NEAREST)

def normalize(block):
	if block is None:
		return {"type":'air',"rotate":0,"weld":'all'}
	if type(block)==str:
		return {"type":block,"rotate":0,"weld":"all"}
	if type(block) in [tuple,list]:
		out={"type":'air',"rotate":0,"weld":'all'}
		out.update(dict(zip(["type","rotate","weld"],block)))
		return out
	out={"type":'air',"rotate":0,"weld":'all'}
	out.update(block)
	return out

def get(vss,xi,yi):
	if xi<0 or yi<0 or yi>=len(vss):
		return normalize("air");
	vs=vss[yi]
	if(xi>=len(vs)):
		return normalize("air");
	return vs[xi]

wafertypes=["accelerometer","capacitor","diode","galvanometer","latch","matcher","potentiometer","sensor","transistor"]
wiretypes=["detector","port","toggler","trigger","wire"]
noweldtypes=["copper_ore","iron_ore","pulp","sand","silicon","spawner","telecross","air"]
twosidetypes=["wire_spool",'wood',"mirror"]

def canweld(side,block):
	if block['type'] in noweldtypes:
		return False
	elif block['type'] in ['cap','flower_magenta','flower_yellow','grass','motor','pedestal','spikes']:
		sides=[False,False,True,False]
	elif block['type'] in 'platform':
		sides=[True,False,False,False]
	elif block['type'] in ['actuator_head','wire_spool','telewall']:# no sides
		sides=[True,False,True,False]
	elif block['type'] in ['combiner','extractor','injector','platform']: # no top/bottom
		sides=[False,True,False,True]
	elif block['type'] in ['actuator_base','arc_furnace','beam_core','collector','creator','destroyer','dismantler','magnet','manipulator','mantler','teleportore']:#no top
		sides=[False,True,True,True]
	else:
		return True
	i={'top':0,'bottom':2,'left':1,'right':3}[side]+block['rotate']
	i=i%4
	return sides[i]


def makeimage(blocks,bsize=128,autoweld=True):
	xsize=max(map(len,blocks))
	ysize=len(blocks)

	newblocks=[[normalize("air") for _ in range(xsize)] for _ in range(ysize)]
	for yi,line in enumerate(blocks):
		for xi,block in enumerate(line):
			block=normalize(block)
			newblocks[yi][xi]=block

	im=PIL.Image.new('RGBA',(bsize*xsize,bsize*ysize),(0,0,0,0))
	for xi in range(xsize):
		for yi in range(ysize):
			block=get(newblocks,xi,yi)
			if block['type']=='air':
				continue
			if block['weld']=='all':
				block['weld']=[True,True,True,True]
			if autoweld:
				weldright=canweld('right',block) and get(newblocks,xi+1,yi)['type']!='air' and canweld('left',get(newblocks,xi+1,yi))
				weldleft=canweld('left',block) and get(newblocks,xi-1,yi)['type']!='air' and canweld('right',get(newblocks,xi-1,yi))
				weldbottom=canweld('bottom',block) and get(newblocks,xi,yi+1)['type']!='air' and canweld('top',get(newblocks,xi,yi+1))
				weldtop=canweld('top',block) and get(newblocks,xi,yi-1)['type']!='air' and canweld('bottom',get(newblocks,xi,yi-1))
				block['weld']=[[b and w,print(f'welded side {i} not allowed\n'*(not w),end='')][0] for i,b,w in zip(range(4),block['weld'],[weldtop,weldleft,weldbottom,weldright])]
			if block['type'] in wafertypes:
				b=WaferBlock(block['type'])
			elif block['type']=='wire_board':
				b=WaferBlock('wire','wafer')
			elif block['type'] in wiretypes:
				b=WaferBlock(block['type'],'frame')
			elif block['type'] in twosidetypes:
				b=TwoSideBlock(block['type'])
			elif block['type'] in noweldtypes:
				b=NoWeldBlock(block['type'])
			elif block['type']=='platform':
				block['weld'][1]=get(newblocks,xi-1,yi)['type']!='platform' and 2 or block['weld'][1]
				block['weld'][3]=get(newblocks,xi+1,yi)['type']!='platform' and 2 or block['weld'][3]
				b=PlatformBlock()
			else:
				b=NormalBlock(block['type'])
			bim=b.draw(block['weld'],block['rotate'],size=bsize)
			im.alpha_composite(bim,(xi*bsize,yi*bsize))
	return im

if __name__=='__main__':
	blocks=[
		['iron_bar',{"type":'wire_spool',"rotate":2,"weld":[False,False,True,False]}],
		['air','iron_bar'],
	]
	im=makeimage(blocks)
	im.show()
	im.save('recipe.png')

	blocks=[
		['cast_iron',{"type":'wire_spool',"rotate":2,"weld":[False,False,True,False]}],
		['cast_iron','cast_iron'],
	]
	#im=makeimage(blocks)
	#im.show()
	#im.save('frecipe.png')

	leftspool={"type":'wire_spool',"rotate":1,"weld":[False,False,False,True]}
	rightspool={"type":'wire_spool',"rotate":1,"weld":[False,True,False,False]}

	blocks=[
		[leftspool,'iron_bar',rightspool],
		[leftspool,'iron_bar',rightspool],
		[leftspool,'iron_bar',rightspool],
	]
	#im=makeimage(blocks)
	#im.show()
	#im.save('inductor.png')

	#im1=makeimage([['wire','glass']])
	#im2=makeimage([['wire_board','glass']])

	#im1.save('E.apng', duration=500, save_all=True, append_images=[im2],loop=0,disposal=0,blend=0)
	#im1.save('E.gif', duration=500, save_all=True, append_images=[im2],loop=0,disposal=2)

	#im=PIL.Image.open('E.apng')
	#im.show()