# -*- coding:utf-8 -*-
from setuptools import setup, find_packages
from pypandoc import convert
def read_md(f):
	return convert(f,'rst')
	
setup(
	author = 'oyp',
	author_email = '13128779595@163.com',
	name = 'basic',
	version = '0.0.1',
	packages = find_packages(),
	description = "basic tools project short description",
	long_description = read_md('README.md') ,
	install_requires = [],
	classifiers = [
		'Development Status :: 4-Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.7',
		'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
		])
