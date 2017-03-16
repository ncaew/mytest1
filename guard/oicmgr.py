from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
import json
from state import *
from singleton import *


class OicDevice(object):
    """Oic device info """
    invade_device_type = ['oic.d.magnetismdetector']
    motion_device_type = ['oic.d.irintrusiondetector']
    fatal_device_type = ['oic.d.flammablegasdetector', 'oic.d.smokesensor',
                         'oic.d.waterleakagedetector']
    alarm_device_type = []

    observe_resource_type = ['oic.r.sensor.motion', 'oic.r.sensor.contact', 'oic.r.sensor.carbonmonoxide',
                             'oic.r.sensor.smoke', 'oic.r.sensor.water']

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

    @staticmethod
    def get_device_type(oicinfo):
        for link in oicinfo['links']:
            if link['rt'].find('oic.d.') >= 0:
                break

        return link['rt']

    def is_detector_alarm(self):
        return self.is_invade_detector() or self.is_motion_detector() \
               or self.is_fatal_detector() or self.is_alarmer()

    def is_invade_detector(self):
        return self.type in OicDevice.invade_device_type

    def is_motion_detector(self):
        return self.type in OicDevice.motion_device_type

    def is_fatal_detector(self):
        return self.type in OicDevice.fatal_device_type

    def is_alarmer(self):
        return self.type in OicDevice.alarm_device_type

    def observe_resources(self, oicinfo, cb):
        for link in oicinfo['links']:
            print(link['rt'])
            if link['rt'].find('oic.r.') >= 0 and \
                            link['rt'] in OicDevice.observe_resource_type:
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

    def _update_oic_device(self, info):
        from tornado_server import WebSocketHandler
        devid = info['id']
        rt = info['rt']
        state = info['value']
        if devid in self._oic_info and devid in self._devices:
            dev = self._devices[devid]
            if rt in dev.res_state:
                old_state = dev.res_state[rt]['value']
            else:
                old_state = False

            dev.res_state[rt] = info
            if old_state is False and state is True:
                WebSocketHandler.send_to_all(json.dumps(dev.res_state))
                if dev.is_invade_detector():
                    GuardState().invade()
                if dev.is_motion_detector() and HouseState().state == "out_house":
                    GuardState().invade()
                if dev.is_fatal_detector():
                    AlarmState().be_alarm()

            if old_state is True and state is False:
                print("state update")
                WebSocketHandler.send_to_all(json.dumps(dev.res_state))
            return dev

    def observe_callback(self, response):
        print(response.payload)
        info = json.loads(response.payload)

        devid = info['id']
        self._locker.acquire()
        dev = self._update_oic_device(info)
        if dev.cancel is True:
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
                if d.is_detector_alarm():
                    d.observe_resources(oicinfo, self.observe_callback)
                    self._oic_info[devid] = oicinfo
                    self._devices[devid] = d

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
        l = []
        for d in self._devices.values():
            a = {}
            a['uuid'] = d.devid
            a['type'] = d.type
            a['position'] = d.position
            if d.res_state.values() is not None:
                rstate = d.res_state.values()[0]['value']
            else:
                rstate = False
            a['status_code'] = rstate
            a['status'] = 'lock' if rstate else 'unlock'
            l.append(a)
        return l

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


    t1 = threading.Thread(target=thread_get_singleton, args=('thread1',))
    t2 = threading.Thread(target=thread_get_singleton, args=('thread2',))
    t1.start()
    t2.start()
