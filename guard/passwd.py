import hashlib
import ConfigParser
import os
import db_proxy

class PwManager(object):
	@staticmethod
	def get_passwd_hash(systime=''):
		pw = db_proxy.get_key('psw')
		if pw is None:
			pw = '123456'
			db_proxy.set_key('psw', pw)
		md5_hex = hashlib.md5(pw + systime)
		return md5_hex.hexdigest()

	@staticmethod
	def update_passwd(old_psw_md5, new_psw):
		if old_psw_md5 == PwManager.get_passwd_hash():
			db_proxy.set_key('psw', new_psw)
			ret = True
		else:
			ret = False
		return ret


if __name__ == '__main__':
	pswm = PwManager()
	print 'Get: '
	print pswm.get_passwd_hash()
	print '\n'
	print 'Update To: 123456'
	pswm.update_passwd('e10adc3949ba59abbe56e057f20f883e', '123456')
	print 'Done.'
