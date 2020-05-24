# Sphinx docstring linter

A linter for Python docstrings in ReStructured Text format.

Ensures that all function parameters and return values are documented
in reStructuredText format and that the resulting docstrings are 
suitable for processing with [Sphinx](http://www.sphinx-doc.org/en/stable/rest.html).


## Example

Example of a function with a docstring in ReStructured Text format.

```Python
def add(a, b):
  """
  Return sum of two fractions.
  
  Fractions are given as tuples (nominator, denominater).
  
  :param (int,int) a: First fraction.
  :param (int,int) b: Second fraction.
  :return: Sum of the two fractions.
  :rtype: (int, int)
  """
  return a[0] * b[1] + b[0] * a[1], a[1] * b[1]
```


## Usage

Recursively lint all files with extension `.py` starting from current
directory:

```
python splint.py
```

Recursively lint all files with extension `.py` starting from the 
specified folder:

```
python splint.py foo/folder
```

If there are no linting errors `splint` outputs nothing. Otherwise
warnings and errors for specific files are reported, e.g.:

```
$ python splint.py ../testdata
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\add_with_docstr.py
module: add_with_docstr.py
  E: Docstring for module is missing
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\add_with_docstr_extra_param.py
module: add_with_docstr_extra_param.py
  E: Docstring for module is missing
1: function: add(a,b)
  E: Additional ':param c' in docstring.
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\add_with_docstr_missing_desc.py
module: add_with_docstr_missing_desc.py
  E: Docstring for module is missing
1: function: add(a,b)
  E: No description in docstring for parameter: b
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\add_with_docstr_missing_return.py
module: add_with_docstr_missing_return.py
  E: Docstring for module is missing
1: function: add(a,b)
  E: ':return: {description}' is missing.
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\add_with_docstr_missing_return_desc.py
module: add_with_docstr_missing_return_desc.py
  E: Docstring for module is missing
1: function: add(a,b)
  E: Description after 'return': missing
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\add_with_docstr_missing_rtype.py
module: add_with_docstr_missing_rtype.py
  E: Docstring for module is missing
1: function: add(a,b)
  W: ':rtype: {description}' is missing.
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\add_with_docstr_missing_type.py
module: add_with_docstr_missing_type.py
  E: Docstring for module is missing
1: function: add(a,b)
  W: No type in docstring for parameter: b
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\add_with_docstr_no_return.py
module: add_with_docstr_no_return.py
  E: Docstring for module is missing
1: function: add(a,b)
  E: Docstring describes return values but function does not return anything!
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\class_with_method.py
module: class_with_method.py
  E: Docstring for module is missing
1: class: Foo
  E: Docstring for class is missing
2: method: add(self,a,b)
  E: Docstring missing
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\class_with_private_method.py
module: class_with_private_method.py
  E: Docstring for module is missing
1: class: Foo
  E: Docstring for class is missing
********************************************************************************
c:\Maet\Projects\Python\sphinx-docstr-linter\testdata\class_with_staticmethod.py
module: class_with_staticmethod.py
  E: Docstring for module is missing
1: class: Foo
  E: Docstring for class is missing
2: method: add(a,b)
  E: Docstring missing
********************************************************************************
SUMMARY
errors: 21
warnings: 2
```
