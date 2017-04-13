import uuid
import logging
import json

from coapthon.resources.resource import Resource
from coapthon.server.coap import CoAP
from coapthon.client.helperclient import HelperClient
import socket
from coapthon import defines

import threading

import time
from guard.WSDiscovery import WSDiscovery
import urlparse
from onvif import ONVIFCamera
from onvif.exceptions import *

logger = logging.getLogger(__name__)


class ObservableResource(Resource):

    def __init__(self, name="Obs", coap_server=None, info={}):
        super(ObservableResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)

        self.info = info
        self.payload = json.dumps(self.info)

    def render_GET(self, request):
        return self

    def render_POST(self, request):
        self.payload = request.payload
        return self

    def update(self, first=False):
        self.payload = json.dumps(self.info)
        if not self._coap_server.stopped.isSet():

            if not first and self._coap_server is not None:
                logger.debug("Periodic Update")
                self._coap_server.notify(self)
                self.observe_count += 1


class MediaResource(Resource):

    def __init__(self, name="Meida", coap_server=None, info={}):
        super(MediaResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)

        self.info = info
        self.payload = json.dumps(self.info)

    def render_GET(self, request):
        self.payload = json.dumps(self.info)
        return self

    def render_POST(self, request):
        self.payload = request.payload
        return self


class OicDoorGuard(CoAP):

    def __init__(self, host, port, media_uri, multicast=False, starting_mid=None):
        CoAP.__init__(self, (host, port), multicast, starting_mid)

        self.oic_device = dict(di='')
        self.oic_device['lt'] = 86400
        self.oic_device['n'] = self.__class__.__name__

        uri_prefix = 'coap://%s:%d' % (host, port)
        oic_d_res = dict(href=uri_prefix + '/oic/d', rel='contained', rt='oic.d.doorbutton')

        media_res = dict(href=uri_prefix + '/MediaResURI', rel='contained', rt='oic.r.media')
        self.oic_device['links'] = [oic_d_res, media_res]

        media_info = {'id': self.oic_device['di'], 'rt': 'oic.r.media', 'media': [{'url': media_uri}]}
        self.media_res = MediaResource(coap_server=self, info=media_info)
        self.add_resource('/MediaResURI', self.media_res)
        print(self.oic_device, media_info)
        self.timer = None
        self._heartbeat = True

    def heartbeat(self):
        if not self._heartbeat:
            if self.timer is not None and self.timer.is_alive():
                self.timer.cancel()
            return
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
        time.sleep(1)
        client.close()
        self.timer = threading.Timer(60, self.heartbeat)
        self.timer.setDaemon(True)
        self.timer.start()

    def stop_heartbeat(self):
        self._heartbeat = False
        if self.timer is not None and self.timer.is_alive():
            self.timer.cancel()

    def restart_heartbeat(self):
        self._heartbeat = True
        self.heartbeat()

#bell_res = dict(href=uri_prefix + '/BellResURI', rel='contained', rt='oic.r.button.bell')
#info = {'id': self.oic_device['di'], 'rt': 'oic.r.button.bell', 'value': False}
#self.add_resource('/BellResURI', ObservableResource(coap_server=self, info=info))

    def add_bell(self, belloic):
        if belloic is not None:
            logger.info('add_bell: %s', belloic)
            self.oic_device['di'] = belloic['di']
            self.media_res.info['id'] = belloic['di']
            for link in belloic['links']:
                if link['rt'] == 'oic.r.button':
                    break
            link['rt'] = 'oic.r.button'
            if link not in self.oic_device['links']:
                self.oic_device['links'].append(link)
            self.stop_heartbeat()
            self.restart_heartbeat()

    def capture_pkt(self):
        pass


class OicDoorGuardThread(object):

    def __init__(self, host, port, media_uri):
        self.server = OicDoorGuard(host, port, media_uri)
        self.thread = threading.Thread(target=self.server.listen, args=(10,))

    def start(self):
        #self.server.heartbeat()
        self.thread.start()

    def stop(self):
        self.server.stop_heartbeat()
        self.server.close()
        self.thread.join()


class OnvifDiscover(object):

    default_user = 'admin'
    default_passwd = '12345'
    wsdl_dir = '/usr/local/wsdl'
    wds = WSDiscovery()
    onvif_urls = set([])
    oic_srv = {}
    stop_probe = False
    oic_bell = None

    @staticmethod
    def probe():
        if OnvifDiscover.stop_probe:
            OnvifDiscover.onvif_urls.clear()
            for d in OnvifDiscover.oic_srv.values():
                d.stop()
                del d
            return
        OnvifDiscover.wds.start()
        ret = OnvifDiscover.wds.searchServices()
        found = set([])
        for service in ret:
            if service.getXAddrs()[0].find('onvif') >= 0:
                logger.debug(service.getXAddrs()[0])
                found.add(service.getXAddrs()[0])

        OnvifDiscover.wds.stop()
        if len(found) > 0:
            dead = OnvifDiscover.onvif_urls - found
            new = found - OnvifDiscover.onvif_urls
            logger.debug('dead set is %s' % dead)
            logger.debug('new set is %s' % new)
            if len(dead) > 0:
                for d in dead:
                    if d in OnvifDiscover.oic_srv:
                        OnvifDiscover.oic_srv[d].stop()
                        del OnvifDiscover.oic_srv[d]
            OnvifDiscover.onvif_urls &= found
            if len(new) > 0:
                for n in new:
                    url = urlparse.urlparse(n)
                    mycam = ONVIFCamera(url.hostname, 80, OnvifDiscover.default_user,
                                        OnvifDiscover.default_passwd, wsdl_dir=OnvifDiscover.wsdl_dir)
                    try:
                        media_uri_orig = mycam.create_media_service().GetStreamUri().Uri
                        pw = OnvifDiscover.default_user + ':' + OnvifDiscover.default_passwd + '@'
                        media_uri = media_uri_orig[:7] + pw + media_uri_orig[7:]
                        logger.info('media_uri is %s' % media_uri)
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.bind(('', 0))
                        port = s.getsockname()[1]
                        s.close()
                        OnvifDiscover.oic_srv[n] = OicDoorGuardThread('127.0.0.1', port, media_uri)

                        OnvifDiscover.oic_srv[n].start()
                        OnvifDiscover.onvif_urls.add(n)

                    except ONVIFError as e:
                        logger.info(n, str(e))
                        continue
        for s in OnvifDiscover.oic_srv.values():
            s.server.add_bell(OnvifDiscover.oic_bell)
        logger.debug('onvif_urls set is %s' % OnvifDiscover.onvif_urls)

        timer = threading.Timer(60, OnvifDiscover.probe)
        timer.setDaemon(True)
        timer.start()

    @staticmethod
    def stop():
        OnvifDiscover.stop_probe = True

    @staticmethod
    def add_bell(belloic):
        OnvifDiscover.oic_bell = belloic

if __name__ == '__main__':

    OnvifDiscover.probe()
    try:
        while True:
            logger.debug('sleep 10')
            time.sleep(10)
    except KeyboardInterrupt:
        print('exit')
        OnvifDiscover.stop()

