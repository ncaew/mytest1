from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
import json
from state import *
from singleton import *
import time
import gettext


class OicDevice(object):
    """Oic device info """
    invade_device_type = ['oic.d.magnetismdetector']
    motion_device_type = ['oic.d.irintrusiondetector']
    fatal_device_type = ['oic.d.flammablegasdetector', 'oic.d.smokesensor',
                         'oic.d.waterleakagedetector']

    alarm_device_type = ['oic.d.alarm']
    bell_device_type = ['oic.d.doorbutton']

    observe_resource_type = ['oic.r.sensor.motion', 'oic.r.sensor.contact', 'oic.r.sensor.carbonmonoxide',
                             'oic.r.sensor.smoke', 'oic.r.sensor.water', 'oic.r.button.bell']
    media_resource_type = ['oic.r.media']

    def __init__(self, oicinfo):
        self.devid = oicinfo['di']
        self.name = oicinfo['n']
        self.type = OicDevice.get_device_type(oicinfo)
        self.res_state = {}
        self.control_state = None
        self.position = None
        self.observers = {}
        self.locker = threading.Lock()
        self.cancel = False
        self.oic_info = oicinfo


    @staticmethod
    def get_device_type(oicinfo):
        for link in oicinfo['links']:
            if link['rt'].find('oic.d.') >= 0:
                break

        return link['rt']

    def get_stream_uri(self):
        uri_list = []
        if self.is_bell():
            href = []
            for link in self.oic_info['links']:
                if link['rt'] in OicDevice.media_resource_type:
                    href.append(link['href'])

            for h in href:
                host, port, uri = parse_uri(h)
                client = HelperClient(server=(host, port))
                response = client.get(uri)
                jsonobj = json.loads(response.payload)
                if 'media' in jsonobj:
                    media = jsonobj['media']
                    for m in media:
                        if 'url' in m and len(m['url']):
                            uri_list.append(m['url'])

        return uri_list

    def is_detector(self):
        return self.is_invade_detector() or self.is_motion_detector() \
               or self.is_fatal_detector() or self.is_bell()

    def is_invade_detector(self):
        return self.type in OicDevice.invade_device_type

    def is_motion_detector(self):
        return self.type in OicDevice.motion_device_type

    def is_fatal_detector(self):
        return self.type in OicDevice.fatal_device_type

    def is_alarmer(self):
        print(self.type)
        return self.type in OicDevice.alarm_device_type

    def is_bell(self):
        return self.type in OicDevice.bell_device_type

    def observe_resources(self, oicinfo, cb):
        for link in oicinfo['links']:
            print(link['rt'])
            if link['rt'].find('oic.r.') >= 0 and \
                            link['rt'] in OicDevice.observe_resource_type:
                rt_info = dict(id=oicinfo['di'], rt=link['rt'], value=False)
                self.res_state[link['rt']] = rt_info
                path = link['href']
                host, port, uri = parse_uri(path)
                client = HelperClient(server=(host, port))
                client.observe(path=uri, callback=cb)
                self.observers[path] = client

    def cancel_observe(self):
        self.cancel = True


@singleton
class OicDeviceManager(object):
    def __init__(self):
        print(self)
        print(self.singleton_lock)
        print('OicDeviceManager')
        self._locker = threading.Lock()
        self._oic_info = {}
        self._devices = {}
        self._alarm_devices = {}

    def setup_alarm(self, on, mode='alarm', seconds=6001):
        alarm_uri = ''
        fire_alarm_uri = ''
        clock_uri = ''
        for devid in self._alarm_devices.keys():
            oic = self._oic_info[devid]
            for link in oic['links']:
                if link['href'].find('/AlarmSwitchResURI') > 0:
                    alarm_uri = link['href']
                if link['href'].find('/FireAlarmResURI') > 0:
                    fire_alarm_uri = link['href']
                if link['href'].find('/ClockResURI') > 0:
                    clock_uri = link['href']

            if on and seconds > 0 and len(clock_uri) > 0:
                p = dict(id=devid, datetime=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                         countdown=seconds)
                host, port, uri = parse_uri(clock_uri)
                client = HelperClient(server=(host, port))
                response = client.post(uri, json.dumps(p))
                print(response.pretty_print())
                client.stop()

            if mode == 'alarm':
                if len(alarm_uri) > 0:
                    p = dict(id=devid, value=on)
                    host, port, uri = parse_uri(alarm_uri)
                    client = HelperClient(server=(host, port))
                    response = client.post(uri, json.dumps(p))
                    print(response.pretty_print())
                    client.stop()
            elif mode == 'fire':
                if len(fire_alarm_uri) > 0:
                    p = dict(id=devid, value=on)
                    host, port, uri = parse_uri(fire_alarm_uri)
                    client = HelperClient(server=(host, port))
                    response = client.post(uri, json.dumps(p))
                    print(response.pretty_print())
                    client.stop()

    def _update_oic_device(self, info):
        from tornado_server import WebSocketHandler
        from state import GuardState, AlarmState, HouseState,StateControl
        devid = info['id']
        rt = info['rt']
        state = info['value']
        if state in ['true', 'false']:
            state = state == 'true'
        if devid in self._oic_info and devid in self._devices:
            dev = self._devices[devid]
            if rt in dev.res_state:
                old_state = dev.res_state[rt]['value']
                if old_state in ['true', 'false']:
                    old_state = old_state == 'true'
            else:
                old_state = False

            dev.res_state[rt] = info
            print(old_state, state)
            if old_state is False and state is True:

                if dev.is_invade_detector():
                    StateControl().invade()
                if dev.is_motion_detector() and HouseState().state == "outgoing":
                    StateControl().invade()
                if dev.is_fatal_detector():
                    StateControl().alert()

                if dev.is_bell():
                    StateControl().bell_ring()

            if old_state != state:
                info['old_value'] = old_state
                oic_event = dict(event='OICNotify', info=info)
                WebSocketHandler.send_to_all(oic_event)
            return dev

    def observe_callback(self, response):
        print(response.payload)
        if response.payload is None:
            print('response.payload is None')
            return
        info = json.loads(response.payload)

        devid = info['id']
        self._locker.acquire()
        dev = self._update_oic_device(info)
        if dev is not None and dev.cancel is True:
            for o in dev.observers.items():
                o.cancel_observing(response, False)
            del dev
            del self._oic_info[devid]

        self._locker.release()

    def add_device(self, oicinfo):
        self._locker.acquire()
        try:
            devid = oicinfo['di']

            if devid not in self._oic_info and devid not in self._devices:
                d = OicDevice(oicinfo)
                if d.is_detector():
                    d.observe_resources(oicinfo, self.observe_callback)
                    self._oic_info[devid] = oicinfo
                    self._devices[devid] = d
                if d.is_alarmer():
                    self._oic_info[devid] = oicinfo
                    self._alarm_devices[devid] = d

        except Exception as e:
            print(e.args)
        finally:
            self._locker.release()

    def del_device(self, devid):
        self._locker.acquire()
        if devid in self._oic_info and devid in self._devices:
            dev = self._devices[devid]
            dev.cancel_observe()
        self._locker.release()

    def get_devices(self):
        t = gettext.translation('app', 'locale', languages=['zh_CN'], fallback=True)
        t.install()
        _ = t.gettext
        l = []
        for d in self._devices.values():
            a = {}
            a['uuid'] = d.devid
            a['type'] = d.type[6:]
            a['type_tr'] = _(d.type)

            a['position'] = d.position
            print(d.res_state)
            if len(d.res_state.values()) > 0:
                rstate = d.res_state.values()[0]['value']
            else:
                rstate = False
            a['status_code'] = 1 if rstate else 0
            a['status'] = 'unlock' if rstate else 'lock'
            vurl = d.get_stream_uri()
            if len(vurl) > 0:
                a['video_url'] = vurl[0]
            else:
                a['video_url'] = ''
            l.append(a)
        return l

    def update_device_alias(self, devid, alias):
        result = True
        if devid in self._devices:
            d = self._devices[devid]
            d.position = alias
        else:
            result = False

        return result

    def all_devices_quiet(self):
        for d in self._devices.values():
            if d.res_state.values() is not None:
                rstate = d.res_state.values()[0]['value']
            else:
                rstate = False
            if rstate:
                return False
        return True


if __name__ == '__main__':
    def thread_get_singleton(name):
        i = 100
        while i > 0:
            print(name)
            a = OicDeviceManager()
            print(a)
            print(a.singleton_lock)
            i -= 1


    OicDeviceManager().setup_alarm(True)
