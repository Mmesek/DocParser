from os.path import dirname
doc = dirname(__file__)+"/docs/resources/Channel.md"

with open(doc,'r',encoding='utf-8') as file:
    f = file.readlines()
sections = {"endpoints":{}}
lastLine = ''
lastSubSection = ''
lastEndpointSection = ''
for line in f:
    headerLevel = line.count("#", 0, 7)
    if headerLevel == 3:
        sections[line] = {"trunk": [], "examples": {}, "structures": {}, "types": {}, "flags": {},
        "json":{}, "query":{}, "params":{}, "limits":{}, "other":{}}
        lastLine = line
        lastSubSection = ''
        lastEndpointSection = ''
    elif headerLevel == 6:
        lastSubSection = line
        _line = line.lower()
        if "example" in _line:
            kind = "examples"
        elif "types" in _line:
            kind = "types"
        elif "structure" in _line:
            kind = "structures"
        elif "flags" in _line:
            kind = "flags"
        elif "json" in _line:
            kind = "json"
        elif "query" in _line:
            kind = "query"
        elif "params" in _line:
            kind = "params"
        elif "limits" in _line:
            kind = "limits"
        else:
            kind = "other"
            print(lastSubSection)
        if lastEndpointSection != '':
            endpointKind = kind
            sections["endpoints"][lastEndpointSection][endpointKind][line] = []
        else:
            sections[lastLine][kind][line] = []
    elif headerLevel == 2 and '%' in line:
        sections["endpoints"][line] = {"trunk": [], "examples": {}, "structures": {}, "types": {}, "flags": {},
        "json":{}, "query":{}, "params":{}, "limits":{}, "other":{}}
        lastEndpointSection = line
        endpointKind = "trunk"

    elif lastLine == '':
        continue
    elif lastSubSection == '':
        sections[lastLine]["trunk"] += [line]
    else:
        if lastEndpointSection in sections["endpoints"]:
            if endpointKind != "trunk":
                sections["endpoints"][lastEndpointSection][endpointKind][lastSubSection] += [line]
            else:
                sections["endpoints"][lastEndpointSection][endpointKind] += [line]
        else:
            sections[lastLine][kind][lastSubSection] += [line]


import parsers
def parseEndpoints(sections, object):
    e = []
    for endpoint in sections[object]:
        e += [parsers.endpointParser(endpoint, sections[object][endpoint])]
    return e


def parseTable(sections, object, kind, structure):
    return parsers.tableParser(structure, kind, sections[object][kind][structure])

f = []
for object in sections:
    if object == "endpoints":
        f += [parseEndpoints(sections, object)]
    else:
        for kind in sections[object]:
            if kind in ["trunk", "examples", "other"]:
                continue
            for structure in sections[object][kind]:
                #if 'Message' in structure:
                    #breakpoint()
                d, v = parseTable(sections, object, kind, structure)
                #if d == '':
                if sections[object]["trunk"] != "":
                    d = sections[object]["trunk"] + [d]
                    sections[object]["trunk"] = ""
                elif d == ["\n"] or d == "\n":
                    d = ""
                f += [{"name":structure.strip('# \n'),"variables":v, "docstring":d}]
import json
with open('results/Channel.json', 'w', newline='', encoding='utf-8') as file:
    import datetime
    f+= [{"generated_date": datetime.datetime.today().strftime('%H:%M %Y/%m/%d')}]
    json.dump(f, file, indent=4)

