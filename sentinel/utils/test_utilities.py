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
    def __init__(self, id, attrs={}, tasks=[]):
        self.id = id
        self.attrs = attrs
        self.list_tasks = tasks

    def tasks(self):
        return self.list_tasks


class SwarmNode():
    def __init__(self, attrs={}):
        self.attrs = attrs
