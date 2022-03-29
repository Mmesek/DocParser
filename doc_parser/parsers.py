import re
from .helpers import check_dict, detect_header, parse_columns, check_list, check_urls
from .models import Parameter, Section, Table, Endpoint
from .patterns import object_name_pattern

from typing import List

def parse_table(text: List[str]) -> Table:
    title, docs, fields, values_start = detect_header(text)
    _params = []
    if not values_start:
        return Table(title, docs, [])
    for line in text[values_start:]:
        values = parse_columns(line)
        if len(values) == 1:
            docs.append(values[0].replace('\\*','*'))
        else:
            p = Parameter(docstring=[])
            for x, field in enumerate(fields):
                field = field.lower()
                if field in ['field', 'name']:
                    field = 'name'
                if x >= len(values):
                    continue
                _is_list, _size, _type = check_list(values[x])
                if '?' in values[x]:
                    p.optional = True
                if _is_list:
                    p.array_size = _size
                else:
                    _is_dict, key_t, _type, = check_dict(values[x])
                    if _is_dict:
                        p.mapping_type = [key_t, _type]
                        p.type = "mapping"
                        continue
                if field == 'default':
                    values[x] = values[x].replace('-','None')
                if values[x] in ['global']:
                    values[x] = '_'+values[x]
                values[x] = values[x].replace("partial","").strip()
                from mlib.utils import cc2jl, title_preserving_caps
                if p and p.type != None and field == 'type':
                    if cc2jl(_type).title() == _type.title().replace(' ','_'):
                        _type = _type.title()
                    p.type = _type
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
                    if field == 'docstring':
                        field = 'description'
                    setattr(p, field, values[x].replace('?','').replace('\*', '').replace('*','').replace('\$','$').strip())
            if p.type and p.name:
                if p.name.isdigit() and not p.type.isdigit():
                    p.type, p.name = p.name, p.type
            _params.append(p)
    return Table(title, docs, _params)

def parse_endpoint(section: Section, table: Table) -> Endpoint:
    endpoint = Endpoint(section.name)
    if type(table) is str:
        endpoint.append_description(table)
    else:
        endpoint.append_description(table.name)
        endpoint.append_description(table.description)
    endpoint.set_permissions()
    endpoint.set_return()
    return endpoint