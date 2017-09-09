=========================
route53-to-cloudformation
=========================

.. image:: https://img.shields.io/pypi/v/route53-to-cloudformation.svg
    :target: https://pypi.python.org/pypi/route53-to-cloudformation

.. image:: https://travis-ci.org/timeoutdigital/route53-to-cloudformation.svg?branch=master
    :target: https://travis-ci.org/timeoutdigital/route53-to-cloudformation


A tool for dumping an existing Route53 Hosted Zone out as a CloudFormation
YAML template. This can be useful for migrating the hosted zone into control
under CloudFormation.

Installation
------------

From pip:

.. code-block:: bash

    pip install route53-to-cloudformation

Usage
-----

Call the tool with the ID of the hosted zone you wish to convert into a fresh
CloudFormation template. It will output it on stdout, so you can inspect it,
or pipe it into a file.

.. code-block:: bash

    $ route53-to-cloudformation ABC123 | head -n 3
    AWSTemplateFormatVersion: 2010-09-09
    Description: DNS for example.com
    Resources:
    $ route53-to-cloudformation ABC123 > mytemplate.yml
