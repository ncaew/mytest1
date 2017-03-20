# https://github.com/tyarkoni/transitions


from transitions.extensions import LockedMachine as Machine
from transitions import State
from timer import Timer
from singleton import *

import logging
from transitions import logger
import json
import Queue
from oicmgr import OicDeviceManager


@singleton
class GuardState(object):
    guarded = State('guarded', on_enter='on_guarded', ignore_invalid_triggers=True)
    unguarded = State('unguarded', on_enter='on_unguarded', ignore_invalid_triggers=True)
    invaded = State('invaded', on_enter='on_invaded', ignore_invalid_triggers=True)

    states = [guarded, invaded, unguarded]

    transitions = [
        {'trigger': 'invade', 'source': 'guarded', 'dest': 'invaded'},
        {'trigger': 'remove_guard', 'source': ['guarded', 'invaded'], 'dest': 'unguarded'},
        {'trigger': 'setup_guard', 'source': 'unguarded', 'dest': 'guarded'},
    ]

    def __init__(self):
        self.machine = Machine(self, states=self.__class__.states,
                               transitions=self.__class__.transitions,
                               initial='guarded', ignore_invalid_triggers=True)
        self.to_alarm_timer = None
        self.to_protect_timer = None
        self.remain_second = 0

    def on_guard_every_time(self, args):
        from tornado_server import WebSocketHandler

        self.remain_second = self.to_protect_timer.remain_second
        info = dict(type='ToProtect', seconds=self.remain_second)
        event = dict(event='CountDown', info=info)
        print(self.remain_second)
        WebSocketHandler.send_to_all(event)

    def timeout_to_guard(self, args):
        from tornado_server import WebSocketHandler
        print('on_timeout')
        self.remain_second = -1
        GuardState().setup_guard()
        info = dict(type='ToProtect')
        event = dict(event='Timeout', info=info)
        WebSocketHandler.send_to_all(event)

    def on_guarded(self):
        print('on_guarded')
        if HouseState().state == 'outgoing':
            if self.to_protect_timer is None or not self.to_protect_timer.is_alive():
                self.to_protect_timer = Timer(1, 30)
                self.to_protect_timer.set_step_action(self.on_guard_every_time, self)
                self.to_protect_timer.set_timeout_action(self.timeout_to_guard, self)
                self.to_protect_timer.start()
        else:
            GuardState().setup_guard()

    def on_unguarded(self):
        print('on_unguarded')
        if self.to_alarm_timer is not None:
            self.to_alarm_timer.cancel()
        AlarmState().be_quiet()

    def on_alarm_every_time(self, args):
        from tornado_server import WebSocketHandler
        print('-------------------on_every_time')
        info = {'event': 'alarm_timer update'}
        self.remain_second = self.to_alarm_timer.remain_second
        info = dict(type='ToAlarm', seconds=self.remain_second)
        event = dict(event='CountDown', info=info)
        print(self.remain_second)
        WebSocketHandler.send_to_all(event)

    def timeout_to_alarm(self, args):
        from tornado_server import WebSocketHandler
        print('on_timeout')
        self.remain_second = -1
        AlarmState().be_alarm()
        info = dict(type='ToAlarm')
        event = dict(event='Timeout', info=info)
        WebSocketHandler.send_to_all(event)

    def on_invaded(self):
        print('on_invaded')
        if self.to_alarm_timer is None or not self.to_alarm_timer.is_alive():
            self.to_alarm_timer = Timer(1, 30)
            self.to_alarm_timer.set_step_action(self.on_alarm_every_time, self)
            self.to_alarm_timer.set_timeout_action(self.timeout_to_alarm, self)
            self.to_alarm_timer.start()


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
        print('on_indoors')

    def on_outgoing(self):
        print('on_outgoing')


@singleton
class AlarmState(object):
    alarm = State('alert', on_enter='on_alarm', ignore_invalid_triggers=True)
    quiet = State('noalert', on_enter='on_quiet', ignore_invalid_triggers=True)

    states = [alarm, quiet]
    transitions = [
        {'trigger': 'be_alarm', 'source': 'noalert', 'dest': 'alert'},
        {'trigger': 'be_quiet', 'source': 'alert', 'dest': 'noalert'},
    ]

    def __init__(self):
        self.machine = Machine(self, states=self.__class__.states,
                               transitions=self.__class__.transitions,
                               initial='noalert', ignore_invalid_triggers=True)

    def on_alarm(self):
        from oicmgr import OicDeviceManager
        print('on_alarm')
        OicDeviceManager().setup_alarm(True)


    def on_quiet(self):
        from oicmgr import OicDeviceManager
        print('on_quiet')
        OicDeviceManager().setup_alarm(False)


@singleton
class StateControl(object):

    def __init__(self):
        self.q = Queue.Queue()

    def update_status(self, status=None):
        g = GuardState()
        h = HouseState()
        a = AlarmState()
        info = {'status': ''}
        if status is None:
            if g.state in ['guarded', 'invaded'] and a.state == 'noalert':
                info['status'] = 'protected'
            if a.state == 'alert':
                info['status'] = 'alert'
            if g.state == 'unguarded' and a.state == 'noalert':
                info['status'] = 'protect_check'
        else:
            info['status'] = status

        if g.state in ['guarded', 'invaded']:
            info['guard_status'] = 'guarded'
        else:
            info['guard_status'] = 'unguarded'

        info['house_status'] = h.state
        info['alarm_status'] = a.state
        info['bell_status'] = 'standby'
        info['remain_second'] = g.remain_second
        info['devices_status'] = OicDeviceManager().get_devices()
        can = []
        ind = {'indoors': 'cannot'}
        out = {'outgoing': 'cannot'}
        #if h.state == 'outgoing' and OicDeviceManager().all_devices_quiet():
        if h.state == 'outgoing' and OicDeviceManager().all_devices_quiet():
            ind = {'indoors': 'can'}
            out = {'outgoing': 'cannot'}
        #if h.state == 'indoors' and OicDeviceManager().all_devices_quiet():
        if h.state == 'indoors' and OicDeviceManager().all_devices_quiet():
            ind = {'indoors': 'cannot'}
            out = {'outgoing': 'can'}

        can.append(ind)
        can.append(out)
        info['canprotect'] = can
        self.q.put(info)

    def get_status(self):
        return self.q.get(True)

    def set_protect_start(self, mode):
        g = GuardState()
        h = HouseState()
        print(mode)
        if mode == 'indoors':
            h.ind()
        if mode == 'outgoing':
            h.outg()
        g.setup_guard()

        self.update_status('protect_starting')

    def cancel_protect(self, action, password):
        print(action, password)
        GuardState().remove_guard()
        self.update_status('unlock_protect')

    def stop_alert(self, alertid):
        print(alertid)
        AlarmState().be_quiet()

    def set_protect(self):
        GuardState().setup_guard()
        self.update_status('protected')

    def bell_do(self, bellid, action):
        print(bellid, action)


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    g = GuardState()
    print(g.__class__.states)
    print(g.state)
    g.remove_guard()
    print(g.state)
    g.setup_guard()
    g.invade()

