#!/usr/bin/python

from coapthon.client.helperclient import HelperClient
import socket
from coapthon import defines
import json

import logging.config
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
'''s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')'''
s.bind(('192.168.1.202', 0))

print s.getsockname()

client = HelperClient(server=('224.0.1.187', 5683), sock=s)
request = client.mk_request(defines.Codes.GET, 'oic/res')
request.type = defines.Types['NON']
request.source = s.getsockname()
print request.pretty_print()
response = client.send_request(request, callback=None, timeout=None)

devlist = json.loads(response.payload)

smartdev = []
for d in devlist:
    for link in d['links']:
        if link['rt'] != 'oic.wk.rdpub':
            smartdev.append(d)

print smartdev

client.close()
