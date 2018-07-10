from codecs import open
from os import path

from setuptools import setup, find_packages

import splint

EXCLUDE = ['testdata*', 'tests*']


def long_description():
    """Return README.md as string for long description."""
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
    name="splint",
    version=splint.__version__,
    url='https://github.com/maet3608/sphinx-docstr-linter',
    author='Stefan Maetschke',
    author_email='stefan.maetschke@gmail.com',
    packages=find_packages(exclude=EXCLUDE),
    description='Linter for Python docstrings with ReStructuredText.',
    long_description=long_description(),
    keywords='linter python docstring restructured text',
    license='Apache Software License (http://www.apache.org/licenses/LICENSE-2.0)',
    scripts=['bin/splint'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)
