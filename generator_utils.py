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