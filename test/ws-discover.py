from guard.WSDiscovery import WSDiscovery
import urlparse
from onvif import ONVIFCamera
from onvif.exceptions import *

wsd = WSDiscovery()
wsd.start()


# ret = wsd.searchServices(scopes=[scope1], timeout=10)
ret = wsd.searchServices(timeout=5)

onvif_url = None

for service in ret:
    print(service.getXAddrs()[0])
    if service.getXAddrs()[0].find('onvif') >= 0:

        onvif_url = service.getXAddrs()[0]
        break

wsd.stop()


if onvif_url is not None:
    print(onvif_url)
    url = urlparse.urlparse(onvif_url)

    #mycam = ONVIFCamera(url.hostname, 80, 'admin', '12345', wsdl_dir='/usr/local/wsdl')
    mycam = ONVIFCamera(url.hostname, 80, '', '', wsdl_dir='/usr/local/wsdl')
    #mycam.devicemgmt.GetServices(False)

    try:
        print(mycam.devicemgmt.GetDeviceInformation())


        media_service = mycam.create_media_service()
        deviceio = mycam.create_deviceio_service()

        print(media_service.GetStreamUri().Uri)
    except ONVIFError as e:
        print(str(e))



