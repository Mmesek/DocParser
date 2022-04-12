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


def to_list(dct, key):
    return [
        Parameter(
            name=v.get("name"),
            documentation=v.get("description"),
            type_=Type(v.get("type")),
            value=v.get("default", None),
            optional=v.get("optional", False),
            nullable=v.get("nullable", False),
        )
        if type(v) is dict
        else Parameter(name=v)
        for v in dct.get(key, [])
    ]


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
                Parameter(name="returns", value=t.render(), sane_value=False),
            )
        )
    else:
        q = []
        decorators = []

    _params = to_list(obj, "parameters")
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
        a = to_list(obj, "parameters")
        methods = [make_function(obj.get("methods", {}).get(f), f, is_method=True) for f in obj.get("methods", [])]
        objects.append(Class(name, docs, attributes=a, methods=methods))
    objects.append("")

rendered = []
for obj in objects:
    if isinstance(obj, Object):
        rendered.append(obj.render())
    else:
        rendered.append(obj)


def to_file():
    with open("code.py", "w", newline="", encoding="utf-8") as file:
        file.write(TEMPLATES.get("newline").join(rendered))


if True:
    to_file()
else:
    print("\n".join(objects))
