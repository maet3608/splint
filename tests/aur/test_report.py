"""
.. module:: test_report
   :synopsis: Unit tests for report module
"""

import pytest

import aur.splint as ad
import aur.report as ar


@pytest.fixture(scope="function")
def clear_report():
    ar.Report.clear()


def create_definition():
    definition = ad.ObjDef('foo')
    definition.errors.append('error')
    definition.warnings.extend(['warning1', 'warning2'])
    return definition


def test_constructor_RFile():
    rfile = ar.RFile('somefile.py')
    assert rfile.filepath == 'somefile.py'
    assert rfile.definitions == []
    assert rfile.n_errors == 0
    assert rfile.n_warnings == 0


def test_add_RFile():
    rfile = ar.RFile('somefile.py')
    definition = create_definition()
    rfile.add(definition)
    assert rfile.definitions[0] == definition
    assert rfile.n_errors == 1
    assert rfile.n_warnings == 2


def test_has_issues_RFile():
    rfile = ar.RFile('somefile.py')
    assert not rfile.has_issues()
    rfile.add(create_definition())
    assert rfile.has_issues()


def test_constructor_Report(clear_report):
    assert len(ar.Report._rfiles) == 0
    assert not ar.Report._rfile


def test_new_file_Report(clear_report):
    ar.Report.new_file('foo.py')
    assert len(ar.Report._rfiles) == 1
    assert ar.Report._rfile


def test_add_Report(clear_report):
    ar.Report.new_file('foo.py')
    definition = create_definition()
    ar.Report.add(definition)
    assert ar.Report._rfile.definitions == [definition]
