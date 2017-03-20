#!/usr/bin/python
# coding:utf-8
import os
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpclient
import tornado.websocket
from oicmgr import OicDeviceManager
import threading

import json
from state import GuardState, HouseState, AlarmState


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """docstring for SocketHandler"""
    clients = set()

    def check_origin(self, origin):
        return True

    @staticmethod
    def send_to_all(message):
        print(message)
        for c in WebSocketHandler.clients:
            c.write_message(json.dumps(message))

    def open(self):
        '''
        self.write_message(json.dumps({
            'type': 'sys',
            'message': 'Welcome to WebSocket',
        }))
        SocketHandler.send_to_all({
            'type': 'sys',
            'message': str(id(self)) + ' has joined',
        })'''
        WebSocketHandler.clients.add(self)

    def on_close(self):
        WebSocketHandler.clients.remove(self)
        '''
        SocketHandler.send_to_all({
            'type': 'sys',
            'message': str(id(self)) + ' has left',
        })'''

    def on_message(self, message):
        pass


class JsonHandler(tornado.web.RequestHandler):
    def post(self):
        print('post message')
        '''
        print(self.request.remote_ip)
        print(self.request.body_arguments)
        data = json_decode(self.request.body)
        user = data['user']
        pw = data['passwd']
        print(user, pw)
        jdata = json.dumps(data)
        print(jdata)
        self.write(jdata)
        '''


class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        g = GuardState()
        h = HouseState()
        a = AlarmState()
        info = {'status': ''}
        if g.state in ['guarded', 'invaded'] and a.state == 'noalert':
            info['status'] = 'protected'
        if a.state == 'alert':
            info['status'] = 'alert'
        if g.state == 'unguarded' and a.state == 'noalert':
            info['status'] = 'protect_check'
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
        if h.state == 'outgoing' and OicDeviceManager().all_devices_quiet():
            ind = {'indoors': 'can'}
            out = {'outgoing': 'cannot'}
        if h.state == 'indoors' and OicDeviceManager().all_devices_quiet():
            ind = {'indoors': 'cannot'}
            out = {'outgoing': 'can'}

        can.append(ind)
        can.append(out)
        info['canprotect'] = can

        self.write(info)


class SetProtectStartHandler(tornado.web.RequestHandler):
    def get(self):
        g = GuardState()
        h = HouseState()
        pmode = self.get_argument('protect', 'unknown')
        print(pmode)
        if pmode == 'indoors':
            h.ind()
        if pmode == 'outgoing':
            h.outg()
        g.setup_guard()
        info = dict(handler=self.__class__.__name__, action='', result='OK')
        event = dict(event='StatusChanged', info=info)

        WebSocketHandler.send_to_all(event)
        self.write('{"result":"OK"}')


class StaticHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class CancelProtectHandler(tornado.web.RequestHandler):
    def get(self):
        g = GuardState()
        action = self.get_argument('action', 'unknown')
        passwd = self.get_argument('passwd', 'unknown')
        print(passwd)
        if action == 'cancel':
            g.remove_guard()

        info = dict(handler=self.__class__.__name__, action=action, result='OK')
        event = dict(event='StatusChanged', info=info)

        WebSocketHandler.send_to_all(event)
        self.write('{"result":"OK"}')


class StopAlertHandler(tornado.web.RequestHandler):
    def get(self):
        alert_id = self.get_argument('alertid', '')
        print("StopAlertHandler", alert_id)
        AlarmState().be_quiet()
        info = dict(handler=self.__class__.__name__, action='', result='OK')
        event = dict(event='StatusChanged', info=info)

        WebSocketHandler.send_to_all(event)
        self.write('{"result": "OK"}')


class SetProtectHandler(tornado.web.RequestHandler):
    def get(self):
        result = self.get_argument('result', '')
        print("SetProtectHandler", result)
        GuardState().setup_guard()
        info = dict(handler=self.__class__.__name__, action='', result='OK')
        event = dict(event='StatusChanged', info=info)

        WebSocketHandler.send_to_all(event)
        self.write('{"result": "OK"}')


class BellHandler(tornado.web.RequestHandler):
    def get(self):
        bellid = self.get_argument('bellid', '')
        action = self.get_argument('action', '')
        print("SetProtectHandler", bellid, action)

        info = dict(handler=self.__class__.__name__, action=action, result='OK')
        event = dict(event='StatusChanged', info=info)

        WebSocketHandler.send_to_all(event)
        self.write('{"result": "OK"}')


class TornadoServer(object):
    """ Tornado web and websocket server"""

    def __init__(self):
        self.webapp = tornado.web.Application(
            handlers=[
                (r"/ws", WebSocketHandler),
                (r"/get_status", StatusHandler),
                (r"/stop_alert", StopAlertHandler),
                (r"/set_password", JsonHandler),
                (r"/set_device_position", JsonHandler),
                (r"/set_cancel_protected", CancelProtectHandler),
                (r"/set_protect_start", SetProtectStartHandler),
                (r"/set_protect", SetProtectHandler),
                (r"/bell_do", BellHandler),
                (r"/", StaticHandler),
            ],
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            debug=True,
        )

    def set_web_app(self, app):
        self.webapp = app


##MAIN
if __name__ == '__main__':
    k = 0
    json_path = 'json/'
    json_files = os.listdir(json_path)
    num = len(json_files)
    print(json_files, num)


    class WebSocketHandler(tornado.websocket.WebSocketHandler):
        """docstring for SocketHandler"""
        clients = set()

        def check_origin(self, origin):
            return True

        @staticmethod
        def send_to_all(message):
            print(json.dumps(message))
            for c in WebSocketHandler.clients:
                c.write_message(json.dumps(message))

        def every_time(self):
            WebSocketHandler.send_to_all({'event': 'loop'})
            timer = threading.Timer(30, self.every_time)
            timer.setDaemon(True)
            timer.start()

        def open(self):
            WebSocketHandler.clients.add(self)
            self.every_time()

        def on_close(self):
            WebSocketHandler.clients.remove(self)

        def on_message(self, message):
            pass


    class StatusHandler(tornado.web.RequestHandler):

        def get(self):
            global k
            i = k % num

            f = open(json_path + json_files[i], mode='rt')
            self.write(f.read())
            k += 1

    class SetPasswordHandler(tornado.web.RequestHandler):
        def get(self):
            pass


    class SetDevPosHandler(tornado.web.RequestHandler):
        def get(self):
            pass


    class StaticHandler(tornado.web.RequestHandler):
        def get(self):
            self.render('index.html')


    wapp = tornado.web.Application(
        handlers=[
            (r"/ws", WebSocketHandler),
            (r"/get_status", StatusHandler),
            (r"/stop_alert", StopAlertHandler),
            (r"/set_password", SetPasswordHandler),
            (r"/set_device_position", SetDevPosHandler),
            (r"/set_cancel_protected", CancelProtectHandler),
            (r"/set_protect_start", SetProtectHandler),
            (r"/set_protect", SetProtectHandler),
            (r"/bell_do", BellHandler),
            (r"/", StaticHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "template"),
        debug=True,
    )

    app = TornadoServer()
    app.set_web_app(wapp)
    app.webapp.listen(8888)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
