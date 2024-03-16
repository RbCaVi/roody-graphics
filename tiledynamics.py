from rsv import readsave

alltiledynamics=[]
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
    for tiledynamic in save['tiledynamics']:
      if type(tiledynamic)==str:
        continue
      alltiledynamics.append(tiledynamic)

  for tiledynamic in alltiledynamics:
    print(tiledynamic)