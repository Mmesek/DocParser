import json
#from json_parser2 import generate_function, generate_object, l
from json_parser2 import *
from utils import check_if_exists, args
syntax, enum, func, types, values, sizes, l, methods = load_language(args()[1])

def load(name):
    with open(f"results/jsons/{name}.json", "r", newline="", encoding="utf-8") as file:
        return json.load(file)

def iterate(name):
    j = load(name)
    s = ""
    e = ""
    routes = []
    for x, i in enumerate(j):
        if x == 0 or type(i) == list:
            for path in i:
                if "deprecated" in path["name"]:
                    continue
                e += generate_function(path)
                routes += [generate_route(path)]
            r = generate_enum_of_routes(routes)
        else:
            if any(j in i.get("name", "") for j in ["Structure","Types", "Flags", "Log Events"]):
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


def save(name, s):
    check_if_exists('results/src'+'/'+args()[1])
    with open('results/src/'+args()[1]+'/'+name+"." + l["fileExt"], "w", newline="", encoding="utf-8") as file:
        file.write(s)

if __name__ == "__main__":
    import sys
    try:
        iterate(sys.argv[3])
    except:
        import glob
        from os.path import dirname
        _o = glob.glob(dirname(__file__) + '/results/jsons/**/*', recursive=True)
        jsons = '- '+'\n- '.join([i.replace('\\', '/').split('/')[-1].split('.')[0] for i in _o])
        print('\n\nSpecify json to generate from as a third argument\n\tAvailable docs:\n'+jsons)