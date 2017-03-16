import threading


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if not hasattr(cls, 'singleton_lock'):
            setattr(cls, 'singleton_lock', threading.Lock())
        if cls not in instances:
            cls.singleton_lock.acquire()
            if cls not in instances:
                instances[cls] = cls(*args, **kw)
            cls.singleton_lock.release()
        return instances[cls]

    return _singleton
