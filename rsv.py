import struct
from rle import derle
from smp import getsmpvalue

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
  savedata=struct.pack(versionformat,save["version"])
  
  tgdatas=[]
  
  for tgh,tg in zip(save['tilegridheaders'],save['tilegrids']):
    assert tgh['boundX']==64
    assert tgh['boundY']==64
    assert len(tg['byteA'])==tgh['boundX']*tgh['boundY']
    byteA=torle(tg['byteA'])
    offsetA=struct.calcsize(tilegridheaderformat)
    assert len(tg['byteB'])==tgh['boundX']*tgh['boundY']
    byteB=torle(tg['byteB'])
    offsetB=offsetA+len(byteA)
    assert len(tg['byteC'])==tgh['boundX']*tgh['boundY']
    byteC=torle(tg['byteC'])
    offsetC=offsetB+len(byteB)
    assert len(tg['byteD'])==tgh['boundX']*tgh['boundY']
    byteD=torle(tg['byteD'])
    offsetD=offsetC+len(byteC)
    assert len(tg['byteE'])==tgh['boundX']*tgh['boundY']
    byteE=torle(tg['byteE'])
    offsetE=offsetD+len(byteD)
    length=offsetE+len(byteE)
    tgdata=struct.pack(
      tilegridheaderformat,
      length,'tile',
      tgh['boundX'],tgh['boundX'],
      offsetA,len(byteA),
      offsetB,len(byteB),
      offsetC,len(byteC),
      offsetD,len(byteD),
      offsetE,len(byteE),
      0,0,0,0,0,0,0,0
    )+byteA+byteB+byteC+byteD+byteE
    tgdatas.append(tgdata)
  
  tddatas=[]
  for td in save['tiledynamics']:
    tddatas.append(bytes(smptostr(td),'utf-8'))
  
  esdatas=[]
  for es in save['entities']:
    tddatas.append(bytes(smptostr(es),'utf-8'))
  
  chdatas=[]
  for ch,tgdata,tddata,esdata in zip(save['chunkheaders'],tgdatas,tddatas,esdatas):
    gridoffset=struct.calcsize(chunkheaderformat)
    dynoffset=gridoffset+len(tg)
    entoffset=dynoffset+len(td)
    length=entoffset+len(es)
    chdata=struct.pack(
      chunkheaderformat,
      length,'chnk',
      ch['posX'],ch['posY'],
      ch['gen_stage'],ch['last_rand_tick'],
      gridoffset,len(tg),
      dynoffset,len(td),
      entoffset,len(es),
    )+tg+td+es
    chdatas.append(chdata)
  
  *choffs,chsize=itertools.accumulate(map(len,chdatas),initial=0)
  chdata=sum(chdatas)
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
  return struct.pack(
    headerformat,
    filesize,b'.rsv',
    header["regionX"],header["regionY"],
    locoffset,len(locs),
    choffset,len(chdata)
  )

def readsave(savedata):
	version,=struct.unpack(versionformat,savedata[:4])
	assert version==1

	data=savedata[4:]
	header=dict(zip(headermembers,struct.unpack(headerformat,data[:40])))

	assert header['filesize']==len(data)
	assert header['magic']==b'.rsv'

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

	chunkheaders=[
		dict(zip(chunkheadermembers,
		  struct.unpack(
		  	chunkheaderformat,
			  data[
			  	header['chunks_offset']+loc['offset']:
			  	header['chunks_offset']+loc['offset']+struct.calcsize(chunkheaderformat)
			  ]
		  )
	 	)) for loc in chunklocations
	]

	assert all([
		ch['gen_stage']==chunkheaders[0]['gen_stage']
		for ch in chunkheaders
	]) # all chunks have the same generation stage

	assert all([
		ch['magic']==b'chnk'
		for ch in chunkheaders
	]) # all chunks have the magic number

	tilegridheaders=[
		dict(zip(
			tilegridheadermembers,
		  struct.unpack(
		  	tilegridheaderformat,
			  data[
			  	header['chunks_offset']+loc['offset']+ch['grid_offset']:
			  	header['chunks_offset']+loc['offset']+ch['grid_offset']+struct.calcsize(tilegridheaderformat)
			  ]
		  )
	  )) for loc,ch in zip(chunklocations,chunkheaders)
	]

	assert all([
		tgh['magic']==b'tile'
		for tgh in tilegridheaders
	]) # all tilegrids have the magic number

	assert all([
		tgh['boundX']==64
		for tgh in tilegridheaders
	]) # all tilegrids have boundX equal to 64

	assert all([
		tgh['boundY']==64
		for tgh in tilegridheaders
	]) # all tilegrids have boundY equal to 64

	assert all([
		tgh['F_offset_spacer']==0
		for tgh in tilegridheaders
	]) # all tilegrids have F_offset_spacer equal to 0

	assert all([
		tgh['F_size_spacer']==0
		for tgh in tilegridheaders
	]) # all tilegrids have F_size_spacer equal to 0

	assert all([
		tgh['G_offset_spacer']==0
		for tgh in tilegridheaders
	]) # all tilegrids have G_offset_spacer equal to 0

	assert all([
		tgh['G_size_spacer']==0
		for tgh in tilegridheaders
	]) # all tilegrids have G_size_spacer equal to 0

	assert all([
		tgh['H_offset_spacer']==0
		for tgh in tilegridheaders
	]) # all tilegrids have H_offset_spacer equal to 0

	assert all([
		tgh['H_size_spacer']==0
		for tgh in tilegridheaders
	]) # all tilegrids have H_size_spacer equal to 0

	assert all([
		tgh['I_offset_spacer']==0
		for tgh in tilegridheaders
	]) # all tilegrids have I_offset_spacer equal to 0

	assert all([
		tgh['I_size_spacer']==0
		for tgh in tilegridheaders
	]) # all tilegrids have I_size_spacer equal to 0

	assert all([
		header['chunks_offset']+ch['grid_offset']+tgh['A_offset']+tgh['A_size']<=header['filesize']
		for ch,tgh in zip(chunkheaders,tilegridheaders)
	]) # all tilegrids have non-cut-off data

	tilegrids=[
		{
		  'byteA':derle(data[
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['A_offset']:
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['A_offset']+tgh['A_size']
		  ]),
		  'byteB':derle(data[
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['B_offset']:
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['B_offset']+tgh['B_size']
		  ]),
		  'byteC':derle(data[
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['C_offset']:
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['C_offset']+tgh['C_size']
		  ]),
		  'byteD':derle(data[
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['D_offset']:
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['D_offset']+tgh['D_size']
		  ]),
		  'byteE':derle(data[
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['E_offset']:
		  	header['chunks_offset']+loc['offset']+ch['grid_offset']+tgh['E_offset']+tgh['E_size']
		  ])
	  } for loc,ch,tgh in zip(chunklocations,chunkheaders,tilegridheaders)
	]

	assert all([
		len(tg['byteA'])==tgh['boundX']*tgh['boundY']
		for tgh,tg in zip(tilegridheaders,tilegrids)
	]) # all tilegrids have full byteA grids

	assert all([
		len(tg['byteB'])==tgh['boundX']*tgh['boundY']
		for tgh,tg in zip(tilegridheaders,tilegrids)
	]) # all tilegrids have full byteB grids

	assert all([
		len(tg['byteC'])==tgh['boundX']*tgh['boundY']
		for tgh,tg in zip(tilegridheaders,tilegrids)
	]) # all tilegrids have full byteC grids

	assert all([
		len(tg['byteD'])==tgh['boundX']*tgh['boundY']
		for tgh,tg in zip(tilegridheaders,tilegrids)
	]) # all tilegrids have full byteD grids

	assert all([
		len(tg['byteE'])==tgh['boundX']*tgh['boundY']
		for tgh,tg in zip(tilegridheaders,tilegrids)
	]) # all tilegrids have full byteE grids

	tiledynamics=[
		getsmpvalue(data[
	  	header['chunks_offset']+loc['offset']+ch['tiledata_offset']:
	  	header['chunks_offset']+loc['offset']+ch['tiledata_offset']+ch['tiledata_size']
	  ].decode('utf-8')) for loc,ch,tgh in zip(chunklocations,chunkheaders,tilegridheaders)
	]

	entities=[
		getsmpvalue(data[
	  	header['chunks_offset']+loc['offset']+ch['entities_offset']:
	  	header['chunks_offset']+loc['offset']+ch['entities_offset']+ch['entities_size']
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