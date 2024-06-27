# the links
# key is link name
# value['link'] is the url
# value['kw'] is the keywords !link recognizes

# the links as one string (used to format into !link description)

from smp import getsmpvalue
import json
from typing import Any, TextIO, Callable
import decorator

config = None

def loadconfig() -> None:
    with open("config.json", encoding="utf-8") as f:
        global config
        config = json.load(f)

def cfgstr(target:str) -> str:
    if config is None: loadconfig()
    base = config
    for tv in target.split("."):
        assert isinstance(base,dict)
        base = base[tv]
    assert isinstance(base,str)
    return base

def _opencfg(open:Callable, target:str, *args:Any, encoding:str|None="utf-8", **kwargs:Any) -> TextIO:
    return open(cfgstr(target), *args, encoding=encoding, **kwargs)

opencfg = decorator.decorate(open,_opencfg,kwsyntax=True)

def cfg(target:str) -> int | str | list | dict:
    if config is None: loadconfig()
    base = config
    for tv in target.split("."):
        assert isinstance(base,dict)
        base = base[tv]
    assert isinstance(base, (int, str, list, dict))
    return base

def getarrowcoords() -> dict[str, tuple[int, int]]:
    racord:dict[str, tuple[int, int]] = {}
    with opencfg("localGame.texture.guidebookArrowCordFile") as f:
        data=getsmpvalue(f.read())
    assert isinstance(data,dict)
    for icon,xy in data.items():
        assert isinstance(xy,str)
        x,y=xy.split(',')
        racord[icon] = (int(x), int(y))
    return racord

def botinit() -> None:
    from assetload import assetinit
    loadconfig()
    assetinit() # roody locale and blocks
