# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from textwrap import dedent

import pytest
from botocore.stub import Stubber

from route53_to_cloudformation import main, make_name, route53


@pytest.fixture(scope='function', autouse=True)
def route53_stub():
    with Stubber(route53) as stubber:
        yield stubber


def test_main(capsys, monkeypatch, route53_stub):
    route53_stub.add_response(
        'get_hosted_zone',
        expected_params={
            'Id': 'ABC123',
        },
        service_response={
            'HostedZone': {
                'Id': 'ABC123',
                'Name': 'example.com.',
                'ResourceRecordSetCount': 1,
                'CallerReference': 'foo',
            },
        }
    )
    route53_stub.add_response(
        'list_resource_record_sets',
        expected_params={
            'HostedZoneId': 'ABC123',
        },
        service_response={
            'ResourceRecordSets': [
                {
                    'Name': 'example.com.',
                    'Type': 'NS',
                    'TTL': 123,
                    'ResourceRecords': [{'Value': 'ignored'}],
                },
                {
                    'Name': 'example.com.',
                    'Type': 'SOA',
                    'TTL': 123,
                    'ResourceRecords': [{'Value': 'ignored'}],
                },
                {
                    'Name': 'example.com.',
                    'Type': 'A',
                    'TTL': 123,
                    'ResourceRecords': [
                        {'Value': '1.2.3.4'},
                    ]
                },
                {
                    'Name': 'alias.example.com.',
                    'Type': 'A',
                    'TTL': 123,
                    'AliasTarget': {
                        'HostedZoneId': 'DEF456',
                        'DNSName': 'alias.example.org',
                        'EvaluateTargetHealth': True,
                    }
                }
            ],
            'IsTruncated': False,
            'MaxItems': '100',
        }
    )
    monkeypatch.setattr(sys, 'argv', ['route53-to-cloudformation', 'ABC123'])

    main()

    out, err = capsys.readouterr()
    assert out == dedent('''\
        AWSTemplateFormatVersion: 2010-09-09
        Description: DNS for example.com
        Resources:
          HostedZone:
            Type: AWS::Route53::HostedZone
            Properties:
              Name: example.com.
              HostedZoneConfig:
                Comment: example.com.
          AliasExampleComA:
            Type: AWS::Route53::RecordSet
            Properties:
              Name: alias.example.com.
              Type: A
              AliasTarget:
                DNSName: alias.example.org
                EvaluateTargetHealth: true
                HostedZoneId: DEF456
              HostedZoneId:
                Ref: HostedZone
          ExampleComA:
            Type: AWS::Route53::RecordSet
            Properties:
              Name: example.com.
              Type: A
              HostedZoneId:
                Ref: HostedZone
              ResourceRecords:
              - 1.2.3.4
              TTL: 123

    ''')
    assert err == ''


@pytest.mark.parametrize('name,type_,expected', [
    ['example.com.', 'A', 'ExampleComA'],
    ['\\052.example.com.', 'A', 'StarExampleComA'],
    ['_foo.example.com.', 'A', 'FooExampleComA'],
    ['-bar.example.com.', 'A', 'BarExampleComA'],
])
def test_make_name(name, type_, expected):
    assert make_name({'Name': name, 'Type': type_}) == expected
