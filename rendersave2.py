from rsv import readsave
from renderblocks import rendergrid

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
    for ch,tilegrid in zip(save['chunkheaders'],save['tilegrids']):
      im,x,y=rendergrid(tilegrid,(64,64)),ch['posX'],ch['posY']
      im.save(os.path.join(d,f"{x}_{y}.png"))