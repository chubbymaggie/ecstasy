#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup.py script for setuptools.
"""

import re

from setuptools import setup, find_packages

version = ''

with open('ecstasy/__init__.py') as init:
	version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
						init.read(), re.MULTILINE).group(1)

with open('README.rst') as readme:
	long_description = readme.read()

requirements = [
	"enum34==1.0.4"
]

test_requirements = [
	"unittest2==1.1.0",
	"python-coveralls==2.5.0"
]

setup(
	name='ecstasy',

	version=version,

	description='A command-line-tool beautifier.',
	long_description=long_description,

	url='https://github.com/goldsborough/ecstasy',

	author='Peter Goldsborough',
	author_email='petergoldsborough@hotmail.com',

	license='MIT',

	classifiers=[
		'Development Status :: 4 - Beta',

		'Intended Audience :: Developers',
		'Topic :: Software Development',

		'License :: OSI Approved :: MIT License',

		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
	],

	keywords='command-line tools formatting styling beautifier markup',

	include_package_data=True,

	packages=find_packages(exclude=['contrib', 'docs', 'test*']),

	install_requires=requirements,

	test_suite="tests",

	tests_require=test_requirements
)
