from doc_parser.iterators import parse_tables, parse_endpoints
from doc_parser.utils import split_sections, open_doc, create_json, save_json

def main(doc):
    sections = split_sections(open_doc(doc))
    sections = parse_tables(sections)
    sections = parse_endpoints(sections)
    #return sections
    structure = create_json(sections)
    save_json(doc, structure)
main('discord')
#main("forked_daapd")
#TODO:
#Parse types correctly?
#Extract object type (enum, struct, function)


# BUG:
# If there is a doc above table it's not being parsed as doc
# If doc also contains [link]() it overwrites section name
#TODO:
# Parse Json correctly & generate