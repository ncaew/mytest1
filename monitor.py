#!/usr/bin/python

# coding:utf-8

from bstm.tornado_server import TornadoServer
from bstm.coapserver import *
from bstm.oicmgr import OicDeviceManager
from bstm.singleton import *
import threading
import tornado


@singleton
class SecureMonitor(object):
    def __init__(self):
        self.tornado = TornadoServer()
        self._coapsrv = CoAPServer('224.0.1.187', 5683, multicast=True)
        self._coapsrv_thread = threading.Thread(target=self._coapservice)


    def _coapservice(self):
        while True:
            try:
                self._coapsrv.listen(10)
            except Exception as e:
                print(e)

    def start_coap_service(self):
        self._coapsrv_thread.start()


if __name__ == '__main__':
    sm = SecureMonitor()
    sm.start_coap_service()
    sm.tornado.webapp.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
