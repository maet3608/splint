"""
.. module:: test_splint
   :synopsis: Unit tests for splint module
"""

import ast

import pytest

import splint.splint as sp
import splint.report as sr


@pytest.fixture(scope="function")
def clear_report():
    sr.Report.clear()


def read(filename):
    """Read content of specified test file.

    :param str filename: Name of file in 'testdata' folder.
    :return: Content of file
    :rtype: str
    """
    with open('testdata/' + filename) as f:
        return f.read()


def read_function(filename):
    """Read content of specified test file and returns first function def.

    :param str filename: Name of file in 'testdata' folder.
    :return: First function definition in file.
    :rtype: ast.FnDef
    """
    return function_node(read(filename))


def function_node(code):
    """Return AST node for first function in code string.

    :param str code: Code, e.g. 'def add(a,b): return a+b'
    :return: AST node for function in code.
    :rtype: ast object
    """
    module = ast.parse(code)
    for node in ast.walk(module):
        if isinstance(node, ast.FunctionDef):
            return node
    raise ValueError("Code has no function: " + code)


def class_node(code):
    """Return AST node for first class in code string.

    :param str code: Code, e.g. 'class Foo(object):pass
    :return: AST node for class in code.
    :rtype: ast object
    """
    module = ast.parse(code)
    for node in ast.walk(module):
        if isinstance(node, ast.ClassDef):
            return node
    raise ValueError("Code has no class: " + code)


def test_constructor_ObjDef():
    definition = sp.ObjDef('foo.py')
    assert definition.name == 'foo.py'
    assert not definition.errors
    assert not definition.warnings


def test_constructor_ModDef():
    code = "def add(a,b): return a+b"
    module = ast.parse(code)
    definition = sp.ModDef(module, 'foo.py')
    assert definition.name == 'foo.py'
    assert definition.errors == ['Docstring for module is missing']
    assert not definition.warnings


def test_constructorClassDef():
    code = "class Foo(object): pass"
    node = class_node(code)
    definition = sp.ClassDef(node)
    assert definition.name == 'Foo'
    assert definition.errors == ['Docstring for class is missing']
    assert not definition.warnings


def test_constructor_FnDef():
    code = "def add(a,b): return a+b"
    fn_node = function_node(code)
    fn_def = sp.FnDef(fn_node, False)
    assert fn_def.name == 'add'
    assert fn_def.lineno == 1
    assert fn_def.params == ['a', 'b']
    assert fn_def.decorators == set()
    assert fn_def.docstr
    assert fn_def.has_return == True
    assert fn_def.raises_exception == False


def test_parameters_FnDef():
    fn_node = function_node("def add(): pass")
    assert sp.FnDef.parameters(fn_node) == []

    fn_node = function_node("def add(a,b): pass")
    assert sp.FnDef.parameters(fn_node) == ['a', 'b']

    fn_node = function_node("def disp(*args): pass")
    assert sp.FnDef.parameters(fn_node) == ['args']

    fn_node = function_node("def disp(**kwargs): pass")
    assert sp.FnDef.parameters(fn_node) == ['kwargs']

    fn_node = function_node("def disp(p1, *args, **kwargs): pass")
    assert sp.FnDef.parameters(fn_node) == ['p1', 'args', 'kwargs']


def test_has_term_FnDef():
    fn_node = function_node("def add(a,b): return a+b")
    assert sp.FnDef._has_term(fn_node, ast.Return) == True

    fn_node = function_node("def fail(): raise ValueError('')")
    assert sp.FnDef._has_term(fn_node, ast.Raise) == True

    fn_node = function_node("def write(a): pass")
    assert sp.FnDef._has_term(fn_node, ast.Return) == False


def test_decorators_FnDef():
    code = read('class_with_staticmethod.py')
    fn_node = function_node(code)
    assert sp.FnDef._decorators(fn_node) == {'staticmethod'}


def test_ignore_first_param_FnDef():
    fn_def = sp.FnDef(function_node("def add(a,b): return a+b"), False)
    assert fn_def._ignore_first_param() == False
    code = read('class_with_staticmethod.py')
    fn_def = sp.FnDef(function_node(code), True)
    assert fn_def._ignore_first_param() == False
    code = read('class_with_method.py')
    fn_def = sp.FnDef(function_node(code), True)
    assert fn_def._ignore_first_param() == True


def test_param_names_FnDef():
    code = read('class_with_method.py')
    fn_def = sp.FnDef(function_node(code), True)
    assert fn_def._param_names() == ['a', 'b']


def test_check_docstring_FnDef():
    fn_def = sp.FnDef(function_node("def add(a,b): return a+b"), False, False)
    assert fn_def._check_docstring() == False
    fn_def = sp.FnDef(read_function('add_with_docstr.py'), False, False)
    assert fn_def._check_docstring() == True


def test_check_params_described_FnDef():
    fn_def = sp.FnDef(function_node("def add(a,b): return a+b"), False, False)
    fn_def._check_params_described()
    assert len(fn_def.errors) == 2
    fn_def = sp.FnDef(read_function('add_with_docstr.py'), False, False)
    fn_def._check_params_described()
    assert not fn_def.errors


def test_check_params_additional_FnDef():
    code = read('add_with_docstr_extra_param.py')
    fn_def = sp.FnDef(function_node(code), False, False)
    fn_def._check_params_additional()
    assert len(fn_def.errors) == 1
    fn_def = sp.FnDef(read_function('add_with_docstr.py'), False, False)
    fn_def._check_params_additional()
    assert not fn_def.errors


def test_check_params_types_FnDef():
    code = read('add_with_docstr_missing_type.py')
    fn_def = sp.FnDef(function_node(code), False, False)
    fn_def._check_params_types()
    assert len(fn_def.warnings) == 1
    code = read('add_with_docstr_missing_desc.py')
    fn_def = sp.FnDef(function_node(code), False, False)
    fn_def._check_params_types()
    assert len(fn_def.errors) == 1
    fn_def = sp.FnDef(read_function('add_with_docstr.py'), False, False)
    fn_def._check_params_types()
    assert not fn_def.errors


def test_check_returns_FnDef():
    fn_def = sp.FnDef(read_function('add_with_docstr.py'), False, False)
    fn_def._check_returns()
    assert not fn_def.errors
    code = read('add_with_docstr_missing_return.py')
    fn_def = sp.FnDef(function_node(code), False, False)
    fn_def._check_returns()
    assert len(fn_def.errors) == 1
    code = read('add_with_docstr_missing_return_desc.py')
    fn_def = sp.FnDef(function_node(code), False, False)
    fn_def._check_returns()
    assert len(fn_def.errors) == 1
    code = read('add_with_docstr_missing_rtype.py')
    fn_def = sp.FnDef(function_node(code), False, False)
    fn_def._check_returns()
    assert len(fn_def.warnings) == 1
    code = read('add_with_docstr_no_return.py')
    fn_def = sp.FnDef(function_node(code), False, False)
    fn_def._check_returns()
    assert len(fn_def.errors) == 1


def test_check_FnDef():
    fn_def = sp.FnDef(read_function('add_with_docstr.py'), False, False)
    fn_def._check()
    assert not fn_def.errors
    assert not fn_def.warnings


def test_construction_DocStr():
    docstr = sp.DocStr(read_function('add_with_docstr.py'))
    assert docstr.text.startswith('Add two numbers')
    assert docstr.params == [['int', 'a', 'First number.'],
                             ['int', 'b', 'Second number.']]
    assert docstr.returns == [['return', 'Sum of the two numbers.'],
                              ['rtype', 'int']]


def test_find_DocStr():
    code = read('add_with_docstr.py')
    assert sp.DocStr._find(r':param\s(.+):(.+)', code) == [
        ['int a', 'First number.'], ['int b', 'Second number.']]


def test_param_annotations_DocStr():
    code = read('add_with_docstr.py')
    assert sp.DocStr.param_annotations(code) == [['int', 'a', 'First number.'],
                                                 ['int', 'b', 'Second number.']]


def test_return_annotations_DocStr():
    code = read('add_with_docstr.py')
    assert sp.DocStr.return_annotations(code) == \
           [['return', 'Sum of the two numbers.'], ['rtype', 'int']]


def test_ignore():
    node = function_node("def foo(): pass")
    assert not sp.ignore(node)
    node = function_node("def __init__(self): pass")
    assert not sp.ignore(node)
    node = function_node("def _foo(): pass")
    assert sp.ignore(node)


def test_walk_ast(clear_report):
    node = class_node(read('class_with_method.py'))
    sr.Report.new_file('class_with_method.py')
    sp.walk_ast(node.body, False)
    assert sr.Report._rfiles
    assert len(sr.Report._rfile.definitions) == 1
    node = class_node(read('class_with_private_method.py'))
    sr.Report.new_file('class_with_private_method.py')
    sp.walk_ast(node.body, False)
    assert sr.Report._rfiles
    assert len(sr.Report._rfile.definitions) == 0


def test_lint(clear_report):
    sp.lint('testdata/class_with_method.py')
    assert sr.Report._rfiles
    assert len(sr.Report._rfile.definitions) == 3


def test_python_files():
    files = list(sp.python_files('tests'))
    assert len(files) == 4
