import PIL.Image, PIL.ImageChops
import smp as smp
import os
from lang import cfgstr
import functools
import collections
import re
import typing
import numpy as np
from assetload import blockinfos, assetinit, idtoblock
import pygame
#import frozendict
import time

class Timer:
    #start

    def __init__(self, s):
        self.s = s

    def __enter__(self):
        self.start = time.time()
        #print(f'{self.s}: start at {self.start}')

    def __exit__(self, exc_type, exc, exc_tb):
        if exc is not None:
            return False
        t = time.time()
        #print(f'{self.s}: ended at {t}')
        #print(f'{self.s}: {t - self.start} seconds')

assetinit()

rimlights:dict[int, np.ndarray] = {}

vec3:typing.TypeAlias = tuple[float, float, float]

def convertim(im: PIL.Image.Image) -> pygame.Surface:
    return pygame.image.fromstring(im.tobytes(), im.size, typing.cast(typing.Any,im.mode)).convert_alpha()

def clamp(a:np.ndarray) -> np.ndarray:
	return np.fmin(np.fmax(a, 0.0), 1.0) # overflow error

def dot(normal:np.ndarray, light:vec3) -> np.ndarray:
	return np.einsum('ijk,k->ij',normal,light)

def diffuse(normal:np.ndarray, light:vec3) -> np.ndarray:
	return np.fmax(dot(normal, light), 0.0)

def quarter_rotate(v:vec3, r:int) -> vec3:
	match r:
		case 0:
			return v
		case 1:
			return (-v[1], v[0], v[2])
		case 2:
			return (-v[0], -v[1], v[2])
		case 3:
			return (v[1], -v[0], v[2])
	raise ValueError('bad rotate')

def calc_diffuse_ambient_light(lightdir:vec3, normal:np.ndarray) -> np.ndarray:
	# calculate diffuse light
	light_diffuse = diffuse(normal, lightdir)
	return light_diffuse * 0.5 + 0.5

def calc_highlights(lightdir:vec3, normal:np.ndarray, rimlight:np.ndarray) -> np.ndarray:
	lightdir2 = (lightdir[0], lightdir[1], 0)
	intensity:np.ndarray = dot(normal, lightdir2) # how much the normal faces toward the light
	s0,s1 = intensity.shape
	highlights = np.empty((s0,s1,3))
	for i in range(s0):
		for j in range(s1):
			pixel = rimlight[int(255 * clamp((intensity[i, j] + 1) / 2))]
			highlights[i, j] = tuple(c * 0.3 for c in pixel)
	return highlights

fullbright_lightdir = (-0.5, 1.0, 1.0)

os.makedirs('cache/normalmapped', exist_ok = True)

normalmap_cache: list[None | pygame.Surface] = [None] * 8 * 256

def apply_normalmap(block_id:int, rotation:int, flip:bool) -> pygame.Surface:
	i = block_id * 8 + rotation * 2 + flip
	im = normalmap_cache[i]
	if im is None:
		f = os.path.join('cache/normalmapped',f'nmapped_{block_id}_{rotation}_{flip}.png')
		try:
			if pygame.image.get_extended():
				im = pygame.image.load(f)
			else:
				im = convertim(PIL.Image.open(f))
		except FileNotFoundError:
			# rotate the light so when the block is rotated back the light is in the right direction
			lightdir:vec3 = quarter_rotate(fullbright_lightdir, rotation);

			light:np.ndarray

			normal_array:np.ndarray

			albedo = getalbedo(block_id)
			normal = getnormal(block_id)

			if normal is None:
				s0,s1 = albedo.size
				normal_array = np.full((s1,s0,3),(0,0,1))
			else:
				normal_array = np.asarray(normal) / 255 * 2 - 1
				normal_array = normal_array / np.atleast_3d(np.linalg.norm(normal_array, axis = 2))
				normal_array = normal_array[:, :, :3]
				# shape (any, any, 3)

			if flip: # flip_uv_x
				normal_array[:, :, 0] = -normal_array[:, :, 0]

			normal_array[:, :, 1] = -normal_array[:, :, 1]

			light = calc_diffuse_ambient_light(lightdir, normal_array)
			light = np.array([light, light, light])
			light = np.moveaxis(light, 0, 2)
			light = clamp(light)
			light = light * 255
			light = light.astype('uint8')
			lightim:PIL.Image.Image = PIL.Image.fromarray(light)

			alpha:PIL.Image.Image = albedo.getchannel('A')
			color:PIL.Image.Image = albedo.convert('RGB')
			diffused:PIL.Image.Image = PIL.ImageChops.multiply(color, lightim)
			out:PIL.Image.Image = diffused

			if block_id in rimlights:
				highlights:np.ndarray = calc_highlights(lightdir, normal_array, rimlights[block_id]);
				highlights = clamp(highlights)
				highlights = highlights.astype('uint8')
				highlightsim:PIL.Image.Image = PIL.Image.fromarray(highlights)
				out = PIL.ImageChops.add(out,highlightsim)
			
			out.putalpha(alpha)

			im = convertim(out)
			pygame.image.save(im, f)
		normalmap_cache[i] = im
	return im

#welded=top,left,bottom,right
#rotate= 0    1    2      3

class WeldSide(typing.TypedDict):
	weld:bool
	wire:bool
	platform:bool
	frame:bool

WeldSides: typing.TypeAlias = tuple[WeldSide,WeldSide,WeldSide,WeldSide]
WeldSideIn: typing.TypeAlias = WeldSide | bool
WeldSidesIn: typing.TypeAlias = tuple[WeldSideIn,WeldSideIn,WeldSideIn,WeldSideIn]

ImageBit: typing.TypeAlias = tuple[int,int,int,int,bool,int,int]

def imagebit(block:int | ImageBit,x:int=0,y:int=0,w:int=16,h:int=16) -> ImageBit:
	# the dimensions of the part of the image to use
	if isinstance(block,tuple):
		# gonna just assume x,y,w,h stays inside the image
		x += block[0]
		y += block[1]
		block = block[6]
	block_id = block
	# rotation
	flip = False # first
	rotation = 0 # second
	return (x, y, w, h, flip, rotation, block_id)

def rotateib(ib:ImageBit, r:int, flip:bool=False) -> ImageBit:
	x,y,w,h,flip,rotation,block_id = ib
	if flip:
		rotation = -rotation % 4
		flip = not flip
	rotation += r
	return (x, y, w, h, flip, rotation, block_id)

def getim(ib:ImageBit) -> pygame.Surface:
	x,y,w,h,flip,rotation,block_id = ib
	im = apply_normalmap(block_id, rotation, flip)
	try:
		im = im.subsurface((x, y, w, h))
	except:
		print(block_id, rotation, flip, x, y, w, h)
		raise
	# i have to calculate the diffuse and "rimlight"
	# self.flip = flip_uv_x
	# self.rotate = either rotation or (3 - rotation)
	if flip:
		im = pygame.transform.flip(im, True, False)
	match rotation:
		case 1:
			im = pygame.transform.rotate(im,270)
		case 2:
			im = pygame.transform.rotate(im,180)
		case 3:
			im = pygame.transform.rotate(im,90)
	return im

Image: typing.TypeAlias = list[tuple[float, float, ImageBit]]

def newimage() -> Image:
	return []

def addimagebit(ims: Image, im:ImageBit, x:float=0, y:float=0) -> None:
	x += im[2] / 2
	y += im[3] / 2
	ims.append((x, y, im))

def addimage(ims: Image, im: Image, x:float=0, y:float=0) -> None:
	for ix, iy, oim in im:
		ims.append((ix + x, iy + y, oim))

def rotateim(ims: Image, r:int, flip:bool=False, center:tuple[int, int]=(8, 8)) -> None:
	x, y = center
	for i, (ix, iy, im) in enumerate(ims):
		im = rotateib(im, r, flip)
		dx = ix - x
		dy = iy - y
		dx, dy = rotatexy(dx, dy, r, flip)
		ims[i]=(x + dx, y + dy, im)

def genimage(ims: Image) -> list[tuple[pygame.Surface,int,int]]:
	out=[]
	for x, y, im in ims:
		pim = getim(im)
		out.append((pim, int(x - pim.get_width() / 2), int(y - pim.get_height() / 2)))
	return out

class BlockDataLoose(typing.TypedDict):
	id:int
	rotate:typing.NotRequired[int]
	weld:typing.NotRequired[WeldSides]
	data:typing.NotRequired[str]
	offsetx:typing.NotRequired[int]
	offsety:typing.NotRequired[int]
	overlayoffsetx:typing.NotRequired[int]
	overlayoffsety:typing.NotRequired[int]
	overlay2offsetx:typing.NotRequired[int]
	overlay2offsety:typing.NotRequired[int]
	overlay3offsetx:typing.NotRequired[int]
	overlay4offsety:typing.NotRequired[int]
	sizex:typing.NotRequired[int]
	sizey:typing.NotRequired[int]

class BlockData(typing.TypedDict):
	id:int
	rotate:int
	weld:WeldSides
	data:typing.NotRequired[str]
	offsetx:typing.NotRequired[int]
	offsety:typing.NotRequired[int]
	overlayoffsetx:typing.NotRequired[int]
	overlayoffsety:typing.NotRequired[int]
	overlay2offsetx:typing.NotRequired[int]
	overlay2offsety:typing.NotRequired[int]
	overlay3offsetx:typing.NotRequired[int]
	overlay4offsety:typing.NotRequired[int]
	sizex:typing.NotRequired[int]
	sizey:typing.NotRequired[int]

BlockDataIn: typing.TypeAlias = BlockDataLoose | str | tuple | list

class BlockDesc(typing.TypedDict):
	wired:bool
	datafilters:list[typing.Callable[[BlockData], BlockData]]
	layers:list[typing.Callable[[BlockData], Image]]

def rotatexy(x:float, y:float, r:int, flip:bool) -> tuple[float,float]:
	if flip:
		x = -x
	if r == 0:
		x, y =  x,  y
	if r == 1:
		x, y = -y,  x
	if r == 2:
		x, y = -x, -y
	if r == 3:
		x, y =  y, -x
	return x, y

blockpaths={}
pthblocktexture = cfgstr("localGame.texture.texturePathFile")
with open(pthblocktexture) as f:
	data=smp.getsmpvalue(f.read())
assert isinstance(data,dict)
for name,texture in data.items():
	assert isinstance(texture,dict) # and that it is str:str
	blockpaths[name] = typing.cast(dict[str,str],texture)
	if 'rimlight' in texture:
		rimlight = PIL.Image.open(os.path.join(cfgstr("localGame.texture.texturePathFolder"),blockpaths[name]['rimlight'])).convert('RGB')
		rimlight_array:np.ndarray = np.asarray(rimlight)[0]
		#print(f'{name} has a rimlight wth shape {rimlight_array.shape}')
		rimlights[blockinfos[name]['id']] = rimlight_array

@functools.cache
def getalbedo(block_id:int) -> PIL.Image.Image:
	block = idtoblock[block_id]
	albedok = os.path.join(cfgstr("localGame.texture.texturePathFolder"),blockpaths[block]['albedo'])
	albedoim = PIL.Image.open(albedok).convert('RGBA')
	return albedoim

@functools.cache
def getnormal(block_id:int) -> PIL.Image.Image | None:
	block = idtoblock[block_id]
	if 'normal' in blockpaths[block]:
		normalk = os.path.join(cfgstr("localGame.texture.texturePathFolder"),blockpaths[block]['normal'])
		return PIL.Image.open(normalk).convert('RGBA')
	else:
		return None

def getblocksbyattr(attr:str) -> list[str]:
	return [b for b,data in blockinfos.items() if attr in data['attributes']]

def getblocksbynotattr(attr:str) -> list[str]:
	return [b for b,data in blockinfos.items() if attr not in data['attributes']]

wiredrawtypes=[(b,data['collision']) for b,data in blockinfos.items() if 'wire_draw' in data['attributes']]

# wire components on a wafer
wafertypes=[b for b,col in wiredrawtypes if 'solid' in col]
# wafer components that have an output side
outputtypes=[
	"diode",
	"galvanometer","latch",
	"potentiometer","transistor",
	"cascade","counter"
]
# wire components on a frame
wiretypes=[b for b,col in wiredrawtypes if 'solid' not in col]
# all blocks that connect to wire
wiredtypes=getblocksbyattr("wire_connect")
# blocks that only face one direction
norotatetypes=getblocksbynotattr("rotatable")
# blocks that only face two directions
twowaytypes=getblocksbyattr("symmetrical")
frametypes=wiretypes+['frame','wire']

def iswelded(side:WeldSide) -> bool:
	return side['weld']

def iswired(side:WeldSide) -> bool:
	return side['wire']

def isframe(side:WeldSide) -> bool:
	return side['frame']

def platformx(side:WeldSide) -> int:
	if side['platform']:
		return 2
	return int(side['weld'])

def makeweldside(side:WeldSideIn) -> WeldSide:
	if isinstance(side,dict):
		return side
	return {'weld':side,'wire':False,'platform':False,'frame':False}

weldedside = makeweldside(True)
unweldedside = makeweldside(False)

def setplatformside(side:WeldSide,other:bool) -> WeldSide:
	if side['weld'] and other:
		side['platform']=True
	return side

def setframeside(side:WeldSide,other:bool) -> WeldSide:
	if side['weld'] and other:
		side['frame']=True
	return side

def setwireside(side:WeldSide,other:bool) -> WeldSide:
	if side['weld'] and other:
		side['wire']=True
	return side

def blockdesc() -> BlockDesc:
	return {
		'wired':False, # does this block connect to wires beside it?
		'datafilters':[], # change the block data (norotate)
		'layers':[] # the layers of the block (actuator/any wire component)
	}

def norotatefilter(data:BlockData) -> BlockData:
	data={**data}
	data['rotate']=0
	return data

def twowayfilter(data:BlockData) -> BlockData:
	data={**data}
	if data['rotate']==1:
		data['rotate']=3
	if data['rotate']==2:
		data['rotate']=0
	return data

@functools.cache
def _getblocktexture(block_id:int,offsetx:int,offsety:int,sizex:int,sizey:int) -> ImageBit:
	return imagebit(block_id,offsetx,offsety,offsetx+sizex,offsety+sizey)

def getblocktexture(data:BlockDataLoose) -> ImageBit:
	blockid=data['id']
	offsetx=data.get('offsetx',0) or 0
	offsety=data.get('offsety',0) or 0
	sizex=data.get('sizex',32) or 32
	sizey=data.get('sizey',32) or 32
	return _getblocktexture(blockid,offsetx,offsety,sizex,sizey)

def drawblocktexture(image:ImageBit,weld:WeldSides) -> Image:
	top,left,bottom,right=weld
	im = newimage()
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			addimagebit(im, imagebit(image,x+16*iswelded(xside),y+16*iswelded(yside),8,8),x,y)
	return im

def defaultblock(data:BlockData) -> Image:
	welded=data['weld']
	rotate=data['rotate']
	image=getblocktexture(typing.cast(BlockDataLoose,data))
	welded=rotatewelded(welded,rotate)
	im=drawblocktexture(image,welded)
	im=rotateblockib(im,rotate)
	return im

def overlay(data:BlockData) -> Image:
	rotate=data['rotate']
	im=getblocktexture({
		**data,
		'offsetx':data.get('overlayoffsetx',0),
		'offsety':data.get('overlayoffsety',0),
		'sizex':16,
		'sizey':16,
	})
	im2 = newimage()
	addimagebit(im2, imagebit(im,0,0,16,16),0,0)
	im2=rotateoverlayib(im2,rotate)
	return im2

def overlay2(data:BlockData) -> Image:
	rotate=data['rotate']
	im=getblocktexture({
		**data,
		'offsetx':data.get('overlay2offsetx',0),
		'offsety':data.get('overlay2offsety',0),
		'sizex':16,
		'sizey':16,
	})
	im2 = newimage()
	addimagebit(im2, imagebit(im,0,0,16,16),0,0)
	return im2

def wafer(data:BlockData) -> Image:
	return defaultblock({**data,'id':blockinfos['wafer']['id']})

def frame(data:BlockData) -> Image:
	welded=data['weld']
	rotate=data['rotate']
	image=getblocktexture({'id':blockinfos['frame']['id'],'sizex':64})
	top,left,bottom,right=rotatewelded(welded,rotate)
	im = newimage()
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			if isframe(xside) or isframe(yside):
				offset=32 # frames have different welding to each other
			else:
				offset=0
			addimagebit(im, imagebit(image,x+offset+16*iswelded(xside),y+16*iswelded(yside),8,8),x,y)
	im=rotateblockib(im,rotate)
	return im

def wiretop(data:BlockData) -> Image:
	if idtoblock[data['id']] in outputtypes:
		welded=data['weld']
		rotate=data['rotate']
		top,_,_,_=rotatewelded(welded,rotate) # different texture by if the output is connected
		data={**data,'offsety':data.get('offsety',0)+16*iswired(top)}
	return overlay(data)

def wire(data:BlockData) -> Image:
	welded=data['weld']
	if 'data' in data:
		bdata=re.fullmatch('(?P<state>on|off)',data['data'])
		if bdata is None:
			raise ValueError('bad value format')
		offset=32 if bdata['state']=='on' else 0
	else:
		offset=0
	image=getblocktexture({'id':blockinfos['wire']['id'],'offsetx':offset})
	top,left,bottom,right=welded
	im = newimage()
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			addimagebit(im, imagebit(image,x+16*iswired(xside),y+16*iswired(yside),8,8),x,y)
	return im

def actuator(data:BlockData) -> Image:
	welded=data['weld']
	rotate=data['rotate']
	top,left,bottom,right=rotatewelded(welded,rotate)
	weld1=weldedside,left,bottom,right
	weld2=top,unweldedside,weldedside,unweldedside
	im1 = defaultblock({**data,'id':blockinfos['actuator_base']['id'],'weld':weld1,'rotate':0})
	im2 = defaultblock({**data,'id':blockinfos['actuator_head']['id'],'weld':weld2,'rotate':0})
	im = Image()
	addimage(im, im1,0,0)
	addimage(im, im2,0,0)
	im=rotateblockib(im,rotate)
	return im

def platform(data:BlockData) -> Image:
	_,left,_,right=data['weld']
	image=getblocktexture({**data,'sizex':48})
	y=0
	if left==0 and right==1 or left==1 and right==0 or left==0 and right==0:
		y=16
	im = newimage()
	for x,xside in [(0,left),(8,right)]:
		addimagebit(im, imagebit(image,x+16*platformx(xside),y,8,16),x,y)
	return im

def wirecomponent(data:BlockData) -> BlockData:
	if 'data' in data:
		typ=idtoblock[data['id']]
		if typ in ["port","accelerometer","matcher","detector","toggler","trigger"]:
			# instantaneous
			# top off bottom on texture
			bdata=re.fullmatch('(?P<state>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			data['overlayoffsety']=16 if bdata['state']=='on' else 0
			data['data']=bdata['state'] or 'off'
		elif typ=="capacitor":
			# non instantaneous
			# top off bottom on texture
			bdata=re.fullmatch('(?P<instate>on|off)?(?P<state>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			data['overlayoffsety']=16 if bdata['state']=='on' else 0
			data['data']=bdata['instate'] or 'off'
		elif typ in ["diode","galvanometer","latch","transistor"]:
			# column 1 off
			# column 2 on
			bdata=re.fullmatch('(?P<instate>on|off)?(?P<outstate>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			data['overlayoffsetx']=16 if bdata['outstate']=='on' else 0
			data['data']=bdata['instate'] or 'off'
		elif typ=="potentiometer": # the rest have a setting
			print('AAAAAAAAAAAAAAAAAAAAAAAAAAA',repr(data['data']))
			bdata=re.fullmatch('(?P<power>[1-9]|1[0-5])(?P<instate>on|off)?(?P<state>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			power = int(bdata['power']) - 1
			x = power % 8
			y = power // 8
			data['overlayoffsetx']=16 if bdata['state']=='on' else 0
			data['overlay2offsetx'] = 16 * (x + 2)
			data['overlay2offsety'] = 16 * y
			data['data']=bdata['instate'] or 'off'
		elif typ=="sensor":
			print('AAAAAAAAAAAAAAAAAAAAAAAAAAA',data['data'])
			bdata=re.fullmatch('(?P<setting>[1-9]|1[0-4])(?P<state>on|off)?',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			setting = int(bdata['setting'])
			x = setting % 8
			y = setting // 8
			data['overlayoffsety']=16 if bdata['state']=='on' else 0
			data['overlay2offsetx'] = 16 * (x + 1)
			data['overlay2offsety'] = 16 * y
			data['data']=bdata['state'] or 'off'
		elif typ=="cascade":
			# delay, in, out
			bdata=re.fullmatch('(?P<delay>[1-7])(?P<instate>on|off)?(?P<state>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			data['overlayoffsetx']=16*(2*(int(bdata['delay'])-1)+(bdata['state']=='on'))
		elif typ=="counter":
			# delay, in, out
			raise ValueError('counter data not supported')
			bdata=re.fullmatch('(?P<delay>[1-7])(?P<instate>on|off)?(?P<state>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			data['overlayoffsetx']=16*(2*(int(bdata['delay'])-1)+(bdata['state']=='on'))
	return data

def counterfilter(data:BlockData) -> BlockData:
	raise NotImplementedError('counterfilter')

def counter(data:BlockData) -> Image:
	raise NotImplementedError('counter')

def sparkcatcherfilter(data:BlockData) -> BlockData:
	if 'data' in data:
		i = int(data['data'])
		x = i % 8
		y = i // 8
		assert y >= 0 and y < 2
		data['overlayoffsetx'] = 32 + x * 16
		data['overlayoffsety'] = y * 16
	return data

blocktypes:collections.defaultdict[str,BlockDesc]=collections.defaultdict(blockdesc)

for t in norotatetypes:
	blocktypes[t]['datafilters'].append(norotatefilter)

for t in twowaytypes:
	blocktypes[t]['datafilters'].append(twowayfilter)

for t in wiretypes+wafertypes+['wire','wire_board']:
	blocktypes[t]['wired']=True

for block in blockpaths:
	blocktypes[block]['layers']=[defaultblock]

if 'player_pilot_chair_controls' in blocktypes: # not a real block
	del blocktypes['player_pilot_chair_controls']

blocktypes['actuator']['layers']=[actuator]
blocktypes['platform']['layers']=[platform]

for t in wafertypes:
	blocktypes[t]['layers']=[wafer,wire,wiretop]
	blocktypes[t]['datafilters'].append(wirecomponent)

for t in wiretypes:
	blocktypes[t]['layers']=[frame,wire,wiretop]
	blocktypes[t]['datafilters'].append(wirecomponent)

blocktypes['potentiometer']['layers'].append(overlay2)
blocktypes['sensor']['layers'].append(overlay2)

#blocktypes['counter']['datafilters'].append(counterfilter)
#blocktypes['counter']['layers']=[wafer,wire,counter]

blocktypes['wire_board']['layers']=[wafer,wire]
blocktypes['wire']['layers']=[frame,wire]
blocktypes['frame']['layers']=[frame]

blocktypes['spark_catcher']['datafilters']=[sparkcatcherfilter]
blocktypes['spark_catcher']['layers']=[defaultblock,overlay]

# rotate an image of a block by rotate
def rotateblockib(im:Image,rotate:int) -> Image:
	if rotate==0:
		pass
	if rotate==3:
		rotateim(im, 1)
	if rotate==1:
		rotateim(im, 3, True)
	if rotate==2:
		rotateim(im, 2, True)
	return im

# rotate an overlay (like galvanometer) by rotate
def rotateoverlayib(im:Image,rotate:int) -> Image:
	if rotate==0:
		pass
	if rotate==3:
		rotateim(im, 1)
	if rotate==1:
		rotateim(im, 3)
	if rotate==2:
		rotateim(im, 2)
	return im

# rotate the welds so they are in the right place when rotated by rotateblock
def rotatewelded(welded:WeldSides,rotate:int) -> WeldSides:
	if rotate==0:
		return welded
	idxs:tuple[int,int,int,int]
	if rotate==3:
		idxs = (3, 0, 1, 2)
	elif rotate==1:
		idxs = (1, 0, 3, 2)
	elif rotate==2:
		idxs = (2, 1, 0, 3)
	else:
		raise ValueError(f'bad rotate {rotate}')
	return ( # mypy dumb
		welded[idxs[0]],
		welded[idxs[1]],
		welded[idxs[2]],
		welded[idxs[3]],
	)

# convert blocks into a standardized format
# for easy processing
def normalize(block:BlockDataIn) -> BlockData:
	weld:WeldSidesIn
	if block is None:
		blockid = 0
		rotate = 0
		weld = (True,True,True,True)
	elif isinstance(block,str):
		blockid = blockinfos[block]['id']
		rotate = 0
		weld = (True,True,True,True)
	elif isinstance(block,(tuple,list)):
		b = dict(zip(["id","rotate","weld"],block))
		blockid = b.get('id') or 0
		rotate = b.get('rotate') or 0
		weld = b.get('weld') or (True,True,True,True)
	else:
		blockid = block.get('id') or 0
		rotate = block.get('rotate') or 0
		weld = block.get('weld') or (True,True,True,True)
	weld2=tuple(makeweldside(w) for w in weld)
	assert len(weld2)==4
	out: BlockData = {
		"id":blockid,
		"rotate":rotate,
		"weld":weld2,
	}
	if isinstance(block,dict):
		out.update(block)
	return out

# get a block from a grid
# if the coordinates are outside the grid, return air
def get(vss:list[list[BlockData]],xi:int,yi:int) -> BlockData:
	if xi<0 or yi<0 or yi>=len(vss):
		return normalize("air");
	vs=vss[yi]
	if(xi>=len(vs)):
		return normalize("air");
	return vs[xi]

def getblockimage(block: BlockData) -> Image:
	blocktype=blocktypes[idtoblock[block['id']]]
	im=Image()
	for datafilter in blocktype['datafilters']:
		block=datafilter(block)
	layers: list[Image] = []
	for layer in blocktype['layers']:
		addimage(im, layer(block),0,0) # paste the block
	return im

air = normalize("air")

# the main method
# blocks is a grid of blocks
# autoweld makes it weld all possible unspecified welds
# autoweld=False makes welds not autocorrect (for rendering roody structures)
def makeimage(blocks:list[list[BlockData]]) -> list[tuple[pygame.Surface,int,int]]:
	xsize=max(map(len,blocks))
	ysize=len(blocks)

	newblocks=[[air for _ in range(xsize)] for _ in range(ysize)]
	for yi,line in enumerate(blocks):
		for xi,blockin in enumerate(line):
			#block=normalize(blockin)
			newblocks[yi][xi]=blockin

	im=Image()
	for xi in range(xsize):
		for yi in range(ysize):
			with Timer(0):
				block=get(newblocks,xi,yi)
				if block['id']==0: # air
					# i need to do beams too nooooooooooooooooooo
					continue
				blockweldtop,blockweldleft,blockweldbottom,blockweldright = block['weld']
				if idtoblock[block['id']]=='platform': # special case
					# check if sides are platform
					blockweldleft = setplatformside(blockweldleft,idtoblock[get(newblocks,xi-1,yi)['id']]!='platform')
					blockweldright = setplatformside(blockweldright,idtoblock[get(newblocks,xi+1,yi)['id']]!='platform')
				if idtoblock[block['id']] in frametypes: # special case
					# check if sides are frame base
					blockweldtop = setframeside(blockweldtop,idtoblock[get(newblocks,xi,yi-1)['id']] in frametypes)
					blockweldleft = setframeside(blockweldleft,idtoblock[get(newblocks,xi-1,yi)['id']] in frametypes)
					blockweldbottom = setframeside(blockweldbottom,idtoblock[get(newblocks,xi,yi+1)['id']] in frametypes)
					blockweldright = setframeside(blockweldright,idtoblock[get(newblocks,xi+1,yi)['id']] in frametypes)
				blocktype=blocktypes[idtoblock[block['id']]]
				if blocktype['wired']:
					# check if sides are wired
					blockweldtop = setwireside(blockweldtop,idtoblock[get(newblocks,xi,yi-1)['id']] in wiredtypes)
					blockweldleft = setwireside(blockweldleft,idtoblock[get(newblocks,xi-1,yi)['id']] in wiredtypes)
					blockweldbottom = setwireside(blockweldbottom,idtoblock[get(newblocks,xi,yi+1)['id']] in wiredtypes)
					blockweldright = setwireside(blockweldright,idtoblock[get(newblocks,xi+1,yi)['id']] in wiredtypes)
			with Timer(2):
				block['weld']=(blockweldtop, blockweldleft, blockweldbottom, blockweldright)
			with Timer(3):
				bim = getblockimage(block)
			addimage(im, bim,xi*16,yi*16)
	return genimage(im)
