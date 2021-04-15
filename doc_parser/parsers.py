import re
from .helpers import detect_header, parse_columns, check_list, check_urls

object_name_pattern = re.compile(r"\[(.*?)\]\(.*?\)")

def parse_table(section: dict) -> dict:
    try:
        title, docs, fields, values_start = detect_header(section)
    except Exception as ex:
        #print(ex)
        return section
    table = {'_params':[]}
    table['_name'] = title
    table['_docs'] = docs

    for line in section[values_start:]:
        values = parse_columns(line)
        if len(values) == 1:
            table['_docs'].append(values[0].replace('\\*','*'))
        else:
            _table = {}
            for x, field in enumerate(fields):
                if x >= len(values):
                    _table[field] = ""
                    continue
                _is_list, _size, _type = check_list(values[x])
                if _is_list:
                    _table['is_list'] = _is_list
                    _table['size'] = _size
                field = field.lower()
                if field in ['field', 'name']:
                    field = 'name'
                #if field in ['Field', 'Name']:# or field == 'Event' or field == 'ID' or field == 'Flag' or field == 'Code' or field == 'Key' or field == 'Permission' or field == 'Value':
                '''if field in ['Field', 'Name'] or field.lower() in ['id', 'code', 'mode', 'permission', "value"]:
                    if field != 'Code' and 'Code' in fields:
                        field = "type"
                    elif any(i in fields for i in ['Field','Name']):
                        if field not in ["Permission","Code"]:
                            swap_types = True
                    #elif ("Name" in fields or "Field" in fields) and field == "Permission":
                    #    pass
                    #else:
                    if "Name" not in fields:
                        field = "name"
                    try:
                        values[x] = values[x].replace("-", "").replace(" ", "").replace("+", "_")
                    except:
                        values.append('')
                elif field in ['Type', "Value", "Key", "Event", "Flag"]:
                    if "Type" not in fields:
                        field = "type"
                    try:
                        name = object_name_pattern.findall(values[x].replace('\*', ''))
                    except IndexError:
                        name = []
                    if name != []:
                        try:
                            values[x] = name[x].title().replace(' ', '_').replace('.', '_').replace("-", "").split('(', 1)[0].strip()
                        except IndexError:
                            values[x] = name[0].title().replace(' ', '_').replace('.', '_').replace("-", "").strip()
                    elif values[x].lower().replace('?','').replace('\*', '').strip() not in ['string','str','int','integer','bigint','binary','boolean','bool','dict','list','array','float']:
                        values[x] = values[x].title().replace('?','').replace('\*', '').strip().replace(' ', '_').split('(', 1)[0].strip()
                    values[x] = values[x].split(';',1)[0].replace('Array_Of_','').replace('List_Of_','')
                    '''
                #if field not in ["description", "explanation"]:
                    #values[x] = values[x].split(';',1)[0].replace('array of ','').replace('list of ','').replace('.', '_').replace("-", "").split('(', 1)[0].strip().replace(' ','_')
                if field == 'default':
                    values[x] = values[x].replace('-','None')
                if values[x] in ['global']:
                    values[x] = '_'+values[x]
                values[x] = values[x].replace("partial","").strip()
                from .utils import cc2jl, title_preserving_caps
                if _type != '' and "type" not in _table and field == 'type':
                    if cc2jl(_type).title() == _type.title().replace(' ','_'):
                        _type = _type.title()
                    _table["type"] = _type#cc2jl(_type).title()
                else:
                    values[x] = check_urls(values[x])
                    values[x] = re.sub(r"#(.*?)}", "}", values[x])
                    objects = object_name_pattern.findall(values[x])
                    if objects != []:
                        values[x] = objects[0]
                        values[x] = title_preserving_caps(values[x]).replace(' ','_')
                    values[x] = values[x].replace("partial","").split("(",1)[0].split(' or ')[0].replace("array of", "").strip()
                    if values[x] != "object" and values[x] != "Object":
                        values[x] = values[x].replace("object","").replace("Object","").strip("_").strip()
                        if values[x] in ['global']:
                            values[x] = '_'+values[x]
                    _table[field] = values[x].replace('?','').replace('\*', '').replace('*','').replace('\$','$').strip()
                if '?' in values[x]:
                    _table["optional"] = True
            if all(i in _table for i in ["type", "name"]):
                if _table["name"].isdigit() and not _table["type"].isdigit():
                    _table["type"], _table["name"] = _table["name"], _table["type"]
            table['_params'].append(_table)

    return table

def parse_endpoint(section: dict) -> dict:
    endpoint = {'_additional':[]}
    for line in section:
        if '%' in line:
            line = [i.strip() for i in line.split('%', 1)]
            endpoint['_name'] = line[0].replace('-','_').replace('`','')
            endpoint['_method'] = line[1].split(' ', 1)[0].strip()
            endpoint['_path'] = line[1].split(' ', 1)[1].strip()
        else:
            endpoint['_additional'].append(line)
    return endpoint