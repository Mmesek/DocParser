from os.path import exists, dirname
def check_if_exists(_dir):
    from os import makedirs
    if exists(f"{dirname(__file__)}/{_dir}") is False:
        print("Creating directory:", _dir)
        makedirs(f"{dirname(__file__)}/{_dir}")
        return True
    return False

def load(name: str):
    import json
    with open(f"results/jsons/{name}.json", "r", newline="", encoding="utf-8") as file:
        return json.load(file)
import json
with open('templates/python.json','r',newline='',encoding='utf-8') as file:
    language = json.load(file).get("language")
LANGUAGE = "python"
def save(name: str, s: str):
    check_if_exists('results/src'+'/'+LANGUAGE)
    with open(dirname(__file__)+'/results/src/'+LANGUAGE+'/'+name+"." + language.get("fileExt"), "w", newline="", encoding="utf-8") as file:
        file.write(s)


def addIndentation(scope):
    return " " * (scope * 4)


def multilineMiddle(scope):
    return "\n" * scope

def generate_documentaion(o):
    d = o.get("docstring", "")
    if type(d) == list:
        d = "\n".join(i for i in d if i not in ["", "\n"])
    if d != "":
        d = multilineMiddle(1) + d.rstrip("\n")
    if d != "":
        d += "\n"
    return d

def cc2jl(my_str):
  """Camel case to joint-lower"""
  my_str = str(my_str)

  r = my_str[0]
  for i, letter in enumerate(my_str[1:], 1):
    if letter.isupper():
      if my_str[i-1].islower() or (i != len(my_str)-1 and my_str[i+1].islower()):
          if my_str[i-1] not in ['_','"',"'"] and my_str[i+1] not in ['_','"',"'"]:
            r += '_'
    r += letter
  return r.strip('_')