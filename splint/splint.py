"""
.. module:: splint
   :synopsis: Checks that docstrings for functions describe all parameters.
"""

from __future__ import print_function, absolute_import

import ast
import sys
import os
import os.path as op
import re

from .report import Report


class ObjDef(object):
    """Base class for definitions of modules, classes or functions."""

    def __init__(self, name):
        """Construct definition base class.

        :param str name: Name of the definition.
        """
        self.name = name
        self.errors = []
        self.warnings = []


class ModDef(ObjDef):
    """Encapsulates a module definition"""

    def __init__(self, mod_node, filepath):
        """Construct module definition.

        :param ast.ModDef mod_node: AST node of module
        :param str filepath: Filepath of module
        """
        _, filename = op.split(filepath)
        super(ModDef, self).__init__(filename)
        if not ast.get_docstring(mod_node):
            self.errors.append("Docstring for module is missing")

    def __repr__(self):  # pragma: no cover
        return "module: " + self.name


class ClassDef(ObjDef):
    """Encapsulates a class definition"""

    def __init__(self, class_node):
        """Construct class definition.

        :param ast.ClassDef class_node: AST node of class
        """
        super(ClassDef, self).__init__(class_node.name)
        self.lineno = class_node.lineno
        if not ast.get_docstring(class_node):
            self.errors.append("Docstring for class is missing")

    def __repr__(self):  # pragma: no cover
        return "{}: class: {}".format(self.lineno, self.name)


class FnDef(ObjDef):
    """Encapsulates a function definition"""

    def __init__(self, fn_node, is_method, check=True):
        """Construct function definition.

        :param ast.FnDef fn_node: AST node of a function.
        :param bool is_method: True if function is a class method.
        :param bool check: Perform docstr checks at construction.
        """
        super(FnDef, self).__init__(fn_node.name)
        self.is_method = is_method
        self.lineno = fn_node.lineno
        self.params = FnDef.parameters(fn_node)
        self.decorators = FnDef._decorators(fn_node)
        self.docstr = DocStr(fn_node)
        self.has_return = FnDef._has_term(fn_node, ast.Return) or \
                          FnDef._has_term(fn_node, ast.Yield)
        self.raises_exception = FnDef._has_term(fn_node, ast.Raise)
        if check:
            self._check()

    def _add_error(self, text):  # pragma: no cover
        self.errors.append(text)

    def _add_warning(self, text):  # pragma: no cover
        self.warnings.append(text)

    @staticmethod
    def parameters(fn_node):
        """Return parameter names of function.

        :param ast.FnDef fn_node: AST node of a function.
        :return: List of parameter names
        :rtype: list
        """

        def name(args):
            if isinstance(args, str):
                return args
            return args.id if 'id' in args._fields else args.arg

        args = fn_node.args
        params = [name(a) for a in args.args if name(a)]
        if args.vararg:
            params.append(name(args.vararg))
        if args.kwarg:
            params.append(name(args.kwarg))
        return params

    @staticmethod
    def _has_term(fn_node, term):
        """Return True if subtree of fn_node has the given AST term"""
        return any(isinstance(n, term) for n in ast.walk(fn_node))

    @staticmethod
    def _decorators(node):
        """Return set of decorator names for the given node."""
        return {d.id for d in node.decorator_list}

    def _ignore_first_param(self):
        """True if function is method and not staticmethod."""
        return self.is_method and 'staticmethod' not in self.decorators

    def _param_names(self):
        """Return set of function parameter names without 'selfs' and alike."""
        return self.params[1:] if self._ignore_first_param() else self.params

    def _check_docstring(self):
        if not self.docstr.text:
            self._add_error('Docstring missing')
            return False
        return True

    def _check_params_described(self):
        """Check if all function params have a docstring representation."""
        ds_names = {name for _, name, _ in self.docstr.params}
        for name in self._param_names():
            if name not in ds_names:
                self._add_error(
                    "':param {type} %s: {description}' is missing." % name)

    def _check_params_additional(self):
        """Check if docstring has more params than function."""
        ds_names = {name for _, name, _ in self.docstr.params}
        fn_names = set(self._param_names())
        for name in ds_names - fn_names:
            self._add_error("Additional ':param %s' in docstring." % name)

    def _check_params_types(self):
        """Check if type or description for parameter is missing"""
        for typ, name, description in self.docstr.params:
            if not typ:
                self._add_warning('No type in docstring for parameter: ' + name)
            if not description:
                self._add_error(
                    'No description in docstring for parameter: ' + name)

    def _check_returns(self):
        """Check if description of return value is missing"""
        returns = {name: desc for name, desc in self.docstr.returns}
        for name, desc in self.docstr.returns:
            if not desc:
                self._add_error("Description after '%s': missing" % name)
        if self.has_return:
            if 'return' not in returns:
                self._add_error("':return: {description}' is missing.")
            if 'rtype' not in returns:
                self._add_warning("':rtype: {description}' is missing.")
        elif returns:
            self._add_error("Docstring describes return values " +
                            "but function does not return anything!")

    def _check(self):
        """Perform all checks for docstring correctness."""
        if self._check_docstring():
            self._check_params_described()
            self._check_params_additional()
            self._check_params_types()
            self._check_returns()

    def __repr__(self):  # pragma: no cover
        sig = ','.join(self.params)
        kind = 'method' if self.is_method else 'function'
        return "{}: {}: {}({})".format(self.lineno, kind, self.name, sig)


class DocStr(object):
    """Encapsulates a Docstring."""

    def __init__(self, fn_node):
        """
        Construct class definition.

        :param ast.FnDef fn_node: AST node of function
        """
        docstr = ast.get_docstring(fn_node)
        self.text = docstr if docstr else ''
        self.params = DocStr.param_annotations(self.text)
        self.returns = DocStr.return_annotations(self.text)

    @staticmethod
    def _find(regex, text):
        """Find all matches of the regular expression within the text"""
        return [[e.strip() for e in ms] for ms in re.findall(regex, text)]

    @staticmethod
    def param_annotations(text):
        """
        Return list of parameter descriptions in docstring text.

        :param str text: Docstring text
        :return: List of lists of format [type, name, description]
        :rtype: list
        """
        regex = r'\s*:param\s([^\s]+\s)?([^\s]+):(.*)'
        return DocStr._find(regex, text)

    @staticmethod
    def return_annotations(text):
        """
        Return annotations of return value.

        :param str text: Docstring text
        :return: Tuple of format (type, description) or None
        :rtype: Tuple or None
        """
        regex = r'\s*:(return|rtype):(.*)'
        return DocStr._find(regex, text)

    def __repr__(self):  # pragma: no cover
        return self.text


def ignore(node):
    """
    Return true if AST node should be ignored when walking the AST.

    :param AST node: AST node.
    :return: True if node should be ignored.
    :rtype: bool
    """
    return isinstance(node, ast.FunctionDef) and \
           node.name.startswith('_') and node.name != '__init__'


def walk_ast(body, is_method):
    """
    Walks the AST starting from the given body and fills report.

    :param AST body: Body of an AST node
    :param bool is_method: True if walking the body of a class method.
    """
    for node in body:
        if ignore(node):
            continue
        if isinstance(node, ast.ClassDef):
            Report.add(ClassDef(node))
            walk_ast(node.body, True)
        elif isinstance(node, ast.FunctionDef):
            Report.add(FnDef(node, is_method))
            walk_ast(node.body, True)


def lint(filepath):
    """Lint the given file.

    :param str filepath: Path to file to lint.
    """
    with open(filepath) as f:
        code = f.read()
    module = ast.parse(code)
    Report.new_file(filepath)
    Report.add(ModDef(module, filepath))
    walk_ast(module.body, False)


def python_files(startdir):
    """
    Return paths of all python files within startdir and all sub-dirs

    :param str startdir: Directory to recursively start the search.
    :return: Full paths of all python files.
    :rtype: generator over file paths
    """
    for dirpath, _, filenames in os.walk(startdir):
        for filename in filenames:
            if filename.endswith('.py'):
                yield os.path.abspath(os.path.join(dirpath, filename))


def main():  # pragma: no cover
    """
    main function to run if started from cmdline.
    """
    argv = sys.argv
    startdir = argv[1] if len(argv) == 2 else '.'
    for fpath in python_files(startdir):
        lint(fpath)

    num_errors, _ = Report.display()
    sys.exit(num_errors)


if __name__ == '__main__':  # pragma: no cover
    main()
