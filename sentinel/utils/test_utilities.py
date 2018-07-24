"""Tests utilities"""
# pylint: disable-msg=too-few-public-methods


class StubResponse():
    """StubResponse for requests"""
    def __init__(self, status_code, result):
        self.status_code = status_code
        self.result = result

    def json(self):
        """Return json result"""
        return self.result


class StubDockerSocket():
    """Stub for docker socket requests"""
    def __init__(self, version="18.03.0-ce", node_name="node1", is_manager=True):
        self.set_version = version
        self.node_name = node_name
        self.is_manager = is_manager

    def version(self):
        """Mock get docker version"""
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
        """Mock get docker info"""
        return {
            "Name": self.node_name,
            "Swarm": {
                "NodeAddr": "192.168.50.5",
                "ControlAvailable": self.is_manager,
            }
        }


class Container():
    """Mock Container object return by docker SDK"""
    def __init__(self, container_id, attrs=None):
        self.id = container_id  # pylint: disable-msg=invalid-name
        self.status = attrs["State"]['Status'] if "State" in attrs else "running"
        self.attrs = attrs if attrs else {}


class SwarmService():
    """Mock Swarm service return by docker SDk"""
    def __init__(self, service_id, attrs=None, tasks=()):
        self.id = service_id  # pylint: disable-msg=invalid-name
        self.attrs = attrs if attrs else {}
        self.list_tasks = tasks if isinstance(tasks, list) else []

    def tasks(self):
        """Mock list tasks for a swarm service return by docker SDK"""
        return self.list_tasks


class SwarmNode():
    """Mock Swarm Node return by docker SDK"""
    def __init__(self, attrs=None):
        self.attrs = attrs if attrs else {}
