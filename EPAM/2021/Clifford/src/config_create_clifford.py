#!/usr/bin/env python3
import os, sys
import json, re
from typing import DefaultDict, OrderedDict

CONFIG_FILE_INPUT  = "_settings_.json"
CONFIG_FILE_OUTPUT = "config_clifford.py"

def make_short_name(s):
    return s.strip().replace(" ","_")


def read_config(path):
    #read config
    config=dict()
    try:
        print("Parsing config file (json)...")
        path=os.path.join(path)
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)
        return None
    finally:
        print("JSON succesfully parsed.")
        for section,cfg in config.items():
            print("{} : {}".format(section,cfg))
        #mod = sys.modules[self.__module__]
    
    return config

CONFIG = read_config(CONFIG_FILE_INPUT)


p = re.compile("^\[(.*)\] (.*)")

par_classes = DefaultDict(dict)

with open(CONFIG_FILE_OUTPUT, "wt+", encoding="utf-8") as f:

    f.write(" # auto-generated config file\n")
    for s in CONFIG['parameters']:
        pname = s['name']
        pvalue= s['value']
        ptype = s['valueType']
        parsed = p.match(pname)
        par_class = parsed.group(1)
        par_name  = parsed.group(2)
        if ptype=="Integer":
            value=int(pvalue)
        elif ptype=="Boolean":
            value=pvalue=="true"
        else:
            value=pvalue
        par_classes[par_class][make_short_name(par_name)]=value

    for cname, cvalues in par_classes.items():
        ovalues = OrderedDict(sorted(cvalues.items()))
        if cname in ["Level"]:
            continue
        f.write("class {}:\n".format(cname.upper()))
        for n,v in ovalues.items():
            f.write("    {} = {}\n".format(n,v))
        f.write("\n")
        # f.write("{} : {},\n".format(name,value))
    # f.write("}\n")

