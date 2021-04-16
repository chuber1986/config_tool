# ConfigTool

Read a configuration file from JSON, JSON5 or YAML. Values can be overwritten by console arguments.
The tool automatically imports classes and creates object instances.

The config filename can be provided via constructor argument, commandline 
argument `--config`, environment variable `CONFIG_FILE` or if exists the 
default path `.configs/config.json` will be used.

## Features:
### Parent file:
A config file can specify a parent config from which it inherits. First,
the parent file will be loaded (recursively) and afterward current entries
override or are added to the parent config. The parent config is specified
by a `parent` tag at the toplevel of the config file.

Example:
```json
{
  "parent": "./templates/parent.json",
  ...
}
```

### Include config
By setting a value to a string starting with `include::` followed a filename,
The tool read an additional config file and inserts it's value replacing the
include-string.

Example:
```json
{
  ...
  "module_a": "include::./modules/module_a.json",
  ...
}
```

### Import config
With the import tag, one can load Python modules, packages, classes or functions
by inserting a value string starting with `import::` followed by the specification
of the Python element. The import string will be replaced by the loaded element.

Example:
```json
{
  ...
  "package_a": "import::path.to.package_a",
  "module_a": "import::path.to.module_a",
  "class_a": "import::path.to.class_a.ClassA",
  "function_a": "import::path.to.class_a.function_a",
  ...
}
```

### Load objects
This feature allows to load and instantiate a Python object. A object is specified
by a dictionary containing a `class` and a `params` key. The `class` key stores a
string containing the qualified classname and `params` contains a dictionary
containing all parameter which will be passed to the constructor of the class.
Parameter can recursively contain other object definitions.

Example:
```json
{
  ...
  "some_object": [{"class": "path.to.package.MyClass",
                   "params": {"a":  1, "b":  2}},
                  {"class": "path.to.package.MyClass",
                   "params": {"a":  3, "b":  3}}],
  ...
}
```

Accessing `some_object` would return `[MyClass(a=1, b=2), MyClass(a=3, b=4)]`.

## Install
### Dependencies
Depending on the file format of your configutaion files you need to install one
or more of the following package:
- `json5`
- `yaml`
- `xmltodict`

For plain `json` no additional setup is required.

### From source
Install the ConfigTool via `pip` from the GitLab Repository:
```bash
python -m pip install https://git.silicon-austria.com/huberc/config_tool.git
```

### Testing
Testing the code is important when contributing the project. Before you create a merge
request, you should test your code to ensure high quality.

To test the source code and generate report you need to install the following packaged:
- `tox`
- `pytest`
- `pylint-json2html`
- `coverage`

Therefore, in the root directory of the ConfigTool execute
```bash
python -m pip install --requirement requirements-dev.txt 
```

To perform all unittests on all supported environments (py36, py37, py38, py39) execute
```bash
tox
```

You can generate a test coverage report with
```bash
tox -e coverage
```

To generate a linting report execute
```bash
pylint --rcfile=.pylintrc config | pylint-json2html -o ./build/pylint.html
```

You show the PyLint result in the console by using
```bash
pylint --output-pylint --output-format text --rcfile=.pylintrc configformat text --rcfile=.pylintrc config
```

## Usage
### Initialize
```python
from config import Config
...
cfg = Config('./config/default.json')
```

### Access values
Considering the following example config:
```json
{
  "a": 123,
  "b": [1, 2, 3],
  "c":  {"a": 1, "b": 2, "c": 3},
  "d": [{"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 2, "c": 3}],
  "e":  {"class": "path.to.package.MyClass",
         "params": {"a":  1, "b":  2}}
}
```

Toplevel elements can be accessed can be accessed by object attributes. The attribute returns
a Python object that can be used as any other.
```python
cfg = ...
...
a = cfg.a
b1 = cfg.b[1]
c1b = cfg.c[1]['b']
e = cfg.e
```

`Config` also provides a getter for the toplevel elements.
```python
cfg = ...
...
a = cfg['a']
b1 = cfg['b'][1]
c1b = cfg['c'][1]['b']
e = cfg['e']
```

Finally, `Config` provides a `get` method that allows for more control when loading an object.
```python
cfg = ...
...
a = cfg.get('a')
b1 = cfg.get('b')[1]
c1b = cfg.get('c')[1]['b']
# If `e` not exists return `[]`
# Otherwise return MyClass(a=1, b=3, c=4)
e = cfg.get('e', default=[], instance=True, b=3, c=4)
```