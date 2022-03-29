from typing import Dict, Type, List, Any, Optional
from .helpers import check_urls

class EmptyMixin:
    @property
    def is_empty(self):
        return all(not i for i in self.__dict__.values())

    def not_empty(self) -> dict:
        return {i:j for i, j in filter(lambda i: i[1], self.__dict__.items())}
    
    def only_value(self):
        v = [i for i in self.not_empty().values()]
        if len(v) == 1:
            return v[0]
        return v

class Structure(EmptyMixin):
    name: str
    description: List[str]
    examples: List[str]
    extra: Optional[Dict[str, Any]]
    def __init__(self, name: str='', docstring: str=[], **kwargs) -> None:
        self.set_name(name or '')
        self.set_description(docstring or [])
        self.examples = []
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def set_name(self, name: str):
        self.name = name.strip('#').strip().replace('-','_').replace('`','')

    def set_description(self, description: List[str]):
        if type(description) is not list:
            description = [description]
        description = [check_urls(i) for i in description if type(i) not in {dict, list}]
        self.description = '\n'.join(description)

    def append_description(self, description: List[str]):
        if type(description) is str:
            description = [description]
        description = [check_urls(i) for i in description if type(i) not in {dict, list}]
        if type(self.description) is list:
            description = self.description + description
        else:
            description = [self.description] + description
        self.description = '\n'.join(description)

class Parameter(Structure):
    type: Type = None
    optional: bool = False
    array_size: Optional[int] = 0
    mapping_type: Optional[List[str]] = None
    default: Optional[Any] = None

class Table(Structure):
    parameters: List[Parameter]
    
    def __init__(self, name: str='', docstring: str=[], parameters: List[Parameter]=None, **kwargs) -> None:
        self.parameters = parameters or []
        super().__init__(name=name, docstring=docstring, **kwargs)

class Endpoint(Table):
    method: str = ''
    path: str = ''
    return_type: str = None
    required_permissions: Optional[List[str]]
    query_parameters: Optional[List[Parameter]]
    json_parameters: Optional[List[Parameter]]
    return_list: Optional[bool] = None
    return_mapping: Optional[bool] = None
    response: Optional[List[Parameter]] = None

    def set_return(self):
        returns = ['']
        if 'Return' in self.description:
            from .patterns import return_pattern
            returns = return_pattern.findall(self.description)
            if returns == []:
                from .patterns import return_empty_pattern
                success = return_empty_pattern.findall(self.description)
                if success != []:
                    returns = ['None']
                elif returns == []:
                    #from .patterns import alt_return
                    #returns = alt_return.findall(self.description)
                    #if returns == []:
                    returns = ['Dict']
                else:
                    returns = [""]
            if returns != [""]:
                from mlib.utils import title_preserving_caps
                returns = [title_preserving_caps(returns[0]).replace(' ','_')]
            returns = [returns[0].replace('Dm_', '').replace('DM_','')]
        if returns != [''] and 'None' not in returns[0] and 'Dict' not in returns[0]:
            self.return_type = returns[0]
            from .patterns import returns_list
            if returns_list.search(self.description):
                self.return_list = True
            else:
                self.return_list = False
        else:
            self.return_list = False
        if not self.return_type and self.method == 'GET':
            self.return_type = 'Dict' #Because GET should return ANYTHING since THAT'S THE WHOLE POINT OF IT, we are doing sort of "catch all" with this here

    def set_permissions(self):
        from .patterns import require_permission_pattern
        self.required_permissions = [i.strip("'").strip("`") for i in require_permission_pattern.findall('\n'.join(self.description))]

    def set_method(self, method: str):
        self.method = method.strip()

    def set_path(self, path: str):
        from .patterns import path_object, path_parameters
        self.path = path_object.sub("}", path_parameters.sub(r'\1_\2', path)).strip()

    def set_path_params(self):
        from .patterns import params_pattern, path_object
        path_params = params_pattern.findall(path_object.sub("}", self.path))
        parameters = [c.strip() for c in path_params]
        self.parameters = list(dict.fromkeys(parameters))

    def add_param(self, name: str, parameter: Parameter):
        if 'query' in name.lower():
            self.query_parameters.append(parameter)
        elif 'json' in name.lower():
            self.json_parameters.append(parameter)

    def add_params(self, name: str, parameters: List[Parameter]):
        if all(i not in name.lower() for i in {'json', 'query'}):
            return
        for param in parameters:
            if type(param) is Parameter:
                self.add_param(name, param)
            else:
                return
        return True

    def __init__(self, doc: str):
        '''Call `.set_permissions` and `.set_return` after setting description. Additionaly, append `query` and `json` params'''
        line = [i.strip() for i in doc.split('%', 1)]
        self.set_name(line[0])
        method, path = line[1].split(' ', 1)
        self.set_method(method)
        self.set_path(path)
        self.set_path_params()
        self.query_parameters = []
        self.json_parameters = []
        self.description = []
        self.required_permissions = []
        self.examples = []
        if self.description:
            #self.set_description(doc)
            self.set_permissions()
            self.set_return()


class Model(Table):
    _type: str
    methods: List[Endpoint]

class Codeblock(EmptyMixin):
    text: List[str]

    def __init__(self) -> None:
        self.text = []

class Section(EmptyMixin):
    name: str
    text: List[str]
    codeblock: List[Codeblock]
    subsections: Dict[str, 'Section']

    def __init__(self, name=None) -> None:
        self.name = name
        self.text = []
        self.codeblock = []
        self.subsections = {}

class ParsedSection(Section):
    endpoint: Endpoint
    model: Model
    examples: List[str]

    def __init__(self, name=None) -> None:
        self.endpoint = None
        self.model = None
        self.examples = []
        super().__init__(name=name)