import json
from generator_utils import *
def load_language(language):
    with open(f"templates/{language}.json", "r", newline="", encoding="utf-8") as file:
        _ = json.load(file)
    global syntax, enum, func, types, values, sizes, l, methods

    syntax = _["structure"]
    enum = _["enum"]
    func = _["function"]
    types = _["types"]
    values = _["values"]
    sizes = _["sizes"]
    l = _["language"]
    methods = _["methods"]
    return syntax, enum, func, types, values, sizes, l, methods

def check_sizes(variables):
    ordered = sorted(variables, key=lambda x: sizes.get(types.get(x["type"], "struct"), 512), reverse=True)
    s = {}
    for v in variables:
        size = sizes.get(types.get(v["type"], "struct"), 512)
        if size not in s:
            s[size] = []
        s[size] += [v]
    f = []
    for v in s:
        f += s[v]

    return ordered

def iterate_variables(o, function=False):
    _enum = False
    if function:
        members = []
    else:
        members = ""
    docs = ""
    enum_type = "int"
    variables = o["variables"]
    for v in variables:
        t = types.get(v.get("type", v.get("flag", "unknown")), v.get("type", v.get("flag", v.get("name", v.get("event", v.get("status", v.get("docstring","")))))))
        if " or " in t:
            t = t.split(" or ")[-1]
        name = v.get("value", v.get("id", v.get("name", v.get("status", v.get("type", '""')))))
        if "Types" in o["name"] or "Flags" in o["name"] or "Events" in o["name"]:
            if not name.isdigit() and "<<" not in name:
                enum_type = types.get("string","string")
                if name[0] != '"':
                    name = f'"{name}"'
            elif ">>" in name or "<<" in name:
                enum_type = types.get("int","int")
            t = t.upper().replace(" ", "_").replace('-','_')
        if "optional" in v:
            t = types.get("nullable", "{TYPE}").format(TYPE=t)
        if "is_list" in v:
            t = types.get("list", "{TYPE}").format(TYPE=t, SIZE=v.get('size',""))
        if "Structure" in o["name"]:
            member = syntax["variable"].format(TYPE=types.get(t, t), VARIABLE=name)
        elif "function" in o["name"]:
            member = {"variable": name, "type": types.get(t, t)}
            member['required'] = v.get('required', True)
            member['default'] = v.get('default', '')
        else:
            member = enum["member"].format(MEMBER=t, VALUE=name)
            name = t
        if v.get("docstring", "") != "":
            docs += multilineMiddle(1) + addIndentation(1) + l["param_docstring"].format(NAME=name, DESC=v["docstring"])
        if not function:
            members += addIndentation(1) + member
        else:
            members += [member]
        if not function and "Types" not in o["name"] and "Flags" not in o["name"] and "Events" not in o["name"]:
            members += l["lineend"]
        elif not function:
            _enum = True
            members += enum["delimeter"]
    if not _enum or function:
        return docs, members, None
    else:
        return docs, members, enum_type

def generate_function(o, constructor=False):
    s = ''
    p = ''
    b = ''
    param_index = []
    d = generate_documentaion(o)
    param_docs = ""
    r = o.get('return', 'null')
    if r == None:
        r = 'null'
    r = types.get(r, r)
    _r = r
    req_perm = ', '.join(['"%s"' % i for i in o.get('required_permission', [])])
    if req_perm != '':
        req_perm = func['decorator'].format(NAME='Permissions', PARAMETERS=req_perm) + '\n'
    if o.get('return_list', False):
        r = types.get('list', '{TYPE}').format(TYPE=r, SIZE=o.get("size",""))
    for param in o.get('parameters', []):
        if 'id' in param:
            param_type = 'snowflake'
        else:
            param_type = 'string'
        if p != '':
            p += ', '
        p += syntax['parameter'].format(TYPE=types.get(param_type, param_type), VARIABLE=param)
    for param_kind in ["json_params", "query_params", "params", "other_params"]:
        if "params" in o.get(param_kind, {}):
            docs, params, none = iterate_variables({"variables":o[param_kind]['params'], "name":"function"}, True)
            if o[param_kind].get("docstring", "") != "":
                d += '\n'+o[param_kind].get("docstring")
            param_docs += docs
            for param in params:
                if p != '':
                    p += ', '
                if True:#param['required'] == "false":
                    if param.get("default", "absent") == "absent" or param.get("default","") == "":
                        val = values.get("none",'""')
                    else:
                        val = param.get("default", values.get("none", '""'))
                    if param["type"] == "int" and ' ' in val:
                        val = val.split(' ')[0]
                    elif param["type"] == "str" and val == '':
                        val = '""'
                    val = values.get(val,val)
                    p += syntax["defaultParameter"].format(TYPE=param["type"].replace(' ','_'), VARIABLE=param["variable"], VALUE=val)
                else:
                    p += syntax["parameter"].format(TYPE=param["type"].replace(' ', '_'), VARIABLE=param["variable"])
                param_index += [param["variable"]]
    s_doc = ''
    if param_docs != "":
        d += multilineMiddle(1) + "Params:" + param_docs + "\n"
    if d != '':
        if l['docstring'] == 'below':
            scope = '    '
            mid = '\n    '
        else:
            mid = '\n  '
            scope = ''
        s_doc += syntax['docstring'].format(DOC=d.replace('\*', '*').replace('\n', mid).rstrip() + '\n'+scope).rstrip() + '\n'
    b = l['openScope'] +'\n' + addIndentation(1) + b
    if l['docstring'] == 'below' and constructor is False:
        b += s_doc + addIndentation(1)
    elif constructor is False:
        s += s_doc
    if o.get('return', None) != None:
        b += func['returnSyntax'].format(RETURN=_r+'()')

    b += '\n' + l['closeScope']
    s += req_perm
    if types.get("constructor") != o["name"]:
        s += func["definition"].format(TYPE=types.get(r, r), NAME=o.get("name").replace("/", "_or_").replace(" ", "_").lower(), PARAMETERS=p, BODY=b)
    else:
        b = ''
        for param in param_index:
            b +=  addIndentation(2) + syntax['memberAssigment'].format(VARIABLE=param, VALUE=param) + l['lineend']
        s += syntax["constructor"].format(PARAMETERS=p) + l['openScope'] +'\n'+ b + addIndentation(1)+ l['closeScope'] +'\n'
    return s+'\n'


def generate_object(o):
    s = ""
    s_doc = ""
    d = generate_documentaion(o)
    # _vars = check_sizes(o['variables'])
    # docs = addIndentation(1) + l['multilineCommentStart']+'\n'
    docs, members, enum_type = iterate_variables(o)
    if docs != "":
        d += multilineMiddle(1) + "Params:" + docs + "\n"
    if d != "":
        if l["docstring"] == "below":
            d += addIndentation(1) + "\n"
            s_doc += (
                syntax["docstring"]
                .format(DOC=d.replace("\*", "*").replace("\n", "\n    ").rstrip() + "\n" + addIndentation(1))
                .rstrip()
            )
        else:
            s_doc += (
                syntax["docstring"].format(DOC=d.replace("\*", "*").replace("\n", "\n  ").rstrip() + "\n").rstrip()
                + "\n"
            )
    if l["docstring"] == "above":
        s += s_doc
    if enum_type == None:
        s += syntax["struct"].format(TYPE=syntax["type"], NAME=o["name"].replace(" ", "_").replace("_Structure", "")) + l["openScope"]
    else:
        if 'flag' in o['name'].lower():
            e = 'flag'
        else:
            e = 'enum'
        s += syntax['struct'].format(TYPE=enum['type'], NAME=enum.get(e, enum.get('enum')).format(NAME=o['name'].replace(' ', '_'), TYPE=enum_type)) + l['openScope']
    if l["docstring"] == "below":
        s += '\n'+addIndentation(1) + s_doc
    s += "\n" + members
    if syntax.get('requireConstructor', False) and not any(i in o['name'].lower() for i in ['type', 'flag', 'event']):
        j = {"name":types.get("constructor",""),"params":{"params":o.get("variables")}}
        s += addIndentation(1) + generate_function(j, constructor=True)
    s += l["closeScope"] + "\n"
    return s

def generate_route(o):
    name = o['name'].upper().replace(' ', '_').replace('/','_OR_')
    val = syntax['route'].format(METHOD=methods.get(o['method'], '"{}"'.format(o['method'])), PATH='"{}"'.format(o.get('path', '')))
    return enum['member'].format(MEMBER=name, VALUE=val)

def generate_enum_of_routes(o):
    m = ""
    for member in o:
        m += addIndentation(1) + member + enum['delimeter']
    if m == "":
        return ""
    s = syntax['struct'].format(TYPE=enum['type'], NAME=enum['enum'].format(NAME='Routes', TYPE='Route')) + l['openScope'] + '\n'
    s+= m
    s+= l['closeScope'] + '\n'
    return s