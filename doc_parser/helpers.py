import re

return_pattern = re.compile(r"Returns .*? \[(.*?)\]\(.*?\) object")
returns_array_custom_type_pattern = re.compile(r"(array|list) of (?:.*?)?\[(.*?)\](\(.*?\))?")
returns_array_base_type_pattern = re.compile(r"(array|list) of (.*)")
return_empty_pattern = re.compile(r"Returns .*? ?204 .*? success")
digits_pattern = re.compile(r"(?i)(\d+|one|two|three|four|five|six|seven|eight|nine|ten)")

json_pattern = re.compile(r"Map of (.*) to ?(.*)")

url_pattern = re.compile(r"\[.*?\]\((.*?\/).*?\)")

from typing import Dict, Type, List, Tuple, Any
from dataclasses import dataclass, asdict

@dataclass
class Structure:
    name: str
    docstring: List[str]
    def __init__(self, name: str='', docstring: str=[], **kwargs) -> None:
        self.name = name.strip('#').strip()
        self.docstring = docstring
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])
    def as_dict(self):
        _dict = asdict(self)
        for field in _dict:
            if field == '_Client':
                continue
            #if is_dataclass(_dict.get(field)):
            #    _dict[field] = asdict(_dict.get(field))
            else:
                from .utils import as_dict
                _dict[field] = as_dict(_dict.get(field))
        if "_Client" in _dict:
            _dict.pop("_Client")
        return _dict

@dataclass
class Parameter(Structure):
    type: Type = None
    optional: bool = False
    array_size: int = 0
    mapping_type: Type = None
    default: Any = None
@dataclass
class Table(Structure):
    parameters: List[Parameter]
    def __init__(self, name: str='', docstring: str=[], parameters: List[Parameter]=[], **kwargs) -> None:
        self.parameters = parameters
        super().__init__(name=name, docstring=docstring, **kwargs)
@dataclass
class Endpoint(Table):
    required_permissions: List[str]
    query_parameters: List[Parameter]
    json_parameters: List[Parameter]
    method: str = ''
    path: str = ''
    return_type: str = None
    return_list: bool = None
    return_mapping: bool = None
@dataclass
class Model(Table):
    methods: List[Endpoint]


def check_urls(doc: str) -> str:
    urls = url_pattern.findall(doc)
    for url in urls:
        nurl = url.replace('/','#').lower().replace('#docs_', 'https://discord.com/developers/docs/').replace('_', '/',1)
        doc = doc.replace(url, nurl)
    return doc
from typing import Tuple
def check_list(field: str) -> Tuple[bool, int, str]:
    is_list = False
    size = 0
    _type = ''
    if 'list of' in field or 'array of' in field:
        returns = returns_array_custom_type_pattern.findall(field)
        if returns != []:
            if returns[0][1] != '':
                _type = check_urls(returns[0][1].replace(' ', '_'))
        else:
            returns = returns_array_base_type_pattern.findall(field)
            if returns != [] and returns[0][1] != '':
                _type = check_urls(returns[0][1].replace(' ', '_'))
        is_list = True
        digit = digits_pattern.findall(field)
        if digit != []:
            digits = {"one":1, "two":2, "three":3, "four":4, "five":5, "six":6, "seven":7, "eigth":8, "nine":9, "ten":10}
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
        _types = json_pattern.findall(field)
        #breakpoint
        key_type, value_type = _types[0]
        if key_type.lower() == 'id':
            key_type = 'snowflake'
        value_type = value_type.replace('Objects', '').replace('Partial','').strip('_').strip()
    return is_dict, key_type, value_type

def detect_header(section: list) -> Tuple[str, list, list, int]:
    table_started = False
    title = None
    docs = []
    for x, line in enumerate(section):
        if '#' in line and not '|' in line:
            title = line
        elif not table_started and '#' not in line:
            docs.append(line)
        column = parse_columns(line)
        if all('---' in value for value in column):
            values_start = x+1
            break
        else:
            fields = column
            table_started = True
    return title, docs, fields, values_start

def parse_columns(row: str) -> list:
    return [i for i in [value.strip() for value in row.split('|')] if i != '']

def extract_return(doc: str) -> Tuple[str, list]:
    returns = ['']
    r = None
    if 'Return' in doc:
        returns = return_pattern.findall(doc)
        if returns == []:
            success = return_empty_pattern.findall(doc)
            if success != []:
                returns = ['None']
            elif returns == []:
                returns = ['Dict']
            else:
                returns = [""]
        if returns != [""]:
            from .utils import cc2jl, title_preserving_caps
            #if returns[0].replace(' ','_').title() == 
            #returns = [cc2jl(returns[0]).title()]
            returns = [title_preserving_caps(returns[0]).replace(' ','_')]
            #returns = [returns[0].replace(' ','_').title()]
        returns = [returns[0].replace('Dm_', '').replace('DM_','')]
    if returns != [''] and 'None' not in returns[0] and 'Dict' not in returns[0]:
        r = returns[0]
        if 'returns a list of' in doc.lower() or 'returns an array of' in doc.lower():
            return_list = True
        else:
            return_list = False
    else:
        return_list = False
    return r, return_list
