from di import DEPENDENCIES


class InjectedParamNotExists(Exception):
    def __init__(self, message):
        self.message = message


class inject_param(object):
    def __init__(self, flag):
        self.flag = flag

    def __call__(self, original_func, *args, **kwargs):
        def wrapper(*args, **kwargs):
            bind = DEPENDENCIES
            try:
                kwargs[self.flag] = bind[self.flag]()
            except KeyError:
                raise InjectedParamNotExists("The param %s not found in dependencies binding." % self.flag)
            return original_func(*args, **kwargs)

        return wrapper
