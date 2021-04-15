import re
params_pattern = re.compile(r"/?{(.*?)}/?")
require_permission_pattern = re.compile("(?i)Requires the (.*?) permission")
from .helpers import check_list, check_urls, extract_return

def open_doc(doc: str) -> list:
    from os.path import dirname
    doc = dirname(__file__)+f"/markdowns/{doc}.md"

    with open(doc,'r',encoding='utf-8') as file:
        lines = [i.strip() for i in file.readlines()]
    return lines

def save_json(name: str, f: list):
    if f == [[]]:
        return
    import json
    with open(f'results/jsons/{name}.json', 'w', newline='', encoding='utf-8') as file:
        import datetime
        f["generated_date"] = datetime.datetime.today().strftime('%H:%M %Y/%m/%d')
        json.dump(f, file, indent=4)

def split_sections(lines: list) -> list:
    sections = []
    section = []
    subsection = False
    for line in lines:
        if '#' in line[0:5]:
            if section != []:
                if subsection:
                    sections[-1].append(section)
                    subsection = False
                else:
                    sections.append(section)
            if 'params' in line.lower() or "parameters" in line.lower():
                subsection = True
            section = []
        if line != '':
            section.append(line)
    if section != []:
        sections.append(section)
    return sections

def check_if_present(parsed, name):
    if name in parsed:
        name = '_'+name
        return check_if_present(parsed, name)
    return name

def create_json(sections: dict) -> list:
    f = {}
    for section in sections:
        if type(section) is dict:
            _obj = {}
            if '_method' in section:
                _obj["description"] = [check_urls(i) for i in section.get("_additional") if type(i) is not dict]
                _obj["method"] = section.get("_method")
                _obj["path"] = section.get("_path")

                doc = '\n'.join(_obj["description"])
                _obj["required_permission"] = [i.strip("'").strip("`") for i in require_permission_pattern.findall(doc)]
                _obj["return"], _obj["return_list"] = extract_return(doc)

                path_params = params_pattern.findall(re.sub(r"#(.*?)}", "}", _obj["path"]).replace(".", "_"))
                _obj["path"] = re.sub(r"#(.*?)}", "}", _obj["path"]).replace(".", "_")
                _obj["parameters"] = [c.strip() for c in path_params]

                for x, i in enumerate(section.get("_additional", {})):
                    if type(section["_additional"][x]) is dict:
                        if "json" in i["_name"].lower():
                            _obj["json_params"] = i["_params"]
                        elif "query" in i["_name"].lower():
                            _obj["query_params"] = i["_params"]
                        else:
                            if "json_params" not in _obj:
                                _obj["json_params"] = []
                            _obj["json_params"] += i["_params"]
            else:
                _obj["description"] = section.get("_docs", "")
                _obj["variables"] = section.get("_params")
            name = check_if_present(f, section.get("_name").strip('#').replace("Event Fields", "").replace(" Object","").strip('_').strip())
            f[name] = _obj
    return f

def cap(word):
    if word == '':
        return word
    return word[0].upper() + word[1:]

def title_preserving_caps(string, whitespace=' '):
    return whitespace.join(map(cap, string.split(whitespace)))

def cc2jl(my_str):
  """Camel case to joint-lower"""

  r = my_str[0].lower()
  for i, letter in enumerate(my_str[1:], 1):
    if letter.isupper():
      if my_str[i-1].islower() or (i != len(my_str)-1 and my_str[i+1].islower()):
        r += '_'
    r += letter.lower()
  return r