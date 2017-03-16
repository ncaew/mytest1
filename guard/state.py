# https://github.com/tyarkoni/transitions


from transitions.extensions import LockedMachine as Machine
from transitions import State
from timer import Timer
from singleton import *

import logging
from transitions import logger
import json


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

    def on_guard_every_time(self):
        from tornado_server import WebSocketHandler
        info = {'event': 'guard_timer update'}
        self.remain_second = self.to_protect_timer.remain_second
        print(self.remain_second)
        WebSocketHandler.send_to_all(json.dumps(info))

    def timeout_to_guard(self):
        from tornado_server import WebSocketHandler
        print('on_timeout')
        self.remain_second = -1
        GuardState().setup_guard()
        info = {'event': 'guard_timer timeout'}
        WebSocketHandler.send_to_all(json.dumps(info))

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
        AlarmState().be_quiet()

    def on_alarm_every_time(self, args):
        from tornado_server import WebSocketHandler
        print('-------------------on_every_time')
        info = {'event': 'alarm_timer update'}
        self.remain_second = self.to_alarm_timer.remain_second
        print(self.remain_second)
        WebSocketHandler.send_to_all(json.dumps(info))

    def timeout_to_alarm(self, args):
        from tornado_server import WebSocketHandler
        print('on_timeout')
        self.remain_second = -1
        AlarmState().be_alarm()
        info = {'event': 'alarm_timer timeout'}
        WebSocketHandler.send_to_all(json.dumps(info))

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
        {'trigger': 'in', 'source': 'outgoing', 'dest': 'indoors'},
        {'trigger': 'out', 'source': 'indoors', 'dest': 'outgoing'},
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
        print('on_alarm')

    def on_quiet(self):
        print('on_quiet')

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    g = GuardState()
    print(g.__class__.states)
    print(g.state)
    g.remove_guard()
    print(g.state)
    g.setup_guard()
    g.invade()

