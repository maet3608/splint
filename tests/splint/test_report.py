"""
.. module:: test_report
   :synopsis: Unit tests for report module
"""

import pytest

import splint.splint as sp
import splint.report as sr


@pytest.fixture(scope="function")
def clear_report():
    sr.Report.clear()


def create_definition():
    definition = sp.ObjDef('foo')
    definition.errors.append('error')
    definition.warnings.extend(['warning1', 'warning2'])
    return definition


def test_constructor_RFile():
    rfile = sr.RFile('somefile.py')
    assert rfile.filepath == 'somefile.py'
    assert rfile.definitions == []
    assert rfile.n_errors == 0
    assert rfile.n_warnings == 0


def test_add_RFile():
    rfile = sr.RFile('somefile.py')
    definition = create_definition()
    rfile.add(definition)
    assert rfile.definitions[0] == definition
    assert rfile.n_errors == 1
    assert rfile.n_warnings == 2


def test_has_issues_RFile():
    rfile = sr.RFile('somefile.py')
    assert not rfile.has_issues()
    rfile.add(create_definition())
    assert rfile.has_issues()


def test_constructor_Report(clear_report):
    assert len(sr.Report._rfiles) == 0
    assert not sr.Report._rfile


def test_new_file_Report(clear_report):
    sr.Report.new_file('foo.py')
    assert len(sr.Report._rfiles) == 1
    assert sr.Report._rfile


def test_add_Report(clear_report):
    sr.Report.new_file('foo.py')
    definition = create_definition()
    sr.Report.add(definition)
    assert sr.Report._rfile.definitions == [definition]
