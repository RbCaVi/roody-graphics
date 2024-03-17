import struct
from rle import derle,torle
from smp import getsmpvalue,smptostr
import itertools

versionformat="<i"
headerformat="<I4s2q4I"
chunklocationformat="<2qIxxxx"
assert struct.calcsize(chunklocationformat)==24
chunkheaderformat="<I4s2q8I"
tilegridheaderformat="<I4s2q20I"

headermembers=[
	"filesize","magic",
	"regionX","regionY",
	"loc_offset","loc_size",
	"chunks_offset","chunks_size"
]

locmembers=[
	'posX','posY','offset'
]

chunkheadermembers=[
	'len','magic',
	'posX','posY',
	'gen_stage','last_rand_tick',
	'grid_offset','grid_size',
	'tiledata_offset','tiledata_size',
	'entities_offset','entities_size'
]

tilegridheadermembers=[
	'len','magic',
	'boundX','boundY', # always 64
	'A_offset','A_size',
	'B_offset','B_size',
	'C_offset','C_size',
	'D_offset','D_size',
	'E_offset','E_size', # the rest are ignored
	'F_offset_spacer','F_size_spacer',
	'G_offset_spacer','G_size_spacer',
	'H_offset_spacer','H_size_spacer',
	'I_offset_spacer','I_size_spacer',
]

def encode(save):
	savedata=b''
	assert save["version"]==1
	version=struct.pack(versionformat,save["version"])
	
	tgdatas=[]
	
	for tgh,tg in zip(save['tilegridheaders'],save['tilegrids']):
		assert tgh['boundX']==64
		assert tgh['boundY']==64
		tgsize=tgh['boundX']*tgh['boundY']
		assert len(tg['byteA'])==tgsize
		assert len(tg['byteB'])==tgsize
		assert len(tg['byteC'])==tgsize
		assert len(tg['byteD'])==tgsize
		assert len(tg['byteE'])==tgsize
		byteA=torle(tg['byteA'])
		byteB=torle(tg['byteB'])
		byteC=torle(tg['byteC'])
		byteD=torle(tg['byteD'])
		byteE=torle(tg['byteE'])
		offsetA=struct.calcsize(tilegridheaderformat)
		offsetB=offsetA+len(byteA)
		offsetC=offsetB+len(byteB)
		offsetD=offsetC+len(byteC)
		offsetE=offsetD+len(byteD)
		length=offsetE+len(byteE)
		tgdata=struct.pack(
			tilegridheaderformat,
			length,b'tile',
			tgh['boundX'],tgh['boundX'],
			offsetA,len(byteA),
			offsetB,len(byteB),
			offsetC,len(byteC),
			offsetD,len(byteD),
			offsetE,len(byteE),
			0,0,0,0,0,0,0,0,0,0
		)+byteA+byteB+byteC+byteD+byteE
		tgdatas.append(tgdata)
	
	tddatas=[]
	for td in save['tiledynamics']:
		tddatas.append(bytes(smptostr(td),'utf-8'))
	
	esdatas=[]
	for es in save['entities']:
		esdatas.append(bytes(smptostr(es),'utf-8'))
	
	chdatas=[]
	for ch,tgdata,tddata,esdata in zip(save['chunkheaders'],tgdatas,tddatas,esdatas):
		gridoffset=struct.calcsize(chunkheaderformat)
		dynoffset=gridoffset+len(tgdata)
		entoffset=dynoffset+len(tddata)
		length=entoffset+len(esdata)
		chdata=struct.pack(
			chunkheaderformat,
			length,b'chnk',
			ch['posX'],ch['posY'],
			ch['gen_stage'],ch['last_rand_tick'],
			gridoffset,len(tgdata),
			dynoffset,len(tddata),
			entoffset,len(esdata),
		)+tgdata+tddata+esdata
		chdatas.append(chdata)
	
	*choffs,chsize=itertools.accumulate(itertools.chain([0],map(len,chdatas)))
	chdata=b''.join(chdatas)
	locs=b''
	for choff,loc in zip(choffs,save['chunklocations']):
		locs+=struct.pack(
			chunklocationformat,
			loc['posX'],loc['posY'],
			choff
		)
	
	locoffset=struct.calcsize(headerformat)
	choffset=locoffset+len(locs)
	filesize=choffset+len(chdata)
	header=save['header']
	return version+struct.pack(
		headerformat,
		filesize,b'.rsv',
		header["regionX"],header["regionY"],
		locoffset,len(locs),
		choffset,len(chdata)
	)+locs+chdata

def readsave(savedata):
	version,=struct.unpack(versionformat,savedata[:4])
	assert version==1

	data=savedata[4:]
	header=dict(zip(headermembers,struct.unpack(headerformat,data[:40])))

	assert header['filesize']==len(data)
	assert True or header['magic']==b'.rsv'

	chunklocations=[
		dict(zip(locmembers,loc)) for loc in
		struct.iter_unpack(
			chunklocationformat,
			data[
				header['loc_offset']:
				header['loc_offset']+header['loc_size']
			]
		)
	]

	assert len(chunklocations)==header['loc_size']/struct.calcsize(chunklocationformat)

	chunkoffset=lambda loc:header['chunks_offset']+loc['offset']

	chunkheaders=[
		dict(zip(chunkheadermembers,
			struct.unpack(
				chunkheaderformat,
				data[
					chunkoffset(loc):
					chunkoffset(loc)+struct.calcsize(chunkheaderformat)
				]
			)
		)) for loc in chunklocations
	]

	assert all([
		ch['gen_stage']==chunkheaders[0]['gen_stage']
		for ch in chunkheaders
	]) # all chunks have the same generation stage

	assert True or all([
		ch['magic']==b'chnk'
		for ch in chunkheaders
	]) # all chunks have the magic number

	gridoffset=lambda loc,ch:chunkoffset(loc)+ch['grid_offset']

	tilegridheaders=[
		dict(zip(
			tilegridheadermembers,
			struct.unpack(
				tilegridheaderformat,
				data[
					gridoffset(loc,ch):
					gridoffset(loc,ch)+struct.calcsize(tilegridheaderformat)
				]
			)
		)) for loc,ch in zip(chunklocations,chunkheaders)
	]

	assert True or all([
		tgh['magic']==b'tile'
		for tgh in tilegridheaders
	]) # all tilegrids have the magic number

	assert all([
		tgh['boundX']==64
		for tgh in tilegridheaders
		for bound in ['boundX','boundY']
	]) # all tilegrids have both bounds equal to 64

	assert all([
		tgh[spacer]==0
		for tgh in tilegridheaders
		for spacer in [
			'F_offset_spacer',
			'F_size_spacer',
			'G_offset_spacer',
			'G_size_spacer',
			'H_offset_spacer',
			'H_size_spacer',
			'I_offset_spacer',
			'I_size_spacer',
		]
	]) # all spacers are equal to 0

	assert all([
		gridoffset(loc,ch)+tgh[f'{c}_offset']+tgh[f'{c}_size']<=header['filesize']
		for loc,ch,tgh in zip(chunklocations,chunkheaders,tilegridheaders)
		for c in 'ABCDE'
	]) # all tilegrids have non-cut-off data

	tilegrids=[
		{
			f'byte{c}':derle(data[
				gridoffset(loc,ch)+tgh[f'{c}_offset']:
				gridoffset(loc,ch)+tgh[f'{c}_offset']+tgh[f'{c}_size']
			]) for c in 'ABCDE'
		} for loc,ch,tgh in zip(chunklocations,chunkheaders,tilegridheaders)
	]

	assert all([
		len(tg[grid])==tgh['boundX']*tgh['boundY']
		for tgh,tg in zip(tilegridheaders,tilegrids)
		for grid in ['byteA','byteB','byteC','byteD','byteE']
	]) # no partial grids

	tiledynamics=[
		getsmpvalue(data[
			chunkoffset(loc)+ch['tiledata_offset']:
			chunkoffset(loc)+ch['tiledata_offset']+ch['tiledata_size']
		].decode('utf-8')) for loc,ch,tgh in zip(chunklocations,chunkheaders,tilegridheaders)
	]

	entities=[
		getsmpvalue(data[
			chunkoffset(loc)+ch['entities_offset']:
			chunkoffset(loc)+ch['entities_offset']+ch['entities_size']
		].decode('utf-8')) for loc,ch,tgh in zip(chunklocations,chunkheaders,tilegridheaders)
	]

	return {
		"version":version,
		"header":header,
		"chunklocations":chunklocations,
		"chunkheaders":chunkheaders,
		"tilegridheaders":tilegridheaders,
		"tilegrids":tilegrids,
		"tiledynamics":tiledynamics,
		"entities":entities,
	}
