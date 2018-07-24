from dependencies_injection.inject_param import inject_param
from zope.interface import Interface
import re


class ServiceInterface(Interface):  # pylint: disable-msg=inherit-non-class
    '''Interface to manage docker service'''

    def get_services(cls, **kwargs):  # pylint: disable-msg=no-method-argument  # noqa
        '''Create services object from docker services'''

    def get_services_from_id(cls, service_id, **kwargs): # noqa
        '''Create services object from one docker service'''


class ServiceBase(object):
    '''Adapter to manage docker service'''

    @classmethod
    def _has_to_be_registred(cls, labels, envs, internal_port):
        labels.update(cls._get_envs_to_dict(envs))

        if "not_register" in labels:
            if "service_%s_name" % internal_port not in labels and "service_%s_tags" % internal_port not in labels:
                return False

        return True

    @classmethod
    @inject_param('logger')
    def _get_tags(cls, labels, envs, internal_port, logger=None):
        tags = []
        keys = ["service_tags", "service_%s_tags" % internal_port]
        envs_dict = cls._get_envs_to_dict(envs)

        for key in keys:
            if key in labels:
                tags.extend(labels[key].split(','))

            if key in envs_dict:
                tags.extend(envs_dict[key].split(','))

        logger.debug("Tags : %s" % list(set(tags)))

        return list(set(tags))

    @classmethod
    def _get_name_from_label_and_envs(cls, labels, envs, internal_port):
        keys = ['service_name', 'service_%s_name' % internal_port]
        envs_dict = cls._get_envs_to_dict(envs)

        for key in keys:
            if key in labels:
                return cls._trim_service_name(labels[key])

            if key in envs_dict:
                return cls._trim_service_name(envs_dict[key])

        return None

    @staticmethod
    @inject_param('logger')
    def _get_envs_to_dict(envs, logger=None):
        envs_dict = {}
        for env in envs:
            envs_dict[env.split('=')[0].lower()] = env.split('=')[1]

        logger.debug("envs : %s" % envs_dict)
        return envs_dict

    @staticmethod
    def _trim_service_name(service_name):
        return re.sub('[^A-Za-z0-9---_.]+', '', service_name).replace('_', '-')
