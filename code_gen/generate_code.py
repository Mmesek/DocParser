from utils import load, save
import json
with open('templates/python.json','r',newline='',encoding='utf-8') as file:
    language = json.load(file).get("language")
import generators

def createPackage(files):
    save(language.get('PackageFile'), generators.package_file(files))

def add_boilerplate(src_code: str, generated_date: str) -> str:
    import datetime
    src_code = language.get("boilerplate") + src_code
    src_code = (
        language.get("comment")
        + "Generated structure from docs at "
        + generated_date
        + "\n"
        + language.get("comment")
        + "Generated source code at "
        + datetime.datetime.today().strftime("%H:%M %Y/%m/%d")
        + "\n"
        + src_code
    )
    return src_code

def main(name: str) -> None:
    json_structure = load(name)
    src_code = ""
    functions = []
    routes = []
    for i in json_structure:
        if "method" in json_structure[i]:
            functions.append(generators.function_definition(json_structure[i], i))
            routes.append(generators.route(json_structure[i], i))
        elif type(json_structure[i]) == dict:
            src_code += generators.structure(json_structure[i], i)

    src_code = (
        add_boilerplate(src_code, json_structure.get("generated_date"))
        + "\n\n" 
        + generators.enum_of_routes(routes) 
        + "\n\n".join(functions)
    )
    save(name, src_code)

main("discord")