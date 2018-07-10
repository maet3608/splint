"""
.. module:: report
   :synopsis: Report class that collects all issues discovered by the linter
"""

from __future__ import print_function


class RFile(object):
    """Stores linter warnings and errors for a specific file."""

    def __init__(self, filepath):
        """Construct report storage for a specific file.

        :param str filepath: Path of the file the report belongs to.
        """

        self.filepath = filepath
        self.definitions = []
        self.n_errors = 0
        self.n_warnings = 0

    def add(self, definition):
        """Add a object definition with its errors and warnings to the report.

        :param ObjDef definition: A module, class or function definition.
        """
        self.definitions.append(definition)
        self.n_errors += len(definition.errors)
        self.n_warnings += len(definition.warnings)

    def has_issues(self):
        """Return true if report for file has errors or warnings.

        :return: True if there are any errors or warnings/
        :rtype: bool
        """
        return self.n_errors + self.n_warnings > 0

    def display(self):  # pragma: no cover
        """Display errors and warnings for the file."""
        for definition in self.definitions:
            if definition.errors or definition.warnings:
                print(definition)
                for error in definition.errors:
                    print("  E: " + error)
                for warning in definition.warnings:
                    print("  W: " + warning)


class Report(object):
    """Stores all file reports."""

    _rfiles = []
    _rfile = None  # current file report

    @staticmethod
    def clear():
        """Clear report"""
        Report._rfiles = []
        Report._rfile = None

    @staticmethod
    def new_file(filepath):
        """Create new report for a file.

        Current file report is set to the new report.

        :param str filepath: Path of the file the report belongs to.
        """
        rfile = RFile(filepath)
        Report._rfile = rfile
        Report._rfiles.append(rfile)

    @staticmethod
    def add(definition):
        """Add object definition to the current file report.

        :param ObjDef definition: A module, class or function definition.
        """
        Report._rfile.add(definition)

    @staticmethod
    def display():  # pragma: no cover
        """
        Display the linter report.

        :return: The number of errors and warnings
        :rtype: Tuple, (number_of_errors, number_of_warnings)
        """

        divider = "*" * 80
        n_errors = 0
        n_warnings = 0
        for rfile in Report._rfiles:
            if rfile.has_issues():
                print(divider)
                print(rfile.filepath)
                rfile.display()
                n_errors += rfile.n_errors
                n_warnings += rfile.n_warnings

        if n_errors or n_warnings:
            print(divider)
            print("SUMMARY")
            print("errors: %d" % n_errors)
            print("warnings: %d" % n_warnings)

        return n_errors, n_warnings
