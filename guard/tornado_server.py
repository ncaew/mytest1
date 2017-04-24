#!/usr/bin/python
# coding:utf-8
import os
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpclient
import tornado.websocket
import uuid
import threading
import json
from state import StateControl
import logging
logger = logging.getLogger(__name__)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """docstring for SocketHandler"""
    clients = set()

    def check_origin(self, origin):
        return True

    @staticmethod
    def send_to_all(message):
        logger.debug(message)
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


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        # self.set_header('Access-Control-Allow-Headers', 'origin, x-csrftoken, content-type, accept')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')
        
    def get_cookie_id(self):
        cookie_id =  self.get_cookie("cookie_id", "")
        if cookie_id == "":
            cookie_id = str(uuid.uuid4())
            print "new cookie_id = " + cookie_id
            self.set_cookie("cookie_id", cookie_id)
        return cookie_id

class StatusHandler(BaseHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        # self.set_header('Access-Control-Allow-Headers', 'origin, x-csrftoken, content-type, accept')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')
        

    def get(self):
        cookie_id = self.get_cookie_id()
        info = StateControl().get_status(cookie_id)
        self.write(info)


class SetProtectStartHandler(BaseHandler):
    def get(self):

        mode = self.get_argument('protect', 'unknown')
        cookie_id = self.get_cookie_id()
        StateControl().new_event_from_webservice("set_protect_start",dict(mode=mode,cookie_id=cookie_id))
        ##StateControl().set_protect_start(mode)

        # info = dict(handler=self.__class__.__name__, action='', result='OK')
        # event = dict(event='StatusChanged', info=info)
        # WebSocketHandler.send_to_all(event)

        self.write('{"result":"OK"}')


class StaticHandler(BaseHandler):
    def get(self):
        self.render('index.html')


class CancelProtectHandler(BaseHandler):
    count = 0

    def get(self):
        from passwd import PwManager
        CancelProtectHandler.count += 1
        mode = self.get_argument('mode', 'unknown')
        action = self.get_argument('action', 'unknown')
        passwd = self.get_argument('passwd', 'unknown')
        systime = self.get_argument('systime', 'unknown')
        cookie_id = self.get_cookie_id()
        if action == 'ok' and passwd != PwManager.get_passwd_hash(systime):
            retv = '{"result":"NOK"}'
            passwd="wrong"
        else:
            retv = '{"result":"OK"}'
            passwd="correct"
            
        StateControl().new_event_from_webservice("cancel_protect",dict(mode=mode, action=action, password=passwd, systime=systime,cookie_id=cookie_id))
        
        self.write(retv)


class StopAlertHandler(BaseHandler):
    def get(self):
        alert_id = self.get_argument('alertid', '')

        StateControl().new_event_from_webservice("stop_alert",dict(alertid=alert_id))
        #StateControl().stop_alert(alertid=alert_id)

        # info = dict(handler=self.__class__.__name__, action='', result='OK')
        # event = dict(event='StatusChanged', info=info)
        # WebSocketHandler.send_to_all(event)

        self.write('{"result": "OK"}')


class SetProtectHandler(BaseHandler):
    def get(self):
        result = self.get_argument('result', '')
        cookie_id = self.get_cookie_id()
        StateControl().new_event_from_webservice("set_protect",dict(result=result,cookie_id=cookie_id))
        #StateControl().set_protect(result)

        # info = dict(handler=self.__class__.__name__, action='', result='OK')
        # event = dict(event='StatusChanged', info=info)
        # WebSocketHandler.send_to_all(event)

        self.write('{"result": "OK"}')


class SetDevAliasHandler(BaseHandler):
    def get(self):
        from oicmgr import OicDeviceManager
        result = 'OK'
        devid = self.get_argument('uuid', '')
        oldname = self.get_argument('oldname', '')
        newname = self.get_argument('newname', '')

        if devid == '':
            result = 'NOK'
        if newname == '':
            result = 'NOK'
        if oldname != newname and newname != '':
            result = 'OK' if OicDeviceManager().update_device_alias(devid, newname) else 'NOK'

        info = {'result': result, 'devices_status': OicDeviceManager().get_devices()}
        self.write(json.dumps(info))

class SetDevAttrHandler(BaseHandler):
    def get(self):
        from oicmgr import OicDeviceManager
        result = 0 #0 mean 'OK'
        devid = self.get_argument('uuid', '')
        posname = self.get_argument('posname', '')
        aliasname = self.get_argument('aliasname', '')
        outdoor = self.get_argument('outdoor', '')
        inhome = self.get_argument('inhome', '')
        
        if devid == '':
            result = 1
        else:
            if aliasname != ''and  OicDeviceManager().update_device_alias(devid, aliasname) == False:
                result += 1
            if posname !=  ''and OicDeviceManager().update_device_posname(devid, posname) == False :
                result += 1
            if outdoor !=  '' and OicDeviceManager().update_device_con_out(devid, outdoor) == False:
                result += 1
            if inhome !=  '' and OicDeviceManager().update_device_con_in(devid, inhome) == False:
                result += 1
    
                    #convert str from num ( 0 == OK )
        result = 'NOK' if result >0 else 'OK'
        info = {'result': result, 'devices_status': OicDeviceManager().get_devices()}
        
        self.write(json.dumps(info))
        logging.info("%s %s (aliasname:%s ,posname:%s, outdoor:%s,inhome:%s) %s %s"%("SetDevAttr",devid,aliasname,posname,outdoor,inhome," return:",json.dumps(info)))

class GetDevicesListHandler(BaseHandler):
    def get(self):
        from oicmgr import OicDeviceManager
        info = {'devices_status': OicDeviceManager().get_devices()}
        self.write(json.dumps(info))


class GetPWHandler(BaseHandler):
    def get(self):
        from passwd import PwManager
        pw = PwManager.get_passwd_hash()

        info = {'protect_pw': pw}
        self.write(json.dumps(info))


class ChangePWHandler(BaseHandler):
    def get(self):
        from passwd import PwManager
        oldpw = self.get_argument('oldpw', '')
        newpw = self.get_argument('newpw', '')
        res = 'OK' if PwManager.update_passwd(oldpw, newpw) else 'NOK'
        info = {'result': res}
        self.write(json.dumps(info))


class BellHandler(BaseHandler):
    def get(self):
        bellid = self.get_argument('bellid', '')
        action = self.get_argument('action', '')
        print("BellHandler", bellid, action)

        StateControl().new_event_from_webservice("bell_do",dict(bellid=bellid,action=action))
        #StateControl().bell_do(bellid=bellid, action=action)

        # info = dict(handler=self.__class__.__name__, action=action, result='OK')
        # event = dict(event='StatusChanged', info=info)
        # WebSocketHandler.send_to_all(event)

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
                (r"/set_cancel_protected", CancelProtectHandler),
                (r"/set_protect_start", SetProtectStartHandler),
                (r"/set_protect", SetProtectHandler),
                (r"/get_devices_list", GetDevicesListHandler),
                (r"/set_device_alias", SetDevAliasHandler),
                (r"/set_device_attr", SetDevAttrHandler),
                (r"/get_protect_pw", GetPWHandler),
                (r"/ch_passwd", ChangePWHandler),
                (r"/bell_do", BellHandler),
                (r"/", StaticHandler),
            ],
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
            log_function=lambda x: None
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


    class StatusHandler(BaseHandler):

        def get(self):
            global k
            i = k % num

            f = open(json_path + json_files[i], mode='rt')
            self.write(f.read())
            k += 1

    class SetPasswordHandler(BaseHandler):
        def get(self):
            pass


    class StaticHandler(BaseHandler):
        def get(self):
            self.render('index.html')


    wapp = tornado.web.Application(
        handlers=[
            (r"/ws", WebSocketHandler),
            (r"/get_status", StatusHandler),
            (r"/stop_alert", StopAlertHandler),
            (r"/set_password", SetPasswordHandler),
            (r"/set_cancel_protected", CancelProtectHandler),
            (r"/set_protect_start", SetProtectHandler),
            (r"/set_protect", SetProtectHandler),
            (r"/get_devices_list", GetDevicesListHandler),
            (r"/set_device_alias", SetDevAliasHandler),
            (r"/set_device_attr", SetDevAttrHandler),
            (r"/get_protect_pw", GetPWHandler),
            (r"/ch_passwd", ChangePWHandler),
            (r"/bell_do", BellHandler),
            (r"/", StaticHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
    )

    
    app = TornadoServer()
    app.set_web_app(wapp)
    app.webapp.listen(8888)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
