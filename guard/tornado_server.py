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
        self.write(json.dumps(info))


class StaticHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class TornadoServer(object):
    """ Tornado web and websocket server"""

    def __init__(self):
        self.webapp = tornado.web.Application(
            handlers=[
                (r"/ws", WebSocketHandler),
                (r"/get_status", StatusHandler),
                (r"/disable_alarm", JsonHandler),
                (r"/set_password", JsonHandler),
                (r"/set_device_position", JsonHandler),
                (r"/set_house_status", JsonHandler),
                (r"/set_guard", JsonHandler),
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
            timer = threading.Timer(2, self.every_time)
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


    class DisAlarmHandler(tornado.web.RequestHandler):
        def get(self):
            pass


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
            (r"/disable_alarm", DisAlarmHandler),
            (r"/set_password", SetPasswordHandler),
            (r"/set_device_position", SetDevPosHandler),
            (r"/set_house_status", JsonHandler),
            (r"/set_guard", JsonHandler),
            (r"/", StaticHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "template"),
        debug=True,
    )

    app = TornadoServer()
    app.set_web_app(wapp)
    app.webapp.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
