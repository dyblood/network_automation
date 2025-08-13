import sys
from argparse import ArgumentParser
from ncclient import manager
import xml.dom.minidom

if __name__ == '__main__':
    parser = ArgumentParser(description='Select options.')
    # Input parameters
    parser.add_argument('--host', type=str, required=False,
                        help="The device IP or DN")
    parser.add_argument('-u', '--username', type=str, default='cisco',
                        help="Go on, guess!")
    parser.add_argument('-p', '--password', type=str, default='cisco',
                        help="Yep, this one too! ;-)")
    parser.add_argument('--port', type=int, default=830,
                        help="Specify this if you want a non-default port")
    args = parser.parse_args()

    m =  manager.connect(host='172.20.19.201',
                         port=830,
                         username='devon.youngblood',
                         password='devNOR!@%125',
                         device_params={'name':"iosxe"})

    hostname_filter = '''
                      <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                          </native>
                      </filter>
                      '''

       # Pretty print the XML reply
    xmlDom = xml.dom.minidom.parseString( str( m.get_config('running', hostname_filter)))
    print(xmlDom.toprettyxml( indent = "  " ))