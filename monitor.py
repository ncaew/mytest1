#!/usr/bin/python

# coding:utf-8

from guard.tornado_server import TornadoServer
from guard.coapserver import *

from guard.singleton import *
import threading
import tornado
from guard.oicbell import *

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)


@singleton
class SecureMonitor(object):
    def __init__(self):
        self.tornado = TornadoServer()
        self._coapsrv = CoAPServer('224.0.1.187', 5683, multicast=True)
        self._coapsrv_thread = threading.Thread(target=self._coapservice)
        self._coapsrv_thread.setDaemon(True)

    def _coapservice(self):
        while True:
            try:
                self._coapsrv.listen(10)
            except Exception as e:
                print(e)

    def start_coap_service(self):
        self._coapsrv_thread.start()

    def stop_coap_service(self):
        self._coapsrv.close()


if __name__ == '__main__':

    probe_thread = threading.Thread(target=OnvifDiscover.probe)
    probe_thread.start()
    sm = SecureMonitor()
    sm.start_coap_service()
    sm.tornado.webapp.listen(8888)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print('exit....')
        OnvifDiscover.stop()
        sm.stop_coap_service()
        tornado.ioloop.IOLoop.instance().stop()
