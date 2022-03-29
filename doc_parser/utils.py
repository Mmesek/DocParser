from typing import List, Dict, Any
from .models import Structure, Section

def open_doc(doc: str) -> List[str]:
    from os.path import dirname
    doc = dirname(__file__)+f"/markdowns/{doc}.md"

    with open(doc,'r',encoding='utf-8') as file:
        lines = [i for i in file.readlines()]
    return lines

def as_dict(object: object) -> Dict[str, Any]:
    from datetime import datetime
    if isinstance(object, Structure):
        d = {}
        for key, value in object.not_empty().items():#object.__dict__.items():
            d[key] = as_dict(value)
        return d
    elif type(object) is dict:
        _object = {}
        for key, value in object.items():
            if value is None:
                continue
            _object[key] = as_dict(value)
        return _object
    elif type(object) is list:
        return [as_dict(key) for key in object]
    elif isinstance(object, datetime):
        return object.isoformat()
    elif type(object) is type:
        return object.__name__
    return object

def save_json(name: str, f: List[Structure]) -> None:
    if f == [[]]:
        return
    f = as_dict(f)
    _f = {"array":[]}
    for i in f.values():
        i.pop('examples', None)
        if type(i) is dict and i.get("name"):
            _name = i.pop("name")
            _f[_name] = i
        else:
            _f["array"].append(i)
    import json
    with open(f'results/jsons/{name}.json', 'w', newline='', encoding='utf-8') as file:
        import datetime
        _f["generated_date"] = datetime.datetime.today().strftime('%H:%M %Y/%m/%d')
        json.dump(_f, file, indent=4)

def split_sections(lines: List[str]) -> Section:
    sections = Section()
    key = sections
    section_name = ''
    previous_section = sections
    current_hashtags = 0
    key = sections
    codeblock = False
    for line in lines:
        if '```' == line.strip() and codeblock:
            codeblock = False
            _codeblock.append(line)
            key.codeblock.append(_codeblock)
            continue
        elif '```' in line.strip() and not codeblock and not '\```':
            codeblock = True
            _codeblock = []
        if codeblock:
            _codeblock.append(line)
            continue
        line = line.strip()

        if line.strip().startswith('#'):
            if line.strip('#').strip() in sections.subsections:
                breakpoint
#                key = sections[line]
            #elif line in key:
            #    key = key[line]
            _hashtags=line.count('#')
            line = line.strip('#').strip()
            if (_hashtags >= 2 and '%' in line) or (_hashtags < current_hashtags):
                # New Section
                section_name = line
                if line not in sections.subsections:
                    sections.subsections[line] = Section(line)
                previous_section = sections
                key = sections.subsections[line]
            elif _hashtags == current_hashtags:
                #New section on same level
                section_name = line
                if line not in previous_section.subsections:
                    previous_section.subsections[line] = Section(line)
                key = previous_section.subsections[line]
            elif _hashtags > current_hashtags:
                # New Subsection
                section_name = line
                if line not in key.subsections:
                    key.subsections[line] = Section(line)
                previous_section = key
                key = key.subsections[line]
            current_hashtags = _hashtags
        elif line != '':
            key.text.append(line)
    return sections.only_value()

def check_if_present(parsed: List[str], name: str) -> str:
    if name in parsed:
        name = '_'+name
        return check_if_present(parsed, name)
    return name
