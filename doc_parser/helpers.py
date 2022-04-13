from typing import Tuple
from .patterns import *

def check_urls(doc: str) -> str:
    urls = url_pattern.findall(doc)
    for url in urls:
        nurl = url.replace('/','#').lower().replace('#docs_', 'https://discord.com/developers/docs/').replace('_', '/',1)
        doc = doc.replace(url, nurl)
    return doc

def check_list(field: str) -> Tuple[bool, int, str]:
    is_list = False
    size = 0
    _type = ''
    if 'list of' in field or 'array of' in field:
        returns = returns_array_custom_type_pattern.findall(field)
        if returns != []:
            if returns[0][1] != '':
                _type = check_urls(returns[0][1].replace(' ', '_').split(',',1)[0])
        else:
            returns = returns_array_base_type_pattern.findall(field)
            if returns != [] and returns[0][1] != '':
                _type = check_urls(returns[0][1].replace(' ', '_').split(',',1)[0])
        is_list = True
        digit = digits_pattern.findall(field)
        if digit != []:
            size = digits.get(digit[0], digit[0])
            size = int(size)
            _type = _type.split("(")[0]
            try:
                _type = _type.split("_")[1]
            except IndexError:
                pass
            #if _type == "Integers":
            #    _type = "integer"
        if is_list and (any(i in _type[-2].lower() for i in ['e','t','r']) and _type.lower().strip()[-1] == 's') or _type.lower() in ['integers', 'strings']:
            _type = _type.strip()[:-1]
    return is_list, size, _type

def check_dict(field: str) -> Tuple[bool, str, str]:
    is_dict = False
    key_type = ''
    value_type = ''
    if 'map of' in field.lower():
        is_dict = True
        _types = json_custom_type_pattern.findall(field)
        if _types == []:
            _types = json_pattern.findall(field)
            key_type, value_type = _types[0]
        else:
            key_type, value_type = _types[0][:2]
        #breakpoint
        if key_type.lower() == 'id':
            key_type = 'snowflake'
        value_type = value_type.replace('Objects', '').replace('Partial','').strip('_').strip()
    return is_dict, key_type, value_type

def detect_header(section: list) -> Tuple[str, list, list, int]:
    table_started = False
    title = None
    docs = []
    values_start = None
    for x, line in enumerate(section):
        if '#' in line and not '|' in line:
            title = line
        elif not table_started and '#' not in line and '|' not in line:
            docs.append(line)
        column = parse_columns(line)
        if all('---' in value for value in column):
            values_start = x+1
            break
        else:
            fields = column
            table_started = True
    if "Description" not in fields:
        for x, field in enumerate(fields):
            if field in {"Meaning", "Status"}:
                fields[x] = "Description"
                break
    if "Name" not in fields:
        for x, field in enumerate(fields):
            if field in {"Explanation", "Flag", "Event", "Permission", "Type", "Level", "Version", "Status", "Explanation", "Field", "Feature", "Mode", "Key", "Description"}:
                fields[x] = "name"
                break
    if "Value" not in fields:
        for x, field in enumerate(fields):
            if field in {"ID", "Value", "websocket url append", "Code", "Structure", "Style", "Extension", "Path", "URL", "Integer", "Key", "Limit"}:
                fields[x] = "value"
                break
            elif field == "Description" and "Type" not in fields:
                fields[x] = "value"
    return title, docs, fields, values_start

def parse_columns(row: str) -> list:
    return [i for i in [value.strip() for value in row.split('|')] if i != '']
