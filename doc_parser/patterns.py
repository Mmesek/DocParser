import re

object_name_pattern = re.compile(r"\[(.*?)\]\(.*?\)")
params_pattern = re.compile(r"/?{(.*?)}/?")
require_permission_pattern = re.compile("(?i)Requires the (.*?) permission")
return_pattern = re.compile(r"Returns .*? \[(.*?)\]\(.*?\) ?(?:on)? (?:object|success|as the body)")
return_empty_pattern = re.compile(r"Returns .*? ?204 .*? success")
alt_return = re.compile(r"Returns (.*?)\.")
returns_list = re.compile(r"(?i)returns an? list|array of")
returns_array_custom_type_pattern = re.compile(r"(array|list) of (?:.*?)?\[(.*?)\](\(.*?\))?")
returns_array_base_type_pattern = re.compile(r"(array|list) of (.*)")

custom_type = re.compile(r"\[(.*?)\](\(.*?\))?")
digits_pattern = re.compile(r"(?i)(\d+|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)")
digits = {"one":1, "two":2, "three":3, "four":4, "five":5, "six":6, "seven":7, "eigth":8, "nine":9, "ten":10}
json_custom_type_pattern = re.compile(r"Map of (.*) to (?:.*?)?\[(.*?)\](\(.*?\))?")
json_pattern = re.compile(r"Map of (.*) to ?(.*)")

url_pattern = re.compile(r"\[.*?\]\((.*?\/).*?\)")
path_object = re.compile(r"#(.*?)}")
path_parameters = re.compile(r"({.*?)\.(.*?})")