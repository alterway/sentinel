# pylint: skip-file
"""Service Base implements ServiceInterface and ServiceBase to inherit in services"""

import re
from zope.interface import implementer
from discovery.layers.domain.service.generalisation.interface.service import ServiceInterface
from ddd_domain_driven_design.domain.utils.multiton import Multiton


@implementer(ServiceInterface)
class ServiceBase(metaclass=Multiton):
    """Adapter to manage docker service"""

    def __init__(self, logger=None):
        self.logger = logger

    def _has_to_be_registred(self, labels, envs, internal_port):
        labels.update(self._get_envs_to_dict(envs))

        # if "not_register" in labels:
        if (
            "not_register" in labels or (
                "service_%s_name" % internal_port not in labels and
                "service_%s_tags" % internal_port not in labels
            )
        ):
            return False

        return True

    def _get_tags(self, labels, envs, internal_port):
        tags = []
        keys = ["service_tags", "service_%s_tags" % internal_port]
        envs_dict = self._get_envs_to_dict(envs)

        for key in keys:
            if key in labels:
                tags.extend(labels[key].split(','))

            if key in envs_dict:
                tags.extend(envs_dict[key].split(','))

        self.logger.debug("Tags : %s", list(set(tags)))

        return list(set(tags))

    def _get_name_from_label_and_envs(self, labels, envs, internal_port):
        keys = ['service_name', 'service_%s_name' % internal_port]
        envs_dict = self._get_envs_to_dict(envs)

        for key in keys:
            if key in labels:
                return self._trim_service_name(labels[key])

            if key in envs_dict:
                return self._trim_service_name(envs_dict[key])

        return None

    def _get_envs_to_dict(self, envs):
        envs_dict = {}
        for env in envs:
            envs_dict[env.split('=')[0].lower()] = env.split('=')[1]

        self.logger.debug("envs : %s", envs_dict)
        return envs_dict

    @staticmethod
    def _trim_service_name(service_name):
        return re.sub('[^A-Za-z0-9---_.]+', '', service_name).replace('_', '-')
