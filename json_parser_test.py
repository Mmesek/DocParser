import json
#from json_parser2 import generate_function, generate_object, l
from json_parser2 import *

def load(name):
    with open(f"results/{name}.json", "r", newline="", encoding="utf-8") as file:
        return json.load(file)

def iterate(name):
    j = load(name)
    s = ""
    e = ""
    routes = []
    for x, i in enumerate(j):
        if x == 0:
            for path in i:
                if "deprecated" in path["name"]:
                    continue
                e += generate_function(path)
                routes += [generate_route(path)]
            r = generate_enum_of_routes(routes)
        else:
            if any(j in i.get("name", "") for j in ["Structure","Types", "Flags"]):
                s += generate_object(i)
            elif i.get("generated_date", "") != "":
                import datetime

                s = l["boilerplate"] + s
                s = (
                    l["comment"]
                    + "Generated structure from docs at "
                    + i["generated_date"]
                    + "\n"
                    + l["comment"]
                    + "Generated source code at "
                    + datetime.datetime.today().strftime("%H:%M %Y/%m/%d")
                    + "\n"
                    + s
                )
            else:
                pass
    s += "\n\n" + r + e
    save(name, s)
from utils import check_if_exists

def save(name, s):
    check_if_exists('results/src')
    with open('results/src/'+name+"." + l["fileExt"], "w", newline="", encoding="utf-8") as file:
        file.write(s)

iterate('Channel')