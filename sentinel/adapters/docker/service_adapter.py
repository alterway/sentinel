from exceptions import NotImplemented
from utils.dependencies_injection import inject_param


class ServiceAdapter():

    def get_services(self):
        raise NotImplemented('Method get_services not implemented')

    def get_services_from_id(self):
        raise NotImplemented('Method get_services_from_id not implemented')

    @inject_param('logger')
    def _has_to_be_registred(self, labels, envs, internal_port, logger=None):
        labels.update(self._get_envs_to_dict(envs))

        if "not_register" in labels:
            if "service_%s_name" % internal_port not in labels and "service_%s_tags" % internal_port not in labels:
                return False

        return True

    @inject_param('logger')
    def _get_tags(self, labels, envs, internal_port, logger=None):
        tags = []
        keys = ["service_tags", "service_%s_tags" % internal_port]
        envs_dict = self._get_envs_to_dict(envs)

        for key in keys:
            if key in labels:
                tags.extend(labels[key].split(','))

            if key in envs_dict:
                tags.extend(envs_dict[key].split(','))

        logger.debug("Tags : %s" % list(set(tags)))

        return list(set(tags))

    @inject_param('logger')
    def _get_name_from_label_and_envs(self, labels, envs, internal_port, logger=None):
        keys = ['service_name', 'service_%s_name' % internal_port]
        envs_dict = self._get_envs_to_dict(envs)

        for key in keys:
            if key in labels:
                return labels[key]

            if key in envs_dict:
                return envs_dict[key]

        return None

    @inject_param('logger')
    def _get_envs_to_dict(self, envs, logger=None):
        envs_dict = {}
        for env in envs:
            envs_dict[env.split('=')[0].lower()] = env.split('=')[1]

        logger.debug("envs : %s" % envs_dict)
        return envs_dict
