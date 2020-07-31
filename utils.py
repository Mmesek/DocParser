from os.path import dirname

def args():
    import sys
    try:
        _in = sys.argv[1]
        _out = sys.argv[2]
    except:
        _in = "discord"
        _out = "dlang"
        import glob
        _i = glob.glob(dirname(__file__) + '/docs_structures/**/*', recursive=True)
        inputs = '- '+'\n- '.join([i.replace('\\','/').split('/')[-1].split('.')[0] for i in _i])
        _o = glob.glob(dirname(__file__) + '/templates/**/*', recursive=True)
        outputs = '- '+'\n- '.join([i.replace('\\', '/').split('/')[-1].split('.')[0] for i in _o])
        print("Missing input and/or output arguments.\n\tExample usage:\njson_parser_test.py discord dlang.\n\n\tSupported Inputs:\n{inputs}\n\tSupported Outputs:\n{outputs}".format(inputs=inputs, outputs=outputs))
        #exit()
    return (_in, _out)


def load_json(path):
    import json
    with open(dirname(__file__)+path,'r',newline='',encoding='utf-8') as file:
        return json.load(file)

def load_file(file):
    with open(file, "r", newline="\n", encoding="utf-8") as f:
        return [x.strip("\n").strip() for x in f.readlines()]

def check_if_exists(_dir):
    from os.path import exists
    from os import makedirs
    if exists(f"{dirname(__file__)}/{_dir}") is False:
        print("Creating directory:", _dir)
        makedirs(f"{dirname(__file__)}/{_dir}")
        return True
    return False

def save_result(name, _json):
    import datetime
    _json["meta"]["generated_date"] = datetime.datetime.today().strftime('%H:%M %Y/%m/%d')
    for kind in _json:
        check_if_exists(name)
        import json
        if '.' in kind:
            kind = kind.split('.')[0:-1]
        with open(f"{dirname(__file__)}/{name}/{kind}.json", "w", newline="", encoding="utf-8") as file:
            json.dump(_json[kind], file, indent=4)