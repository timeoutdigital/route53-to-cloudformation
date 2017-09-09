# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import datetime as dt
import sys

import boto3
import yaml
from six.moves import builtins

__version__ = '1.0.0'


def main():
    args = parser.parse_args(sys.argv[1:])
    template = create_cloudformation_template(args.hosted_zone_id)
    print(template)


parser = argparse.ArgumentParser(
    description="""
    Output a Route53 Hosted Zone as a CloudFormation YAML template.
    """
)
parser.add_argument(
    'hosted_zone_id',
    type=str,
    help='The ID of the Route53 Hosted Zone to export',
)


route53 = boto3.client('route53')


def create_cloudformation_template(hosted_zone_id):
    return yaml.dump(
        create_cloudformation_dict(hosted_zone_id),
        allow_unicode=True,
        default_flow_style=False,
    )


def create_cloudformation_dict(hosted_zone_id):
    template = {
        'AWSTemplateFormatVersion': dt.date(2010, 9, 9),
    }
    zone_data = route53.get_hosted_zone(Id=hosted_zone_id)['HostedZone']
    domain_name = zone_data['Name'].rstrip('.')

    template['Description'] = 'DNS for ' + domain_name

    template['Resources'] = create_resources(zone_data)

    return template


def create_resources(zone_data):
    resources = {
        'HostedZone': {
            'Type': 'AWS::Route53::HostedZone',
            'Properties': {
                'Name': zone_data['Name'],
                'HostedZoneConfig': {
                    'Comment': zone_data['Name'],
                }
            }
        }
    }

    for x, record_set in enumerate(all_record_sets(zone_data['Id'])):
        # Don't export NS and SOA for root of domain, as Route53 automatically creates them for new zones
        if record_set['Name'] == zone_data['Name'] and record_set['Type'] in ('NS', 'SOA'):
            continue

        name = make_name(record_set)

        properties = {
            'HostedZoneId': {'Ref': 'HostedZone'},
            'Name': record_set['Name'],
            'Type': record_set['Type'],
        }
        if 'ResourceRecords' in record_set:
            properties['ResourceRecords'] = [
                rec['Value'] for rec in record_set['ResourceRecords']
            ]
            properties['TTL'] = record_set['TTL']
        else:
            properties['AliasTarget'] = {
                'DNSName': record_set['AliasTarget']['DNSName'],
                'HostedZoneId': record_set['AliasTarget']['HostedZoneId'],
                'EvaluateTargetHealth': record_set['AliasTarget']['EvaluateTargetHealth'],
            }

        resources[name] = {
            'Type': 'AWS::Route53::RecordSet',
            'Properties': properties
        }
    return resources


def all_record_sets(hosted_zone_id):
    paginator = route53.get_paginator('list_resource_record_sets')
    pages = paginator.paginate(
        HostedZoneId=hosted_zone_id,
    )
    for page in pages:
        for record_set in page['ResourceRecordSets']:
            yield record_set


def make_name(record_set):
    name = record_set['Name'].title()

    # * is common in record sets but comes as \\052
    name = name.replace('\\052', 'Star')

    # Replace a load of characters disallowed in Cloudformation
    name = name.replace('.', '').replace('_', '').replace('-', '')

    # Make it more unique by including type
    name += record_set['Type']

    return name


# Make PyYAML use nice order
# ref https://sourceforge.net/p/yaml/mailman/message/23596068/

def represent_dict(self, data):
    priority = {
        # Top level
        'AWSTemplateFormatVersion': 10,
        'Description': 20,
        'Resources': 30,
        # Resources
        'HostedZone': 10,
        # Per resource
        'Type': 10,
        'Properties': 20,
        # Properties
        'Name': 10,
    }

    def key_function(tup):
        key, value = tup
        return priority.get(key, 100), key

    items = list(data.items())
    items.sort(key=key_function)
    return self.represent_mapping('tag:yaml.org,2002:map', items)


yaml.add_representer(dict, represent_dict)

if sys.version_info[0] < 3:
    # Make PyYAML represent all unicode as strings, since we aren't using safe_dump
    # Ref https://stackoverflow.com/questions/1950306/pyyaml-dumping-without-tags

    def unicode_representer(dumper, uni):
        return yaml.ScalarNode(tag='tag:yaml.org,2002:str', value=uni)

    yaml.add_representer(builtins.unicode, unicode_representer)


if __name__ == '__main__':
    main()
