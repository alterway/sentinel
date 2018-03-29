class StubResponse():
    def __init__(self, status_code, result):
        self.status_code = status_code
        self.result = result

    def json(self):
        return self.result


class StubDockerSocket():
    def __init__(self, version="18.03.0-ce", node_name="node1", is_manager=True):
        self.set_version = version
        self.node_name = node_name
        self.is_manager = is_manager

    def version(self):
        return {
            u'KernelVersion': u'4.4.0-116-generic',
            u'Components': [
                {
                    u'Version': u'%s' % self.set_version,
                    u'Name': u'Engine',
                    u'Details': {
                        u'KernelVersion': u'4.4.0-116-generic',
                        u'Os': u'linux',
                        u'BuildTime': u'2018-03-21T23:08:31.000000000+00:00',
                        u'ApiVersion': u'1.37',
                        u'MinAPIVersion': u'1.12',
                        u'GitCommit': u'0520e24',
                        u'Arch': u'amd64',
                        u'Experimental': u'false',
                        u'GoVersion': u'go1.9.4'
                    }
                }
            ],
            u'Arch': u'amd64',
            u'BuildTime': u'2018-03-21T23:08:31.000000000+00:00',
            u'ApiVersion': u'1.37',
            u'Platform': {u'Name': u''},
            u'Version': u'%s' % self.set_version,
            u'MinAPIVersion': u'1.12',
            u'GitCommit': u'0520e24',
            u'Os': u'linux',
            u'GoVersion': u'go1.9.4'
        }

    def info(self):
        return {
            "Name": self.node_name,
            "Swarm": {
                "NodeAddr": "192.168.50.5",
                "ControlAvailable": self.is_manager,
            }
        }


class Container():
    def __init__(self, id, attrs={}):
        self.id = id
        self.status = attrs["State"]['Status'] if "State" in attrs else "running"
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
