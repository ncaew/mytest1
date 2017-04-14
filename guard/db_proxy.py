import hashlib
import ConfigParser
import os
db_file_path = os.getcwd() + '/db.ini'
def check_db():
	
	if not os.path.exists(db_file_path):
		ini_file = open(db_file_path, 'w')
		ini_config = ConfigParser.ConfigParser()
		ini_config.add_section('User')
		ini_config.set('User', 'stub', '')
		ini_config.write(ini_file)
		ini_file.close()
		return False
	return True

def get_value_from_cache(key_name):
	return ""

def update_cache(key_name,value):
	return

def get_key(key_name):

	if check_db() == False:
		return ""
	
	#first return from memory cache
	v_cache =  get_value_from_cache(key_name)
	if v_cache != "":
		return v_cache

	ini_config = ConfigParser.ConfigParser()
	ini_config.read(db_file_path)
	try:
		if key_name == 'psw':
			value= ini_config.get('User', key_name)
		else:#other key
			value= ini_config.get('User', key_name)
	except Exception as e:
		value = None
		
	return value


def set_key(key_name,value):
 
	check_db()
	ini_file = open(db_file_path, 'w')
	ini_config = ConfigParser.ConfigParser()
	ini_config.add_section('User')
	ini_config.set('User', key_name, value)
	ini_config.write(ini_file)
	ini_file.close()
	
	update_cache(key_name,value)
	pass

