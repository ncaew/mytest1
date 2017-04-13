import logging
import json

from coapthon.resources.resource import Resource
from coapthon.server.coap import CoAP
from coapthon.client.helperclient import HelperClient
import socket
from coapthon import defines

import threading
import uuid

from multiprocessing import Process
import os

import time

logger = logging.getLogger(__name__)


class AlarmLv1Resource(Resource):

    def __init__(self, name="AlarmLv1", coap_server=None, info={}):
        super(AlarmLv1Resource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)

        self.info = info
        self.payload = json.dumps(self.info)
        self.p = Process(target=self.play)
        self.stop = False

    def play(self):
        while not self.stop:
            os.system('ogg123 static/sounds/alerm.ogg')

    def render_GET(self, request):
        self.payload = json.dumps(self.info)
        return self

    def render_POST(self, request):
        logger.debug('%s get POST %s', self.__class__.__name__, request.payload)
        val = json.loads(request.payload)
        if val['value']:
            if not self.p.is_alive():
                self.stop = False
                self.p.start()
        else:
            if self.p.is_alive():
                self.stop = True
                self.p.terminate()
        return self


class OicAlarmLv1(CoAP):

    def __init__(self, host, port, multicast=False, starting_mid=None):
        CoAP.__init__(self, (host, port), multicast, starting_mid)
        self.oic_device = dict(di=str(uuid.uuid4()))
        self.oic_device['lt'] = 86400
        self.oic_device['n'] = self.__class__.__name__
        uri_prefix = 'coap://%s:%d' % (host, port)
        oic_d_res = dict(href=uri_prefix + '/oic/d', rel='contained', rt='oic.d.alarmlv1')
        alarm_res = dict(href=uri_prefix + '/AlarmLv1ResURI', rel='contained', rt='oic.r.switch.binary')
        self.oic_device['links'] = [oic_d_res, alarm_res]
        self.add_resource('/AlarmLv1ResURI', AlarmLv1Resource(coap_server=self))

    def publish(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        '''s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')'''
        s.bind(('0.0.0.0', 0))
        client = HelperClient(server=('224.0.1.187', 5683), sock=s)

        request = client.mk_request(defines.Codes.POST, 'oic/rd')
        request.type = defines.Types['NON']
        request.payload = json.dumps(self.oic_device)
        try:
            client.send_request(request, callback=None, timeout=1)
        except Exception:
            pass

        client.close()


class OicAlarmLv1Thread(object):

    def __init__(self, host, port):
        self.server = OicAlarmLv1(host, port)
        self.thread = threading.Thread(target=self.server.listen, args=(10,))

    def start(self):
        #self.server.heartbeat()
        self.thread.start()
        self.server.publish()

    def stop(self):
        self.server.close()
        self.thread.join()

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    o = OicAlarmLv1Thread('127.0.0.1', port)
    o.start()
    client = HelperClient(server=('127.0.0.1', port))
    p = dict(id=o.server.oic_device['di'], value=str(True))
    response = client.post('/AlarmLv1ResURI', json.dumps(p))
    time.sleep(5)
    p['value'] = False
    response = client.post('/AlarmLv1ResURI', json.dumps(p))
    client.close()
    o.stop()
