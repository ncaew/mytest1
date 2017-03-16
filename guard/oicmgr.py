from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
import json
from bstm.state import *
from bstm import *


class OicDevice(object):
    """Oic device info """
    invade_type = []
    motion_type = []
    fatal_type = []
    alarm_type = []

    def __init__(self, oicinfo):
        self.id = oicinfo['di']
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

    def is_invade_detector(self):
        return self.type in OicDevice.invade_type

    def is_motion_detector(self):
        return self.type in OicDevice.motion_type

    def is_fatal_detector(self):
        return self.type in OicDevice.fatal_type

    def is_alarmer(self):
        return self.type in OicDevice.alarm_type

    def observe_resources(self, oicinfo, cb):
        for link in oicinfo['links']:
            if link['rt'].find('oic.r.') >= 0:
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

    def _update_oic_device(self, devid, rt, state):
        if devid in self._oic_info and devid in self._devices:
            dev = self._devices[devid]
            old_state = dev.res_state[rt]
            dev.res_state[rt] = state
            if old_state is False and state is True:
                if dev.is_invade_detector():
                    GuardState().invade()
                if dev.is_motion_detector() and HouseState().state == "out_house":
                    GuardState().invade()
                if dev.is_fatal_detector():
                    AlarmState().alarm()
            return dev

    def observe_callback(self, response):
        print(response.payload)
        info = json.loads(response.payload)
        devid = info['id']
        state = info['value']
        rt = info['rt']
        self._locker.acquire()
        dev = self._update_oic_device(devid, rt, state)
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
                d.observe_resources(oicinfo, self.observe_callback())
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
