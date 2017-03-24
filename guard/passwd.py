import hashlib
import ConfigParser
import os


class PwManager(object):
    @staticmethod
    def get_passwd_hash(systime=''):
        file_path = os.getcwd() + '/config.ini'
        print 'config.ini: ' + file_path

        if os.path.exists(file_path):
            ini_config = ConfigParser.ConfigParser()
            ini_config.read(file_path)
            pw = ini_config.get('User', 'psw')
            md5_hex = hashlib.md5(pw + systime)
            return md5_hex.hexdigest()
        else:
            ini_file = open(file_path, 'w')
            ini_config = ConfigParser.ConfigParser()
            ini_config.add_section('User')
            ini_config.set('User', 'psw', '123456')
            ini_config.write(ini_file)
            ini_file.close()
            md5_hex = hashlib.md5('123456' + systime)
            return md5_hex.hexdigest()

    @staticmethod
    def update_passwd(old_psw_md5, new_psw):
        if old_psw_md5 == PwManager.get_passwd_hash():
            file_path = os.getcwd() + '/config.ini'
            ini_file = open(file_path, 'w')
            ini_config = ConfigParser.ConfigParser()
            ini_config.add_section('User')
            ini_config.set('User', 'psw', new_psw)
            ini_config.write(ini_file)
            ini_file.close()
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
    # pswm.update_passwd('e10adc3949ba59abbe56e057f20f883e', '123456')
    print 'Done.'
