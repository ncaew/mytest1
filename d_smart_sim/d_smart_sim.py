import logging
import threading
import json
import uuid
import platform
import Queue

from coapthon.resources.resource import Resource
from coapthon.server.coap import CoAP
from coapthon.client.helperclient import HelperClient
import socket
from coapthon import defines

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpclient
import tornado.websocket
import os

logger = logging.getLogger(__name__)


class ObservableResource(Resource):

    def __init__(self, name="Obs", coap_server=None, info={}):
        super(ObservableResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)

        self.info = info
        self.payload = json.dumps(self.info)
        self.period = 30
        self.update(True)

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


class CoAPServerPlugTest(CoAP):
    def __init__(self, host, port, multicast=False, starting_mid=None):
        CoAP.__init__(self, (host, port), multicast, starting_mid)

        # create logger
        logger.setLevel(logging.INFO)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)
        self.reslist = {}
        self.obs = {}

    def add_resources(self, res=[]):
        for r in res:
            self.reslist[r.info['id']] = r.info
            o = ObservableResource(coap_server=self, info=r.info)
            self.obs[r.info['id']] = o
            self.add_resource(r.path, o)


class MyResource(object):
    def __init__(self):
        self.path = None
        self.info = None


if __name__ == '__main__':
    server = CoAPServerPlugTest('127.0.0.1', 40000)

    def create_resource(devid, rnum, rt):
        mr = MyResource()
        mr.path = "ResURI%d" % rnum
        mr.info = {'id': '%s' % devid,  'rt': 'oic.r.%s' % rt, 'value': False}

        print(json.dumps(mr.info))
        return mr

    def create_device(ip, port, rnum, dt, rt):
        pat = '''{
            "di" : "%(uuid)s",
            "links" : [
                {
                    "href" : "coap://%(ip)s:%(port)d/oic/d",
                    "rel" : "contained",
                    "rt" : "oic.d.%(dt)s"
                },
                {
                    "href" : "coap://%(ip)s:%(port)d/ResURI%(rnum)d",
                    "rel" : "contained",
                    "rt" : "oic.r.%(rt)s"
                }
            ],
            "lt" : 86400,
            "n" : "%(name)s"
        }'''
        dinfo = {}
        dinfo['uuid'] = uuid.uuid4()
        dinfo['ip'] = ip
        dinfo['port'] = port
        dinfo['dt'] = dt
        dinfo['rt'] = rt
        dinfo['rnum'] = rnum
        dinfo['name'] = uuid.uuid4()

        print(pat % dinfo)
        d = json.loads(pat % dinfo)
        m = create_resource(dinfo['uuid'], rnum, rt)
        return d, m

    def create_bell_device(ip, port, rnum, dt, rt):
        pat = '''{
            "di" : "%(uuid)s",
            "links" : [
                {
                    "href" : "coap://%(ip)s:%(port)d/oic/d",
                    "rel" : "contained",
                    "rt" : "oic.d.%(dt)s"
                },
                {
                    "href" : "coap://%(ip)s:%(port)d/ResURI%(rnum)d",
                    "rel" : "contained",
                    "rt" : "oic.r.%(rt)s"
                }
            ],
            "lt" : 86400,
            "n" : "%(name)s"
        }'''
        dinfo = {}
        dinfo['uuid'] = uuid.uuid4()
        dinfo['ip'] = ip
        dinfo['port'] = port
        dinfo['dt'] = dt
        dinfo['rt'] = rt
        dinfo['rnum'] = rnum
        dinfo['name'] = uuid.uuid4()

        print(pat % dinfo)
        d = json.loads(pat % dinfo)
        media = {'rel': 'contained', 'rt': 'oic.r.media', 'href': "coap://%s:%d/ResURI%d" % (ip, port, rnum)}
        d['links'].append(media)
        m = create_resource(dinfo['uuid'], rnum, rt)
        media = {'url': 'rtsp://admin:12345@192.168.1.188:554/Streaming/Channels/'
                    '1?transportmode=unicast&profile=Profile_1'}
        m.info['media'] = [media]
        return d, m

    def create_devices(ip, port):
        dl = []
        ml = []
        i = 1
        d, m = create_device(ip, port, i, "irintrusiondetector", 'sensor.motion')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "magnetismdetector", 'sensor.contact')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "magnetismdetector", 'sensor.contact')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "magnetismdetector", 'sensor.contact')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "magnetismdetector", 'sensor.contact')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "flammablegasdetector", 'sensor.carbonmonoxide')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "smokesensor", 'sensor.smoke')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "waterleakagedetector", 'sensor.water')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "Bellbuttonswitch", 'button')
        dl.append(d)
        ml.append(m)
        i += 1

        return dl, ml

    def post_devices(devs):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        '''s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')'''
        s.bind(('0.0.0.0', 0))
        if platform.system() == "Windows":
            logger.info('rum DEMO Mode on ' + platform.system())
            client = HelperClient(server=('127.0.0.1', 5683), sock=s)
        else:
            client = HelperClient(server=('224.0.1.187', 5683), sock=s)
        

        try:
            for d in devs:
                request = client.mk_request(defines.Codes.POST, 'oic/rd')
                request.type = defines.Types['NON']
                request.payload = json.dumps(d)

                client.send_request(request, callback=None, timeout=1)
        except KeyboardInterrupt:
            client.close()
            return
        except Queue.Empty:
            pass

        timer = threading.Timer(30, post_devices, (devs,))
        timer.setDaemon(True)
        timer.start()


    class StaticHandler(tornado.web.RequestHandler):

        def get(self):
            self.write('It works')

    class OicHandler(tornado.web.RequestHandler):

        def get(self):
            global server

            self.write(json.dumps(server.reslist))

    class ChangeOicHandler(tornado.web.RequestHandler):

        def get(self):
            global server

            devid = self.get_argument('id')
            print(server.reslist[devid])
            oldval = server.reslist[devid]['value']

            server.reslist[devid]['value'] = not oldval
            o = server.obs[devid]
            o.payload = json.dumps(o.info)
            server.notify(o)
            print(oldval)

            self.write('{}')


    class WebSocketHandler(tornado.websocket.WebSocketHandler):
        """docstring for SocketHandler"""
        clients = set()

        def check_origin(self, origin):
            return True

        @staticmethod
        def send_to_all(message):
            print(json.dumps(message))
            for c in WebSocketHandler.clients:
                c.write_message(json.dumps(message))

        def open(self):
            WebSocketHandler.clients.add(self)

        def on_close(self):
            WebSocketHandler.clients.remove(self)

        def on_message(self, message):
            pass



    dlist, rlist = create_devices('127.0.0.1', 40000)
    server.add_resources(rlist)
    post_devices(dlist)
    t = threading.Thread(target=server.listen, args=(10,))
    t.setDaemon(True)
    t.start()
    wapp = tornado.web.Application(
        handlers=[
            (r"/ws", WebSocketHandler),
            (r"/", StaticHandler),
            (r"/get_oicinfo", OicHandler),
            (r"/change_oicinfo", ChangeOicHandler)
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
    )
    try:
        wapp.listen(8000)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "Server Shutdown"
        tornado.ioloop.IOLoop.instance().stop()
        server.close()
        t.join(1)
        print "Exiting..."
