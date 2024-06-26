import datetime
import json
from models import Object, Parameter, Function, Class, Type, TEMPLATES

objects = []
with open("code_gen-mk2/boilerplate.py", "r", newline="", encoding="utf-8") as file:
    objects.append(file.read())

objects.append(
    TEMPLATES.get("comment") + "Generated source code at " + f'{datetime.datetime.today().strftime("%H:%M %Y/%m/%d")}'
)
objects.append("")
default_values = TEMPLATES.get("default_values")


def to_list(dct, key, _class=False, mandatory=False):
    return [
        (
            Parameter(
                name=v.get("name"),
                documentation=v.get("description"),
                type_=Type(v.get("type")),
                value=v.get(
                    "value",
                    (
                        v.get(
                            "default",
                            default_values.get(
                                "nullable"
                                if v.get("nullable")
                                else (
                                    "optional"
                                    if v.get("optional")
                                    else (
                                        "list"
                                        if v.get("type", "").startswith("list")
                                        else "dict" if v.get("type", "").startswith("dict") else v.get("type", "None")
                                    )
                                )
                            ),
                        )
                    ),
                ),
                optional=v.get("optional", False),
                nullable=v.get("nullable", False),
                _template="parameter" if not _class else "attribute",
            )
            if type(v) is dict
            else Parameter(name=v, type_=Type(TEMPLATES.get("default_types").get(v, "str")), mandatory=mandatory)
        )
        for v in dct.get(key, [])
        if v
    ]


default_bases = TEMPLATES.get("default_bases") or []
default_decorators = TEMPLATES.get("default_decorators") or []
if default_decorators:
    default_decorators = [Function(d) for d in default_decorators]


def make_function(obj, name, **kwargs):
    # obj = dct.get(key)
    t = Type(obj.get("return_type"))
    if "path" in obj:
        q = to_list(obj, "query_parameters")
        method = obj.get("method")
        path = obj.get("path")
        req_permissions = [Parameter(value=v) for v in obj.get("required_permission", [])]
        decorators = []
        if req_permissions:
            decorators.append(Permissions.with_arguments(*req_permissions))

        decorators.append(
            RouteDecorator.with_arguments(
                Parameter(name="method", value=method),
                Parameter(name="path", value=path),
                # Parameter(name="returns", value=t.render(), _sanitize_value=False),
            )
        )
    else:
        q = []
        decorators = []

    _params = to_list(obj, "parameters", mandatory=True)
    j = to_list(obj, "json_parameters")
    j.sort(key=lambda x: (x.optional, False if x.value is None else True))
    _params.extend(j)
    _seen = set()
    params = []
    for param in _params:
        if param.name in _seen:
            continue
        params.append(param)
        _seen.add(param.name)

    return Function(
        parameters=params,
        name=name,
        return_type=t,
        documentation=obj.get("description"),
        keyword_only=q,
        decorators=decorators,
        **kwargs,
    )


with open("results/jsons/discord.json", "r", newline="", encoding="utf-8") as file:
    t = json.load(file)


RouteDecorator = Function(name="route")
Permissions = Function(name="permissions")

for name, obj in t.items():
    if type(obj) is not dict:
        continue
    objects.append("")
    docs = obj.get("description", "")
    if "path" in obj:
        objects.append(make_function(obj, name))
    else:
        a = to_list(obj, "parameters", True)
        methods = [make_function(obj.get("methods", {}).get(f), f, is_method=True) for f in obj.get("methods", [])]
        if not a and not methods:
            continue
        objects.append(
            Class(name, docs, attributes=a, methods=methods, bases=default_bases, decorators=default_decorators)
        )
    objects.append("")

rendered = []
for obj in objects:
    if isinstance(obj, Object):
        rendered.append(obj.render())
    else:
        rendered.append(obj)


def to_file():
    with open("generated_code.py", "w", newline="", encoding="utf-8") as file:
        file.write(TEMPLATES.get("newline").join(rendered))


if True:
    to_file()
else:
    print("\n".join(objects))
