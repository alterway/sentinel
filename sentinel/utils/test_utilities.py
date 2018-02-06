class StubResponse():
    def __init__(self, status_code, result):
        self.status_code = status_code
        self.result = result

    def json(self):
        return self.result


class Container():
    def __init__(self, id, status='created', attrs={}):
        self.id = id
        self.status = status
        self.attrs = attrs


class SwarmService():
    def __init__(self, id, attrs={}):
        self.id = id
        self.attrs = attrs


class SwarmNode():
    def __init__(self, attrs={}):
        self.attrs = attrs
