import datetime
import json
from models import Parameter, Function, Argument, Class, TEMPLATES

objects = []
objects.append(TEMPLATES.get("comment") + "Generated source code at")
objects.append(TEMPLATES.get("comment") + f'{datetime.datetime.today().strftime("%H:%M %Y/%m/%d")}')
objects.append(TEMPLATES.get("newline") * 2)


def to_list(dct, key):
    return [
        Parameter(
            name=v.get("name"),
            documentation=v.get("description"),
            type_=TEMPLATES.get("types", {}).get(v.get("type"), v.get("type")),
        )
        for v in dct.get(key, [])
    ]


def make_function(dct, key, decorators=None, **kwargs):
    obj = dct.get(key)

    return Function(
        parameters=to_list(obj, "parameters"),
        decorators=decorators,
        return_type=obj.get("return_type"),
        documentation=obj.get("description"),
        **kwargs,
    )

with open("code_gen-mk2/test.json", "r", newline="", encoding="utf-8") as file:
    t = json.load(file)


RouteDecorator = Function(name="route")
Permissions = Function(name="permissions")

for name, obj in t.items():
    docs = obj.get("description")
    if "path" in obj:
        q = to_list(obj, "query_parameters")
        method = obj.get("method")
        path = obj.get("path")
        req_permissions = [Argument(value=v) for v in obj.get("required_permission")]
        decorators = []
        if req_permissions:
            decorators.append(Permissions.with_arguments(*req_permissions))

        decorators.append(
            RouteDecorator.with_arguments(
                Argument(name="method", value=method),
                Argument(name="path", value=path),
            )
        )
        objects.append(make_function(obj, name, name=name, keyword_only=q, decorators=decorators))
    else:
        a = to_list(obj, "parameters")
        methods = [make_function(f) for f in obj.get("methods")]
        objects.append(Class(name, docs, attributes=a, methods=methods))
    objects.append(TEMPLATES.get("newline") * 2)

def to_file():
    with open('code.py','w',newline='',encoding='utf-8') as file:
        file.writelines(objects)

if True:
    to_file()
else:
    print("\n".join(objects))
