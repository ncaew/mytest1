import hashlib
import ConfigParser


class PwManager(object):
    @staticmethod
    def get_passwd_hash():
        ini_config = ConfigParser.ConfigParser()
        ini_config.read('d:\\config.ini')
        pw = ini_config.get('User', 'psw')
        m = hashlib.md5()
        m.update(pw)
        return m.hexdigest()

    @staticmethod
    def update_passwd(old_psw_md5, new_psw):
        if old_psw_md5 == PswManager.get_passwd_hash():
            ini_file = open("d:\\config.ini", 'w')
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
    pswm.update_passwd('e10adc3949ba59abbe56e057f20f883e', '123456')
    print 'Done.'
