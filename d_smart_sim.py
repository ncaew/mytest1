import logging
import threading
import json
import uuid


from coapthon.resources.resource import Resource
from coapthon.server.coap import CoAP
from coapthon.client.helperclient import HelperClient
import socket
from coapthon import defines

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
        v = self.info['value']
        self.info['value'] = not v
        self.payload = json.dumps(self.info)
        if not self._coap_server.stopped.isSet():

            timer = threading.Timer(self.period, self.update)
            timer.setDaemon(True)
            timer.start()

            if not first and self._coap_server is not None:
                logger.debug("Periodic Update")
                self._coap_server.notify(self)
                self.observe_count += 1


class CoAPServerPlugTest(CoAP):
    def __init__(self, host, port, multicast=False, starting_mid=None):
        CoAP.__init__(self, (host, port), multicast, starting_mid)

        # create logger
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

    def add_resources(self, res=[]):
        for r in res:
            self.add_resource(r.path, ObservableResource(coap_server=self, info=r.info))


class MyResource(object):
    def __init__(self):
        self.path = None
        self.info = None


if __name__ == '__main__':
    def create_resource(devid, rnum, rt):
        mr = MyResource()
        mr.path = "ResURI%d" % rnum
        mr.info = {'id': '%s' % devid,  'rt': 'oic.r.%s' % rt, 'value': 'False'}
        print(json.dumps(mr.path))
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
        return dl, ml

    def post_devices(devs):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        '''s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')'''
        s.bind(('0.0.0.0', 0))
        client = HelperClient(server=('224.0.1.187', 5683), sock=s)

        for d in devs:
            request = client.mk_request(defines.Codes.POST, 'oic/rd')
            request.type = defines.Types['NON']
            request.payload = json.dumps(d)
            try:
                client.send_request(request, callback=None, timeout=1)
            except Exception:
                pass

        timer = threading.Timer(30, post_devices, (devs,))
        timer.setDaemon(True)
        timer.start()

    server = CoAPServerPlugTest('127.0.0.1', 40000)
    dlist, rlist = create_devices('127.0.0.1', 40000)
    server.add_resources(rlist)
    post_devices(dlist)
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print "Server Shutdown"
        server.close()
        print "Exiting..."
