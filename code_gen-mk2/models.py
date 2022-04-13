from dataclasses import dataclass
from re import template
from textwrap import indent
from typing import Any, Optional
from mlib.utils import try_quote, clean, unquote

TEMPLATES = {
    "Object": "name={name}, documentation={documentation}",
    "Parameter": ["{name}", ": {type_}", " = {default}"],
}

import json


def get_templates():
    with open("code_gen-mk2/python.json", "r", newline="", encoding="utf-8") as file:
        return json.load(file)


TEMPLATES = get_templates()


@dataclass
class Type:
    type: type
    key_type: str = None
    value_type: str = None
    is_array: bool = False
    array_size: int = None
    lowercase: bool = False

    def render(self, optional: bool = False, nullable: bool = False):
        TYPES = TEMPLATES.get("types", {})
        _type = TYPES.get(self.type, self.type)
        if self.is_array:
            _type = TYPES.get("array", "{type}").format(type=_type, size=self.array_size)
        if optional:
            _type = TYPES.get("optional", "{type}").format(type=_type)
        if nullable:
            _type = TYPES.get("nullable", "{type}").format(type=_type)
        return _type


@dataclass
class Object:
    """Base Object metadata"""

    name: str
    """Object's name"""
    documentation: str = ""
    """Object's docstring"""
    lowercase: bool = True
    sane_value: bool = True
    constant: bool = False

    def __post_init__(self):
        for field in self.__dict__:
            value = getattr(self, field)
            if value is list:
                self.__setattr__(field, [])

    def __str__(self):
        template = TEMPLATES.get(self.__class__.__name__)
        if type(template) is list:
            s = ""
            for _template in template:
                try:
                    s += _template.format_map({k: v for k, v in self.__dict__.items() if v is not Optional})
                except KeyError:
                    continue
        else:
            s = template.format_map({k: v for k, v in self.__dict__.items()})
        return s

    def render(self):
        pass

    def format_docs(self, **documentation):
        _docs = documentation.get("main")
        if not _docs:
            return
        template = TEMPLATES.get("documentation", {})
        docstring = TEMPLATES.get("docstring", "")  # TODO Move
        INDENT = TEMPLATES.get("indent") * (2 if getattr(self, "is_method", False) else 1)
        docs = indent(TEMPLATES.get("newline").join(_docs).strip(), INDENT)
        if docs.strip():
            return docstring.format(documentation=docs, indent=INDENT, newline=TEMPLATES.get("newline"))

    def format(self, template, **d):
        if not self.name:
            return ""

        d.update(
            {
                "name": clean(self.name),
                "newline": TEMPLATES.get("newline"),
                "documentation": self.format_docs(main=self.documentation),
                "indent": TEMPLATES.get("indent"),
            }
        )
        if self.sane_value and d.get("value", None) not in [None, "None"]:
            v = TEMPLATES.get("values", {}).get(d["value"], d["value"])
            import re

            flag = re.compile("\d+ ?<< ?\d+")
            if not flag.search(v):
                v = try_quote(unquote(v))
            if d["value"] == "absent":
                breakpoint
            d["value"] = v  # try_quote(v)
        if not self.constant and self.lowercase and "name" in d:
            d["name"] = d["name"].lower()
        elif self.constant and d.get("name"):
            d["name"] = d["name"].upper()
        if "Structure" in self.name and not d.get("documentation"):
            breakpoint
        if type(template) is list:
            s = ""
            for _template in template:
                try:
                    s += _template.format_map({k: v for k, v in d.items() if v is not None})
                except KeyError:
                    continue
        else:
            s = template.format_map({k: v for k, v in d.items()})
        return s


@dataclass
class Parameter(Object):
    """Parameter metadata"""

    type_: Type = None
    """Parameter type"""
    optional: bool = False
    """Whether this parameter is optional"""
    nullable: bool = False
    """Whether this parameter is nullable"""
    # array_size: Optional[int] = 0
    """Array size (If it's an array)"""
    # mapping_type: Optional[tuple[str, str]] = Optional
    """Tuple representing key and value types for dictonaries (maps) or array type and item type (lists or sets)"""
    # default: Optional[Any] = Optional
    """Default value"""
    value: Optional[Any] = None
    """Argument or Default value"""
    lowercase: bool = True

    def render(self):
        template = TEMPLATES.get("parameter")

        return self.format(template, type=self.type_.render(self.optional) if self.type_ else None, value=self.value)

    def as_argument(self):
        template = TEMPLATES.get("argument")
        return self.format(template, value=self.value)


@dataclass
class Function(Object):
    """Function metadata"""

    parameters: list[Parameter] = list
    """List of parameters in this function"""
    keyword_only: list[Parameter] = list
    """List of keyword-only parameters in this function"""
    return_type: Type = Type(None)
    """Return type"""
    is_method: bool = False
    """Whether it's a method"""
    decorators: Optional[list["Function"]] = list
    """List of Functions decorating this function"""
    examples: Optional[str] = Optional
    """Example usage of this function"""
    arguments: Optional[list[Parameter]] = list
    # arguments: Optional[list[Argument]] = Optional
    """Arguments to use with this function"""
    lowercase: bool = True

    def with_arguments(self, *arguments: Parameter) -> "Function":
        """Returns Function with specified arguments for function call rendering"""
        return Function(name=self.name, arguments=arguments)

    def render(self):
        template = TEMPLATES.get("function" if not self.is_method else "method", {})
        decorators = "\n".join([d.as_decorator() for d in self.decorators])
        decorators = indent(decorators, TEMPLATES.get("indent") * (0 if not self.is_method else 1))
        parameters = ", ".join([p.render() for p in self.parameters])
        kwargs = ", ".join([k.render() for k in self.keyword_only])
        if not kwargs:
            breakpoint
        all_params = []
        if parameters:
            all_params.append(parameters)
        if kwargs:
            all_params.append(TEMPLATES.get("keyword_only"))
            all_params.append(kwargs)
        params = ", ".join(all_params)
        s = self.format(
            template.get("definition"),
            async_keyword=TEMPLATES.get("async"),
            parameters=params,
            decorators=decorators,
            return_type=self.return_type.render(),
        )
        return s

    def as_call(self):
        template = TEMPLATES.get("function", {})
        return self.format(
            template.get("call", ""), arguments=", ".join([a.as_argument() for a in self.arguments if a.value])
        )

    def as_decorator(self):
        template = TEMPLATES.get("decorator", "")
        return self.format(template, arguments=", ".join([a.as_argument() for a in self.arguments if a.value]))


@dataclass
class Class(Object):
    """Class metadata"""

    bases: list["Class"] = list
    """Types this Class inherits from"""
    attributes: list[Parameter] = list
    """Atributes/Fields of this Class"""
    methods: Optional[list[Function]] = list
    """List of methods attached to this Class"""
    examples: Optional[str] = Optional
    """Example usage of this Class"""
    lowercase: bool = False

    def render(self):
        if any(
            i in self.name.lower()
            for i in {
                "type",
                "enum",
                "mode",
                "limits",
                "level",
                "tier",
                "features",
                "behaviours",
                "versions",
                "commands",
                "events",
                "opcodes",
                "url",
                "scope",
                "error",
                "format",
                "style",
                "endpoint",
            }
        ):
            _type = "enum"
        elif "flag" in self.name.lower():
            _type = "flag"
        else:  # if "structure" in self.name.lower():
            # elif any(i in self.name.lower() for i in {"structure", "fields", "object", "response", "params", "properties", "parameters", "activity", "info"}):
            _type = "class"
        from mlib.utils import replace_multiple

        self.name = replace_multiple(self.name, TEMPLATES.get("to_strip", []), "").strip()

        template = TEMPLATES.get(_type, {})
        if _type in {"enum", "flag"}:
            for a in self.attributes:
                a.constant = True
                # if a.name is not None:
                #    a.name = a.name.upper()
            # self.attributes = [a.name.upper() for a in self.attributes if a.name]
        attributes = indent("\n".join([a.render() for a in self.attributes]), TEMPLATES.get("indent"))
        methods = "\n".join([m.render() for m in self.methods])
        bases = ", ".join(self.bases)
        s: str = self.format(template.get("definition"), bases=bases, attributes=attributes, methods=methods)
        if len(set([i.strip() for i in s.splitlines()])) <= 1:
            return ""
        return s
