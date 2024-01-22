spawnrecipes = ["residue","air","dirt","sediment","stone","leaf_maple","log_maple","leaf_pine","log_pine","iron_vein","iron_ore","copper_vein","copper_ore","grass","flower_magenta","flower_yellow","ice","snow","residue","core_ore"]

icons=[
    ["dirt","grass","sediment","stone","iron_vein","iron_ore","copper_vein","copper_ore","sand","leaf_maple","log_maple","leaf_pine","log_pine","water","snow"],
    ["iron_bar","iron_plate","cast_iron","oxide","copper_bar","wire_spool","silicon","wafer","pulp","rubber","sawdust","calcium_bar","peltmellow","compressed_stone"],
    ["frame","platform","lamp","display","cap","chair","chair_pilot","spikes","foam","adobe"],
    ["wire","wire_board","port","inductor","diode","cascade","potentiometer","transistor","latch","galvanometer","counter","capacitor"],
    ["toggler","trigger","sensor","detector","matcher","accelerometer"],
    ["extractor","arc_furnace","combiner","motor","manipulator","mantler","dismantler","destroyer","collector"],
    ["roller","dynamic_roller","ice","magnet","actuator","actuator_head","actuator_base","teleportore","telecross","telewall"],
    ["flower_magenta","flower_yellow","residue","injector","glass","glass_magenta","glass_yellow","glass_cyan","beam_core","mirror","prism"],
    ["core_ore","raw_core","mass_core","rail_core","force_core","refined_core","catalyst_core","soul_core","pedestal","summonore"]
]

iconpositions={icon:f"{x},{y+5}" for y,line in enumerate(icons) for x,icon in enumerate(line)}

initialobjectives = {
    "iron_ore":{"amount":5,"position":[2,0],"passives":["faster_unwelding"]},
    "copper_ore":{"amount":5,"position":[4,0],"passives":["faster_welding"]},
    "stone":{"amount":5,"position":[6,0],"passives":["higher_jump"]},
    "log_pine":{"amount":5,"position":[7,0],"passives":["longer_reach"]},
    "log_maple":{"amount":5,"position":[8,0],"passives":["longer_reach"]},
    "core_ore":{"amount":5,"position":[4,10],"passives":["core_economy"]},
    "residue":{"amount":5,"position":[9,12],"passives":["bigger_inventory"]}
}

objectives = {
    "oxide": {"requirements":["iron_ore"],"amount":5,"position":[0,1],"force":"vh"},
    "iron_bar": {"requirements":["iron_ore"],"amount":5,"position":[2,1]},
    "copper_bar": {"requirements":["copper_ore"],"amount":5,"position":[4,1]},
    "compressed_stone": {"requirements":["stone"],"amount":5,"position":[5,1],"force":"vh"},
    "sand": {"requirements":["stone"],"amount":5,"position":[6,1]},
    "sawdust": {"requirements":["log_pine"],"amount":5,"position":[7,1]},
    "pulp": {"requirements":["log_maple"],"amount":5,"position":[8,1]},
    "platform": {"requirements":["log_maple"],"amount":5,"position":[9,1],"force":"vh"},
    "calcium_bar": {"requirements":["oxide"],"amount":5,"position":[0,2],"force":"vh"},
    "peltmellow": {"requirements":["oxide"],"amount":5,"position":[1,2]},
    "cast_iron": {"requirements":["iron_bar"],"amount":5,"position":[1,3],"force":"vhv"},
    "roller": {"requirements":["iron_plate"],"amount":5,"position":[2,4]},
    "dynamic_roller": {"requirements":["iron_plate","roller"],"amount":5,"position":[1,5]},
    "frame": {"requirements":["iron_bar"],"amount":5,"position":[3,2],"force":"vh"},
    "wire_spool": {"requirements":["copper_bar"],"amount":5,"position":[5,2]},
    "silicon": {"requirements":["sand"],"amount":5,"position":[6,2]},
    "rubber": {"requirements":["pulp"],"amount":5,"position":[8,2],"passives":["roller_replication"]},
    "spikes": {"requirements":["calcium_bar"],"amount":5,"position":[0,3]},
    "foam": {"requirements":["peltmellow"],"amount":5,"position":[0,4]},
    "iron_plate": {"requirements":["iron_bar"],"amount":5,"position":[2,3]},
    "magnet": {"requirements":["iron_bar","wire_spool"],"amount":5,"position":[3,5]},
    "motor": {"requirements":["iron_bar","wire_spool"],"amount":5,"position":[3,6]},
    "inductor": {"requirements":["iron_bar","wire_spool"],"amount":5,"position":[3,7]},
    "accelerometer": {"requirements":["iron_bar","wafer","magnet"],"amount":5,"position":[4,6]},
    "wire": {"requirements":["frame","wire_spool"],"amount":5,"position":[4,3],"force":"vh"},
    "glass": {"requirements":["silicon"],"amount":5,"position":[7,3],"force":"vh"},
    "wafer": {"requirements":["silicon"],"amount":5,"position":[6,3]},
    "cap": {"requirements":["rubber"],"amount":5,"position":[9,3],"force":"vh"},
    "arc_furnace": {"requirements":["wire_spool","cast_iron"],"amount":5,"position":[1,4]},
    "port": {"requirements":["frame","wire"],"amount":5,"position":[3,4],"force":"vhv"},
    "potentiometer": {"requirements":["wire_board"],"amount":5,"position":[4,5]},
    "diode": {"requirements":["wafer","wire"],"amount":5,"position":[5,5],"force":"vh"},
    "transistor": {"requirements":["wafer","wire_board"],"amount":5,"position":[6,5],"force":"vh"},
    "lamp": {"requirements":["wire_spool","glass"],"amount":5,"position":[7,4]},
    "water": {"requirements":["foam"],"amount":5,"position":[0,5]},
    "mantler": {"requirements":["roller","cast_iron","wire_spool"],"amount":5,"position":[2,5]},
    "wire_board": {"requirements":["wire","wafer"],"amount":5,"position":[4,4]},
    "mirror": {"requirements":["iron_plate","glass"],"amount":5,"position":[3,8]},
    "dismantler": {"requirements":["oxide","iron_plate","motor"],"amount":5,"position":[1,8]},
    "destroyer": {"requirements":["oxide","iron_plate","motor","dismantler"],"amount":5,"position":[1,9]},
    "extractor": {"requirements":["oxide","iron_bar","motor"],"amount":5,"position":[1,7]},
    "chair": {"requirements":["peltmellow","cap","rubber"],"amount":5,"position":[8,6]},
    "display": {"requirements":["lamp","iron_plate","wire_board"],"amount":5,"position":[7,5]},
    "adobe": {"requirements":["water"],"amount":5,"position":[0,6]},
    "cascade": {"requirements":["diode"],"amount":5,"position":[5,6]},
    "toggler": {"requirements":["wire","transistor"],"amount":5,"position":[6,6]},
    "galvanometer": {"requirements":["wire","wafer","magnet"],"amount":5,"position":[5,8]},
    "latch": {"requirements":["wire_board","transistor"],"amount":5,"position":[5,7]},
    "trigger": {"requirements":["wire","glass"],"amount":5,"position":[6,7]},
    "detector": {"requirements":["toggler","rubber"],"amount":5,"position":[7,7]},
    "glass_yellow": {"requirements":["glass","flower_yellow"],"amount":5,"position":[9,15]},
    "glass_magenta": {"requirements":["glass","flower_magenta"],"amount":5,"position":[9,14]},
    "glass_cyan": {"requirements":["glass","residue"],"amount":5,"position":[9,13]},
    "prism": {"requirements":["glass"],"amount":5,"position":[9,7]},
    "manipulator": {"requirements":["motor","trigger"],"amount":5,"position":[4,8]},
    "chair_pilot": {"requirements":["chair","toggler"],"amount":5,"position":[8,7]},
    "capacitor": {"requirements":["wire_spool","wafer"],"amount":5,"position":[4,7]},
    "counter": {"requirements":["wire_board","latch","glass","galvanometer"],"amount":5,"position":[3,9]},
    "sensor": {"requirements":["trigger","latch","potentiometer"],"amount":5,"position":[6,9]},
    "matcher": {"requirements":["transistor","sensor","galvanometer"],"amount":5,"position":[5,9]},
    "actuator_base": {"requirements":["motor","iron_bar"],"amount":5,"position":[1,10]},
    "actuator_head": {"requirements":["copper_bar","iron_bar"],"amount":5,"position":[3,10]},
    "actuator": {"requirements":["actuator_base","actuator_head"],"amount":5,"position":[1,11]},
    "injector": {"requirements":["actuator","iron_plate","glass"],"amount":5,"position":[1,12]},
    "iron_vein": {"requirements":["injector","mass_core","iron_ore"],"amount":5,"position":[1,13]},
    "copper_vein": {"requirements":["injector","mass_core","copper_ore"],"amount":5,"position":[2,13]},
    "raw_core": {"requirements":["core_ore","cast_iron"],"amount":5,"position":[3,11]},
    "mass_core": {"requirements":["raw_core"],"amount":5,"position":[3,12]},
    "rail_core": {"requirements":["raw_core","mass_core"],"amount":5,"position":[4,13],"force":"vh"},
    "refined_core": {"requirements":["mass_core","cast_iron"],"amount":5,"position":[3,13]},
    "combiner": {"requirements":["raw_core","frame","iron_plate","magnet","diode"],"amount":5,"position":[6,12]},
    "catalyst_core": {"requirements":["refined_core","cast_iron"],"amount":5,"position":[3,14]},
    "beam_core": {"requirements":["iron_plate","refined_core","lamp","glass"],"amount":5,"position":[4,14]},
    "soul_core": {"requirements":["catalyst_core","peltmellow","cast_iron"],"amount":5,"position":[3,15]},
    "teleportore": {"requirements":["catalyst_core","beam_core","glass_magenta"],"amount":5,"position":[4,15]},
    "telecross": {"requirements":["raw_core","teleportore","calcium_bar"],"amount":5,"position":[4,16]},
    "collector": {"requirements":["rubber","teleportore","peltmellow"],"amount":5,"position":[5,16]},
    "summonore": {"requirements":["collector","peltmellow","soul_core","teleportore","sensor"],"amount":5,"position":[5,17]},
    "telewall": {"requirements":["telecross"],"amount":5,"position":[4,17]},
    "pedestal": {"requirements":["soul_core","calcium_bar","platform","sensor"],"amount":5,"position":[3,16]},
    "sediment": {"requirements":["sawdust","oxide","injector"],"amount":5,"position":[2,15]},
    "grass": {"requirements":["sawdust","injector"],"amount":5,"position":[0,15]},
    "flower_yellow": {"requirements":["sawdust","injector"],"amount":5,"position":[0,14]},
    "flower_magenta": {"requirements":["sawdust","injector"],"amount":5,"position":[0,13]},
    "dirt": {"requirements":["grass","injector"],"amount":5,"position":[2,16]}
}

def _smptostr(smp,indented,indent):
    if type(smp) in [str,int]:
        return str(smp),False # do not add newlines around
    if type(smp) is list:
        s=''
        for x in smp:
            xs,xnl=_smptostr(x,indented+indent,indent)
            nl=f'\n{indented}' if xnl else ''
            s+=f'\n{indented}[{xs}{nl}]'
        return s,True
    if type(smp) is dict:
        s=''
        for k,v in smp.items():
            xs,xnl=_smptostr(v,indented+indent,indent)
            nl=f'\n{indented}' if xnl else ''
            s+=f'\n{indented}{{{k}}}:{{{xs}{nl}}}'
        return s,True

def smptostr(smp,indent='  '):
    return _smptostr(smp,'',indent)[0].lstrip('\n')

objectivessmp=[
    {
        'name':'spawn',
        'recipes':spawnrecipes,
        'invisible':1
    }
]

for block,bdata in initialobjectives.items():
    objective={
        'name':block,
        'costs':[{'block':block,'amount':bdata['amount']}],
        'icon':iconpositions[block],
        'override_location':f'{bdata["position"][0]},{bdata["position"][1]}'
    }
    if 'passives' in bdata:
        objective['passives']=bdata['passives']
    objectivessmp.append(objective)

for oname,odata in objectives.items():
    hiddenobjective={
        'name':f'{oname}_unlock',
        'requirements':odata['requirements'],
        'recipes':[oname],
        'invisible':1
    }
    objective={
        'name':oname,
        'requirements':odata['requirements'],
        'costs':[{'block':oname,'amount':odata['amount']}],
        'icon':iconpositions[oname],
        'override_location':f'{odata["position"][0]},{odata["position"][1]}'
    }
    if 'force' in odata:
        objective[f'force_{odata["force"]}']=1
    if 'passives' in odata:
        objective['passives']=odata['passives']
    objectivessmp.append(hiddenobjective)
    objectivessmp.append(objective)

with open("research_objectives.smp", "w") as f:
    f.write(smptostr(objectivessmp))