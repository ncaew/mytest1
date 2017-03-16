import threading


class Timer(object):
    """ timer to count down, notify every step"""

    def __init__(self, step, timeout):
        self._step = step
        self._step_action = None
        self._step_action_args = None
        self._timeout = timeout
        self._timeout_action = None
        self._tmargs = None
        self._timer = threading.Timer(step, self._action)
        self._count_down = 0

    def start(self):
        self._count_down = self._timeout / self._step
        if self._timer.is_alive():
            t = threading.Timer(self._step, self._action)
            self._timer = t
        self._timer.start()

    def cancel(self):
        self._timer.cancel()

    def is_alive(self):
        return self._timer.is_alive()

    def set_step_action(self, action, args):
        self._step_action = action
        self._step_action_args = args

    def set_timeout_action(self, action, args):
        self._timeout_action = action
        self._tmargs = args

    def _action(self):
        self._count_down -= 1
        print(self._count_down * self._step)
        if self._count_down == 0:
            self._timer.cancel()
            if self._step_action is not None:
                self._step_action(self._step_action_args)
            if self._timeout_action is not None:
                self._timeout_action(self._tmargs)
        else:
            if self._step_action is not None:
                self._step_action(self._step_action_args)
            t = threading.Timer(self._step, self._action)
            self._timer = t
            self._timer.start()

if __name__ == '__main__':
    def print1s(a):
        print(a)

    def printtimeout(a):
        print(a)

    t = Timer(10, 30)
    t.set_step_action(print1s, "111111")
    t.set_timeout_action(printtimeout, "timeout")
    t.start()
