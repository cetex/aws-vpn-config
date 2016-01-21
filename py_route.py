import boto3
import json
import re
import xml.etree.ElementTree as ET
import jinja2

def amzn_xml_to_json ( amzn_xml ):

	root = ET.fromstring(amzn_xml)
        tun = dict()

	for tunnel in root.findall("ipsec_tunnel"):
		# Local Params of the VPN gateway
                tun['cgw_tunnel_outside_address']  = tunnel.find("customer_gateway/tunnel_outside_address/ip_address").text
                tun['cgw_tunnel_inside_address']  = tunnel.find("customer_gateway/tunnel_inside_address/ip_address").text
                tun['cgw_tunnel_inside_mask']  = tunnel.find("customer_gateway/tunnel_inside_address/network_mask").text
                tun['cgw_cidr']  = tunnel.find("customer_gateway/tunnel_inside_address/network_cidr").text
                tun['cgw_bgp_asn']  = tunnel.find("customer_gateway/bgp/asn").text
                tun['cgw_bgp_holdtime']  = tunnel.find("customer_gateway/bgp/hold_time").text

		# Amazon's side of the VPN gateway
		tun['vpn_tunnel_outside_address']  = tunnel.find("vpn_gateway/tunnel_outside_address/ip_address").text
		tun['vpn_tunnel_inside_address']  = tunnel.find("vpn_gateway/tunnel_inside_address/ip_address").text
		tun['vpn_tunnel_inside_mask']  = tunnel.find("vpn_gateway/tunnel_inside_address/network_mask").text
		tun['vpn_cidr']  = tunnel.find("vpn_gateway/tunnel_inside_address/network_cidr").text
                tun['vpn_bgp_asn']  = tunnel.find("vpn_gateway/bgp/asn").text
                tun['vpn_bgp_holdtime']  = tunnel.find("vpn_gateway/bgp/hold_time").text


		# IPSec specific params
		## Phase 1
		tun['ike_authentication_protocol'] = tunnel.find("ike/authentication_protocol").text
                tun['ike_encryption_protocol'] = tunnel.find("ike/encryption_protocol").text
                tun['ike_lifetime'] = tunnel.find("ike/lifetime").text
                tun['ike_perfect_forward_secrecy'] = tunnel.find("ike/perfect_forward_secrecy").text
                tun['ike_mode'] = tunnel.find("ike/mode").text
                tun['ike_pre_shared_key'] = tunnel.find("ike/pre_shared_key").text


		## Phase 2
		tun['ipsec_protocol'] = tunnel.find("ipsec/protocol").text
                tun['ipsec_authentication_protocol'] = tunnel.find("ipsec/authentication_protocol").text
                tun['ipsec_encryption_protocol'] = tunnel.find("ipsec/encryption_protocol").text
                tun['ipsec_lifetime'] = tunnel.find("ipsec/lifetime").text
                tun['ipsec_perfect_forward_secrecy'] = tunnel.find("ipsec/perfect_forward_secrecy").text
                tun['ipsec_mode'] = tunnel.find("ipsec/mode").text
                tun['ipsec_clear_df_bit'] = tunnel.find("ipsec/clear_df_bit").text
		tun['ipsec_fragmentation_before_encryption'] = tunnel.find("ipsec/fragmentation_before_encryption").text
		tun['ipsec_tcp_mss_adjustment'] = tunnel.find("ipsec/tcp_mss_adjustment").text
                tun['ipsec_dpd_interval'] = tunnel.find("ipsec/dead_peer_detection/interval").text
                tun['ipsec_dpd_retries'] = tunnel.find("ipsec/dead_peer_detection/retries").text

		return tun

## Main 
client = boto3.client('ec2')

response = client.describe_vpn_connections( DryRun=False, )

vpns = response["VpnConnections"]

i = 0
conf = {} 
for child in vpns:
    for key, value in child.iteritems():
        if re.search("CustomerGatewayConfiguration", key):
            conf[i] = amzn_xml_to_json(value)
    i += 1 

for gateway in conf:
    print gateway

