import re
from .helpers import check_dict, detect_header, parse_columns, check_list, check_urls, Structure, Endpoint, Model, Parameter

object_name_pattern = re.compile(r"\[(.*?)\]\(.*?\)")

def squash_sections(sections: list):
    _sections = []
    current_section = []
    for section in sections:
        if type(section) is list:
            current_section = section
        elif len(current_section) > 0 and ' '.join(section.name.split(' ')[:-1]) in current_section[0].strip('#').strip():
            current_section.append(section)
        else:
            if current_section != []:
                _sections.append(current_section)
                current_section = []
            _sections.append(section)
    return _sections

def parse_table(section: dict) -> Structure:
    try:
        title, docs, fields, values_start = detect_header(section)
    except Exception as ex:
        title = section[0]
        docs = section[1:]
        fields = []
        values_start = None
    m = Model(name=title, parameters=[], methods=[])
    if not values_start:
        m.set_description(docs)
        return m
    for line in section[values_start:]:
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
                from .utils import cc2jl, title_preserving_caps
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
                    if field == 'description':
                        field = 'docstring'
                    setattr(p, field, values[x].replace('?','').replace('\*', '').replace('*','').replace('\$','$').strip())
            if p.type and p.name:
                if p.name.isdigit() and not p.type.isdigit():
                    p.type, p.name = p.name, p.type
            m.parameters.append(p)
    if any(i in m.name.lower() for i in {"type", "modes", "enum"}):
        m.name = re.sub(r"enum|modes", "", m.name, flags=re.IGNORECASE).strip()
        if len(m.name.split(' ')) > 2:
            m.name = re.sub(r"types?", "", m.name, flags=re.IGNORECASE).strip()
        m._type = "enum"
    elif any(i in m.name.lower() for i in {"structure", "object"}):
        #m.name = m.name.rstrip("structure").rstrip("object")
        m.name = re.sub(r"structure|objects?", "", m.name, flags=re.IGNORECASE).strip()
        m._type = "model"
    elif any(i in m.name.lower() for i in {"flags"}):
        m._type = "flag"
    m.set_description(docs)
    return m

def parse_endpoint(section: dict) -> Endpoint:
    endpoint = Endpoint(docstring=[])
    docs = []
    for line in section:
        if type(line) is Model:
            if 'query' in line.name.lower():
                endpoint.query_parameters = line.parameters
            elif 'json' in line.name.lower():
                endpoint.json_parameters = line.parameters
            else:
                endpoint.parameters = line.parameters
            continue
        elif '%' in line:
            line = [i.strip() for i in line.split('%', 1)]
            endpoint.set_name(line[0])
            endpoint.method = line[1].split(' ', 1)[0].strip()
            endpoint.path = re.sub(r"#(.*?)}", "}", line[1].split(' ', 1)[1].strip()).replace(".", "_")
        else:
            
            docs.append(line)
    endpoint.set_description(docs)
    from .utils import require_permission_pattern, extract_return, params_pattern
    endpoint.required_permissions = [i.strip("'").strip("`") for i in require_permission_pattern.findall('\n'.join(endpoint.docstring))]
    endpoint.return_type, endpoint.return_list = extract_return(endpoint.docstring)
    path_params = params_pattern.findall(re.sub(r"#(.*?)}", "}", endpoint.path).replace(".", "_"))
    parameters = [c.strip() for c in path_params]
    endpoint.parameters = list(dict.fromkeys(parameters))
    
    return endpoint