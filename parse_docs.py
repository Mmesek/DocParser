from doc_parser.iterators import extract_objects, extract_single, flatter, make_models, parse_section, parse_structures, split_endpoints, trim_empty, extract_endpoints, parse_parameters
from doc_parser.utils import split_sections, open_doc, save_json

def main(doc):
    sections = split_sections(open_doc(doc))
    endpoints, sections = extract_endpoints(sections)
    objects, sections = extract_objects(sections)
    #objects, sections = extract_structures(objects, sections)
    #objects = parse_parameters(objects)
    #objects = merge_objects(objects)
    #endpoints = clean_endpoints(endpoints)
    #objects = clean_objects(objects)
    #_sections = prepare_json(endpoints, objects, sections)
    #_sections = {"endpoints":endpoints, "models":objects}
    endpoints.update(objects)
    for o in endpoints.values():
        o.description = [o.description]
    save_json(doc, endpoints)
    #sections = parse_section(sections)
    #sections = trim_empty(sections)
    #sections = extract_single(sections)
    #endpoints, nested, objects, sections = split_endpoints(sections)
    #sections = make_models(sections)
    #sections = flatter(sections)
    #sections = merge_sections(sections)
    #save_json(doc, sections)
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