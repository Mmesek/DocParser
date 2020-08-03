import re

column_pattern = re.compile(r"\| (.*?) ")
value_pattern = re.compile(r"(?=\| (.*?) \|)")
params_pattern = re.compile(r"/?{(.*?)}/?")
return_pattern = re.compile("Returns .*? \[(.*?)\]\(.*?\) object")
return_empty_pattern = re.compile("Returns .*? ?204 .*? success")
require_permission_pattern = re.compile("(?i)Requires the (.*?) permission")

def endpointParser(title, content):
    e = title.split(" % ", 1)
    name = e[0].strip("#").strip().replace('-','_')
    s = e[1].split(" ", 1)
    method = s[0].split("/")[0]
    path = s[1].strip()
    path = re.sub(r"#(.*?)}", "}", path).replace(".", "_")
    path_params = params_pattern.findall(path)
    pos = [c.strip() for c in path_params]
    params = {}
    for kind in content:
        if kind == "trunk" or kind == 'other' or kind == 'examples':
            continue
        for table in content[kind]:
            docstring, p = tableParser(table, kind, content[kind][table])
            params[kind] = {"docstring":docstring, "params":p}
    content["trunk"] = [check_urls(i) for i in content["trunk"]]
    j = {"name": name, "method": method, "path": path, "docstring": content["trunk"],
    "parameters": pos}
    j["json_params"] = params.pop("json", [])
    j["query_params"] = params.pop("query", [])
    j["params"] = params.pop("params", [])
    j["other_params"] = params
    j["return"] = None

    doc = '\n'.join(content["trunk"])
    j["required_permission"] = [i.strip("'").strip("`") for i in require_permission_pattern.findall(doc)]

    returns = ['']
    if 'Return' in doc:
        returns = return_pattern.findall(doc)
        if returns == []:
            success = return_empty_pattern.findall(doc)
            if success != []:
                returns = ['None']
            elif returns == []:
                returns = ['Dict']
            else:
                returns = [""]
        if returns != [""]:
            returns = [returns[0].replace(' ','_').title()]
        returns = [returns[0].replace('Dm_', '')]
    if returns != [''] and 'None' not in returns[0] and 'Dict' not in returns[0]:
        j["return"] = returns[0]
        if 'returns a list of' in doc.lower() or 'returns an array of' in doc.lower():
            j["return_list"] = True
        else:
            j["return_list"] = False
    else:
        j["return_list"] = False

    return j

def tableParser(name, kind, table):
    for x, line in enumerate(table):
        if "---" in line and "|" in line: #"Field" in line or 
            start_at = x - 1
            x = x-1
            break
    columns = [c.strip() for c in column_pattern.findall(table[x])]
    params = {}
    docstring = ''
    if columns != []:
        enum = {}
        for x, column in enumerate(columns):
            enum[x] = column
            params[column] = []
        for line in table[start_at + 2:]:
            values = value_pattern.finditer(line)
            for x, value in enumerate(values):
                value = value.group(1).strip()
                if enum[x] == "Field":
                    value = value.replace(r"\*", "").replace("-", "").replace(" ", "").replace("+", "_")
                elif enum[x] == "Type":
                    value = value.replace(r"\*", "").replace("?", "")
                else:
                    value = value
                params[enum[x]] += [value.strip()]
            if value_pattern.search(line) is None:
                if line != '\n':
                    docstring += line
    j = []
    if params == {}:
        return docstring, j
    for x in range(len(params[columns[0]])):
        v = {}
        for column in params:
            if column == 'Field':
                if '?' in params[column][x]:
                    v["optional"] = True
                    params[column][x] = params[column][x].strip('?')
                name = re.findall(r"\[(.*?)\]\(.*?\)", params[column][x])
                if name != []:
                    v["name"] = name[0].replace('.', '_')
                else:
                    v["name"] = params[column][x]
            elif column == 'Description':
                v['docstring'] = check_urls(params[column][x])
            elif column == 'Type':
                if '?' in params[column][x]:
                    v["nullable"] = True
                    params[column][x] = params[column][x].strip('?')
                if 'list of' in params[column][x] or 'array of' in params[column][x]:
                    returns = re.findall(r"(array|list) of (?:.*?)?\[(.*?)\]\(.*?\)", params[column][x])
                    if returns != []:
                        if returns[0][1] != '':
                            v["type"] = check_urls(returns[0][1].replace(' ', '_').title())
                    else:
                        returns = re.findall(r"(array|list) of (.*)", params[column][x])
                        if returns != [] and returns[0][1] != '':
                            if returns[0][1] == 'snowflakes':
                                v["type"] = "snowflake"
                            else:
                                v["type"] = check_urls(returns[0][1].replace(' ', '_').title())
                    v["is_list"] = True
                else:
                    returns = re.findall(r"\[(.*?)\]\(.*?\)", params[column][x])
                    if returns != []:
                        v["type"] = check_urls(returns[0].replace(' ', '_').title())
                    else:
                        v[column.lower()] = check_urls(params[column][x])
            else:
                v[column.lower()] = check_urls(params[column][x])
        j += [v]
    return docstring, j


url_pattern = re.compile(r"\[.*?\]\((.*?\/).*?\)")
def check_urls(doc):
    urls = url_pattern.findall(doc)
    for url in urls:
        nurl = url.replace('/','#').lower().replace('#docs_', 'https://discord.com/developers/docs/').replace('_', '/',1)
        doc = doc.replace(url, nurl)
    return doc