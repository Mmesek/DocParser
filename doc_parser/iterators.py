from .helpers import detect_header, parse_columns, check_list
from .parsers import parse_table, parse_endpoint

def parse_tables(sections: dict) -> dict:
    for section in sections:
        for value in section:
            if type(value) is list:
                section[section.index(value)] = parse_table(value)
            elif '#' in value or ('---' in value and '|' in value):
                headerLevel = value.count("#", 0, 7)
                if (headerLevel == 6 or headerLevel == 4 or '---' in value) and not 'example' in value.lower():
                    _section = parse_table(section)
                    sections[sections.index(section)] = _section
                    break
    return sections

def parse_endpoints(sections: dict) -> dict:
    for section in sections:
        for value in section:
            if '##' in value and '%' in value:
                sections[sections.index(section)] = parse_endpoint(section)
    return sections