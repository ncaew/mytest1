# https://github.com/tyarkoni/transitions

from transitions.extensions import LockedMachine as Machine
from transitions import State
from bstm import *
from bstm.timer import Timer

import logging
from transitions import logger


@singleton
class GuardState(object):
    guarded = State('guarded', on_enter='on_guarded')
    unguarded = State('unguarded', on_enter='on_unguarded')
    invaded = State('invaded', on_enter='on_invaded')

    states = [guarded, invaded, unguarded]

    transitions = [
        {'trigger': 'invade', 'source': 'guarded', 'dest': 'invaded'},
        {'trigger': 'remove_guard', 'source': ['guarded', 'invaded'], 'dest': 'unguarded'},
        {'trigger': 'setup_guard', 'source': 'unguarded', 'dest': 'guarded'},
    ]

    def __init__(self):
        self.machine = Machine(self, states=self.__class__.states,
                               transitions=self.__class__.transitions,
                               initial='guarded')
        self.timer = None

    def on_guarded(self):
        print('on_guarded')

    def on_unguarded(self):
        print('on_unguarded')

    def on_every_time(self, args):
        print('on_every_time')

    def on_timeout(self, args):
        print('on_timeout')
        AlarmState().be_alarm()

    def on_invaded(self):
        print('on_invaded')
        if self.timer is None or not self.timer.is_alive():
            self.timer = Timer(1, 30)
            self.timer.set_step_action(self.on_every_time, self)
            self.timer.set_timeout_action(self.on_timeout, self)
            self.timer.start()


@singleton
class HouseState(object):
    in_house = State('in_house', on_enter='on_in_house')
    out_house = State('out_house', on_enter='on_out_house')

    states = [in_house, out_house]
    transitions = [
        {'trigger': 'in', 'source': 'out_house', 'dest': 'in_house'},
        {'trigger': 'out', 'source': 'in_house', 'dest': 'out_house'},
    ]

    def __init__(self):
        self.machine = Machine(self, states=self.__class__.states,
                               transitions=self.__class__.transitions,
                               initial='out_house')

    def on_in_house(self):
        print('on_in_house')

    def on_out_house(self):
        print('on_out_house')


@singleton
class AlarmState(object):
    alarm = State('alarm', on_enter='on_alarm')
    quiet = State('quiet', on_enter='on_quiet')

    states = [alarm, quiet]
    transitions = [
        {'trigger': 'be_alarm', 'source': 'quiet', 'dest': 'alarm'},
        {'trigger': 'be_quiet', 'source': 'alarm', 'dest': 'quiet'},
    ]

    def __init__(self):
        self.machine = Machine(self, states=self.__class__.states,
                               transitions=self.__class__.transitions,
                               initial='quiet')

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

