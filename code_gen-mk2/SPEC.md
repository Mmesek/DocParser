# Keywords:

## Universal:
- `name`
- `documentation`
- `newline`
- `indent`
# Class:
- `bases`
- `attributes`
- `methods`
# Parameter/Attribute:
- `type`
- `default`
# Function:
- `async`
- `parameters`
- `return`
- `arguments`
- `function_call`
# Documentation:
- `description`
- `return`
- `return_description`
- `parameters` - Parameters of this object
# Route:
- `path`
- `url_method`
- `query_arguments`
- `json_arguments`
- `arguments`
- `result`
- `name_upper`
# Special keys:
- `*_join` - Join method. Options:
    - `none` - Default. Joins without anything inbetween
    - `newline` - Join list with a newline. Doesn't insert indentation
    - `CHARACTER` - Character(s) used as a delimiter
- `*_missing` - Behaviour on missing keyword
    - `skip` - Default. Skips item
    - `fail` - Forfeits entire formatting. DOES NOTHING AT ALL.
    - `default` - Inserts default type/value.
- `*_single` - Singular argument style overwrite (Defaults to global style)

# Schema:
Any value can be either in a form of string or list. When value is a List, keys `*_join` and `*_missing` can be defined to manage join behaviour
Single value style for list values like arguments or parameters can be managed by setting `*_single`

# TODO
- Decorators
- Enums
- Not implemented stub
- Types & Sizes?
- Constructor

```json5
{
    "global_templates":[
        // Actual (raw text) documentation
        "documentation",
        // Name of current object
        "name",
        // Single indentation
        "indent",
        // Newline character
        "newline",
    ],
    // Meta template configuration
    "meta": {
        // String to use as an indentation
        "indent":"",
        // String to use as a newline
        "newline":"\n",
        // File extention for final file
        "file_ext": "",
        // Boilerplate code to include at the begining of the file
        "boilerplate": "",
        // Path to File that should be included at the begining of the generated file
        "boilerplate_path": ""
    },

    // Single variable docstring. *Usualy* single line but it's not guaranteed.
    "inline_docstring": "",

    // Main docstring for any object
    "docstring": "",

    // Single Parameter style
    "parameter": {
        "templates":[
            // Setting up Type for current parameter
            "type",
            // Setting up Default value for current parameter
            "default"
        ]
    },
    // Single argument style
    "argument": "",

    "class": {
        // Entire Class definition (with body)
        "definition": {
            "templates": [
                // Objects from which current Class inherits from
                "bases",
                // Attributes of this class
                "attributes"
                // Methods attached to this class
                "methods"
            ],
        },
        // Attribute style. Uses same keys `parameter` use
        "attribute": {},
    },
    "function": {
        "templates":[ // TODO
            //
            "async",
            //
            "arguments",
            //
            "return",
            //
            "parameters",
            //
            "function_call"
        ],
        // Function definition
        "definition": "",
        // Body of function
        "body": "",
        // Usage of function in code
        "call": ""
    },
    // Works exactly the same way `function` work; contains same keys
    "method": {},
    // TODO
    "documentation": {
        "templates":[ // TODO
            "base",
            //
            "return",
            //
            "return_description",
            //
            "description",
            //
            "indent",
            //
            "parameters",
            //
            "name"
        ],
        //
        "docstring":"",
        //
        "parameters":"",
        //
        "parameter_documentation":"",
        //
        "inline_parameter_documentation":"",
        //
        "returns":"",
    },
    // Route object style
    "route": {
        "templates": [
            // Uppercased name of this Route
            "name_upper",
            // URL Method for this Route
            "method",
            // Path for this Route
            "path",
            // Type factory of return object
            "result",
            // List of arguments to pass to Route object
            "arguments",
            // Arguments meant for URL
            "query_arguments",
            // Arguments meant for JSON Payload
            "json_arguments",
        ],
        // Route Definition
        "definition": "",
        // Usage of this Route by code
        "usage": "",
        // Argument to pass as a JSON Payload
        "json_argument": "",
        // Argument to pass as a Query Parameters
        "query_argument": ""
    },
    // Function body for stubs/not implemented methods
    "not_impl":"",
    // Function call above another/decorating function
    "decorator":{
        "templates":[
            "arguments"
        ]
    },
    // Enumeration style
    "enum":{
        "templates":[
            // List of all enum members
            "members",
            // Type of a member
            "type",
            // Value of a member
            "value"
        ],
        // Style of a single member
        "member": ""
    },
    // Works exactly the same way `enum` work; contains same keys
    "flag":{},
    // Types translation
    "types":{
        "templates":[
            // Type
            "type",
            // Type of Key in mapping
            "key",
            // Type of Value in mapping
            "value",
            // Size of an array
            "size"
        ],
        "string": "",
        "boolean":"",
        "integer": "",
        "big_integer": "",
        "optional":"",
        "nullable":"",
        "array":"",
        "object":"",
        "json":"",
        "null": "",
        "binary":"",
        "iso8601_timestamp": "",
        "timestamp":"",
        "mixed": "",
        "file contents":"",
        "constructor":"",
        "image_data":"",
        "flag":""
    }
}
```