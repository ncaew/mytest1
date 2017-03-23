import hashlib

class PwManager(object):

    @staticmethod
    def get_passwd_hash():
        pw = ''
        m = hashlib.md5()
        m.update(pw)
        return m.digest()

    @staticmethod
    def update_passwd(old, new):
        ret = True
        if old == PwManager.get_passwd_hash():
            print("TODO,  update and save passwd")
        else:
            ret = False

        return ret
