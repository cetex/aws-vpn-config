#!/usr/bin/env python
from aws_vpn_config import awsVpnConfig
from pprint import pprint
from jinja2 import Environment, FileSystemLoader
import os

cfgrdr = awsVpnConfig(region='ap-southeast-1')
config = cfgrdr.get()

for index, vpn in enumerate(config):
    print("VPN config: {}".format(index))
    pprint(vpn)

for vpn in config:
    # Gets second octet "x" from CidrBlock 10.x.0.0/y
    # This is used for naming tunnel interfaces in templating
    vpn['NetId'] = vpn['CidrBlock'].split(".")[1]

templates = ['myCisco']
templatedir = os.path.realpath("./templates")
ENV = Environment(loader=FileSystemLoader(templatedir))
for tmplt in templates:
    template = ENV.get_template(tmplt + ".j2")
    print template.render(config=config)
