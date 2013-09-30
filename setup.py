# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='python-subledger',
    version='0.1',
    author=u'R.R. Nederhoed',
    author_email='rr@nederhoed.com',
    packages=['subledger'],
    url='https://github.com/nederhoed/python-subledger',
    license='No licence yet, see LICENCE.txt',
    description='Python client for the Subledger in-app accounting service.',
    long_description=open('README.md').read(),
    zip_safe=False,
    packages=find_packages(),
)
