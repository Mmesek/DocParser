from json_parser_test import iterate, createPackage
from utils import args, listFiles
from docs_downloader import download_docs
from docs_parser import create_json, parse_docs, save_json
import time
s = time.time()
docs_exists = True
if not docs_exists:
    download_docs(args()[0])
    print("Downloading docs...")
else:
    print("Docs already exists. Skipping download.")

docs = [i for i in listFiles('docs', True) if '.md' in i]
total = []
for doc in docs:
    total = []
    print("Parsing", doc)
    total += create_json(parse_docs(doc))
    save_json(doc.split('/')[-1].split('\\')[-1].replace('.md', '').strip('_'), total)
#save_json('Discord', total)

parsed_docs = listFiles('results/jsons')
for doc in parsed_docs:
    print("Generating code for", doc)
    iterate(doc)
createPackage(parsed_docs)

print("Done in", time.time() - s)