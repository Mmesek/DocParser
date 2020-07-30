from os.path import dirname

docs_path = "docs\\"
_docs_path = dirname(__file__)+"/"+docs_path

from utils import load_json, check_if_exists

def download_docs(src):
    import requests
    j = load_json(f"/docs_structures/{src}.json")
    base = j['base_url']
    docs_to_download = j['files']
    for link in docs_to_download:
        print("Downloading", link)
        r = requests.get(base + link)
        if "/" in link:
            check_if_exists(docs_path + link.split("/")[0])
        with open(_docs_path + link.replace("/", "\\"), "wb") as file:
            file.write(r.content)

if __name__ == "__main__":
    import sys
    try:
        src = sys.argv[1]
    except:
        print('Specify json in docs_structures to use')
    download_docs(src)