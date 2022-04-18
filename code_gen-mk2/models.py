import json
import re
from typing import Any, Optional
from dataclasses import dataclass
from textwrap import indent

from mlib.utils import try_quote, clean, unquote, replace_multiple

FLAG = re.compile("\d+ ?<< ?\d+")


def get_templates(_t = "code_gen-mk2/python.json"):
    with open(_t, "r", newline="", encoding="utf-8") as file:
        return json.load(file)


TEMPLATES = get_templates()
TRANSLATIONS = get_templates("templates/discord.json")


@dataclass
class Object:
    """Base Object metadata"""

    name: str
    """Object's name"""
    documentation: str = None
    """Object's docstring"""
    _lowercase: bool = True
    """Whether name should be lowercased"""
    _sanitize_value: bool = True
    """Whether should attempt to sanitize and quote value"""
    _constant: bool = False
    """Whether name should be uppercased in case of constant"""
    _template: str = "parameter"
    """Template to use"""

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
        if self._template == "attribute":
            t = "inline_docstring"
        else:
            t = "docstring"
        params = documentation.get("parameters")

        docstring = TEMPLATES.get(t, "")  # TODO Move
        INDENT = TEMPLATES.get("indent") * (2 if getattr(self, "is_method", False) else 1)

        if type(_docs) is list:
            docs = indent(TEMPLATES.get("newline").join(_docs).strip(), INDENT)
        else:
            docs = _docs
        if docs:
            docs = docs.replace('"',"'")

        if params:
            _params = indent(TEMPLATES.get("newline").join(params).strip(), INDENT)
            s = ""
            d = {"parameters": _params, "indent": INDENT, "newline": TEMPLATES.get("newline")}
            for _template in template.get("parameters"):
                try:
                    s += _template.format_map({k: v for k, v in d.items() if v is not None})
                except KeyError:
                    continue
            docs += TEMPLATES.get("newline") + s.replace("{indent}", INDENT)

        if docs.strip():
            return docstring.format(documentation=docs, indent=INDENT, newline=TEMPLATES.get("newline"))

    def format(self, template, **d):
        if not self.name:
            return ""

        d.update(
            {
                "name": clean(self.name),
                "newline": TEMPLATES.get("newline"),
                "documentation": self.format_docs(main=self.documentation, parameters=d.get("parameters_docs", None)),
                "indent": TEMPLATES.get("indent"),
            }
        )
        if self._sanitize_value and d.get("value", None) not in [None, "None"]:
            v = d["value"]
            if not FLAG.search(v):
                v = try_quote(unquote(v))
            v = TEMPLATES.get("values", {}).get(d["value"], v)

            d["value"] = v
        if not self._constant and self._lowercase and "name" in d:
            d["name"] = d["name"].lower()
        elif self._constant and d.get("name"):
            d["name"] = d["name"].upper()

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
class Type(Object):
    """Type metadata"""

    key_type: str = None
    """Type of Key or main type"""
    value_type: Optional[str] = None
    """Type of value (If mapping)"""
    is_array: bool = False
    """Whether it's an array. If set, empty `array_size` means dynamic array"""
    array_size: Optional[int] = None
    """Array size (If it's an array)"""
    def __post_init__(self):
        self.name = TRANSLATIONS.get("translations", {}).get(self.name, self.name)
        return super().__post_init__()

    def render(self, optional: bool = False, nullable: bool = False):
        TYPES = TEMPLATES.get("types", {})
        _type = TYPES.get(self.name, self.name)
        if self.is_array:
            _type = TYPES.get("array", "{type}").format(type=_type, size=self.array_size)
        if nullable:
            _type = TYPES.get("nullable", "{type}").format(type=_type)
        if optional:
            _type = TYPES.get("optional", "{type}").format(type=_type)
        return _type


@dataclass
class Parameter(Object):
    """Parameter metadata"""

    type_: Type = None
    """Parameter type"""
    optional: bool = False
    """Whether this parameter is optional"""
    nullable: bool = False
    """Whether this parameter is nullable"""
    value: Optional[Any] = None
    """Argument or Default value"""

    def render_docs(self):
        template = TEMPLATES.get("documentation")
        template = template.get("parameter_documentation")
        s = ""
        for _template in template:
            try:
                if self.documentation:
                    s += _template.format(name=self.name, description=self.documentation, indent="{indent}", newline=TEMPLATES.get("newline"))
            except KeyError:
                continue
        return s

    def render(self):
        template = TEMPLATES.get(self._template)

        return self.format(template, type=self.type_.render(self.optional, self.nullable) if self.type_ else None, value=self.value)

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
    """Arguments to use with this function"""

    def with_arguments(self, *arguments: Parameter) -> "Function":
        """Returns Function with specified arguments for function call rendering"""
        return Function(name=self.name, arguments=arguments)

    def render(self):
        template = TEMPLATES.get("function" if not self.is_method else "method", {})
        decorators = "\n".join([d.as_decorator() for d in self.decorators])
        decorators = indent(decorators, TEMPLATES.get("indent") * (0 if not self.is_method else 1))
        parameters = ", ".join([p.render() for p in self.parameters])
        kwargs = ", ".join([k.render() for k in self.keyword_only])
        all_params = []
        docs = [p.render_docs() for p in self.parameters]
        if parameters:
            all_params.append(parameters)
        if kwargs:
            all_params.append(TEMPLATES.get("keyword_only"))
            all_params.append(kwargs)
            docs.extend([k.render_docs() for k in self.keyword_only])
        docs = [_ for _ in docs if _]
        params = ", ".join(all_params)
        s = self.format(
            template.get("definition"),
            async_keyword=TEMPLATES.get("async"),
            parameters=params,
            decorators=decorators,
            return_type=self.return_type.render(),
            parameters_docs=docs,
        )
        return s

    def as_call(self):
        template = TEMPLATES.get("function", {})
        return self.format(
            template.get("call", ""), arguments=", ".join([a.as_argument() for a in self.arguments if a.value])
        )

    def as_decorator(self):
        template = TEMPLATES.get("decorator", "")
        return self.format(template, arguments=", ".join([a.as_argument() for a in self.arguments if a.value]) if self.arguments else None)


@dataclass
class Class(Object):
    """Class metadata"""

    bases: list["Class"] = list
    """Types this Class inherits from"""
    attributes: list[Parameter] = list
    """Atributes/Fields of this Class"""
    methods: Optional[list[Function]] = list
    """List of methods attached to this Class"""
    decorators: Optional[list["Function"]] = list
    """List of Functions decorating this class"""
    examples: Optional[str] = Optional
    """Example usage of this Class"""
    _lowercase: bool = False

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
        else:
            # elif any(i in self.name.lower() for i in {"structure", "fields", "object", "response", "params", "properties", "parameters", "activity", "info"}):
            _type = "class"

        self.name = replace_multiple(self.name, TEMPLATES.get("to_strip", []), "").strip()

        template = TEMPLATES.get(_type, {})
        if _type in {"enum", "flag"}:
            for a in self.attributes:
                a._constant = True
        decorators = "\n".join([d.as_decorator() for d in self.decorators])
        attributes = indent("\n".join([a.render() for a in self.attributes]), TEMPLATES.get("indent"))
        methods = "\n".join([m.render() for m in self.methods])
        bases = ", ".join(self.bases) if self.bases else None
        s: str = self.format(template.get("definition"), bases=bases, attributes=attributes, methods=methods, decorators=decorators)
        if len(set([i.strip() for i in s.splitlines()])) <= 1:
            return ""
        return s
