from rsv import readsave
from renderblocks import rendergrid
from smp import getsmpvalue
import PIL.Image

if __name__=='__main__':
  import sys
  import os
  savefolder=sys.argv[1]

  d=os.path.join(savefolder,'images')
  os.makedirs(d,exist_ok=True)

  with open('entities/entities.smp') as f:
    data=getsmpvalue(f.read())
    entitydata={e['name']:e for e in data}

  entityims={}
  for name,edata in entitydata.items():
    entityims[name]=PIL.Image.open(edata['texture'])

  for filename in os.listdir(savefolder):
    if not filename.endswith('.rsv'):
      continue
    print(filename)
    savefile=os.path.join(savefolder,filename)
    with open(savefile,'rb') as f:
      savedata=f.read()

    save=readsave(savedata)
    for ch,tilegrid,entities in zip(save['chunkheaders'],save['tilegrids'],save['entities']):
      im,x,y=rendergrid(tilegrid,(64,64)),ch['posX'],ch['posY']
      if type(entities)!=str:
        for entity in entities:
          edata=entitydata[entity['type']]
          ex,ey=[int(c) for c in entity['kinematic']['position'].split(',')]
          ew,eh=[int(c) for c in edata['size'].split(',')]
          ex-=(256-ew)//2
          ey-=(256-eh)//2
          frame=int(entity.get('animation_walk_cycle',0))//int(edata.get('animation_walk_holds',3))
          assert frame<int(edata.get('animation_walk_frames',1))
          # entities are drawn from top left
          eim=entityims[entity['type']].crop((frame*16,0,(frame+1)*16,16))
          ex//=16 # 16 is entity coords to pixel coords
          ey//=16
          ex-=ch['posX']*16*64 # entity coords are absolute
          ey-=ch['posY']*16*64 # make them relative to the chunk
          print('drawing entity at',ex,ey)
          im.alpha_composite(eim,(ex,ey))
      im.save(os.path.join(d,f"{x}_{y}.png"))