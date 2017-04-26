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
        self.type = OicDevice.get_device_type(oicinfo)
        self.use_name_pos_fromDB = "local"
        
        # fill "name" , "position" to oic
        self.name = oicinfo['n']
        self.position = ""

        if self.use_name_pos_fromDB == "local":
            tmp_v = db_proxy.get_dev_attr(str(self.devid), "name")
            if tmp_v !="" :
                self.name = tmp_v
            tmp_v = db_proxy.get_dev_attr(str(self.devid), "position")
            if tmp_v != "":
                self.position = tmp_v
            
        if self.position == "":
            self.position = "default position"

 
        ## fill "detectorgroup"  to oic
        self.detectorgroup = []
        if self.is_invade_detector():
            self.detectorgroup.append("invadedetector")
        if self.is_motion_detector():
            self.detectorgroup.append("motiondetector")
        if self.is_fatal_detector():
            self.detectorgroup.append("fataldetector")
        if self.is_bell():
            self.detectorgroup.append("belldetector")

            # set action_in_doorprotect/action_in_outprotect
            # action contain : if detecter:   alart,noaction,insist_alart,insist_noaction
            #   if smart-ele-socket: poweron,poweroff,
        if self.is_fatal_detector():
            self.action_in_doorprotect = "insist_alart"
            self.action_in_outprotect = "insist_alart"
        elif self.is_bell():
            self.action_in_doorprotect = "insist_alart"
            self.action_in_outprotect = "insist_noaction"
        elif len(self.get_detectorgroup_define()) > 0:  # genera detector look up DB for user-defined-value
            self.action_in_doorprotect = db_proxy.get_dev_attr(str(self.devid), "action_in_doorprotect")
            self.action_in_outprotect = db_proxy.get_dev_attr(str(self.devid), "action_in_outprotect")
            if self.action_in_doorprotect == "" and self.is_invade_detector():
                self.action_in_doorprotect = "alart"
            elif self.action_in_doorprotect == "" : #and self.is_motion_detector()
                self.action_in_doorprotect = "noaction"
            if self.action_in_outprotect == "": #both is_invade_detector  is_motion_detector
                self.action_in_outprotect = "alart"
            pass
        elif self.is_smart_elesocket():
            self.action_in_doorprotect = db_proxy.get_dev_attr(str(self.devid), "action_in_doorprotect")
            self.action_in_outprotect = db_proxy.get_dev_attr(str(self.devid), "action_in_outprotect")
            if self.action_in_doorprotect == "":
                self.action_in_doorprotect = "noaction"
            if self.action_in_outprotect == "":
                self.action_in_outprotect = "noaction"
            pass
        else:  # not dector and not elesocket
            self.action_in_doorprotect = "insist_noaction"
            self.action_in_outprotect = "insist_noaction"

        self.res_state = {}
        self.control_state = None
        self.observers = {}
        self.locker = threading.Lock()
        self.cancel = False
        self.oic_info = oicinfo

        db_proxy.set_dev_attr(str(self.devid), "name", str(self.name))
        db_proxy.set_dev_attr(str(self.devid), "type", str(self.type))
        db_proxy.set_dev_attr(str(self.devid), "position", str(self.position))
        db_proxy.set_dev_attr(str(self.devid), "action_in_doorprotect", str(self.action_in_doorprotect))
        db_proxy.set_dev_attr(str(self.devid), "action_in_outprotect", str(self.action_in_outprotect))

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

        logger.debug('get_device_type uri_list: %s', uri_list)
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

    def get_detectorgroup_define(self):
        return self.detectorgroup;

    def is_smart_elesocket(self):
        b = self.type == 'oic.d.smart.elesocket'  # todo repell this type
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
        else: #bell swtich
            res = 'alarm' if rstate else 'no_alarm'
        return res


@singleton
class OicDeviceManager(object):
    def __init__(self):
        self._locker = threading.Lock()
        self._oic_info = {}
        self._devices = {}
        self._alarm_devices = {}
        

    def setup_alarm_level1(self, on, mode='alarm', seconds=6001):
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
            # logger.debug('%s %s', old_state, state)
            # if old_state is False and state is True:
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
                logger.info("\r\n STATE-MACHINE >>> Output ws(OICNotify)  :" + str(oic_event) + "\r\n")
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
        logger.debug('add_device %s %s',oicinfo['di'],OicDevice.get_device_type(oicinfo))#
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
        logger.info('del_device %s', devid)
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
            a['action_in_doorprotect'] = d.action_in_doorprotect
            a['action_in_outprotect'] = d.action_in_outprotect
            a['detector_group_define'] = str(d.detectorgroup)

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
        
        if d.use_name_pos_fromDB == "local" :
            # commit to DB , alway return true
            db_proxy.set_dev_attr(devid, "name", alias)
        else:  # todo  commit to d.smarthome
            pass
        return result

    def update_device_posname(self, devid, posname):
        result = True
        if devid in self._devices:
            d = self._devices[devid]
            d.position = posname
        else:
            result = False

        if d.use_name_pos_fromDB == "local":
            # commit to DB , alway return true
            db_proxy.set_dev_attr(devid, "position", posname)
        else:  # todo  commit to d.smarthome
            pass
        return result

    def update_device_con_out(self, devid, con):
        '''con : on/off '''
        # set action_in_doorprotect/action_in_outprotect
        # action contain : if detecter:   alart,noaction,insist_alart,insist_noaction
        #   if smart-ele-socket: poweron,poweroff,
        result = True
        if devid in self._devices:
            d = self._devices[devid]
            if d.is_smart_elesocket():
                d.action_in_outprotect = "poweron" if con == "on" else "poweroff"
            elif d.is_bell():
                result = False
            elif len(d.get_detectorgroup_define()) > 0:
                d.action_in_outprotect = "alart" if con == "on" else "noaction"
        else:
            result = False

        # commit to DB , alway return true
        db_proxy.set_dev_attr(devid, "action_in_outprotect", con)

        return result

    def update_device_con_in(self, devid, con):
        '''con : on/off '''
        # set action_in_doorprotect/action_in_outprotect
        # action contain : if detecter:   alart,noaction,insist_alart,insist_noaction
        #   if smart-ele-socket: poweron,poweroff,
        result = True
        if devid in self._devices:
            d = self._devices[devid]
            if d.is_smart_elesocket():
                d.action_in_doorprotect = "poweron" if con == "on" else "poweroff"
            elif d.is_bell():
                result = False
            elif len(d.get_detectorgroup_define()) > 0:
                d.action_in_doorprotect = "alart" if con == "on" else "noaction"
        else:
            result = False

        # commit to DB , alway return true
        db_proxy.set_dev_attr(devid, "action_in_doorprotect", con)

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

    ### todo add device exe funtion like :
    def set_camera_devices_media_start(self,camera_uuid=""):
        '''
        :param belluuid:
        :return url that played by web vlc controls:
        '''
        logger.info("todo imp set_camera_devices_media_start belluuid:%s" % camera_uuid)
        return "rtsp://admin:12345@192.168.1.188:554/Streaming/Channels/1?transportmode=unicast&profile=Profile_1"
        pass

    def get_bell_binddevices_locker(self,belluuid=""):
        '''
        :param belluuid:
        :return the uuid of oic.d.doorlocker that bind with this bell:
        '''
        logger.info("todo imp get_bell_binddevices_locker belluuid:%s" % belluuid)
        return "11111111-1111-1111-1111-111111111111"
        pass
    def set_door_locker_onoff(self,uuid,mode="on"):
        logger.info("todo imp set_door_locker_onoff  door-uuid:%s %s " % (uuid,mode))
        pass
    def set_robot_action_off(self,mode="off"):
        logger.info("todo imp set_robot_action_off %s" % mode)
        pass
    def set_water_valve_off(self,mode="off"):
        logger.info("todo imp set_water_valve_off %s" % mode)
        pass
    
    def set_turn_elesocket_onoff(self,uuid,mode):
        logger.info("todo imp set_turn_elesocket_onoff %s %s" % (uuid ,mode) )
        pass
    def set_outgoing_powersave(self, mode="powersave-on"): #  set ele-socket device
        '''
        :param mode:  "powersave-on" / "powersave-off"
        :return:
        '''
        logger.info("set_outgoing_powersave %s" % ( mode))
        if mode=="powersave-on" :
            for dev in self.get_devices() :# find all type is ele-socket
                if dev['type'] == "oic.d.ele-socket" :
                    self.set_turn_elesocket_onoff(dev.uuid, "on" if dev.action_in_outprotect =="poweron" else "off") # "poweroff"

    def setup_alarm_level2(self, on, mode='alarm', seconds=6001):
        logger.info("todo imp setup_alarm_level2 %s" % on )
        pass
    def setup_alarm_level3(self, on, mode='alarm', seconds=6001):
        logger.info("todo imp setup_alarm_level3 %s" % on)
        pass

if __name__ == '__main__':
    def thread_get_singleton(name):
        i = 100
        while i > 0:
            print(name)
            a = OicDeviceManager()
            print(a)
            print(a.singleton_lock)
            i -= 1


    OicDeviceManager().setup_alarm_level1(True)
