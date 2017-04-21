#! /usr/bin/python
# coding=utf8

import ConfigParser
import base64
import os

db_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ini_hold_chinese.ini'))

user_name = '中文字符串'

if not os.path.exists(db_file_path):
    ini_file = open(db_file_path, 'w')
    ini_config = ConfigParser.ConfigParser()
    ini_config.add_section('User')
    value = base64.urlsafe_b64encode(user_name)
    ini_config.set('User', 'Name', value)
    ini_config.set('User', 'Name2', user_name)
    ini_config.write(ini_file)
    ini_file.close()
else:
    ini_config = ConfigParser.ConfigParser()
    ini_config.read(db_file_path)
    value = ini_config.get('User', 'Name')
    user_name_from_ini = base64.urlsafe_b64decode(value)
    print user_name_from_ini
    print ini_config.get('User', 'Name2')
