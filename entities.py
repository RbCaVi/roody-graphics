from rsv import readsave
from renderblocks import rendergrid
from smp import getsmpvalue
import PIL
import PIL.Image

allentities=[]
if __name__=='__main__':
  import sys
  import os
  savefolder=sys.argv[1]

  d=os.path.join(savefolder,'images')
  os.makedirs(d,exist_ok=True)

  for filename in os.listdir(savefolder):
    if not filename.endswith('.rsv'):
      continue
    print(filename)
    savefile=os.path.join(savefolder,filename)
    with open(savefile,'rb') as f:
      savedata=f.read()

    save=readsave(savedata)
    for entities in save['entities']:
      if type(entities)==str:
        continue
      for entity in entities:
        allentities.append(entity)

  with open('entities/entities.smp') as f:
    data=getsmpvalue(f.read())
    entitydata={e['name']:e for e in data}

  entityims={}
  for name,edata in entitydata.items():
    entityims[name]=PIL.Image.open(edata['texture'])

  for entity in allentities:
    edata=entitydata[entity['type']]
    coords=[int(c)/16 for c in entity['kinematic']['position'].split(',')] # 16 is entity coords to pixel coords
    frame=int(entity.get('animation_walk_cycle',0))//int(edata.get('animation_walk_holds',3))
    assert frame<int(edata.get('animation_walk_frames',1))
    # entities are drawn from top left
    entityims[entity['type']].crop((frame*16,0,(frame+1)*16,16)).show()