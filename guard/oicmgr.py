from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
import json
import logging
from singleton import *
import time
import gettext
import db_proxy
from oicbell import OnvifDiscover
import db_proxy
logger = logging.getLogger(__name__)


class OicDevice(object):
    """Oic device info """
    invade_device_type = ['oic.d.magnetismdetector']
    motion_device_type = ['oic.d.irintrusiondetector']
    fatal_device_type = ['oic.d.flammablegasdetector', 'oic.d.smokesensor',
                         'oic.d.waterleakagedetector']

    alarm_device_type = ['oic.d.alarm']
    bell_device_type = ['oic.d.doorbutton']

    observe_resource_type = ['oic.r.sensor.motion', 'oic.r.sensor.contact', 'oic.r.sensor.carbonmonoxide',
                             'oic.r.sensor.smoke', 'oic.r.sensor.water', 'oic.r.button']
    media_resource_type = ['oic.r.media']

    def __init__(self, oicinfo):
        self.devid = oicinfo['di']
        self.name = oicinfo['n']
        self.type = OicDevice.get_device_type(oicinfo)
        self.position = ""
        self.con_alert_indoor = "false"
        self.con_alert_outdoor = "false"
        

        self.res_state = {}
        self.control_state = None
        self.observers = {}
        self.locker = threading.Lock()
        self.cancel = False
        self.oic_info = oicinfo
        
        db_proxy.set_dev_attr(str(self.devid),"name",str(self.name))
        db_proxy.set_dev_attr(str(self.devid),"type", str(self.type))
        db_proxy.set_dev_attr(str(self.devid),"position",str(self.position))
        db_proxy.set_dev_attr(str(self.devid),"con_alert_indoor",str(self.con_alert_indoor))
        db_proxy.set_dev_attr(str(self.devid),"con_alert_outdoor",str(self.con_alert_outdoor))



    @staticmethod
    def get_device_type(oicinfo):
        for link in oicinfo['links']:
            if link['rt'].find('oic.d.') >= 0:
                break

        logger.debug('get_device_type: %s', link['rt'])
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

        logger.debug('get_device_type uri_list: %s',uri_list)
        return uri_list

    def is_detector(self):
        b = self.is_invade_detector() or self.is_motion_detector() or self.is_fatal_detector() or self.is_bell()
        logger.debug('is_detector: %s', b)
        return b

    def is_invade_detector(self):
        b = self.type in OicDevice.invade_device_type
        logger.debug('is_invade_detector: %s', b)
        return b

    def is_motion_detector(self):
        b = self.type in OicDevice.motion_device_type
        logger.debug('is_motion_detector: %s', b)
        return b

    def is_fatal_detector(self):
        b = self.type in OicDevice.fatal_device_type
        logger.debug('is_fatal_detector: %s', b)
        return b

    def is_alarmer(self):
        b = self.type in OicDevice.alarm_device_type
        logger.debug('is_alarmer: %s', b)
        return b

    def is_bell(self):
        b = self.type in OicDevice.bell_device_type
        logger.debug('is_bell: %s', b)
        return b

    def observe_resources(self, oicinfo, cb):
        for link in oicinfo['links']:

            if link['rt'].find('oic.r.') >= 0 and \
                            link['rt'] in OicDevice.observe_resource_type:

                rt_info = dict(id=oicinfo['di'], rt=link['rt'], value=False)
                self.res_state[link['rt']] = rt_info
                path = link['href']
                if path not in self.observers:
                    logger.debug('observe_resources: %s %s', link['rt'], path)
                    host, port, uri = parse_uri(path)
                    client = HelperClient(server=(host, port))
                    client.observe(path=uri, callback=cb)
                    self.observers[path] = client

    def cancel_observe(self):
        self.cancel = True

    def get_status_str(self, rstate):
        res = ''
        if self.is_invade_detector():
            res = 'unlock' if rstate else 'lock'
        elif self.is_motion_detector():
            res = 'motion' if rstate else 'no_motion'
        elif self.is_fatal_detector():
            res = 'alarm' if rstate else 'no_alarm'
        return res



@singleton
class OicDeviceManager(object):
    def __init__(self):
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
                logger.debug('set alarm clock:%s', response.pretty_print())
                client.stop()

            if mode == 'alarm':
                if len(alarm_uri) > 0:
                    p = dict(id=devid, value=on)
                    host, port, uri = parse_uri(alarm_uri)
                    client = HelperClient(server=(host, port))
                    response = client.post(uri, json.dumps(p))
                    logger.debug('setup_alarm alarm response:%s', response.pretty_print())
                    client.stop()
            elif mode == 'fire':
                if len(fire_alarm_uri) > 0:
                    p = dict(id=devid, value=on)
                    host, port, uri = parse_uri(fire_alarm_uri)
                    client = HelperClient(server=(host, port))
                    response = client.post(uri, json.dumps(p))
                    logger.debug('setup_alarm  response:%s', response.pretty_print())
                    client.stop()

    def _update_oic_device(self, info):
        from tornado_server import WebSocketHandler
        from state import StateControl
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
            

            StateControl().new_event_from_oic(dev,info,old_state)
			#logger.debug('%s %s', old_state, state)
            #if old_state is False and state is True:
            #    if dev.is_invade_detector():
            #        StateControl().invade()
            #    if dev.is_motion_detector() and HouseState().state == "outgoing":
            #        StateControl().invade()
            #    if dev.is_fatal_detector():
            #        StateControl().alert()
            #    if dev.is_bell():
            #        StateControl().bell_ring()

            if old_state != state:
                info['old_value'] = old_state
                oic_event = dict(event='OICNotify', info=info)
                WebSocketHandler.send_to_all(oic_event)
            return dev

    def observe_callback(self, response):
        logger.debug('%s', response.payload)
        if response.payload is None:
            logger.error('response.payload is None')
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
        logger.debug('%s', oicinfo)
        self._locker.acquire()
        try:
            devid = oicinfo['di']


            if devid not in self._oic_info and devid not in self._devices:
                d = OicDevice(oicinfo)
                if d.type == 'oic.d.Bellbuttonswitch':
                    OnvifDiscover.add_bell(oicinfo)

                if d.is_detector():
                    d.observe_resources(oicinfo, self.observe_callback)
                    self._oic_info[devid] = oicinfo
                    self._devices[devid] = d
                if d.is_alarmer():
                    self._oic_info[devid] = oicinfo
                    self._alarm_devices[devid] = d

        except Exception as e:
            logger.error(e.args)
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
            a['con_alert_indoor'] = d.con_alert_indoor
            a['con_alert_outdoor'] = d.con_alert_outdoor

            
            if len(d.res_state.values()) > 0:
                rstate = d.res_state.values()[0]['value']
            else:
                rstate = False
            a['status_code'] = 1 if rstate else 0
            a['status'] = _(d.get_status_str(rstate))
            vurl = d.get_stream_uri()
            if len(vurl) > 0:
                a['video_url'] = vurl[0]
            else:
                a['video_url'] = ''
            l.append(a)
            logger.debug("device info:%s", a)
        return l

    def update_device_alias(self, devid, alias):
        result = True
        if devid in self._devices:
            d = self._devices[devid]
            d.name = alias
        else:
            result = False
		#todo  commit to d.smarthome  # copy logic from setup_alarm
        return result

    def update_device_posname(self, devid, posname):
        result = True
        if devid in self._devices:
            d = self._devices[devid]
            d.position = posname
        else:
            result = False
        # todo  commit to d.smarthome  # copy logic from setup_alarm
        return result

    def update_device_con_out(self, devid, con):
        result = True
        if devid in self._devices:
	        d = self._devices[devid]
	        d.con_alert_outdoor = con
        else:
	        result = False
	        
        # todo commit to DB , alway return true
        db_proxy.set_dev_attr(devid,"con_alert_outdoor",con)
        
        return result

    def update_device_con_in(self, devid, con):
        result = True
        if devid in self._devices:
	        d = self._devices[devid]
	        d.con_alert_indoor = con
        else:
	        result = False

        # todo commit to DB , alway return true
        db_proxy.set_dev_attr(devid,"con_alert_outdoor",con)
        
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
