#!/usr/bin/python
# coding:utf-8
import os
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpclient
import tornado.websocket
from tornado.escape import json_decode

import json


class TornadoServer(object):
    """ Tornado web and websocket server"""

    class WebSocketHandler(tornado.websocket.WebSocketHandler):
        """docstring for SocketHandler"""
        clients = set()

        def check_origin(self, origin):
            return True

        @staticmethod
        def send_to_all(message):
            for c in TornadoServer.WebSocketHandler.clients:
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
            TornadoServer.WebSocketHandler.clients.add(self)

        def on_close(self):
            TornadoServer.WebSocketHandler.clients.remove(self)
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
            print(self.request.remote_ip)
            print(self.request.body_arguments)
            data = json_decode(self.request.body)
            user = data['user']
            pw = data['passwd']
            print(user, pw)
            jdata = json.dumps(data)
            print(jdata)
            self.write(jdata)

    class StatusHandler(tornado.web.RequestHandler):
        def get(self):
            self.write(json.dumps(test_data))

    class StaticHandler(tornado.web.RequestHandler):
        def get(self):
            self.render('index.html')

    def __init__(self):
        self.webapp = tornado.web.Application(
            handlers=[
                (r"/ws", TornadoServer.WebSocketHandler),
                (r"/get_status", TornadoServer.StatusHandler),
                (r"/disable_alarm", TornadoServer.JsonHandler),
                (r"/set_password", TornadoServer.JsonHandler),
                (r"/set_device_position", TornadoServer.JsonHandler),
                (r"/set_house_status", TornadoServer.JsonHandler),
                (r"/set_guard", TornadoServer.JsonHandler),
                (r"/", TornadoServer.StaticHandler),
            ],
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            debug=True,
        )

    def set_web_app(self, app):
        self.webapp = app


##MAIN
if __name__ == '__main__':
    global test_data

    class WebSocketHandler(tornado.websocket.WebSocketHandler):
        """docstring for SocketHandler"""
        clients = set()

        def check_origin(self, origin):
            return True

        @staticmethod
        def send_to_all(message):
            for c in TornadoServer.WebSocketHandler.clients:
                c.write_message(json.dumps(message))

        def open(self):
            TornadoServer.WebSocketHandler.clients.add(self)

        def on_close(self):
            TornadoServer.WebSocketHandler.clients.remove(self)

        def on_message(self, message):
            pass

    class StatusHandler(tornado.web.RequestHandler):
        def get(self):
            self.write(json.dumps(test_data))

    class DisAlarmHandler(tornado.web.RequestHandler):
        def get(self):
            test_data['alarm_status'] = 'quiet'
            self.write(json.dumps(test_data))


    class SetPasswordHandler(tornado.web.RequestHandler):
        def get(self):
            self.write(json.dumps(test_data))

    class SetDevPosHandler(tornado.web.RequestHandler):
        def get(self):
            self.write(json.dumps(test_data))

    class StaticHandler(tornado.web.RequestHandler):
        def get(self):
            self.render('index.html')
    test_1 = \
        {"status": "protected",
         "_comment_status": "protect_check/protect_starting/protected/unlock_protect/alert/bell_ring/bell_view",
         "guard_status": "guarded", "_comment_guard_status": "guarded/unguarded", "house_status": "outgoing",
         "_comment_house_status": "outgoing/indoors", "protect_stime": "2016-10-10 18:30:00",
         "_comment_protect_stime": "yyyy-MM-dd HH:mm:ss", "bell_status": "standby",
         "_comment_bell_status": "standby/ringing/conversation", "alarm_status": "noalert",
         "_comment_alarm_status": "noalert/alert", "alert_reason": "", "_comment_alert_reason": "用中文描述报警的原因",
         "remain_second": -1, "_comment_remain_second": "-1/0/1/2/... seconds",
         "canprotect": [{"indoors": "can"}, {"outgoing": "can"}],
         "devices_status": [{"type": "door", "position": "户外门", "status_code": "0", "status": "锁定"},
                            {"type": "door", "position": "户内门", "status_code": "1", "status": "未锁"},
                            {"type": "window", "position": "厨房窗", "status_code": "2", "status": "未关闭"},
                            {"type": "smoke", "position": "厨房", "status_code": "3", "status": "未锁"},
                            {"type": "water", "position": "南卧室", "status_code": "4", "status": "未锁"},
                            {"type": "gas", "position": "北卧室", "status_code": "5", "status": "未锁"},
                            {"type": "human", "position": "北卧室", "status_code": "6", "status": "未锁"}]}
    test_2 = \
        {"status": "alert",
         "_comment_status": "protect_check/protect_starting/protected/unlock_protect/alert/bell_ring/bell_view",
         "guard_status": "guarded", "_comment_guard_status": "guarded/unguarded", "house_status": "outgoing",
         "_comment_house_status": "outgoing/indoors", "protect_stime": "2016-10-10 18:30:00",
         "_comment_protect_stime": "yyyy-MM-dd HH:mm:ss", "bell_status": "standby",
         "_comment_bell_status": "standby/ringing/conversation", "alarm_status": "alert",
         "_comment_alarm_status": "noalert/alert", "alert_reason": "厨房窗 未关闭", "_comment_alert_reason": "用中文描述报警的原因",
         "remain_second": -1, "_comment_remain_second": "-1/0/1/2/... seconds",
         "canprotect": [{"indoors": "cannot"}, {"outgoing": "cannot"}],
         "devices_status": [{"type": "door", "position": "户外门", "status_code": "0", "status": "锁定"},
                            {"type": "door", "position": "户内门", "status_code": "1", "status": "未锁"},
                            {"type": "window", "position": "厨房窗", "status_code": "2", "status": "未关闭"},
                            {"type": "smoke", "position": "厨房", "status_code": "3", "status": "未锁"},
                            {"type": "water", "position": "南卧室", "status_code": "4", "status": "未锁"},
                            {"type": "gas", "position": "北卧室", "status_code": "5", "status": "未锁"},
                            {"type": "human", "position": "北卧室", "status_code": "6", "status": "未锁"}]}
    test_3 = \
        {"status": "protect_check",
         "_comment_status": "protect_check/protect_starting/protected/unlock_protect/alert/bell_ring/bell_view",
         "guard_status": "unguarded", "_comment_guard_status": "guarded/unguarded", "house_status": "indoors",
         "_comment_house_status": "outgoing/indoors", "protect_stime": "2016-10-10 18:30:00",
         "_comment_protect_stime": "yyyy-MM-dd HH:mm:ss", "bell_status": "standby",
         "_comment_bell_status": "standby/ringing/conversation", "alarm_status": "noalert",
         "_comment_alarm_status": "noalert/alert", "remain_second": -1,
         "_comment_remain_second": "-1/0/1/2/... seconds", "canprotect": [{"indoors": "can"}, {"outgoing": "cannot"}],
         "devices_status": [{"type": "door", "position": "户外门", "status_code": "0", "status": "锁定"},
                            {"type": "door", "position": "户内门", "status_code": "1", "status": "未锁"},
                            {"type": "window", "position": "厨房窗", "status_code": "2", "status": "未关闭"},
                            {"type": "smoke", "position": "厨房", "status_code": "3", "status": "未锁"},
                            {"type": "water", "position": "南卧室", "status_code": "4", "status": "未锁"},
                            {"type": "gas", "position": "北卧室", "status_code": "5", "status": "未锁"},
                            {"type": "human", "position": "北卧室", "status_code": "6", "status": "未锁"}]}
    test_4 = \
        {"status": "protect_starting",
         "_comment_status": "protect_check/protect_starting/protected/unlock_protect/alert/bell_ring/bell_view",
         "guard_status": "unguarded", "_comment_guard_status": "guarded/unguarded", "house_status": "outgoing",
         "_comment_house_status": "outgoing/indoors", "protect_stime": "2016-10-10 18:30:00",
         "_comment_protect_stime": "yyyy-MM-dd HH:mm:ss", "bell_status": "standby",
         "_comment_bell_status": "standby/ringing/conversation", "alarm_status": "noalert",
         "_comment_alarm_status": "noalert/alert", "remain_second": -1,
         "_comment_remain_second": "-1/0/1/2/... seconds", "canprotect": [{"indoors": "can"}, {"outgoing": "cannot"}],
         "devices_status": [{"type": "door", "position": "户外门", "status_code": "0", "status": "锁定"},
                            {"type": "door", "position": "户内门", "status_code": "1", "status": "未锁"},
                            {"type": "window", "position": "厨房窗", "status_code": "2", "status": "未关闭"},
                            {"type": "smoke", "position": "厨房", "status_code": "3", "status": "未锁"},
                            {"type": "water", "position": "南卧室", "status_code": "4", "status": "未锁"},
                            {"type": "gas", "position": "北卧室", "status_code": "5", "status": "未锁"},
                            {"type": "human", "position": "北卧室", "status_code": "6", "status": "未锁"}]}
    test_5 = \
        {"status": "unlock_protect",
         "_comment_status": "protect_check/protect_starting/protected/unlock_protect/alert/bell_ring/bell_view",
         "guard_status": "unguarded", "_comment_guard_status": "guarded/unguarded", "house_status": "indoors",
         "_comment_house_status": "outgoing/indoors", "protect_stime": "",
         "_comment_protect_stime": "yyyy-MM-dd HH:mm:ss", "bell_status": "standby",
         "_comment_bell_status": "standby/ringing/conversation", "alarm_status": "noalert",
         "_comment_alarm_status": "noalert/alert", "alert_reason": "", "_comment_alert_reason": "用中文描述报警的原因",
         "remain_second": -1, "_comment_remain_second": "-1/0/1/2/... seconds",
         "canprotect": [{"indoors": "cannot"}, {"outgoing": "cannot"}],
         "devices_status": [{"type": "door", "position": "户外门", "status_code": "0", "status": "锁定"},
                            {"type": "door", "uuid": "", "position": "户内门", "status_code": "1", "status": "未锁"},
                            {"type": "window", "position": "厨房窗", "status_code": "2", "status": "未关闭"},
                            {"type": "smoke", "position": "厨房", "status_code": "3", "status": "未锁"},
                            {"type": "water", "position": "南卧室", "status_code": "4", "status": "未锁"},
                            {"type": "gas", "position": "北卧室", "status_code": "5", "status": "未锁"},
                            {"type": "human", "position": "北卧室", "status_code": "6", "status": "未锁"}]}
    test_6 = \
        {"status": "bell_ring",
         "_comment_status": "protect_check/protect_starting/protected/unlock_protect/alert/bell_ring/bell_view",
         "guard_status": "guarded", "_comment_guard_status": "guarded/unguarded", "house_status": "indoors",
         "_comment_house_status": "outgoing/indoors", "protect_stime": "2016-10-10 18:30:00",
         "_comment_protect_stime": "yyyy-MM-dd HH:mm:ss", "bell_status": "ringing",
         "_comment_bell_status": "standby/ringing/conversation", "alarm_status": "noalert",
         "_comment_alarm_status": "noalert/alert", "remain_second": -1,
         "_comment_remain_second": "-1/0/1/2/... seconds", "canprotect": [{"indoors": "can"}, {"outgoing": "cannot"}],
         "devices_status": [{"type": "door", "position": "户外门", "status_code": "0", "status": "锁定"},
                            {"type": "door", "position": "户内门", "status_code": "1", "status": "未锁"},
                            {"type": "window", "position": "厨房窗", "status_code": "2", "status": "未关闭"},
                            {"type": "smoke", "position": "厨房", "status_code": "3", "status": "未锁"},
                            {"type": "water", "position": "南卧室", "status_code": "4", "status": "未锁"},
                            {"type": "gas", "position": "北卧室", "status_code": "5", "status": "未锁"},
                            {"type": "human", "position": "北卧室", "status_code": "6", "status": "未锁"}]}
    test_7 = \
        {"status": "bell_view",
         "_comment_status": "protect_check/protect_starting/protected/unlock_protect/alert/bell_ring/bell_view",
         "guard_status": "guarded", "_comment_guard_status": "guarded/unguarded", "house_status": "indoors",
         "_comment_house_status": "outgoing/indoors", "protect_stime": "2016-10-10 18:30:00",
         "_comment_protect_stime": "yyyy-MM-dd HH:mm:ss", "bell_status": "conversation",
         "_comment_bell_status": "standby/ringing/conversation", "alarm_status": "noalert",
         "_comment_alarm_status": "noalert/alert", "remain_second": -1,
         "_comment_remain_second": "-1/0/1/2/... seconds", "canprotect": [{"indoors": "can"}, {"outgoing": "cannot"}],
         "devices_status": [{"type": "door", "position": "户外门", "status_code": "0", "status": "锁定"},
                            {"type": "door", "position": "户内门", "status_code": "1", "status": "未锁"},
                            {"type": "window", "position": "厨房窗", "status_code": "2", "status": "未关闭"},
                            {"type": "smoke", "position": "厨房", "status_code": "3", "status": "未锁"},
                            {"type": "water", "position": "南卧室", "status_code": "4", "status": "未锁"},
                            {"type": "gas", "position": "北卧室", "status_code": "5", "status": "未锁"},
                            {"type": "human", "position": "北卧室", "status_code": "6", "status": "未锁"}]}

    test_data = test_1
    wapp = tornado.web.Application(
            handlers=[
                (r"/ws", WebSocketHandler),
                (r"/get_status", StatusHandler),
                (r"/disable_alarm", DisAlarmHandler),
                (r"/set_password", SetPasswordHandler),
                (r"/set_device_position", SetDevPosHandler),
                (r"/set_house_status", TornadoServer.JsonHandler),
                (r"/set_guard", TornadoServer.JsonHandler),
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
