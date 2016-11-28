#!/usr/bin/env python
from aws_vpn_config import awsVpnConfig
from pprint import pprint
from jinja2 import Environment, FileSystemLoader
import os

cfgrdr = awsVpnConfig(region='eu-west-1')
config = cfgrdr.get()

# Resort the vpn configs
# We want to split the output by which router it's going to be used on.
# So let's move the list of configs to a dict based on what router it's
# connecting to.
newConfig = {}
for vpn in config:
    # Gets second octet "x" from CidrBlock 10.x.0.0/y
    # This is used for naming tunnel interfaces in templating
    vpn['NetId'] = vpn['CidrBlock'].split(".")[1]
    
    # A bit ugly, but both (all) CustomerGatewayConfigurations for 
    # one vpn config are always going to the same Customer Gateway ip
    # so we just need to grab any of them.
    routerIP = vpn['CustomerGatewayConfiguration'][0]['cgw_tunnel_outside_address']
    if routerIP not in newConfig:
        newConfig[routerIP] = []
    
    # append routerip inside the vpn config, also not pretty but works
    vpn['RouterIP'] = routerIP
    newConfig[routerIP].append(vpn)
    pprint(newConfig[routerIP])


templates = ['myCisco']
templatedir = os.path.realpath("./templates")
for key, value in newConfig.items():
    ENV = Environment(loader=FileSystemLoader(templatedir))
    for tmplt in templates:
        template = ENV.get_template(tmplt + ".j2")
        print(template.render(config=value))
