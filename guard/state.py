
## -*- coding: utf-8 -*-
import logging
from transitions.extensions import LockedMachine as Machine
from transitions import State
from timer import Timer
from singleton import *
import sys
import traceback

from transitions import logger
import json
import Queue
from oicmgr import OicDeviceManager

from collections import deque
import time
import datetime
logger = logging.getLogger(__name__)


@singleton
class GuardState(object):
    
    unguarded = State('unguarded', on_enter='on_unguarded', ignore_invalid_triggers=True)
    guarded   = State('guarded', on_enter='on_guarded', ignore_invalid_triggers=True)
    invaded_P1 = State('invaded_P1', on_enter='on_invadedP1', ignore_invalid_triggers=True)#phase 1 : try unlock
    invaded_AL1 = State('invaded_AL1', on_enter='on_invaded_AL1', ignore_invalid_triggers=True)#phase 2 : level 1 alart
    invaded_AL2 = State('invaded_AL2', on_enter='on_invaded_AL2', ignore_invalid_triggers=True)#phase 3 : level 2 alart
    invaded_AL3 = State('invaded_AL3', on_enter='on_invaded_AL3', ignore_invalid_triggers=True)#phase 4 : level 3 alart
    states = [unguarded, guarded, invaded_P1,invaded_AL1, invaded_AL2,invaded_AL3]
    #todo in __init__ to read those value from ini file
    
    _SEC_UNGUARD2GUARD_WAITUSER = 60
    _SEC_GUARD2UNGUARD_USERSURE = 30
    _SEC_INVADE_PHASE1_MAXTIME = 30 # phase1 unlock keyboard 30 second limit
    _SEC_INVADE_AL1_MAXTIME = 30 # level1 alert has 30 second limit
    _SEC_INVADE_AL2_MAXTIME = 30 # level2 alert has 30 second limit
    _SEC_NETWORK_DELAY = 10
    transitions = [
        {'trigger': 'trigger_invade', 'source': ['guarded','invaded_AL1','invaded_AL2','invaded_AL3'],  'dest': 'invaded_P1'},
        {'trigger': 'trigger_invadeAL1', 'source': 'invaded_P1', 'dest': 'invaded_AL1'},
        {'trigger': 'trigger_invadeAL2', 'source': 'invaded_AL1', 'dest': 'invaded_AL2'},
        {'trigger': 'trigger_invadeAL3', 'source': 'invaded_AL2', 'dest': 'invaded_AL3'},
        {'trigger': 'trigger_unguard_inner', 'source': ['guarded', 'invaded_P1'], 'dest': 'unguarded'},
        {'trigger': 'trigger_guard', 'source': 'unguarded', 'dest': 'guarded'},
    ]

    ''''''
    requests_guard2unguard_list=[]
    
    def guard2unguard_timeout(self, args):# now guard state --> keep guard state
        self.notify_client_websocket(dict(handler="2unguard",  result='timeout'),event='StatusChanged')
        pass
    
    def get_guard_request_clients(self):
        ret_list =[]
        td = datetime.datetime.now()
        for item in self.requests_guard2unguard_list:
            if (item[1] + datetime.timedelta( seconds= (self._SEC_GUARD2UNGUARD_USERSURE + self._SEC_NETWORK_DELAY)) ) < td  \
                                 or item[1]>td :
                self.requests_guard2unguard_list.remove(item)
            else:
                ret_list.append( item[0])
        #print "test-get" , self.requests_guard2unguard_list
        return ret_list

    def add_requests_guard2unguard(self,cookie_id):
        self.requests_guard2unguard_list.append([cookie_id, datetime.datetime.now()])
        #print "test-add", self.requests_guard2unguard_list
        self.remain_second = self._SEC_GUARD2UNGUARD_USERSURE
        self.guard2unguard_timer = Timer(self._SEC_GUARD2UNGUARD_USERSURE + self._SEC_NETWORK_DELAY,
                                         self._SEC_GUARD2UNGUARD_USERSURE + self._SEC_NETWORK_DELAY ,"guard2unguard",cookie_id)
        self.guard2unguard_timer.set_timeout_action(self.guard2unguard_timeout, self)
        self.guard2unguard_timer.start()
    def remove_guard2unguard_client(self,cookie_id):
        for item in self.requests_guard2unguard_list:
            if item[0] == cookie_id:
                self.requests_guard2unguard_list.remove(item)
        #print "test-remove-one", self.requests_guard2unguard_list
        #todo  at more 1 client, need restart for other client
        if self.guard2unguard_timer is not None and self.guard2unguard_timer.cookie_id == cookie_id:
            self.guard2unguard_timer.cancel()
            self.guard2unguard_timer=None
    def remove_all_guard2unguard(self):
        is_removed = 0
        for item in self.requests_guard2unguard_list:
                self.requests_guard2unguard_list.remove(item)
                is_removed+=1
        #print "test-remove-all", self.requests_guard2unguard_list
        if self.guard2unguard_timer is not None :
            self.guard2unguard_timer.cancel()
            self.guard2unguard_timer=None
            is_removed += 1
        return is_removed
    ''''''
    ''''''
    requests_unguard2guard_list = []

    def get_unguard_request_clients(self):
        ret_list =[]
        td = datetime.datetime.now()
        for item in self.requests_unguard2guard_list:
            if (item[1] + datetime.timedelta( seconds= (self._SEC_UNGUARD2GUARD_WAITUSER + self._SEC_NETWORK_DELAY)) ) < td \
                                or item[1] > td:
                self.requests_unguard2guard_list.remove(item)
            else:
                ret_list.append( item[0])
        return ret_list

    def unguard2guard_timeout(self, args):# now unguard state --> to guard state
        self.notify_client_websocket(dict(handler="2guard",  result='timeout'),event='StatusChanged')
        pass
    def add_requests_unguard2guard(self,cookie_id):
        self.requests_unguard2guard_list.append([cookie_id, datetime.datetime.now()])
        #print "2test-add", self.requests_unguard2guard_list
        self.remain_second = self._SEC_UNGUARD2GUARD_WAITUSER
        self.unguard2guard_timer = Timer(self._SEC_UNGUARD2GUARD_WAITUSER + self._SEC_NETWORK_DELAY,
                                         self._SEC_UNGUARD2GUARD_WAITUSER + self._SEC_NETWORK_DELAY,
                                         "unguard2guard",cookie_id)
        self.unguard2guard_timer.set_timeout_action(self.unguard2guard_timeout, self)
        self.unguard2guard_timer.start()

    def remove_unguard2guard_client(self, cookie_id):
        for item in self.requests_unguard2guard_list:
            if item[0] == cookie_id:
                self.requests_unguard2guard_list.remove(item)
        #print "2test-remove-one", self.requests_unguard2guard_list
        # todo  at more 1 client, need restart for other client
        if self.unguard2guard_timer is not None and self.unguard2guard_timer.cookie_id == cookie_id:
            self.unguard2guard_timer.cancel()
            self.unguard2guard_timer = None

    def remove_all_unguard2guard(self):
        is_removed = 0
        for item in self.requests_unguard2guard_list:
            self.requests_unguard2guard_list.remove(item)
            is_removed += 1
        #print "test-remove-all", self.requests_unguard2guard_list
        if self.unguard2guard_timer is not None:
            self.unguard2guard_timer.cancel()
            self.unguard2guard_timer = None
            is_removed += 1
        return is_removed
    ''''''
    invade_event_list = []
    def add_invade_event(self,suuid,svalue,sname, spos,sdate):
        self.invade_event_list.append([suuid,svalue,sname, spos,sdate,"noread"])
       
    def mark_invade_event_read(self,suuid,sdate):

        for item in self.invade_event_list:
            pass

    def remove_all_invade_event(self):
        for item in self.invade_event_list:
            self.invade_event_list.remove(item)
   
    ''''''
    def __init__(self):
        self.machine = Machine(self, states=self.__class__.states,
                               transitions=self.__class__.transitions,
                               initial='guarded', ignore_invalid_triggers=True)
        self.to_alarm_timer = None
        self.guarded_powersave_timer = None
        self.guard2unguard_timer = None
        self.unguard2guard_timer = None
        self.remain_second = 0
        self.state_start_time = datetime.datetime.now()

    def guarded_powersave_action(self, args):
        logger.debug('set_powersave_mode')
        OicDeviceManager().set_outgoing_powersave("powersave-on")
        StateControl().notify_client_websocket(dict(handler="powersave",  result='action'),event='StatusChanged')

    def unset_powersave_mode(self):
        if self.guarded_powersave_timer is not None :# or  self.guarded_powersave_timer.is_alive():
            self.guarded_powersave_timer.cancel()
            self.guarded_powersave_timer = None
        logger.debug('unset_powersave_mode')
        OicDeviceManager().set_outgoing_powersave("powersave-off")

    def trigger_unguard(self):
        if HouseState().state == 'outgoing':
            self.unset_powersave_mode()
        self.trigger_unguard_inner()
        
    def on_guarded(self):
        logger.debug('on_guarded')
        self.state_start_time = datetime.datetime.now()
        if self.remove_all_unguard2guard() >0 :
            logger.error('Why , has unguard2guard client in this time')
        if HouseState().state == 'outgoing':
            if self.guarded_powersave_timer is not None :# or  self.guarded_powersave_timer.is_alive():
                self.guarded_powersave_timer.cancel()
                self.guarded_powersave_timer = None
            self.guarded_powersave_timer = Timer(60, 60,"guarded_powersave_timer")
            self.guarded_powersave_timer.set_timeout_action(self.guarded_powersave_action, self)
            self.guarded_powersave_timer.start()

    def on_unguarded(self):
        logger.debug('on_unguarded')
        self.state_start_time = datetime.datetime.now()
        if self.remove_all_guard2unguard() >0 :
            logger.error('Why , has guard2unguard client in this time')
        if self.to_alarm_timer is not None:
            self.to_alarm_timer.cancel()
        #AlarmState().be_quiet()
        OicDeviceManager().setup_alarm_level3(False)
        OicDeviceManager().setup_alarm_level2(False)
        OicDeviceManager().setup_alarm_level1(False)
        

    def on_alarm_every_time(self, args):
        self.remain_second = self.to_alarm_timer.remain_second
        logger.debug('on_alarm_every_time: %d', self.remain_second)
        StateControl().notify_client_websocket( dict(type='ToAlarm', seconds=self.remain_second) ,event="CountDown")

    def on_invaded_P1_timeout(self, args):
        logger.debug('invadep1_timeout --> Alert level1 ')
        self.remain_second = self._SEC_INVADE_AL1_MAXTIME
        self.trigger_invadeAL1()
    def on_invadedP1(self):
        logger.debug('on_invadedP1')
        if HouseState().state=="indoors": # home protect no im-keyboard(P1 phase)
            self.trigger_invadeAL1()
        else: #outdoor invade most is room-owner comeback , so provide a P1 phase
            self.remain_second = self._SEC_INVADE_PHASE1_MAXTIME
            if self.to_alarm_timer is None or not self.to_alarm_timer.is_alive():
                self.to_alarm_timer = Timer( self._SEC_INVADE_PHASE1_MAXTIME + self._SEC_NETWORK_DELAY, \
                                             self._SEC_INVADE_PHASE1_MAXTIME + self._SEC_NETWORK_DELAY,  "to_alarm_timer")
                #self.to_alarm_timer.set_step_action(self.on_alarm_every_time, self)
                self.to_alarm_timer.set_timeout_action(self.on_invaded_P1_timeout, self)
                self.to_alarm_timer.start()
            else:
                 logger.error('Why , to_alarm_timer is running')
    
    def on_invaded_AL1_timeout(self, args):
        logger.debug('on_invaded_AL1_timeout --> Alert level2 ')
        self.remain_second = self._SEC_INVADE_AL2_MAXTIME
        self.trigger_invadeAL2()
    def on_invaded_AL1(self):
        logger.debug('on_invadedAL1')
        if self.to_alarm_timer is not None or  self.to_alarm_timer.is_alive():
            self.to_alarm_timer.cancel()
            
        StateControl().notify_client_websocket(event='StatusChanged')
        self.remain_second = self._SEC_INVADE_AL1_MAXTIME
        self.to_alarm_timer = Timer(self._SEC_INVADE_AL1_MAXTIME + self._SEC_NETWORK_DELAY, \
                                    self._SEC_INVADE_AL1_MAXTIME + self._SEC_NETWORK_DELAY, "to_alarm_timer")
        # self.to_alarm_timer.set_step_action(self.on_alarm_every_time, self)
        self.to_alarm_timer.set_timeout_action(self.on_invaded_AL1_timeout, self)
        self.to_alarm_timer.start()
        OicDeviceManager().setup_alarm_level1(True)
    def on_invaded_AL2_timeout(self, args):
        logger.debug('on_invaded_AL2_timeout --> Alert level3 ')
        self.trigger_invadeAL3()
    def on_invaded_AL2(self):
        logger.debug('on_invadedAL2')
        if self.to_alarm_timer is not None or self.to_alarm_timer.is_alive():
            self.to_alarm_timer.cancel()
    
        StateControl().notify_client_websocket(event='StatusChanged')
        self.remain_second = self._SEC_INVADE_AL2_MAXTIME
    
        self.to_alarm_timer = Timer(self._SEC_INVADE_AL2_MAXTIME + self._SEC_NETWORK_DELAY, \
                                    self._SEC_INVADE_AL2_MAXTIME + self._SEC_NETWORK_DELAY, "to_alarm_timer")
        # self.to_alarm_timer.set_step_action(self.on_alarm_every_time, self)
        self.to_alarm_timer.set_timeout_action(self.on_invaded_AL2_timeout, self)
        self.to_alarm_timer.start()
        OicDeviceManager().setup_alarm_level2(True)
    def on_invaded_AL3(self):
        logger.debug('on_invadedAL3')
        if self.to_alarm_timer is not None:
            self.to_alarm_timer.cancel()
        OicDeviceManager().setup_alarm_level3(True)
@singleton
class HouseState(object):
    in_house = State('indoors', on_enter='on_indoors', ignore_invalid_triggers=True)
    out_house = State('outgoing', on_enter='on_outgoing', ignore_invalid_triggers=True)

    states = [in_house, out_house]
    transitions = [
        {'trigger': 'ind', 'source': 'outgoing', 'dest': 'indoors'},
        {'trigger': 'outg', 'source': 'indoors', 'dest': 'outgoing'},
    ]

    def __init__(self):
        self.machine = Machine(self, states=self.__class__.states,
                               transitions=self.__class__.transitions,
                               initial='outgoing', ignore_invalid_triggers=True)

    def on_indoors(self):
        logger.debug('on_indoors')

    def on_outgoing(self):
        logging.debug('on_outgoing')


@singleton
class BellState(object):
    noaction  = State('noaction', on_enter='on_noaction', ignore_invalid_triggers=True)
    ringing   = State('ringing',  on_enter='on_ringing',   ignore_invalid_triggers=True)
    connected = State('connected',on_enter='on_connected',ignore_invalid_triggers=True)
    states = [noaction, ringing,connected]
    transitions = [
        {'trigger': 'bell_ringing', 'source': 'noaction', 'dest': 'ringing'},
        {'trigger': 'bell_startstream', 'source': 'ringing', 'dest': 'connected'},
        {'trigger': 'bell_close', 'source': ['ringing','connected'], 'dest': 'noaction'},
    ]

    def __init__(self):
        self.machine = Machine(self, states=self.__class__.states,
                               transitions=self.__class__.transitions,
                               initial='noaction', ignore_invalid_triggers=True)
        self.ts_uuid=""
        self.ts_vedio_url = ""
    def set_ts_uuid(self,uuid):
        self.ts_uuid = uuid

    def trigger_bell_startstream(self):
        self.ts_vedio_url= OicDeviceManager().get_bell_binddevices_url(self.ts_uuid )
        self.bell_startstream()
    
    def trigger_bell_close(self):
        self.bell_close()
    
    def on_noaction(self):
        logger.debug('bell closed')
    def on_ringing(self):
        logging.debug('on_outgoing')
    def on_connected(self):
        logging.debug('on_connected')

@singleton
class AlarmState(object):
    quiet = State('noalert', on_enter='on_quiet', ignore_invalid_triggers=True)
    alert_level1 = State('alert_level1', on_enter='on_alart_l1', ignore_invalid_triggers=True)
    #alert_level2 = State('alert_level2', on_enter='on_alart_l2', ignore_invalid_triggers=True)
    #alert_level3 = State('alert_level3', on_enter='on_alart_l3', ignore_invalid_triggers=True)

    states = [quiet,alert_level1]#  ,alert_level2,alert_level3 ]
    transitions = [
        {'trigger': 'be_alarm', 'source': 'noalert', 'dest': 'alert_level1'},
        {'trigger': 'be_quiet', 'source': 'alert_level1', 'dest': 'noalert'},
    ]

    def __init__(self):
        self.machine = Machine(self, states=self.__class__.states,
                               transitions=self.__class__.transitions,
                               initial='noalert', ignore_invalid_triggers=True)
        self._alert_timer = None
        self.fataldetector_event_queue = deque()

    def on_alart_l1(self):
        logger.debug('on_alart_level1')
        OicDeviceManager().setup_alarm_level1(True)
        StateControl().notify_client_websocket(event='StatusChanged')


    def on_quiet(self):
        from oicmgr import OicDeviceManager
        logger.debug('on_quiet')
        OicDeviceManager().setup_alarm_level1(False)
        StateControl().notify_client_websocket(event='StatusChanged')

class State_Event(object):
    event_source=""
    event_name=""
    event_para=None
    def __init__(self,source):
        self.event_source = source
        pass
 
 
@singleton
class StateControl(object):

    def __init__(self):
        self.q = Queue.Queue()
        self.state = 'protected'
        self.StatusChanged_info =""
        
        
    def update_self_status(self, status=None, timeout=1,cookie_id=""):
        g = GuardState()
        h = HouseState()
        a = AlarmState()
        b = BellState()
        if status is None:
            info = {'status': self.state}
        else:
            self.state = status
            info = {'status': status}
            
        if a.state != "noalert": # alert_fatal is most high level
            print "now alert_fatal queue : ", a.fataldetector_event_queue
            info['status'] = "alert_fatal"
        elif g.state == 'guarded':
            tmp_g2uglist = g.get_guard_request_clients()
                # if cookie_id in tmp_g2uglist:
            # all client sync to one screen
            if tmp_g2uglist.__len__() > 0:
                info['status'] = "unlock_protect"
            else:
                info['status'] = "protected"
            # debug
            for client in tmp_g2uglist:
                info['debug_status_%s' % client] = "unlock_protect"
        elif g.state == 'unguarded':
            tmp_g2uglist = g.get_unguard_request_clients()
    
            # if cookie_id in tmp_g2uglist:
            # all client sync to one screen
            if tmp_g2uglist.__len__() > 0:
                info['status'] = "protect_starting"
            else:
                info['status'] = "protect_check"
            for client in tmp_g2uglist:
                info['debug_status_%s' % client] = "protect_starting"
        elif g.state == 'invaded_P1':
                info['status'] = "unlock_protect"
        elif g.state == 'invaded_AL1':
                info['status'] = "protect_invade"
            
        if b.state != 'noaction' and ((g.state == 'guarded' and  h.state == 'indoors') or g.state == 'unguarded' ) :
            if b.state == "ringing":
                info['status'] = "bell_ring"
            elif  b.state == "connected":
                info['status'] = "bell_view"
                
        self.state = info['status']
        return info
    def get_remain_time(self):
        g = GuardState()
        # h = HouseState()
        # a = AlarmState()
        # b = BellState()
        time_remained=g.remain_second
        # print('get_remain_time status:%s, g.state:%s, h.state:%s, a.state:%s b.state:%s return %d'% \
        #         (self.state, g.state, h.state, a.state,b.state, time_remained))
        return time_remained
    def update_status(self, status=None, timeout=1, cookie_id=""):
        logger.debug("oldway: update_status with (status=%s,timeout=%d )" % (status,timeout) )
        # try:
        #     traceback.print_stack(limit=4)
        # except BaseException as e:
        #     pass

            
    def update_status2(self, status=None, timeout=1,cookie_id=""):
        g = GuardState()
        h = HouseState()
        a = AlarmState()
        b = BellState()
        logger.info('update_status:%s, g.state:%s, h.state:%s, a.state:%s b.state:%s' %(self.state, g.state, h.state, a.state ,b.state))
        info = self.update_self_status( status,timeout,cookie_id)
 
        if g.state in ['guarded', 'invaded_P1']:
            info['guard_status'] = 'guarded'
        else:
            info['guard_status'] = 'unguarded'

        info['house_status'] = h.state
        info['alarm_status'] = a.state
        if self.state == 'bell_ring':
            info['bell_status'] = 'ringing'
        elif self.state == 'bell_view':
            info['bell_status'] = 'conversation'
        else:
            info['bell_status'] = 'standby'
        info['remain_second'] = self.get_remain_time();
        devs = OicDeviceManager().get_devices()
        #todo  for devs uuid ==
        if info['status'] == "bell_view" :
            for dev in devs:
                if dev['uuid'] == b.ts_uuid :
                    dev['video_url'] =b.ts_vedio_url
       
        info['devices_status'] = devs
        can = []
        ind = {'indoors': 'cannot'}
        out = {'outgoing': 'cannot'}
        #if h.state == 'outgoing' and OicDeviceManager().all_devices_quiet():
        if h.state == 'outgoing':
            ind = {'indoors': 'can'}
            out = {'outgoing': 'cannot'}
        #if h.state == 'indoors' and OicDeviceManager().all_devices_quiet():
        if h.state == 'indoors':
            ind = {'indoors': 'cannot'}
            out = {'outgoing': 'can'}

        if g.state == 'unguarded':
            ind = {'indoors': 'can'}
            out = {'outgoing': 'can'}

        can.append(ind)
        can.append(out)
        info['canprotect'] = can
        logger.debug("%s", info)
        self.q.put(info)
        logger.debug('update_status:%s, g.state:%s, h.state:%s, a.state:%s', status, g.state, h.state, a.state)

    def get_status(self,cookie_id=''):
        if self.q.empty():
            self.update_status2(cookie_id=cookie_id)
        while not self.q.empty():
            a = self.q.get(True)
            
        if a['status'] == "protect_invade" or a['status'] == "alert_fatal":
            a['status2'] =a['status']
            a['status'] = "alert_message"

        logger.info("\r\n STATE-MACHINE >>> Output  : \r\n" +  str(a) + "\r\n" )

        return a

    def set_protect(self, result,cookie_id):
        logger.debug('%s', result)
        g = GuardState()
        if result == 'cancel':
            g.remove_unguard2guard_client(cookie_id)
            g.trigger_unguard()
            self.update_status('protect_check')
        else:
            g.remove_all_unguard2guard()
            g.trigger_guard()
            self.update_status('protected')
    def stop_alert(self, alertid):
        g =GuardState()
        a = AlarmState()
        logger.debug('%s %s', alertid, g.state)
        if g.state == 'invaded_AL1':
            g.trigger_invade()
            #self.update_status('unlock_protect', 30)
        else:
            if len(a.fataldetector_event_queue) > 0:
                a.fataldetector_event_queue.popleft()
            if len(a.fataldetector_event_queue) == 0:
                AlarmState().be_quiet()
            #self.update_status('protect_check')

    def alert(self, str_now ,devid=''):
        e = {'devid': devid}
        a = AlarmState()
        logger.debug('alert: %s' % e)
        if e not in a.fataldetector_event_queue:
            a.fataldetector_event_queue.append(e)

        #if self.state == 'protect_check':
        a.be_alarm()
        #self.update_status('alert_message')
        


    #todo add a method for inject a event by json string
    def inject_event(self,string_json):
        from collections import namedtuple
        e = json.loads(string_json, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        self.state_process_event(e)

    
    def state_process_event(self, event):

        #print type(event) == "guard.state.State_Event"
        status_info = self.update_self_status()
        g = GuardState()
        h = HouseState()
        a = AlarmState()
        b = BellState()
        tmp_stat="uistate:%s, g.state:%s, h.state:%s, a.state:%s b.state:%s" % (status_info['status'] ,g.state, h.state, a.state ,b.state)
        logger.info("\r\n STATE-MACHINE <<< input_event  : \r\n" +json.dumps(event.__dict__) + "\r\n @STATE:" + tmp_stat )
        #todo recorect follow MAIN state control logic
        if event.event_source == 'oic_event' and event.event_name == "state_changed":
            
            str_now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            

            #old logic ==> new logic
            #if "invadedetector" in event.event_para['dev_detectorgroup']:
            #    g.trigger_invade()
            #if "motiondetector"  in event.event_para['dev_detectorgroup'] and h.state == "outgoing":
            #    g.trigger_invade()
            if "invadedetector" in event.event_para['dev_detectorgroup'] or \
                            "motiondetector" in event.event_para['dev_detectorgroup']:
                tmp_isingored = 1
                if h.state=="indoors" and \
                    (event.event_para['dev_action_in_doorprotect']=="alart" or event.event_para['dev_action_in_doorprotect']=="insist_alart"):
                    tmp_isingored = 0
                elif h.state=="outgoing" and \
                    (event.event_para['dev_action_in_outprotect']=="alart" or event.event_para['dev_action_in_outprotect']=="insist_alart"):
                    tmp_isingored = 0
                # todo  log  those event to logfile
                if tmp_isingored == 1:
                    logger.info ("this event is ignored")
                else:
                    g.add_invade_event(event.event_para['dev_devid'], \
                                            event.event_para['dev_name'], \
                                            event.event_para['dev_position'], \
                                            event.event_para['dev_info_value'],str_now)
                    if g.state == "guarded" and status_info['status'] != "protect_starting" : # todo bell status ??
                        g.trigger_invade()
            elif "fataldetector" in event.event_para['dev_detectorgroup']  :
                StateControl().alert(str_now, event.event_para['dev_info_id'])
                if event.event_para["dev_type"] == "oic.d.waterleakagedetector" :
                    OicDeviceManager().set_water_valve_off("off")
                elif event.event_para["dev_type"] == "oic.d.flammablegasdetector" \
                     or event.event_para["dev_type"] == "oic.d.smokesensor":
                    OicDeviceManager().set_robot_action_off("off")
                
            if "belldetector" in event.event_para['dev_detectorgroup'] :
                if str(event.event_para['dev_info_value']).lower() == "true":
                    StateControl().bell_ring(event.event_para['dev_devid'])
               
                
            self.notify_client_websocket(dict(handler="oic_event",  result='OK'),event='StatusChanged')
        elif event.event_source == 'webservice':
            if event.event_name == "set_protect_start":
                logger.debug("set_protect_start("+event.event_para["mode"]+ event.event_para["cookie_id"]+")")
                if event.event_para["mode"] in ['home', 'indoors']:
                    h.ind()
                if event.event_para["mode"] in ['out', 'outgoing']:
                    h.outg()
                if event.event_para["mode"] in ['home', 'indoors']:
                    g.trigger_guard()
                else:
                    g.add_requests_unguard2guard(event.event_para["cookie_id"])
                
            elif event.event_name  == "cancel_protect":
                logger.debug('cancel_protect: %s %s %s %s %s',event.event_para["mode"], event.event_para["action"], event.event_para["password"],
                                    event.event_para["systime"], event.event_para["cookie_id"] )
                if event.event_para["action"] == 'cancel' and g.state == "invaded_P1" :
                    self.notify_client_websocket(event='StatusChanged')
                    g.trigger_invadeAL1()
                elif event.event_para["action"] == 'cancel' and g.state == 'guarded':
                    g.remove_guard2unguard_client( event.event_para["cookie_id"])
                elif event.event_para["action"] == 'start' and self.state == 'protected' and g.state == 'guarded':
                    g.add_requests_guard2unguard( event.event_para["cookie_id"])
                elif event.event_para["action"] == 'ok' and event.event_para["password"] != "correct" and g.state == 'invaded_P1' :#@STATE:uistate:unlock_protect, g.state:invaded_P1, h.state:outgoing, a.state:noalert b.state:noaction
                    pass
                elif event.event_para["action"] == 'ok': #todo guard or alert
                    g.remove_all_guard2unguard()
                    if len(a.fataldetector_event_queue) == 0:
                        # check password
                        if event.event_para["password"] == "correct":
                            GuardState().trigger_unguard()
                            HouseState().ind()
                            AlarmState().be_quiet()
                    else: #g.state:invaded, h.state:outgoing, a.state:alert
                        if AlarmState().state == 'noalert':
                            AlarmState().be_alarm()
                        else:
                            self.update_status('alert_message')
            elif event.event_name  == "stop_alert":
                self.stop_alert(event.event_para["alertid"])
            elif event.event_name  == "set_protect":
                self.set_protect(event.event_para["result"],event.event_para["cookie_id"])
            elif event.event_name  == "bell_do":
                self.bell_do(event.event_para["bellid"], event.event_para["action"])

        self.notify_client_websocket_real()
       
    def state_machine_internal_timer_event(self):
        logger.info("statemachine input Event state_machine_internal_timer_event")
        e = State_Event("inter_timer_event")
        e.event_name = ""
        e.event_para = None
        self.state_process_event(e)
        return
    
    def new_event_from_webservice(self, event_name, event_para):
        logger.info("statemachine input Event web:" + str(event_name) + str(event_para))
        e = State_Event("webservice")
        e.event_name = event_name
        e.event_para = event_para
        self.state_process_event(e)
        return
 

    def new_event_from_oic(self,dev,dev_info,oldstate):
    
        logger.info("statemachine input Event oic:%s  %s->%s" %(dev.position,str(oldstate),str(dev_info['value'])) )
        
        e = State_Event("oic_event")
        if str(dev_info['value']).lower() != str(oldstate).lower() :
            e.event_name = "state_changed"
        else:
            e.event_name = "device_join"
            
        #todo if actual env disable this return , now avoid more print caused by d_smart_sim.py
        if e.event_name == "device_join":
            return
        
        
        e.event_para = dict (dev_info_rt=dev_info['rt'],dev_info_id=dev_info['id'],dev_info_value=dev_info['value'],
                             oldstate=oldstate,
                             dev_devid=dev.devid ,
                             dev_name=dev.name,
                             dev_position=dev.position,
                             dev_type=dev.type,
                             dev_detectorgroup=dev.detectorgroup,
                             dev_action_in_doorprotect=dev.action_in_doorprotect,
                             dev_action_in_outprotect=dev.action_in_outprotect,
                             dev_control_state=dev.control_state,
                             dev_cancel=dev.cancel,
                             
                              )
        self.state_process_event(e)
        return
        


 
    def bell_ring(self,uuid):
        b =BellState()
        b.set_ts_uuid(uuid)
        b.bell_ringing()
        # if GuardState().state == 'unguarded' or HouseState().state == 'indoors':
        #     self.update_status('bell_ring')

    def bell_do(self, bellid, action):
        logger.debug('%s %s', bellid, action)
        b =BellState()
        if action == 'startstream':
            b.trigger_bell_startstream()
        elif action == 'opendoor':
            OicDeviceManager().set_door_locker_onoff(OicDeviceManager().get_bell_binddevices_locker(b.ts_uuid))
            time.sleep(3)
            b.trigger_bell_close()
        elif action == 'reject':
            b.trigger_bell_close()
                
    # def notify_client_StatusChanged(self,info=""):
    #     from tornado_server import WebSocketHandler
    #     event = dict(event='StatusChanged',info=info)
    #     WebSocketHandler.send_to_all(event)
    #     logger.info("\r\n STATE-MACHINE >>> Output ws(StatusChanged)  :" + str(event) + "\r\n")
    # def notify_client_CountDown(self,info=""):
    #     from tornado_server import WebSocketHandler
    #     event = dict(event='CountDown',info=info)
    #     WebSocketHandler.send_to_all(event)
    #     logger.info("\r\n STATE-MACHINE >>> Output ws(CountDown)  :" + str(event) + "\r\n")
    def notify_client_websocket_real(self, info="", event='StatusChanged'):
        from tornado_server import WebSocketHandler
        if event=='StatusChanged' and info=="":
            info = self.StatusChanged_info
            
        msg = dict(event=event, info=info)
        WebSocketHandler.send_to_all(msg)
        logger.info("\r\n STATE-MACHINE >>> Output ws(" + event + ")  :" + str(msg) + "\r\n")
    def notify_client_websocket(self,info="" ,event='StatusChanged' ):
        if event=='StatusChanged':
            self.StatusChanged_info=info
        else:
            self.notify_client_websocket_real(info=info ,event=event)
     
     
def test_callback():
    g = GuardState()
    g.trigger_unguard()
if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    g = GuardState()
    h = HouseState()

    print(g.__class__.states)
    print(g.state)

    g.trigger_unguard()
    h.outg()

    g.trigger_guard()
    g.trigger_invade()
    g.trigger_invadeAL1()
    g.trigger_invadeAL2()
    g.trigger_invadeAL3()
    g.trigger_invade()

    timer = threading.Timer(100,test_callback )
    timer.setDaemon(True)
    timer.start()
    timer.join()
    
    print "test over"
  
    
