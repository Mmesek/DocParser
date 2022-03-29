from doc_parser.utils import check_if_present
from typing import Dict, Tuple
from .parsers import parse_table, parse_endpoint
from .models import Endpoint, Model, Section, ParsedSection, Structure, Table

def check_parameters(section, _section, s):
    _added = False
    if 'query' in section.name.lower():
        #print_values(s)
        _added = True
        for param in s if type(s) is list else s['parameters'] if type(s) is dict else s.text if type(s.text) is list else s.text.parameters:
            _section.endpoint.query_parameters.append(param)
    elif 'json' in section.name.lower():
        #print_values(s)
        _added = True
        for param in s if type(s) is list else s['parameters'] if type(s) is dict else s.text if type(s.text) is list else s.text.parameters:
            _section.endpoint.json_parameters.append(param)
    if getattr(s, 'text', None) and type(s.text) is not list:
        if type(s.text) is str or s.text.name:
            if _section.endpoint.description == '':
                _section.endpoint.description = []
            _section.endpoint.append_description(s.text.name if type(s.text) is not str else s.text)
            if type(s.text) is str:
                s.text = None
            else:
                s.text.name = None
            _added = True
        if s.text and type(s.text) is not str and s.text.description:
            _section.endpoint.append_description(s.text.description)
            s.text.description = None
            _added = True
        if len(s.codeblock):
            _section.endpoint.append_description(s.codeblock)
            s.codeblock = []
            _added = True
    elif type(s) is dict:
        _section.endpoint.append_description(s.get('name', ''))
        #if 'text' in s:
        #    _section.endpoint.append_description(s.get('text', ''))
        _section.endpoint.append_description(s.get('description', ''))
        #if 'codeblock' in s:
        #    _section.endpoint.examples.append(s.get('codeblock'))
        _added = True
    return _added

def parse_section(section: Section) -> ParsedSection:
    _section = ParsedSection()
    if section.text != []:
        t = parse_table(section.text)
        if len(t.not_empty()) == 1:
            _section.text = [i for i in t.not_empty().values()][0]
        #    print(t.not_empty().keys())
        else:
            _section.text = t# if t.parameters else t.docstring
    if section.codeblock != []:
        _section.codeblock = section.codeblock
    if section.name:
        if '%' in section.name:
            parse_endpoint(section, _section)
            
        _section.name = _section.name or section.name

    for subsection in section.subsections.values():
        s = parse_section(subsection)
        _added = False
        if _section.endpoint and not 'example' in subsection.name.lower():
            _added = check_parameters(subsection, _section, s)
        if not _added and ('example' in subsection.name.lower()) or (subsection.codeblock and not subsection.subsections):
            if _section.endpoint:
                _section.endpoint.examples.append(subsection)
                _added = True
            else:
                _section.examples.append(subsection)
                _added = True
        if not _added:
            if type(s) is ParsedSection and not s.is_empty:
                _section.subsections[s.name if s.name else subsection.name] = s
            elif hasattr(s, 'name'):
                _section.subsections[s.name if s.name else subsection.name] = s
            elif s:
                _section.subsections[subsection.name] = s

    if not _section.subsections and not _section.codeblock:
        if _section.endpoint and _section.name == _section.endpoint.name and not _section.model and not _section.text:
            return _section.endpoint
        elif _section.model and _section.name == _section.model and not _section.endpoint and not _section.text:
            return _section.model
        elif len(_section.not_empty()) == 1 and not _section.text:
            return [i for i in _section.not_empty().values()][0]
        elif type(_section.text) in {ParsedSection, Table} and len(_section.text.not_empty()):
            return {i: j for i, j in _section.text.not_empty().items()}

    elif _section.not_empty():
        return _section.not_empty()

    return _section

def parse_section(section):
    if section.text:
        return parse_table(section.text)
    return Table()


def extract_endpoints(sections: Dict[str, Section]) -> Tuple[Dict[str, Endpoint], Dict[str, Section]]:
    _endpoints = {}
    _sections = {}
    for key, section in sections.items():
        if '%' in key:
            endpoint = parse_endpoint(section, parse_section(section))
            for _key, subsection in section.subsections.items():
                is_extra = True
                if 'query' in subsection.name.lower():
                    is_extra = False
                    for param in parse_section(subsection).parameters:
                        endpoint.query_parameters.append(param)
                if 'json' in subsection.name.lower():
                    is_extra = False
                    for param in parse_section(subsection).parameters:
                        endpoint.json_parameters.append(param)
                if subsection.codeblock:
                    is_extra = False
                    endpoint.examples.append(subsection)
                if 'Response' in subsection.name and is_extra:
                    is_extra = False
                    t = parse_section(subsection)
                    endpoint.response = t.only_value()
                if is_extra:
                    if not subsection.codeblock and not subsection.subsections:
                        if subsection.name:
                            endpoint.append_description(subsection.name)
                        if subsection.text:
                            endpoint.append_description(subsection.text)
                    else:
                        endpoint.extra[_key] = subsection
                endpoint.set_permissions()
                endpoint.set_return()
            _endpoints[endpoint.name] = endpoint
        else:
            _sections[key] = section
    return _endpoints, _sections

class Attribute:
    name: str
    value: str
    can_type: bool = False
    #can_value: bool = True
    can_name: bool = True
    @property
    def can_name(self):
        return not self.value.isdigit() and not self.value[0].isdigit() and ' ' not in self.value and not '"' in self.value
    def can_type(self):
        return not self.value.isdigit() and not self.value[0].isdigit() and ' ' not in self.value and not '"' in self.value

    def __init__(self, name, value) -> None:
        self.name = name
        self.value = value
from typing import List
def parse_parameters(objects: Dict[str, Model]) -> Dict[str, Model]:
    for object in objects.values():
        for parameter in object.parameters:
            collect: List[Attribute] = []
            for name, attr in parameter.not_empty().items():
                if name not in {'array_size', 'optional', 'mapping_type'}:
                    collect.append(Attribute(name, attr))
            for attr in collect:
                if attr.name not in {'description', 'value'} and (attr.value.isdigit() or attr.value[0].isdigit() or ' ' in attr.value):
                    breakpoint
                else:
                    breakpoint
                if attr.name in {'description', 'default', 'name', 'type'}:
                    #Correct name!
                    breakpoint
                else:
                    if attr.can_name and not parameter.name:
                        #attr.name = 'name'
                        setattr(parameter, 'name', attr.value)
                        setattr(parameter, attr.name, None)
                    elif not parameter.default:
                        setattr(parameter, 'default', attr.value)
                        setattr(parameter, attr.name, None)
                        #attr.name = 'default'
                    elif not parameter.description:
                        setattr(parameter, 'description', attr.value)
                        setattr(parameter, attr.name, None)
                    elif attr.name == 'type' and attr.can_type and not parameter.default:
                        setattr(parameter, 'default', attr.value)
                        setattr(parameter, attr.name, None)
                    else:
                        if attr.value.count(' ') < parameter.description.count(' ') and not parameter.name:
                            setattr(parameter, 'name', attr.value.replace(' ', '_'))
                            setattr(parameter, attr.name, None)
                        elif not parameter.name:
                            setattr(parameter, 'name', parameter.description.replace(' ','_'))
                            setattr(parameter, 'description', attr.value)
                            setattr(parameter, attr.name, None)
                        else:
                            #parameter.description += ' - '+ attr.value
                            breakpoint
                        breakpoint
            if parameter.type and not parameter.name:
                parameter.type, parameter.name = parameter.name, parameter.type
            if not parameter.name and parameter.description:
                parameter.description, parameter.name = parameter.name, parameter.description
            if parameter.description and parameter.default and len(parameter.description) < len(parameter.default):
                parameter.description, parameter.default = parameter.default, parameter.description
    return objects

def extract_objects(sections: Dict[str, Section], master: Model=None) -> Tuple[Dict[str, Model], Dict[str, Section]]:
    _sections = {}
    _models = {}
    for key, section in sections.items():
        if section.codeblock and master:
            master.examples.append(section.codeblock)
        t = parse_section(section)
        m = Model(section.name, t.name+t.description, t.parameters)
        for _key, sub in section.subsections.items():
            _m, _s = extract_objects({_key: sub}, m)
            for k, nested_s in _s.items():
                if 'example' in k or nested_s.codeblock:
                    m.examples.append(nested_s)
                else:
                    #m.append_description(nested_s.name)
                    _t = parse_section(nested_s)
                    m.append_description(_t.description)
                    #k = check_if_present(_models, k)
                    #_sections[k] = nested_s
            for k, nested_m in _m.items():
                k = check_if_present(_models, k)
                _models[k] = nested_m
        if m.parameters:
            _models[key] = m
        elif master:
            master.append_description(m.name)
            master.append_description(m.description)
        else:
            _sections[key] = m
    if _sections:
        breakpoint


    return _models, _sections
    

def extract_objects2(sections: Dict[str, Section]) -> Tuple[Dict[str, Model], Dict[str, Section]]:
    _sections = {}
    _models = {}
    for key, section in sections.items():
        if any(i in key for i in {'Object', 'Structure'}):
            t = parse_section(section)
            m = Model(section.name, t.name+t.description, t.parameters)
            t = None
            for _key, sub in section.subsections.items():
                _added = False
                if 'Structure' in _key:
                    t = parse_section(sub)
                    m.append_description(t.description)
                    for param in t.parameters:
                        m.parameters.append(param)
                    t = None
                    _models[key] = m
                elif 'example' in _key.lower() or sub.codeblock:
                    m.examples.append(sub)
                else:
                    _t = parse_section(sub)
                    if _t.parameters:
                        _m = Model(sub.name, _t.description, _t.parameters)
                        _t = None
                        _models[_key] = _m
                    else:#if not m.parameters:
                        m.append_description(_t.name)
                        m.append_description(_t.description)
                        breakpoint
                    _added = True
        else:
            t = parse_section(section)
            m = Model(section.name, t.name+t.description, t.parameters)
            _objects, _sub = extract_objects(section.subsections)
            for k, obj in _objects.items():
                if 'example' in k.lower():
                    m.examples.append(obj)
                else:
                    k = check_if_present(_models, k)
                    _models[k] = obj
            for k, sub in _sub.items():
                if 'example' in k.lower():
                    m.examples.append(sub)
                else:
                    if sub.parameters:
                        k = check_if_present(_models, k)
                        _models[k] = sub
                    k = check_if_present(_sections, k)
                    _sections[k] = sub
            _sections[key] = m#section
    return _models, _sections


def trim_empty(sections: ParsedSection) -> Dict[str, Structure]:
    _sections = {}
    for key, section in sections.items():
        if type(section) in {ParsedSection, Table} and len(section.not_empty()) == 1:
            s = [i for i in section.not_empty().values()][0]
        elif type(section) in {ParsedSection, Table} and len(section.not_empty()):
            s = {i: j for i, j in section.not_empty().items()}
        elif type(section) is dict:
            s = trim_empty(section)
        else:
            s = section
        _sections[key] = s
    if len(_sections) == 1:
        return list(_sections.values())[0]
    return _sections

def split_endpoints(sections):
    _endpoints = {}
    _nested_endpoint = {}
    _objects = {}
    _sections = {}
    for key, section in sections.get('subsections', sections).items():
        if type(section) is Endpoint:
            _endpoints[key] = section
        elif '%' in key or type(section) is dict and 'endpoint' in section:
            _nested_endpoint[key] = section
        elif any(i in key for i in {'Object', 'Resource'}):
            _objects[key] = section
        else:
            _sections[key] = section
    return _endpoints, _nested_endpoint, _objects, _sections

def extract_single(sections):
    _sections = {}
    for key, section in sections.get('subsections', sections).items():
        if type(section) is dict and len(section) == 1:
            _ = [i for i in section.items()][0]
            key, value = _[0], _[1]
            _sections[key] = value
        else:
            _sections[key] = section
    return _sections

def parse_structures(sections):
    _sections = {}
    for key, section in sections.get('subsections', sections).items():
        if type(section) is dict:
            if 'parameters' in section or type(section.get('text', None)) is list:
                m = Model(
                        section.get('name', key), 
                        section.get('description', 
                                    section.get('text', '') if type(section.get('text', '')) is str else ''), 
                        section.get('parameters', 
                                    section.get('text', []) if type(section.get('text', [])) is list else []))
                _sections[key] = m
            else:
                _sections[key] = parse_structures(section)
        else:
            _sections[key] = section
    return _sections

def flatter(sections):
    _sections = {}
    for key, section in sections.get('subsections', sections).items():
        if type(section) in {Model, Endpoint}:
            _sections[key] = section
        else:
            if type(section) is dict:
                for _key, subsection in section.get('subsections', section).items():
                    _sections[_key] = subsection
    return _sections



def make_models(sections: Dict[str, ParsedSection]) -> Dict[str, ParsedSection]:
    _models = {}
    for key, section in sections.items():
        if type(section) is dict:
            m = Model(section.get('name', key), section.get('text', ''))
            if 'subsections' in section:
                if type(section['subsections']) is list:
                    m.parameters = section['subsections']
                elif type(section['subsections']) is dict:
                    for _key, subsection in section['subsections'].items():
                        if type(subsection) is str:
                            m.append_description(subsection)
                        elif type(subsection) is list and "structure" in _key.lower():
                            m.parameters = subsection
                        elif type(subsection) is dict:
                            make_models(subsection)
            _models[key] = m
        else:
            _models[key] = section
    return _models