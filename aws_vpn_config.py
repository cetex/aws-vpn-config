#!/usr/bin/env python
"""
Class to make aws vpn configuration easily accessible.
"""
import py_route
import boto3
import json

class awsVpnConfig(object):
    def __init__(self, boto_client=None, region='eu-west-1'):
        if boto_client is None:
                self.client = boto3.client('ec2', region_name=region)
        else:
                self.client = boto_client
        self.region = region
        self.data = None

    def get(self):
        self.getVpnConfig()
        self.parseXML()
        self.getVgwConfig()
        self.getVpcConfig()
        return self.data

    def getVpnConfig(self):
        """
        Gets vpn configurations for the region
        """
        data = self.client.describe_vpn_connections(DryRun=False)
        self.data = []
        # Remove deleted vpns since they're useless for us and just breaks everything else.
        for vpn in data['VpnConnections']:
            if vpn['State'] != "deleted":
                self.data.append(vpn)
        # Hacky way, but region may be nice to access within each config
        for vpn in self.data:
            vpn['Region'] = self.region
        for vpn in self.data:
            vpn['Tags'] = self.fixTags(vpn['Tags'])

    def getVpcConfig(self):
        """
        Gets vgw + vpc config and adds what subnet the vpn is for
        also gets vpc tags
        """
        data = self.client.describe_vpcs()
        vpcData = data['Vpcs']
        for vpn in self.data:
            for vpc in vpcData:
                if vpn['VpcId'] == vpc['VpcId']:
                    vpn['VpcTags'] = self.fixTags(vpc['Tags'])
                    vpn['CidrBlock'] = vpc['CidrBlock']

    def getVgwConfig(self):
        """
        Gets vgw config and adds what vpc the vpn is for
        also gets vgw tags
        """
        data = self.client.describe_vpn_gateways()
        vgwData = data['VpnGateways']
        for vpn in self.data:
            for vgw in vgwData:
                if vpn['VpnGatewayId'] == vgw['VpnGatewayId']:
                    vpn['VgwTags'] = self.fixTags(vgw['Tags'])
                    vpn['VpcId'] = vgw['VpcAttachments'][0]['VpcId']


    def parseXML(self):
        """
        Concerts CustomerGatewayConfiguration
        from XML to json
        """
        for vpn in self.data:
            if 'CustomerGatewayConfiguration' in vpn:
                vpn['CustomerGatewayConfiguration'] = \
                        py_route.amzn_xml_to_json(vpn['CustomerGatewayConfiguration'])

    def fixTags(self, tags):
        """
        Modifies tags from a list:
        [{u'Key': 'aws:cloudformation:stack-name', u'Value': 'Compute1'},
        {u'Key': 'aws:cloudformation:logical-id',u'Value': 'VpnConnectionSecondary'}]
        to a more pythonic dict like:
        {'aws:cloudformation:stack-name': 'Compute1',
        'aws:cloudformation:logical-id': 'VpnConnectionSecondary'}
        """
        newTags = {}
        for tag in tags:
            newTags[tag['Key']] = tag['Value']
        return newTags

