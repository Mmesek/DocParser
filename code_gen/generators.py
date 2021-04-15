import json
from utils import cc2jl
with open('templates/python.json','r',newline='',encoding='utf-8') as file:
    _ = json.load(file)

language = _.get("language")
function = _.get("function")
types = _.get("types")
_values = _.get("values")
_default_values = _.get("default_values")
_documentation = _.get("documentation")
_structure = _.get("structure")


with open('templates/discord.json','r',newline='',encoding='utf-8') as file:
    _discord = json.load(file)
_translations = _discord.get("translations")

ENUMS = ["type", "code", "events", "level", "tier", "endpoints", "enum", "versions", "commands", "features", "modes", "options", "urls", "scopes", "formats", "limits", "behavior"]

def iterate_params(params, get="description"):
    for i in params:
        name = "name"
        if i.get(name, i.get("id", "")).isdigit():
            name = "type"
        name = i.get(name, i.get("field", i.get("permission", i.get("flag", i.get("type", i.get("code", i.get("event", i.get("level", i.get("feature", i.get("key", i.get("mode", i.get("status", i.get("description", "")))))))))))))
        yield name, i.get(get, "")

def documentation(structure: dict, scope) -> str:
    doc = structure.get("description",[])
    if _documentation.get("perMember"):
        return _documentation.get("object").format(DOC=f"\n{addIndentation(scope)}".join(doc))
    _doc = []
    for name, desc in iterate_params(structure.get("variables", [])):
        if desc != '':
            _doc.append(language.get("param_docstring").format(NAME=name, DESC=desc, INDENTATION=addIndentation(1)))

    for name, desc in iterate_params(structure.get("query_params", [])):
        if desc != '':
            _doc.append(language.get("param_docstring").format(NAME=name, DESC=desc, INDENTATION=addIndentation(1)))

    for name, desc in iterate_params(structure.get("json_params", [])):
        if desc != '':
            _doc.append(language.get("param_docstring").format(NAME=name, DESC=desc, INDENTATION=addIndentation(1)))

    if _doc != []:
        if doc != []:
            doc.append("")
        doc.append("Params\n"+addIndentation(1)+"------")
    doc += _doc
    if doc == []:
        return ""
    return _documentation.get("object").format(DOC=f"\n{addIndentation(scope)}"+f"\n{addIndentation(scope)}".join(doc)+f"\n{addIndentation(scope)}")

def iterate_variables(variables):
    params = []
    default_params = []
    for variable in variables:
        name = variable.get("name", "Any").replace("/",'_').replace("`",'').split('(',1)[0].strip().replace(" ","_").strip("$").replace('.','_')
        type = types.get(variable.get("type", "Any").lower().replace(" ","_"), cc2jl(variable.get("type", "Any")))
        if type in _translations:
            type = _translations.get(type)
        _type = type
        if variable.get("is_list", False):
            type = types.get("list").format(TYPE=type)
        if "default" in variable:
            default = variable.get("default")
            value = _values.get(default, default).replace("/",'_').replace("`",'').split('(',1)[0].strip().replace(" ","_")
            if value == "":
                value = _default_values.get(type,_default_values.get("none"))
            elif type == types.get("string"):
                if value[0] not in ["'", '"']:
                    value = language.get("string") + value + language.get("string")
            default_params.append(language.get("defaultParameter").format(VARIABLE=name, TYPE=type, VALUE=value))
#        elif variable.get("optional", False):
        else:
            default_params.append(language.get("defaultParameter").format(VARIABLE=name, TYPE=types.get(_type.lower(), type), VALUE=_default_values.get(_type.lower(), 'None')))
 #           params.append(language.get("parameter").format(VARIABLE=name, TYPE=type))
    params = ", ".join(params + default_params)
    if params == "":
        return []
    return [params]
from utils import addIndentation
def function_definition(structure: dict, name: str) -> str:
    name = name.lower().replace("/",'_').replace("`",'').split('(',1)[0].strip().replace(" ","_")

    parameters = [language.get("parameter").format(VARIABLE=i, TYPE=types.get("integer")) for i in structure.get("parameters")]
    typed_parameters = iterate_variables(structure.get("query_params", []) + structure.get("json_params", []))
    parameters = ", ".join(["self"] + parameters + typed_parameters)
    type = cc2jl(structure.get("return"))
    if type in _translations:
        type = _translations.get(type)

    body = language.get("openScope")+"\n"
    if _documentation.get("place") == "below":
        body += addIndentation(1) + documentation(structure, 1) + "\n"
    args = [("path", 'f"'+structure.get("path")+language.get("string")), ("method", language.get("string")+structure.get("method")+language.get("string"))]
    _p = "{"+', '.join([language.get("json_member").format(VARIABLE=i.get("name"), VALUE=i.get("name")) for i in structure.get("query_params", [])])+"}"
    if _p != "{}":
        args.append(("params", _p))
    _j = "{"+', '.join([language.get("json_member").format(VARIABLE=i.get("name"), VALUE=i.get("name")) for i in structure.get("json_params", [])])+"}"
    if _j != "{}":
        args.append(("json", _j))
    args = [language.get("argument").format(PARAMETER=i[0],VALUE=i[1]) for i in args if i != ()]
    body += addIndentation(1)
    if structure.get("return", None):
        body += "r = "
    body += function.get("api_call").format(PARAMETERS=", ".join(args))#"not_impl")
    if structure.get("return", None):
        body += "\n"+addIndentation(1)
        if not structure.get("return_list", False):
            body += function.get("returnSyntax").format(RETURN=type)+"(**r)" #TODO
        else:
            body += function.get("returnListSyntax").format(TYPE=type, UNPACK=language.get("unpack"), RETURN="r") #TODO
            type = types.get("list").format(TYPE=type)
    func = ''
    if structure.get("required_permission") != []:
        func += function.get("decorator").format(NAME="Permissions", PARAMETERS=", ".join(['"%s"' % i for i in structure.get("required_permission")]))+'\n'
    func += function.get("definition").format(NAME=name, PARAMETERS=parameters, TYPE=type, BODY=body)
    return func

def structure(structure: dict, name: str) -> str:
    name = name.replace("/",'_').replace("`",'').split('(',1)[0].strip().replace(" ","_").replace("_Structure","")
    docs = language.get("openScope")+"\n"
    body = ""
    constructor = ""
    slots = []
    parameters = []
    if _documentation.get("place") == "below":
        if "Type" in name:
            breakpoint
        d = documentation(structure, 1)
        if d !="":
            docs += addIndentation(1) + d + "\n"
    enum_type = set()
    for variable in structure.get("variables", []):
        var_name = variable.get("name", variable.get("field", variable.get("type", variable.get("event", variable.get("flag", variable.get("level", variable.get("feature", variable.get("mode", variable.get("permission", variable.get("key", variable.get("parameter", variable.get("status", variable.get("structure", variable.get("description", "None"))))))))))))))
        type = variable.get("type", variable.get("value", variable.get("code", variable.get("id", variable.get("key", variable.get("integer", variable.get("status", variable.get("path", variable.get("url", variable.get("extension", variable.get("description", "None")))))))))))
        if type.count(' ') > 3:
            type = language.get("string") + type + language.get("string")
        elif var_name.count(' ') > 3:
            var_name = language.get("string") + var_name + language.get("string")
        if var_name == type:
            type = variable.get("value", variable.get("code", variable.get("id", variable.get("key", variable.get("integer", language.get("string")+ variable.get("status", variable.get("path", variable.get("structure", variable.get("url", variable.get("extension", variable.get("description", "None"))))))+language.get("string"))))))
        if var_name.isdigit():
            var_name, type = type, var_name
        if type.isdigit() or "<<" in type:
            var_name = var_name.upper()
        if any(i in type for i in [' ','_']) and not type[0].isdigit():
            type = type.title().replace(' ','_')
        if type[0] not in ['"',"'"]:
            type = type.replace(",","").replace(".","_").replace("'",'').replace('"','').split('(',1)[0].strip()
        type = types.get(type.lower().strip(), cc2jl(type)).strip('_').replace('`','').replace('.','_')
        if type in _translations:
            type = _translations.get(type)
        if variable.get("is_list", False):
            _type = type
            type = types.get("list").format(TYPE=type)
        var_name = var_name.replace('$','').replace('`','').replace(' ','_').replace("+","").replace('.','_').strip()
        if var_name[0] not in ['"',"'"]:
            var_name = var_name.replace("'",'').replace('"','')
        enum_type.add(type)
        #TODO: docstring per member
        _v = _structure.get("variable")
        slots.append(var_name)
        if any(i in name.lower() for i in ENUMS+["flags"]):
            _v = _structure.get("enumVariable")
#        if "default" not in variable:
#            if var_name != "None":
            if any(i in name.lower() for i in ["urls", "image_format"]):
                type = f'"{type}"'
            body += addIndentation(1) + _v.format(VARIABLE=var_name, TYPE=type) + '\n'
        else:
            default = variable.get("default", "None").replace('`','')
            default = _values.get(default, default)
            if type == types.get("string"):
                if default[0] not in ["'", '"']:
                    default = language.get("string") + default + language.get("string")
            if default in ["-","+",""] or default in ["None", '"None"']:
                default = _default_values.get(type,_default_values.get('none'))
            body += addIndentation(1) + _structure.get("defaultVariable").format(VARIABLE=var_name, TYPE=type, VALUE=default) + '\n'
            constructor += addIndentation(2) + _structure.get("memberAssigment").format(VARIABLE=var_name, TYPE=type, VALUE=_structure.get("cast").format(TYPE=type+'.fromisoformat' if type == 'datetime' else type, UNPACK=language.get("unpack") if type not in ['str','int', 'Snowflake', 'bool', 'datetime'] else '', VALUE=var_name, DEFAULT=default)
            if not variable.get("is_list") else
            _structure.get("list_cast").format(TYPE=_type+'.fromisoformat' if _type == 'datetime' else _type, UNPACK=language.get("unpack") if _type not in ['str','int', 'Snowflake', 'bool', 'datetime'] else '', VALUE=var_name, DEFAULT=default)
            ) + '\n'

    if 'slots' in language.get('additional', []) and not any(i in name.lower() for i in ENUMS+["flags"]):
        slots = addIndentation(1)+_structure.get("slots").format(VARIABLES="', '".join(slots))+'\n'
    else:
        slots = ""
    d = "definitionInheritance"
    parent = "DiscordObject"
    constructible = True
    if "flag" in name.lower():
        parent = _structure.get("flag")
        d = "definitionInheritance"
        constructible = False
    elif any(i in name.lower() for i in ENUMS):
        parent = _structure.get("enum")
        d = "definitionInheritance"
        constructible = False
    struct = ''
    if parent not in [_structure.get('flag'),_structure.get('enum')]:
        struct += language.get("decorator").format(NAME="dataclass")+'\n'
    enum_type = list(enum_type)[0]
    if body == "":
        return ""
    body = docs+slots+body
    if _structure.get("requireConstructor", False) and constructible:
        body += addIndentation(1) + _structure.get("constructor").format(PARAMETERS=', '.join(iterate_variables(structure.get("variables"))))+ language.get("openScope") +"\n" + constructor + "\n"
    struct += _structure.get(d).format(NAME=cc2jl(name), PARENT=parent, TYPE=enum_type, BODY=body+'\n\n')
    return struct

def route(structure: dict, name: str) -> str:
    return ""

def enum_of_routes(routes: list) -> str:
    return ""

def package_file(file_names: str) -> str:
    return ""
