import struct
from rle import derle
from smp import getsmpvalue

headerformat="<I4s2q4I"
chunklocationformat="<2qIxxxx"
assert struct.calcsize(chunklocationformat)==24
chunkheaderformat="<I4s2q8I"
tilegridheaderformat="<I4s2q20I"

def readsave(savedata):
	version,=struct.unpack('<i',savedata[:4])
	assert version==1

	data=savedata[4:]
	header=dict(zip([
		"filesize","magic",
		"regionX","regionY",
		"loc_offset","loc_size",
		"chunks_offset","chunks_size"
	],struct.unpack(headerformat,data[:40])))

	assert header['filesize']==len(data)
	assert header['magic']==b'.rsv'

	chunklocations=[
		dict(zip([
			'posX','posY','offset'
		],loc)) for loc in
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
		dict(zip(
			[
		    'len','magic',
		    'posX','posY',
		    'gen_stage','last_rand_tick',
		    'grid_offset','grid_size',
		    'tiledata_offset','tiledata_size',
		    'entities_offset','entities_size'
		  ],
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
			[
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
		  ],
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
		"header":header,
		"chunklocations":chunklocations,
		"chunkheaders":chunkheaders,
		"tilegridheaders":tilegridheaders,
		"tilegrids":tilegrids,
		"tiledynamics":tiledynamics,
		"entities":entities,
	}
