from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
import json
from bstm.oicmgr import *


class CoAPServer(CoAP):
    """receive muticast post/delete to oic/rd"""

    def __init__(self, host, port, multicast=False):
        CoAP.__init__(self, (host, port), multicast)
        '''self.add_resource('oic/rd', BasicResource())'''
        self.add_resource('oic/', CoAPServer.DirResource())
        self.add_resource('oic/rd/', CoAPServer.RdResource())

    class DirResource(Resource):
        """oic/ resource not impl"""
        def __init__(self, name="DirResource", coap_server=None):
            super(CoAPServer.DirResource, self).__init__(name, coap_server, visible=False,
                                                         observable=False, allow_children=True)

        def render_GET(self, request):
            print(request)
            return self

        def render_PUT(self, request):
            return self

        def render_POST(self, request):
            print request
            return self

        def render_DELETE(self, request):
            print request
            return True

    class RdResource(Resource):
        """oic/rd resource """
        def __init__(self, name="RdResource", coap_server=None):
            super(CoAPServer.RdResource, self).__init__(name, coap_server, visible=True,
                                                        observable=True, allow_children=True)

        def render_GET(self, request):
            print request
            return self

        def render_PUT(self, request):
            return self

        def render_POST(self, request):
            print request.payload
            dev = json.loads(request.payload)
            print dev
            OicDeviceManager().add_device(dev)

            return self

        def render_DELETE(self, request):
            print(request.uri_query)
            OicDeviceManager.del_device(request.uri_query)
            return True

if __name__ == '__main__':
    srv = CoAPServer('224.0.1.187', 5683, multicast=True)
    srv.listen(10)
