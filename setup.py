# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import codecs
import os
import re

from setuptools import setup


def get_version(filename):
    with codecs.open(filename, 'r', 'utf-8') as fp:
        contents = fp.read()
    return re.search(r'__version__ = ["\']([^"\']+)["\']', contents).group(1)


version = get_version(os.path.join('route53_to_cloudformation.py'))

with codecs.open('README.rst', 'r', 'utf-8') as readme_file:
    readme = readme_file.read()

with codecs.open('HISTORY.rst', 'r', 'utf-8') as history_file:
    history = history_file.read()


setup(
    name='route53-to-cloudformation',
    version=version,
    author='Adam Johnson',
    author_email='me@adamj.eu',
    description='Dump an existing Route53 Hosted Zone as a CloudFormation '
                'YAML template',
    long_description=readme + '\n\n' + history,
    license='ISC License',
    url='https://github.com/timeoutdigital/route53-to-cloudformation',
    keywords=['aws', 'cloudformation', 'route53'],
    install_requires=[
        'boto3>=1.4.0',
        'PyYAML',
        'six',
    ],
    py_modules=['route53_to_cloudformation'],
    entry_points={
        'console_scripts': [
            'route53-to-cloudformation = route53_to_cloudformation:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
)
